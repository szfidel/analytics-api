"""/src/api/signals/routing.py"""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, select
from timescaledb.hyperfunctions import time_bucket

from .models import (
    SignalBucketSchema,
    SignalCreateSchema,
    SignalModel,
    SignalBatchSchema,
    SignalBatchResponseSchema,
    SignalBatchItemResponse,
)

router = APIRouter()


def get_db_session():
    """Get database session - deferred import to avoid circular dependency"""
    from api.db.session import get_session as _get_session
    yield from _get_session()


# GET /api/signals/
@router.get("/", response_model=list[SignalBucketSchema])
def read_signals(
    duration: str = Query(default="1 day"),
    context_window_id: str | None = Query(default=None),
    signal_sources: list = Query(default=None),
    session: Session = Depends(get_db_session),
):
    """List signals with time-bucketing and aggregation.
    
    Query Parameters:
    - duration: Time bucket duration (e.g., "1 hour", "7 days")
    - context_window_id: Filter by conversation ID
    - signal_sources: Filter by signal sources
    """
    bucket = time_bucket(duration, SignalModel.time)
    lookup_signal_sources = (
        signal_sources
        if isinstance(signal_sources, list) and len(signal_sources) > 0
        else None
    )

    query = (
        select(
            bucket.label("bucket"),
            SignalModel.signal_source.label("signal_source"),
            SignalModel.agent_id.label("agent_id"),
            func.avg(SignalModel.signal_score).label("avg_signal_score"),
            func.avg(SignalModel.emotional_tone).label("avg_emotional_tone"),
            func.count().label("total_count"),
        )
        .group_by(
            bucket,
            SignalModel.signal_source,
            SignalModel.agent_id,
        )
        .order_by(
            bucket,
            SignalModel.signal_source,
            SignalModel.agent_id,
        )
    )

    if context_window_id:
        query = query.where(SignalModel.context_window_id == context_window_id)

    if lookup_signal_sources:
        query = query.where(SignalModel.signal_source.in_(lookup_signal_sources))

    results = session.exec(query).fetchall()
    return results


# POST /api/signals/
@router.post("/", response_model=SignalModel)
def create_signal(payload: SignalCreateSchema, session: Session = Depends(get_db_session)):
    """Create a new signal.
    
    Parameters:
    - raw_content: Text/message content
    - context_window_id: Conversation ID (required)
    - signal_source: Source identifier (Axis, M, Neo, person, Slack, etc.)
    - signal_score: 0-1 coherence strength
    - signal_vector: Pinecone vector DB reference
    """
    data = payload.model_dump()

    # Serialize payload dict to JSON string for storage
    if data.get("payload") is not None:
        data["payload"] = json.dumps(data["payload"])

    # Create SignalModel instance and persist to database
    obj = SignalModel.model_validate(data)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


# GET /api/signals/{signal_id}
@router.get("/{signal_id}", response_model=SignalModel)
def get_signal(signal_id: int, session: Session = Depends(get_db_session)):
    """Retrieve a single signal by ID."""
    query = select(SignalModel).where(SignalModel.id == signal_id)
    result = session.exec(query).first()
    if not result:
        raise HTTPException(status_code=404, detail="Signal not found")
    return result


# POST /api/signals/batch
@router.post("/batch", response_model=SignalBatchResponseSchema)
def create_signals_batch(
    batch: SignalBatchSchema,
    session: Session = Depends(get_db_session),
):
    """Create multiple signals in a single batch transaction.
    
    Supports two modes:
    - fail_on_error=True: All-or-nothing ACID semantics (rollback on first error)
    - fail_on_error=False: Best-effort (continue processing, report errors)
    
    Parameters:
    - signals: List of signal objects to create
    - fail_on_error: If True, rollback entire batch on first error
    
    Returns detailed results for each signal with success/error status.
    """
    results: list[SignalBatchItemResponse] = []
    successful_count = 0
    failed_count = 0
    
    try:
        for index, signal_data in enumerate(batch.signals):
            try:
                # Convert payload dict to JSON string if present
                data = signal_data.model_dump()
                if data.get("payload") is not None:
                    data["payload"] = json.dumps(data["payload"])
                
                # Create and persist signal
                obj = SignalModel.model_validate(data)
                session.add(obj)
                session.flush()  # Flush to get the ID without committing
                
                results.append(
                    SignalBatchItemResponse(
                        index=index,
                        success=True,
                        signal_id=obj.id,
                    )
                )
                successful_count += 1
                
            except Exception as e:
                failed_count += 1
                error_msg = str(e)
                results.append(
                    SignalBatchItemResponse(
                        index=index,
                        success=False,
                        error=error_msg,
                    )
                )
                
                # If fail_on_error is True, rollback entire batch
                if batch.fail_on_error:
                    session.rollback()
                    raise HTTPException(
                        status_code=400,
                        detail=f"Batch failed at index {index}: {error_msg}. No signals were created."
                    )
        
        # Commit all successful signals
        session.commit()
        
        return SignalBatchResponseSchema(
            total_count=len(batch.signals),
            successful_count=successful_count,
            failed_count=failed_count,
            results=results,
        )
        
    except HTTPException:
        raise  # Re-raise HTTPException from fail_on_error mode
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during batch processing: {str(e)}"
        )


# GET /api/signals/conversation/{context_window_id}
@router.get("/conversation/{context_window_id}", response_model=list[SignalModel])
def get_signals_by_conversation(
    context_window_id: str,
    limit: int = Query(default=100),
    session: Session = Depends(get_db_session),
):
    """Retrieve all signals in a conversation."""
    query = (
        select(SignalModel)
        .where(SignalModel.context_window_id == context_window_id)
        .order_by(SignalModel.time)
        .limit(limit)
    )
    results = session.exec(query).fetchall()
    return results
