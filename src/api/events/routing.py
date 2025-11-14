from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, select
from timescaledb.hyperfunctions import time_bucket

from api.db.session import get_session

from .models import EventBucketSchema, EventCreateSchema, EventModel

router = APIRouter()

DEFAULT_SIGNAL_TYPES = ["relational", "emotional", "behavioral"]


# Get data here
# List View
# GET /api/events/
@router.get("/", response_model=list[EventBucketSchema])
def read_events(
    duration: str = Query(default="1 day"),
    signal_types: list = Query(default=None),
    # agent_ids: List[str] = Query(default=None),
    session: Session = Depends(get_session),
):
    # a bunch of items in a table
    bucket = time_bucket(duration, EventModel.time)
    lookup_signal_types = (
        signal_types
        if isinstance(signal_types, list) and len(signal_types) > 0
        else DEFAULT_SIGNAL_TYPES
    )

    query = (
        select(
            bucket.label("bucket"),
            EventModel.signal_type.label("signal_type"),
            EventModel.agent_id.label("agent_id"),
            func.avg(EventModel.emotional_tone).label("avg_emotional_tone"),
            func.avg(EventModel.drift_score).label("avg_drift_score"),
            func.count().label("total_count"),
        )
        .where(EventModel.signal_type.in_(lookup_signal_types))
        .group_by(
            bucket,
            EventModel.signal_type,
            EventModel.agent_id,
        )
        .order_by(
            bucket,
            EventModel.signal_type,
            EventModel.agent_id,
        )
    )

    # if agent_ids and isinstance(agent_ids, list) and len(agent_ids) > 0:
    #    query = query.where(EventModel.agent_id.in_(agent_ids))

    results = session.exec(query).fetchall()
    return results


# SEND DATA HERE
# create view
# POST /api/events/
@router.post("/", response_model=EventModel)
def create_event(payload: EventCreateSchema, session: Session = Depends(get_session)):
    # a bunch of items in a table
    data = payload.model_dump()  # payload -> dict -> pydantic
    obj = EventModel.model_validate(data)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


# GET /api/events/12
@router.get("/{event_id}", response_model=EventModel)
def get_event(event_id: int, session: Session = Depends(get_session)):
    # a single row
    query = select(EventModel).where(EventModel.id == event_id)
    result = session.exec(query).first()
    if not result:
        raise HTTPException(status_code=404, detail="Event not found")
    return result
