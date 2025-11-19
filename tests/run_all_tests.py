"""Master test runner - runs all endpoint tests in sequence."""

import sys
from test_create_conversation import test_create_conversation
from test_get_conversation import test_get_conversation
from test_create_signal import test_create_signal, test_create_multiple_signals
from test_list_signals import test_list_signals
from test_get_signals_by_conversation import test_get_signals_by_conversation
from test_get_signal import test_get_signal
from test_patch_conversation import test_end_conversation, test_update_coherence_scores
from test_get_coherence import test_get_coherence


def run_full_workflow():
    """Run a complete test workflow:
    1. Create a conversation
    2. Create multiple signals for it
    3. Retrieve signals by conversation
    4. Get coherence metrics
    5. Update conversation
    """
    print("=" * 80)
    print("🚀 FULL WORKFLOW TEST")
    print("=" * 80)

    # Step 1: Create conversation
    print("\n\n📌 STEP 1: Create Conversation")
    print("-" * 80)
    conv = test_create_conversation()
    if not conv:
        print("❌ Failed to create conversation. Aborting.")
        return False

    conv_id = conv.get("conversation_id")
    print(f"\n✅ Conversation created: {conv_id}")

    # Step 2: Create multiple signals
    print("\n\n📌 STEP 2: Create Multiple Signals")
    print("-" * 80)
    signals = test_create_multiple_signals(conv_id, count=5)
    if not signals:
        print("⚠️ Failed to create signals. Continuing...")
    else:
        print(f"\n✅ Created {len(signals)} signals")

    # Step 3: Retrieve signals by conversation
    print("\n\n📌 STEP 3: Retrieve Signals by Conversation")
    print("-" * 80)
    retrieved_signals = test_get_signals_by_conversation(conv_id)
    if not retrieved_signals:
        print("⚠️ Failed to retrieve signals")
    else:
        print(f"\n✅ Retrieved {len(retrieved_signals)} signals")

    # Step 4: Get coherence metrics
    print("\n\n📌 STEP 4: Get Coherence Metrics")
    print("-" * 80)
    coherence = test_get_coherence(conv_id, window_size="5m")
    if not coherence:
        print("⚠️ Failed to get coherence metrics")
    else:
        print(f"\n✅ Coherence score: {coherence.get('coherence_score_current')}")

    # Step 5: Update conversation
    print("\n\n📌 STEP 5: Update Conversation (End it)")
    print("-" * 80)
    updated = test_end_conversation(conv_id)
    if not updated:
        print("⚠️ Failed to update conversation")
    else:
        print(f"\n✅ Conversation updated: ended_at set")

    # Step 6: Verify conversation was updated
    print("\n\n📌 STEP 6: Verify Conversation Update")
    print("-" * 80)
    verified = test_get_conversation(conv_id)
    if verified and verified.get("ended_at"):
        print(f"\n✅ Verification successful - conversation ended")
    else:
        print(f"⚠️ Verification incomplete")

    print("\n\n" + "=" * 80)
    print("✅ FULL WORKFLOW TEST COMPLETED")
    print("=" * 80)

    return True


def run_endpoint_tests():
    """Run individual endpoint tests."""
    print("=" * 80)
    print("🧪 INDIVIDUAL ENDPOINT TESTS")
    print("=" * 80)

    # Test all GET endpoints
    print("\n\n📌 Testing GET Endpoints")
    print("-" * 80)

    print("\n✓ GET /api/signals/ (list)")
    test_list_signals(duration="1 day")

    print("\n✓ GET /api/signals/{id} (retrieve single)")
    # Note: requires a valid signal ID from previous test

    # Test coherence with different window sizes
    print("\n✓ GET /api/conversations/{id}/coherence (different windows)")
    print("   (Requires valid conversation ID)")


def run_stress_test(conversation_id, signal_count=50):
    """Run a stress test by creating many signals."""
    print("=" * 80)
    print(f"💥 STRESS TEST: Creating {signal_count} signals")
    print("=" * 80)

    print(f"\nCreating {signal_count} signals for conversation: {conversation_id}\n")

    signals = test_create_multiple_signals(conversation_id, count=signal_count)

    if signals:
        print(f"\n✅ Successfully created {len(signals)} signals")

        # Get coherence metrics
        print("\n📊 Computing coherence metrics after stress test...\n")
        coherence = test_get_coherence(conversation_id)

        if coherence:
            print(
                f"\n✅ Coherence score after {signal_count} signals: {coherence.get('coherence_score_current')}"
            )
    else:
        print(f"\n❌ Failed to create signals")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Master test runner for all endpoints")
    parser.add_argument(
        "--mode",
        choices=["workflow", "endpoints", "stress"],
        default="workflow",
        help="Test mode to run (default: workflow)",
    )
    parser.add_argument(
        "--conversation-id", help="Conversation ID for stress test or specific tests"
    )
    parser.add_argument(
        "--signal-count",
        type=int,
        default=50,
        help="Number of signals for stress test (default: 50)",
    )

    args = parser.parse_args()

    if args.mode == "workflow":
        success = run_full_workflow()
        sys.exit(0 if success else 1)

    elif args.mode == "endpoints":
        run_endpoint_tests()

    elif args.mode == "stress":
        if not args.conversation_id:
            print("❌ Error: --conversation-id required for stress test")
            sys.exit(1)
        run_stress_test(args.conversation_id, args.signal_count)
