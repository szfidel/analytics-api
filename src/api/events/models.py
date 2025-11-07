from datetime import datetime, timezone
from typing import List, Optional

# from pydantic import BaseModel, Field
import sqlmodel
from sqlmodel import Field, SQLModel
from timescaledb import TimescaleModel
from timescaledb.utils import get_utc_now

# page visits at any given time


class EventModel(TimescaleModel, table=True):
    """Event data model for TimescaleDB hypertable."""

    # id: int = Field(default=None, primary_key=True)
    # timestamp: datetime = Field(index=True)  # TimescaleDB time column
    user_id: Optional[str] = Field(default=None, index=True)
    agent_id: Optional[str] = Field(default=None, index=True)
    signal_type: Optional[str] = Field(default=None, index=True)
    emotional_tone: Optional[float] = Field(default=None)
    drift_score: Optional[float] = Field(default=None)
    escalate_flag: int = Field(default=0)  # NOT NULL constraint
    payload: Optional[str] = Field(default=None, index=True)  # JSON type
    relationship_context: Optional[str] = Field(default=None)
    diagnostic_notes: Optional[str] = Field(default=None)

    # TimescaleDB hypertable configuration
    __tablename__ = "events"
    __chunk_time_interval__ = "INTERVAL 1 day"
    __drop_after__ = "INTERVAL 6 months"


class EventCreateSchema(SQLModel):
    """Schema for creating new events."""

    timestamp: datetime
    user_id: Optional[str] = Field(default=None)
    agent_id: Optional[str] = Field(default=None)
    signal_type: str
    emotional_tone: Optional[float] = Field(default=None)
    drift_score: Optional[float] = Field(default=None)
    escalate_flag: int = Field(default=0)
    relationship_context: Optional[str] = Field(default=None)
    diagnostic_notes: Optional[str] = Field(default=None)


class EventReadSchema(SQLModel):
    """Schema for reading events (includes ID)."""

    id: int
    timestamp: datetime
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    signal_type: Optional[str] = None
    emotional_tone: Optional[float] = None
    drift_score: Optional[float] = None
    escalate_flag: int
    relationship_context: Optional[str] = None
    diagnostic_notes: Optional[str] = None


class EventListSchema(SQLModel):
    """Schema for paginated event lists."""

    results: List[EventReadSchema]
    count: int


class EventBucketSchema(SQLModel):
    """Schema for time-bucketed aggregations."""

    bucket: datetime
    signal_type: str
    agent_id: Optional[str] = None
    avg_emotional_tone: Optional[float] = 0.0
    avg_drift_score: Optional[float] = 0.0
    total_count: int = 0
