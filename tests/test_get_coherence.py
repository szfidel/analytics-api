"""Test GET /api/conversations/{id}/coherence endpoint (CORE ENDPOINT)."""

import requests

# Base API configuration
BASE_URL = "http://localhost:8002"
CONVERSATIONS_ENDPOINT = f"{BASE_URL}/api/conversations"


def test_get_coherence(conversation_id, window_size="5m"):
    """Test retrieving coherence metrics for a conversation.
    
    This is the CORE endpoint that computes:
    - Drift metrics (moving variance)
    - Overall coherence score
    - Signal sources breakdown
    - Time range analysis
    """
    endpoint = f"{CONVERSATIONS_ENDPOINT}/{conversation_id}/coherence"
    params = {"window_size": window_size}

    try:
        response = requests.get(endpoint, params=params)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Coherence metrics retrieved successfully")
            print(f"   Conversation: {result.get('conversation_id')}")
            print(f"   Window Size: {window_size}")
            print()

            # Overall coherence score
            print(f"   📊 Overall Coherence:")
            print(f"     Current Score: {result.get('coherence_score_current')}")
            print(f"     Trend: {result.get('coherence_score_trend')}")
            print()

            # Drift metrics per window
            drift_metrics = result.get('drift_metrics', [])
            print(f"   📈 Drift Metrics ({len(drift_metrics)} windows):")
            for i, metric in enumerate(drift_metrics, 1):
                print(f"     Window {i}:")
                print(f"       Start: {metric.get('window_start')}")
                print(f"       End: {metric.get('window_end')}")
                print(f"       Drift Score: {metric.get('drift_score'):.4f}")
                print(f"       Signal Count: {metric.get('signal_count')}")
                print(f"       Coherence Trend: {metric.get('coherence_trend')}")
            print()

            # Signal sources breakdown
            signal_sources = result.get('signal_sources', {})
            print(f"   📡 Signal Sources:")
            for source, count in signal_sources.items():
                print(f"     {source}: {count} signals")
            print()

            # Time range
            print(f"   ⏱️  Time Range:")
            print(f"     Start: {result.get('time_range_start')}")
            print(f"     End: {result.get('time_range_end')}")
            print(f"     Total Signals: {result.get('total_signal_count')}")
            print()

            # Interpretation
            coherence = result.get('coherence_score_current')
            if coherence is not None:
                if coherence >= 0.8:
                    interpretation = "🟢 Excellent alignment"
                elif coherence >= 0.6:
                    interpretation = "🟡 Good alignment"
                elif coherence >= 0.4:
                    interpretation = "🟠 Fair alignment"
                else:
                    interpretation = "🔴 Poor alignment"

                print(f"   💡 Interpretation: {interpretation}")

            return result
        elif response.status_code == 404:
            print(f"❌ Conversation not found (404)")
            return None
        else:
            print(f"❌ Failed to retrieve coherence ({response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error retrieving coherence: {e}")
        return None


def test_coherence_with_different_windows(conversation_id):
    """Test coherence computation with different window sizes."""
    window_sizes = ["30s", "5m", "15m", "1h"]

    for window_size in window_sizes:
        print(f"\n📊 Computing coherence (window: {window_size})...\n")
        test_get_coherence(conversation_id, window_size=window_size)


def test_coherence_interpretation(conversation_id):
    """Test coherence retrieval and show detailed interpretation."""
    print(f"\n🔬 Detailed Coherence Analysis...\n")

    result = test_get_coherence(conversation_id)

    if result:
        coherence = result.get('coherence_score_current')
        drift_metrics = result.get('drift_metrics', [])

        if drift_metrics:
            avg_drift = sum(m.get('drift_score', 0) for m in drift_metrics) / len(
                drift_metrics
            )

            print(f"\n   📌 Analysis:")
            print(f"     Coherence = 1 - avg(drift)")
            print(f"     Coherence = 1 - {avg_drift:.4f}")
            print(f"     Coherence = {coherence:.4f}")
            print()

            if avg_drift < 0.1:
                print(f"     ✅ Very low drift = highly coherent signals")
            elif avg_drift < 0.3:
                print(f"     ✓ Low drift = coherent signals")
            elif avg_drift < 0.6:
                print(f"     ⚠️ Moderate drift = some variation in signals")
            else:
                print(f"     ❌ High drift = incoherent signals")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test GET /api/conversations/{id}/coherence (CORE ENDPOINT)"
    )
    parser.add_argument("conversation_id", help="Conversation ID")
    parser.add_argument(
        "--window-size",
        default="5m",
        help="Drift calculation window size (e.g., '5m', '1h')",
    )
    parser.add_argument(
        "--test-windows",
        action="store_true",
        help="Test with different window sizes",
    )
    parser.add_argument(
        "--detailed", action="store_true", help="Show detailed interpretation"
    )

    args = parser.parse_args()

    if args.test_windows:
        test_coherence_with_different_windows(args.conversation_id)
    elif args.detailed:
        test_coherence_interpretation(args.conversation_id)
    else:
        test_get_coherence(args.conversation_id, window_size=args.window_size)
