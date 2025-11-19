"""Test GET /api/signals/{id} endpoint."""

import requests

# Base API configuration
BASE_URL = "http://localhost:8002"
SIGNALS_ENDPOINT = f"{BASE_URL}/api/signals"


def test_get_signal(signal_id):
    """Test retrieving a signal by ID."""
    endpoint = f"{SIGNALS_ENDPOINT}/{signal_id}"

    try:
        response = requests.get(endpoint)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Signal retrieved successfully")
            print(f"   ID: {result.get('id')}")
            print(f"   Source: {result.get('signal_source')}")
            print(f"   Score: {result.get('signal_score')}")
            print(f"   Conversation: {result.get('context_window_id')}")
            print(f"   User: {result.get('user_id')}")
            print(f"   Agent: {result.get('agent_id')}")
            print(f"   Vector: {result.get('signal_vector')}")
            print(f"   Content: {result.get('raw_content')}")
            print(f"   Emotional Tone: {result.get('emotional_tone')}")
            return result
        elif response.status_code == 404:
            print(f"❌ Signal not found (404)")
            print(f"   ID: {signal_id}")
            return None
        else:
            print(f"❌ Failed to retrieve signal ({response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error retrieving signal: {e}")
        return None


def test_get_nonexistent_signal():
    """Test retrieving a non-existent signal (should return 404)."""
    fake_id = 999999

    print(f"\n🔍 Testing non-existent signal (expecting 404)...\n")
    result = test_get_signal(fake_id)

    if result is None:
        print(f"✅ Correctly handled non-existent signal")
    else:
        print(f"⚠️ Unexpected: signal should not exist")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test GET /api/signals/{id}")
    parser.add_argument("signal_id", type=int, help="Signal ID to retrieve")

    args = parser.parse_args()

    test_get_signal(args.signal_id)
