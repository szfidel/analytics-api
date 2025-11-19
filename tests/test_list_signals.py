"""Test GET /api/signals/ endpoint (list with aggregation)."""

import requests

# Base API configuration
BASE_URL = "http://localhost:8002"
SIGNALS_ENDPOINT = f"{BASE_URL}/api/signals/"


def test_list_signals(duration="1 day", signal_sources=None, context_window_id=None):
    """Test listing signals with time-bucketing and aggregation."""
    params = {"duration": duration}

    if signal_sources:
        params["signal_sources"] = signal_sources

    if context_window_id:
        params["context_window_id"] = context_window_id

    try:
        response = requests.get(SIGNALS_ENDPOINT, params=params)

        if response.status_code == 200:
            results = response.json()
            print(f"✅ Signals listed successfully (found {len(results)} buckets)")
            print(f"   Duration: {duration}")

            if signal_sources:
                print(f"   Filter Sources: {signal_sources}")

            if context_window_id:
                print(f"   Filter Conversation: {context_window_id}")

            print()

            for i, bucket in enumerate(results, 1):
                print(f"   Bucket {i}:")
                print(f"     Time: {bucket.get('bucket')}")
                print(f"     Source: {bucket.get('signal_source')}")
                print(f"     Agent: {bucket.get('agent_id')}")
                print(f"     Avg Signal Score: {bucket.get('avg_signal_score')}")
                print(f"     Avg Emotional Tone: {bucket.get('avg_emotional_tone')}")
                print(f"     Count: {bucket.get('total_count')}")
                print()

            return results
        else:
            print(f"❌ Failed to list signals ({response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error listing signals: {e}")
        return None


def test_list_signals_by_duration(durations=None):
    """Test listing signals with different time bucket durations."""
    if durations is None:
        durations = ["1 hour", "6 hours", "1 day", "7 days"]

    for duration in durations:
        print(f"\n📊 Listing signals (duration: {duration})...\n")
        test_list_signals(duration=duration)


def test_list_signals_by_source(conversation_id=None):
    """Test filtering signals by source."""
    sources = ["Axis", "M", "Neo", "person", "Slack"]

    for source in sources:
        print(f"\n📊 Listing signals (source: {source})...\n")
        test_list_signals(
            signal_sources=[source], context_window_id=conversation_id
        )


def test_list_signals_for_conversation(conversation_id):
    """Test listing signals for a specific conversation."""
    print(f"\n📊 Listing signals for conversation: {conversation_id}\n")
    return test_list_signals(context_window_id=conversation_id)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test GET /api/signals/")
    parser.add_argument(
        "--duration",
        default="1 day",
        help="Time bucket duration (e.g., '1 hour', '7 days')",
    )
    parser.add_argument(
        "--sources", nargs="+", help="Filter by signal sources (e.g., Axis M Neo)"
    )
    parser.add_argument("--conversation-id", help="Filter by conversation ID")
    parser.add_argument(
        "--test-durations",
        action="store_true",
        help="Test multiple duration buckets",
    )
    parser.add_argument(
        "--test-sources", action="store_true", help="Test filtering by all sources"
    )

    args = parser.parse_args()

    if args.test_durations:
        test_list_signals_by_duration()
    elif args.test_sources:
        test_list_signals_by_source(args.conversation_id)
    elif args.conversation_id:
        test_list_signals_for_conversation(args.conversation_id)
    else:
        test_list_signals(
            duration=args.duration,
            signal_sources=args.sources,
            context_window_id=args.conversation_id,
        )
