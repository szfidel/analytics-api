"""Test GET /api/signals/conversation/{context_window_id} endpoint."""

import requests

# Base API configuration
BASE_URL = "http://localhost:8002"
SIGNALS_ENDPOINT = f"{BASE_URL}/api/signals/conversation"


def test_get_signals_by_conversation(conversation_id, limit=100):
    """Test retrieving all signals in a conversation."""
    endpoint = f"{SIGNALS_ENDPOINT}/{conversation_id}"
    params = {"limit": limit}

    try:
        response = requests.get(endpoint, params=params)

        if response.status_code == 200:
            results = response.json()
            print(f"✅ Signals retrieved successfully (found {len(results)} signals)")
            print(f"   Conversation: {conversation_id}")
            print(f"   Limit: {limit}")
            print()

            for i, signal in enumerate(results, 1):
                print(f"   Signal {i}:")
                print(f"     ID: {signal.get('id')}")
                print(f"     Time: {signal.get('timestamp')}")
                print(f"     Source: {signal.get('signal_source')}")
                print(f"     Score: {signal.get('signal_score')}")
                print(f"     User: {signal.get('user_id')}")
                print(f"     Agent: {signal.get('agent_id')}")
                print(f"     Content: {signal.get('raw_content')}")
                print()

            # Summary statistics
            if results:
                scores = [s.get('signal_score', 0) for s in results]
                avg_score = sum(scores) / len(scores)
                min_score = min(scores)
                max_score = max(scores)

                print(f"   📊 Statistics:")
                print(f"     Average Score: {avg_score:.3f}")
                print(f"     Min Score: {min_score:.3f}")
                print(f"     Max Score: {max_score:.3f}")
                print(f"     Range: {max_score - min_score:.3f}")

            return results
        elif response.status_code == 404:
            print(f"❌ Conversation not found (404)")
            print(f"   ID: {conversation_id}")
            return None
        else:
            print(f"❌ Failed to retrieve signals ({response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error retrieving signals: {e}")
        return None


def test_get_signals_with_different_limits(conversation_id):
    """Test retrieving signals with different limit values."""
    limits = [5, 10, 50, 100]

    for limit in limits:
        print(f"\n📊 Retrieving signals (limit: {limit})...\n")
        test_get_signals_by_conversation(conversation_id, limit=limit)


def test_get_nonexistent_conversation_signals():
    """Test retrieving signals from non-existent conversation (should return 404)."""
    fake_id = "00000000-0000-0000-0000-000000000000"

    print(f"\n🔍 Testing signals for non-existent conversation...\n")
    result = test_get_signals_by_conversation(fake_id)

    if result is None:
        print(f"✅ Correctly handled non-existent conversation")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test GET /api/signals/conversation/{context_window_id}"
    )
    parser.add_argument("conversation_id", help="Conversation ID")
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum signals to return (default: 100)",
    )
    parser.add_argument(
        "--test-limits",
        action="store_true",
        help="Test with different limit values",
    )

    args = parser.parse_args()

    if args.test_limits:
        test_get_signals_with_different_limits(args.conversation_id)
    else:
        test_get_signals_by_conversation(args.conversation_id, limit=args.limit)
