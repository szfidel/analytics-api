"""/src/api/conversations/routing.py"""

from datetime import datetime

from api.signals.coherence_scorer import compute_coherence_from_drift
from api.signals.drift_calculator import compute_drift_over_windows, parse_window_size
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
    query = select(ConversationModel).where(ConversationModel.id == conversation_id)
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

    # Parse window size (e.g., "5m" -> 300 seconds)
    window_seconds = parse_window_size(window_size)

    # Compute drift metrics over sliding windows
    drift_metrics_raw = compute_drift_over_windows(signals, window_seconds)
    drift_metrics = [
        SignalDriftMetricReadSchema(
            id=0,
            conversation_id=conversation_id,
            window_start=m["window_start"],
            window_end=m["window_end"],
            drift_score=m["drift_score"],
            signal_count=m["signal_count"],
            coherence_trend=None,
        )
        for m in drift_metrics_raw
    ]

    # Count signals by source
    signal_sources = {}
    for signal in signals:
        source = signal.signal_source
        signal_sources[source] = signal_sources.get(source, 0) + 1

    # Compute overall coherence from drift and signals
    coherence_score = compute_coherence_from_drift(drift_metrics_raw, signals)

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
