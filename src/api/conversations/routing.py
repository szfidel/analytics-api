"""/src/api/conversations/routing.py"""

import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
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
def get_conversation(
    conversation_id: str, session: Session = Depends(get_db_session)
):
    """Retrieve conversation details."""
    query = select(ConversationModel).where(
        ConversationModel.id == conversation_id
    )
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
    query = select(ConversationModel).where(
        ConversationModel.id == conversation_id
    )
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
@router.get(
    "/{conversation_id}/coherence", response_model=CoherenceResponseSchema
)
def get_coherence(
    conversation_id: str,
    window_size: str = Query(default="5m"),
    session: Session = Depends(get_db_session),
):
    """Get coherence metrics for a conversation.
    
    Parameters:
    - window_size: Time window for drift calculation (e.g., "5m", "1h")
    
    Returns:
    - Current coherence score
    - Coherence trend
    - Drift metrics over sliding windows
    - Signal breakdown by source
    """
    # Import here to avoid circular dependency
    from api.signals.models import SignalModel
    
    # Get conversation
    query = select(ConversationModel).where(
        ConversationModel.id == conversation_id
    )
    conv = session.exec(query).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get all signals in conversation
    signals_query = (
        select(SignalModel)
        .where(SignalModel.context_window_id == conversation_id)
        .order_by(SignalModel.time.asc())  # type: ignore
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
    
    # Parse window size (simplified: "5m" -> 5 minutes, "1h" -> 1 hour)
    window_seconds = _parse_window_size(window_size)
    
    # Compute drift metrics over sliding windows
    drift_metrics = _compute_drift_metrics(signals, window_seconds, session)
    
    # Count signals by source
    signal_sources = {}
    for signal in signals:
        source = signal.signal_source
        signal_sources[source] = signal_sources.get(source, 0) + 1
    
    # Compute overall coherence from drift and signals
    coherence_score = _compute_coherence(drift_metrics, signals)
    
    time_range_start = signals[0].time if signals else None
    time_range_end = signals[-1].time if signals else None
    
    return CoherenceResponseSchema(
        id=conversation_id,
        coherence_score_current=coherence_score,
        coherence_score_trend=None,  # TODO: compute trend
        drift_metrics=drift_metrics,
        signal_sources=signal_sources,
        total_signal_count=len(signals),
        time_range_start=time_range_start,
        time_range_end=time_range_end,
    )


def _parse_window_size(window_str: str) -> int:
    """Parse window size string (e.g., '5m', '1h') into seconds."""
    window_str = window_str.strip().lower()
    
    if window_str.endswith("m"):
        return int(window_str[:-1]) * 60
    elif window_str.endswith("h"):
        return int(window_str[:-1]) * 3600
    elif window_str.endswith("s"):
        return int(window_str[:-1])
    else:
        # Default to 5 minutes
        return 300


def _compute_drift_metrics(
    signals, window_seconds: int, session: Session
) -> list[SignalDriftMetricReadSchema]:
    """Compute drift metrics over sliding windows.
    
    Drift = moving variance of signal_scores within each window.
    """
    if not signals:
        return []
    
    metrics = []
    first_time = signals[0].time
    last_time = signals[-1].time
    
    # Create sliding windows
    current_start = first_time
    while current_start < last_time:
        current_end = current_start + timedelta(seconds=window_seconds)
        
        # Get signals in this window
        window_signals = [
            s for s in signals
            if current_start <= s.time < current_end
        ]
        
        if window_signals:
            # Compute variance of signal_scores
            signal_scores = [s.signal_score for s in window_signals]
            drift = _compute_variance(signal_scores)
            
            metric = SignalDriftMetricReadSchema(
                id=0,  # Placeholder, would be generated from DB
                conversation_id=signals[0].context_window_id,
                window_start=current_start,
                window_end=current_end,
                drift_score=drift,
                signal_count=len(window_signals),
                coherence_trend=None,
            )
            metrics.append(metric)
        
        current_start = current_end
    
    return metrics


def _compute_variance(values: list[float]) -> float:
    """Compute variance of a list of values, normalized to 0-1."""
    if not values or len(values) < 2:
        return 0.0
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    
    # Normalize to 0-1 (max variance is 0.25 for uniform 0-1 distribution)
    # Clamp between 0 and 1
    normalized_variance = min(1.0, variance * 4)
    return normalized_variance


def _compute_coherence(
    drift_metrics: list[SignalDriftMetricReadSchema],
    signals,
) -> float:
    """Compute coherence score from drift metrics.
    
    Simple formula: coherence = 1 - avg(drift_scores)
    """
    if not drift_metrics or not signals:
        # If no drift metrics, use average signal score
        if signals:
            avg_signal_score = sum(s.signal_score for s in signals) / len(signals)
            return avg_signal_score
        return 0.5
    
    avg_drift = sum(m.drift_score for m in drift_metrics) / len(drift_metrics)
    coherence = max(0.0, min(1.0, 1.0 - avg_drift))
    
    return coherence
