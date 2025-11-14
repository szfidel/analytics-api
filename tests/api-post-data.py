import json
import random
from datetime import datetime, timezone

import requests
import timescaledb
from decouple import config as decouple_config
from sqlmodel import Session, text

# Load database configuration
DATABASE_URL = str(decouple_config("DATABASE_URL", default=""))
DB_TIMEZONE = str(decouple_config("DB_TIMEZONE", default="UTC"))

if not DATABASE_URL:
    raise NotImplementedError("DATABASE_URL environment variable not set")

# Create engine for raw SQL inserts
engine = timescaledb.create_engine(DATABASE_URL, timezone=DB_TIMEZONE)  # type: ignore

# Base API configuration
PATH = "/api/events/"
BASE_URL = "http://localhost:8002"
CREATE_ENDPOINT = f"{BASE_URL}{PATH}"

# Example list of user and agent IDs to vary inserts
user_ids = ["u_123", "u_456", "u_789"]
agent_ids = ["Axis", "Orion", "Nova"]
signal_types = ["relational", "emotional", "behavioral"]


def generate_event():
    """Generate one random event payload."""
    emotional_tone = round(random.uniform(0.2, 0.9), 2)
    drift_score = round(random.uniform(0.0, 0.5), 2)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": random.choice(user_ids),
        "agent_id": random.choice(agent_ids),
        "signal_type": random.choice(signal_types),
        "emotional_tone": emotional_tone,
        "drift_score": drift_score,
        "escalate_flag": 0 if emotional_tone > 0.4 else 1,
        "payload": {
            "transcript": "User interaction sample event.",
            "confidence": round(random.uniform(0.8, 0.99), 2),
            "language": "en-US",
        },
        "relationship_context": "customer_support",
        "diagnostic_notes": "Auto-generated event for testing.",
    }


def post_event(event_data):
    """Send one event to the API via HTTP POST request."""
    try:
        response = requests.post(CREATE_ENDPOINT, json=event_data)
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Event created via API: {response.json()}")
        else:
            print(f"⚠️ API Failed ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ Error posting event via API: {e}")


def insert_event_raw_sql(event_data):
    """Insert one event directly into the database using raw SQL.

    Uses SQLAlchemy text() for raw SQL execution with proper session
    management (exec and commit pattern). This is useful for bulk inserts
    and bypassing the API layer.

    Args:
        event_data: Dictionary containing event fields (timestamp, user_id, etc.)
    """
    try:
        with Session(engine) as session:
            # Extract payload JSON as string (PostgreSQL expects JSONB format)
            payload_json = json.dumps(event_data.get("payload", {}))

            # Build raw SQL query using text() for parameterized execution
            # Use bindparams() to safely bind parameters without escaping issues
            query = text(
                """INSERT INTO events (
                time,
                user_id,
                agent_id,
                signal_type,
                emotional_tone,
                drift_score,
                escalate_flag,
                payload,
                relationship_context,
                diagnostic_notes
            )
            VALUES (
                NOW(),
                :user_id,
                :agent_id,
                :signal_type,
                :emotional_tone,
                :drift_score,
                :escalate_flag,
                CAST(:payload AS jsonb),
                :relationship_context,
                :diagnostic_notes
            )"""
            ).bindparams(
                user_id=event_data["user_id"],
                agent_id=event_data["agent_id"],
                signal_type=event_data["signal_type"],
                emotional_tone=event_data["emotional_tone"],
                drift_score=event_data["drift_score"],
                escalate_flag=event_data["escalate_flag"],
                payload=payload_json,
                relationship_context=event_data["relationship_context"],
                diagnostic_notes=event_data["diagnostic_notes"],
            )

            # Execute the parameterized query and commit the transaction
            session.exec(query)  # type: ignore
            session.commit()
            print(f"✅ Event inserted via raw SQL: {event_data['user_id']}")
    except Exception as e:
        print(f"❌ Error inserting event via raw SQL: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Insert events into analytics API")
    parser.add_argument(
        "--method",
        choices=["api", "sql", "both"],
        default="sql",
        help="Insertion method: api (HTTP POST), sql (raw SQL), or both (default: api)",
    )
    parser.add_argument(
        "--count", type=int, default=5, help="Number of events to insert (default: 5)"
    )

    args = parser.parse_args()

    print(f"\n📊 Inserting {args.count} events using method: {args.method}\n")

    for i in range(args.count):
        event = generate_event()

        if args.method in ("api", "both"):
            post_event(event)

        if args.method in ("sql", "both"):
            insert_event_raw_sql(event)

        if i < args.count - 1:
            print()
