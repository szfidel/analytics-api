import json
import random
from datetime import datetime, timezone

import requests

# Base API configuration
path = "/api/events/"
base_url = "http://localhost:8002"
create_endpoint = f"{base_url}{path}"

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
    """Send one event to the API."""
    try:
        response = requests.post(create_endpoint, json=event_data)
        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Event created: {response.json()}")
        else:
            print(f"⚠️ Failed ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ Error posting event: {e}")


if __name__ == "__main__":
    # Insert multiple events
    for _ in range(5):
        event = generate_event()
        post_event(event)
