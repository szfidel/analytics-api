"""Test POST /api/signals/ endpoint."""

import random
from datetime import datetime, timezone

import requests

# Base API configuration
BASE_URL = "http://localhost:8002"
SIGNALS_ENDPOINT = f"{BASE_URL}/api/signals/"

# Signal sources and configuration
SIGNAL_SOURCES = ["Axis", "M", "Neo", "person", "Slack"]


def generate_signal(conversation_id):
    """Generate a signal payload."""
    signal_score = round(random.uniform(0.3, 0.95), 2)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": f"user_{random.randint(1, 5):03d}",
        "agent_id": f"agent_{random.randint(1, 3):03d}",
        "raw_content": "Sample signal content from the conversation.",
        "context_window_id": conversation_id,
        "signal_source": random.choice(SIGNAL_SOURCES),
        "signal_score": signal_score,
        "signal_vector": f"pinecone_vec_{random.randint(1000, 9999)}",
        "emotional_tone": round(random.uniform(0.2, 0.9), 2),
        "escalate_flag": 0,
        "payload": {
            "metadata": "test signal",
            "confidence": round(random.uniform(0.7, 0.99), 2),
        },
    }


def test_create_signal(conversation_id):
    """Test creating a new signal via POST endpoint."""
    signal_data = generate_signal(conversation_id)

    try:
        response = requests.post(SIGNALS_ENDPOINT, json=signal_data)

        if response.status_code in (200, 201):
            result = response.json()
            print(f"✅ Signal created successfully")
            print(f"   ID: {result.get('id')}")
            print(f"   Source: {result.get('signal_source')}")
            print(f"   Score: {result.get('signal_score')}")
            print(f"   User: {result.get('user_id')}")
            print(f"   Content: {result.get('raw_content')}")
            return result
        else:
            print(f"❌ Failed to create signal ({response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error creating signal: {e}")
        return None


def test_create_multiple_signals(conversation_id, count=5):
    """Test creating multiple signals for a conversation."""
    print(f"\n📊 Creating {count} signals for conversation...\n")

    signals = []
    for i in range(count):
        signal = test_create_signal(conversation_id)
        if signal:
            signals.append(signal)

        if i < count - 1:
            print()

    return signals


def test_create_signals_with_varying_scores(conversation_id):
    """Test creating signals with different score ranges."""
    print(f"\n📊 Creating signals with varying scores...\n")

    score_ranges = [
        (0.1, 0.3, "Low coherence"),
        (0.3, 0.6, "Medium coherence"),
        (0.6, 0.8, "High coherence"),
        (0.8, 0.95, "Very high coherence"),
    ]

    for min_score, max_score, label in score_ranges:
        signal_data = generate_signal(conversation_id)
        signal_data["signal_score"] = round(random.uniform(min_score, max_score), 2)

        print(f"Creating signal ({label}, score={signal_data['signal_score']})...")
        test_create_signal(conversation_id)
        print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test POST /api/signals/")
    parser.add_argument("conversation_id", help="Conversation ID for the signal")
    parser.add_argument(
        "--count", type=int, default=1, help="Number of signals to create"
    )
    parser.add_argument(
        "--varying-scores",
        action="store_true",
        help="Create signals with varying score ranges",
    )

    args = parser.parse_args()

    if args.varying_scores:
        test_create_signals_with_varying_scores(args.conversation_id)
    elif args.count == 1:
        test_create_signal(args.conversation_id)
    else:
        test_create_multiple_signals(args.conversation_id, args.count)
