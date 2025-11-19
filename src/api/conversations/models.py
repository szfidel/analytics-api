"""/src/api/conversations/models.py"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlmodel import Field, SQLModel


class ConversationModel(SQLModel, table=True):
    """Conversation/Session model for tracking discourse coherence.
    
    Groups signals into conversations/timelines for coherence scoring
    and drift analysis over sliding windows.
    """

    __tablename__ = "conversations"

    conversation_id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
    )
    user_id: str | None = Field(default=None, index=True)
    agent_id: str | None = Field(default=None, index=True)
    started_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    ended_at: datetime | None = Field(default=None, index=True)
    
    # Coherence tracking
    coherence_score_current: float | None = Field(default=None)  # 0-1
    coherence_score_trend: float | None = Field(default=None)  # slope or trend value
    
    # Metadata
    context_metadata: str | None = Field(default=None)  # JSON context


class SignalDriftMetricModel(SQLModel, table=True):
    """Signal drift metrics per conversation window.
    
    Tracks moving variance of signal_scores over sliding time windows.
    Core of the Coherence Signal Architecture.
    """

    __tablename__ = "signal_drift_metrics"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: str = Field(index=True)  # FK to ConversationModel
    window_start: datetime = Field(index=True)
    window_end: datetime = Field(index=True)
    drift_score: float = Field(default=0.0)  # Moving variance 0-1
    signal_count: int = Field(default=0)  # Signals in window
    coherence_trend: float | None = Field(default=None)  # Directional trend


class ConversationCreateSchema(SQLModel):
    """Schema for creating a new conversation."""

    user_id: str | None = Field(default=None)
    agent_id: str | None = Field(default=None)
    started_at: datetime | None = Field(default=None)
    context_metadata: dict[str, Any] | None = Field(default=None)


class ConversationReadSchema(SQLModel):
    """Schema for reading conversation details."""

    conversation_id: str
    user_id: str | None = None
    agent_id: str | None = None
    started_at: datetime
    ended_at: datetime | None = None
    coherence_score_current: float | None = None
    coherence_score_trend: float | None = None


class ConversationUpdateSchema(SQLModel):
    """Schema for updating a conversation."""

    ended_at: datetime | None = Field(default=None)
    coherence_score_current: float | None = Field(default=None)
    coherence_score_trend: float | None = Field(default=None)


class SignalDriftMetricReadSchema(SQLModel):
    """Schema for reading drift metrics."""

    id: int
    conversation_id: str
    window_start: datetime
    window_end: datetime
    drift_score: float
    signal_count: int
    coherence_trend: float | None = None


class CoherenceResponseSchema(SQLModel):
    """Response schema for coherence endpoint."""

    conversation_id: str
    coherence_score_current: float | None = None
    coherence_score_trend: float | None = None
    drift_metrics: list[SignalDriftMetricReadSchema] = Field(default_factory=list)
    signal_sources: dict[str, int] = Field(default_factory=dict)  # Count by source
    total_signal_count: int = 0
    time_range_start: datetime | None = None
    time_range_end: datetime | None = None
