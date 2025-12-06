"""/src/api/conversations/routing.py"""

from datetime import datetime

from api.signals.coherence_service import calculate_and_persist_coherence
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from .models import (
    CoherenceResponseSchema,
    ConversationCreateSchema,
    ConversationModel,
    ConversationReadSchema,
    ConversationUpdateSchema,
    SignalDriftMetricReadSchema,
)

router = APIRouter()


def get_db_session():
    """Get database session - deferred import to avoid circular dependency"""
    from api.db.session import get_session as _get_session

    yield from _get_session()


# POST /api/conversations/
@router.post("/", response_model=ConversationReadSchema)
def create_conversation(
    payload: ConversationCreateSchema, session: Session = Depends(get_db_session)
):
    """Create a new conversation/session."""
    data = payload.model_dump()

    # Set started_at to now if not provided
    if data.get("started_at") is None:
        data["started_at"] = datetime.utcnow()

    conv = ConversationModel.model_validate(data)
    session.add(conv)
    session.commit()
    session.refresh(conv)
    return conv


# GET /api/conversations/{conversation_id}
@router.get("/{conversation_id}", response_model=ConversationReadSchema)
def get_conversation(conversation_id: str, session: Session = Depends(get_db_session)):
    """Retrieve conversation details."""
    query = select(ConversationModel).where(ConversationModel.id == conversation_id)
    result = session.exec(query).first()
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


# PATCH /api/conversations/{conversation_id}
@router.patch("/{conversation_id}", response_model=ConversationReadSchema)
def update_conversation(
    conversation_id: str,
    payload: ConversationUpdateSchema,
    session: Session = Depends(get_db_session),
):
    """Update conversation (end_at, coherence scores)."""
    query = select(ConversationModel).where(ConversationModel.id == conversation_id)
    conv = session.exec(query).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Update fields
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(conv, key, value)

    session.add(conv)
    session.commit()
    session.refresh(conv)
    return conv


# GET /api/conversations/{conversation_id}/coherence
@router.get("/{conversation_id}/coherence", response_model=CoherenceResponseSchema)
def get_coherence(
    conversation_id: str,
    window_size: str = Query(default="5m"),
    session: Session = Depends(get_db_session),
):
    """Get coherence metrics for a conversation.

    This endpoint calculates and persists coherence metrics to the database:
    
    Parameters:
    - window_size: Time window for drift calculation (e.g., "5m", "1h")

    Returns:
    - Current coherence score (persisted to conversations table)
    - Coherence trend (persisted to conversations table)
    - Drift metrics over sliding windows (persisted to signal_drift_metrics table)
    - Signal breakdown by source
    
    All metrics are stored in the database for historical analysis.
    """
    # Import here to avoid circular dependency
    from api.signals.models import SignalModel

    # Get conversation
    query = select(ConversationModel).where(ConversationModel.id == conversation_id)
    conv = session.exec(query).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get all signals in conversation
    signals_query = (
        select(SignalModel)
        .where(SignalModel.context_window_id == conversation_id)
        .order_by(SignalModel.time)  # type: ignore
    )
    signals = session.exec(signals_query).fetchall()

    if not signals:
        return CoherenceResponseSchema(
            id=conversation_id,
            coherence_score_current=None,
            coherence_score_trend=None,
            drift_metrics=[],
            signal_sources={},
            total_signal_count=0,
        )

    # Calculate and persist coherence metrics
    # This function handles:
    # 1. Calculating drift metrics
    # 2. Saving drift metrics to signal_drift_metrics table
    # 3. Calculating coherence score
    # 4. Saving coherence score to conversations table
    # 5. Calculating trend (if available)
    # 6. Saving trend to conversations table
    result = calculate_and_persist_coherence(
        conversation_id=conversation_id,
        signals=signals,
        window_size=window_size,
        session=session,
    )

    # Convert drift metrics to response schema
    drift_metrics = [
        SignalDriftMetricReadSchema(
            id=m.get("id", 0),
            conversation_id=conversation_id,
            window_start=m["window_start"],
            window_end=m["window_end"],
            drift_score=m["drift_score"],
            signal_count=m["signal_count"],
            coherence_trend=m.get("coherence_trend"),
        )
        for m in result["drift_metrics"]
    ]

    return CoherenceResponseSchema(
        id=conversation_id,
        coherence_score_current=result["coherence_score_current"],
        coherence_score_trend=result["coherence_score_trend"],
        drift_metrics=drift_metrics,
        signal_sources=result["signal_sources"],
        total_signal_count=result["total_signal_count"],
        time_range_start=result["time_range_start"],
        time_range_end=result["time_range_end"],
    )
