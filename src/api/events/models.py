"""/src/api/events/models.py"""

from datetime import datetime
from typing import Any

from sqlmodel import Field, SQLModel
from timescaledb import TimescaleModel


class EventModel(TimescaleModel, table=True):
    """Event data model for TimescaleDB hypertable.
       TimescaleModel is an abstract base class for Timescale hypertable.
       By default has:

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"autoincrement": True},
    )
    time: datetime = Field(
        default_factory=get_utc_now,
        sa_type=sqlmodel.DateTime(timezone=True),
        primary_key=True,
        nullable=False,
    )
    """

    user_id: str | None = Field(default=None, index=True)
    agent_id: str | None = Field(default=None, index=True)
    signal_type: str | None = Field(default=None, index=True)
    emotional_tone: float | None = Field(default=None)
    drift_score: float | None = Field(default=None)
    escalate_flag: int = Field(default=0)  # NOT NULL constraint
    payload: str | None = Field(
        default=None, index=True
    )  # JSON stored as text/jsonb in PostgreSQL
    relationship_context: str | None = None
    diagnostic_notes: str | None = None

    # TimescaleDB hypertable configuration
    __tablename__ = "events"
    __chunk_time_interval__ = "INTERVAL 1 day"
    __drop_after__ = "INTERVAL 6 months"


class EventCreateSchema(SQLModel):
    """Schema for creating new events."""

    timestamp: datetime
    user_id: str | None = Field(default=None)
    agent_id: str | None = Field(default=None)
    signal_type: str
    emotional_tone: float | None = Field(default=None)
    drift_score: float | None = Field(default=None)
    escalate_flag: int = Field(default=0)
    payload: dict[str, Any] | None = Field(default=None)  # JSON payload as dict
    relationship_context: str | None = Field(default=None)
    diagnostic_notes: str | None = Field(default=None)


class EventReadSchema(SQLModel):
    """Schema for reading events (includes ID)."""

    id: int
    timestamp: datetime
    user_id: str | None = None
    agent_id: str | None = None
    signal_type: str | None = None
    emotional_tone: float | None = None
    drift_score: float | None = None
    escalate_flag: int
    relationship_context: str | None = None
    diagnostic_notes: str | None = None


class EventListSchema(SQLModel):
    """Schema for paginated event lists."""

    results: list[EventReadSchema]
    count: int


class EventBucketSchema(SQLModel):
    """Schema for time-bucketed aggregations."""

    bucket: datetime
    signal_type: str
    agent_id: str | None = None
    avg_emotional_tone: float | None = 0.0
    avg_drift_score: float | None = 0.0
    total_count: int = 0
