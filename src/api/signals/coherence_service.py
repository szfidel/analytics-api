"""/src/api/signals/coherence_service.py

Service module for coherence calculations with database persistence.
Handles computing and storing drift metrics and coherence scores.
"""

from sqlmodel import Session, select

from api.signals.coherence_scorer import compute_coherence_from_drift
from api.signals.drift_calculator import (
    compute_drift_over_windows,
    parse_window_size,
)


def calculate_and_persist_coherence(
    conversation_id: str,
    signals,
    window_size: str = "5m",
    session: Session | None = None,
) -> dict:
    """Calculate coherence metrics and persist them to the database.
    
    This is the main service function that:
    1. Calculates drift metrics over time windows
    2. Persists drift metrics to signal_drift_metrics table
    3. Calculates coherence scores
    4. Updates conversation with coherence scores
    5. Returns the complete coherence response
    
    Parameters:
        conversation_id: The conversation/context window ID
        signals: List of SignalModel objects
        window_size: Time window string (e.g., "5m", "1h")
        session: SQLModel database session
    
    Returns:
        Dictionary with all coherence metrics and calculated values
    """
    # Deferred imports to avoid circular dependencies
    from api.conversations.models import (
        ConversationModel,
        SignalDriftMetricModel,
    )
    
    if not signals:
        return {
            "conversation_id": conversation_id,
            "coherence_score_current": None,
            "coherence_score_trend": None,
            "drift_metrics": [],
            "signal_sources": {},
            "total_signal_count": 0,
            "time_range_start": None,
            "time_range_end": None,
        }
    
    # Parse window size
    window_seconds = parse_window_size(window_size)
    
    # Calculate drift metrics
    drift_metrics_raw = compute_drift_over_windows(signals, window_seconds)
    
    # Persist drift metrics to database
    persisted_drift_metrics = []
    if session and drift_metrics_raw:
        # First, delete old drift metrics for this conversation
        # (to avoid duplication if calculating again)
        delete_query = select(SignalDriftMetricModel).where(
            SignalDriftMetricModel.conversation_id == conversation_id
        )
        old_metrics = session.exec(delete_query).fetchall()
        for metric in old_metrics:
            session.delete(metric)
        
        # Now save new drift metrics
        for drift_metric in drift_metrics_raw:
            metric_model = SignalDriftMetricModel(
                conversation_id=conversation_id,
                window_start=drift_metric["window_start"],
                window_end=drift_metric["window_end"],
                drift_score=drift_metric["drift_score"],
                signal_count=drift_metric["signal_count"],
                coherence_trend=None,  # Will be set separately if needed
            )
            session.add(metric_model)
            persisted_drift_metrics.append(metric_model)
        
        session.commit()
    
    # Count signals by source
    signal_sources = {}
    for signal in signals:
        source = signal.signal_source
        signal_sources[source] = signal_sources.get(source, 0) + 1
    
    # Calculate coherence from drift metrics
    coherence_score = compute_coherence_from_drift(drift_metrics_raw, signals)
    
    # Calculate coherence trend (if we have historical data)
    coherence_trend = None
    if session:
        coherence_trend = calculate_coherence_trend(
            conversation_id, coherence_score, session
        )
    
    # Update conversation with coherence scores
    if session:
        update_conversation_coherence(
            conversation_id, coherence_score, coherence_trend, session
        )
    
    # Prepare time range
    time_range_start = signals[0].time if signals else None
    time_range_end = signals[-1].time if signals else None
    
    return {
        "conversation_id": conversation_id,
        "coherence_score_current": coherence_score,
        "coherence_score_trend": coherence_trend,
        "drift_metrics": drift_metrics_raw,
        "signal_sources": signal_sources,
        "total_signal_count": len(signals),
        "time_range_start": time_range_start,
        "time_range_end": time_range_end,
    }


def update_conversation_coherence(
    conversation_id: str,
    coherence_score: float,
    coherence_trend: float | None,
    session: Session,
) -> None:
    """Update conversation record with coherence scores.
    
    Parameters:
        conversation_id: The conversation ID
        coherence_score: Calculated coherence score (0-1)
        coherence_trend: Calculated trend slope (optional)
        session: SQLModel database session
    """
    # Deferred import to avoid circular dependencies
    from api.conversations.models import ConversationModel
    
    query = select(ConversationModel).where(
        ConversationModel.id == conversation_id
    )
    conversation = session.exec(query).first()
    
    if conversation:
        conversation.coherence_score_current = coherence_score
        if coherence_trend is not None:
            conversation.coherence_score_trend = coherence_trend
        
        session.add(conversation)
        session.commit()
        session.refresh(conversation)


def calculate_coherence_trend(
    conversation_id: str,
    current_coherence: float,
    session: Session,
) -> float | None:
    """Calculate coherence trend based on historical coherence scores.
    
    Fetches historical coherence scores from the database and calculates
    the trend (slope) to show if coherence is improving or degrading.
    
    Parameters:
        conversation_id: The conversation ID
        current_coherence: The current coherence score
        session: SQLModel database session
    
    Returns:
        Trend slope (positive = improving, negative = degrading) or None
    """
    # Deferred import to avoid circular dependencies
    from api.conversations.models import ConversationModel
    
    # Query conversation to get historical scores
    query = select(ConversationModel).where(
        ConversationModel.id == conversation_id
    )
    conversation = session.exec(query).first()
    
    if not conversation or not conversation.coherence_score_current:
        return None
    
    # For now, we'll return None since we don't have a history table
    # In the future, this could query a coherence_history table
    # or use TimescaleDB continuous aggregates
    return None


def get_drift_metrics_for_conversation(
    conversation_id: str,
    session: Session,
) -> list[dict]:
    """Retrieve stored drift metrics for a conversation.
    
    Parameters:
        conversation_id: The conversation ID
        session: SQLModel database session
    
    Returns:
        List of drift metric dictionaries
    """
    # Deferred import to avoid circular dependencies
    from api.conversations.models import SignalDriftMetricModel
    
    query = (
        select(SignalDriftMetricModel)
        .where(SignalDriftMetricModel.conversation_id == conversation_id)
        .order_by(SignalDriftMetricModel.window_start)  # type: ignore
    )
    
    metrics = session.exec(query).fetchall()
    
    return [
        {
            "id": m.id,
            "conversation_id": m.conversation_id,
            "window_start": m.window_start,
            "window_end": m.window_end,
            "drift_score": m.drift_score,
            "signal_count": m.signal_count,
            "coherence_trend": m.coherence_trend,
        }
        for m in metrics
    ]


def delete_drift_metrics_for_conversation(
    conversation_id: str,
    session: Session,
) -> int:
    """Delete all drift metrics for a conversation.
    
    Parameters:
        conversation_id: The conversation ID
        session: SQLModel database session
    
    Returns:
        Number of metrics deleted
    """
    # Deferred import to avoid circular dependencies
    from api.conversations.models import SignalDriftMetricModel
    
    query = select(SignalDriftMetricModel).where(
        SignalDriftMetricModel.conversation_id == conversation_id
    )
    metrics = session.exec(query).fetchall()
    
    for metric in metrics:
        session.delete(metric)
    
    session.commit()
    
    return len(metrics)
