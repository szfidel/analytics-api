"""/src/api/signals/models.py"""

from datetime import datetime
from typing import Any

from sqlmodel import Field, SQLModel
from timescaledb import TimescaleModel


class SignalModel(TimescaleModel, table=True):
    """Signal data model for Coherence Signal Architecture.
    
    Replaces EventModel with vector-native signal capture.
    TimescaleModel provides:
    - id: Optional[int] (auto-incremented primary key)
    - time: datetime (TimescaleDB time primary key, defaults to UTC now)
    """

    user_id: str | None = Field(default=None, index=True)
    agent_id: str | None = Field(default=None, index=True)
    
    # Core signal capture
    raw_content: str | None = Field(default=None)  # Text, speaker, message content
    context_window_id: str = Field(index=True)  # FK to conversation, UUID
    signal_source: str = Field(default="unknown")  # "Axis", "M", "Neo", "person", "Slack", etc.
    signal_score: float = Field(default=0.5)  # 0-1 coherence strength
    signal_vector: str | None = Field(default=None)  # Pinecone vector DB reference
    
    # Legacy/optional fields for compatibility
    emotional_tone: float | None = Field(default=None)
    escalate_flag: int = Field(default=0)
    payload: str | None = Field(default=None)  # JSON stored as text/jsonb
    relationship_context: str | None = None
    diagnostic_notes: str | None = None

    # TimescaleDB hypertable configuration
    __tablename__ = "signals"
    __chunk_time_interval__ = "INTERVAL 1 day"
    __drop_after__ = "INTERVAL 6 months"


class SignalCreateSchema(SQLModel):
    """Schema for creating new signals."""

    timestamp: datetime | None = Field(default=None)  # Optional, defaults to now
    user_id: str | None = Field(default=None)
    agent_id: str | None = Field(default=None)
    raw_content: str | None = Field(default=None)
    context_window_id: str  # Required: conversation ID
    signal_source: str = Field(default="unknown")
    signal_score: float = Field(default=0.5)  # 0-1
    signal_vector: str | None = Field(default=None)  # Pinecone reference
    emotional_tone: float | None = Field(default=None)
    escalate_flag: int = Field(default=0)
    payload: dict[str, Any] | None = Field(default=None)
    relationship_context: str | None = Field(default=None)
    diagnostic_notes: str | None = Field(default=None)


class SignalReadSchema(SQLModel):
    """Schema for reading signals (includes ID)."""

    id: int
    timestamp: datetime
    user_id: str | None = None
    agent_id: str | None = None
    raw_content: str | None = None
    context_window_id: str
    signal_source: str
    signal_score: float
    signal_vector: str | None = None
    emotional_tone: float | None = None
    escalate_flag: int
    relationship_context: str | None = None
    diagnostic_notes: str | None = None


class SignalListSchema(SQLModel):
    """Schema for paginated signal lists."""

    results: list[SignalReadSchema]
    count: int


class SignalBucketSchema(SQLModel):
    """Schema for time-bucketed aggregations."""

    bucket: datetime
    signal_source: str
    agent_id: str | None = None
    avg_signal_score: float = 0.0
    avg_emotional_tone: float | None = 0.0
    total_count: int = 0
