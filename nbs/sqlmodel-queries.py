import sys
from pathlib import Path
from pprint import pprint

from sqlalchemy import func
from sqlmodel import Session, select
from timescaledb.hyperfunctions import time_bucket

src_path = Path("../src").resolve()
print(src_path)
sys.path.append(str(src_path))

from api.db.session import engine
from api.events.models import EventModel

with Session(engine) as session:
    query = select(EventModel).limit(10)
    compiled_query = query.compile(compile_kwargs={"literal_binds": True})
    print(compiled_query)
    print("")
    print(str(query))
    results = session.exec(query).fetchall()
    pprint(results)


with Session(engine) as session:
    bucket = time_bucket("1 day", EventModel.time)
    signal_types = ["relational", "emotional", "behavioral"]
    query = (
        select(
            bucket.label("bucket"),
            EventModel.signal_type,
            EventModel.agent_id,
            func.avg(EventModel.emotional_tone).label("avg_emotional_tone"),
            func.avg(EventModel.drift_score).label("avg_drift_score"),
            # func.sum(func.case((EventModel.escalate_flag > 0, 1), else_=0)).label("escalate_count"),
            func.count().label("total_count"),
        )
        .where(EventModel.signal_type.in_(signal_types))
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

    compiled_query = query.compile(compile_kwargs={"literal_binds": True})
    print(compiled_query)
    results = session.exec(query).fetchall()
    pprint(results)
