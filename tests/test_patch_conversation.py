"""Test PATCH /api/conversations/{id} endpoint."""

from datetime import datetime, timezone

import requests

# Base API configuration
BASE_URL = "http://localhost:8002"
CONVERSATIONS_ENDPOINT = f"{BASE_URL}/api/conversations"


def test_patch_conversation(conversation_id, update_data):
    """Test updating a conversation via PATCH endpoint."""
    endpoint = f"{CONVERSATIONS_ENDPOINT}/{conversation_id}"

    try:
        response = requests.patch(endpoint, json=update_data)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Conversation updated successfully")
            print(f"   ID: {result.get('id')}")
            print(f"   Ended: {result.get('ended_at')}")
            print(f"   Coherence Score: {result.get('coherence_score_current')}")
            print(f"   Coherence Trend: {result.get('coherence_score_trend')}")
            return result
        elif response.status_code == 404:
            print(f"❌ Conversation not found (404)")
            return None
        else:
            print(f"❌ Failed to update conversation ({response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error updating conversation: {e}")
        return None


def test_end_conversation(conversation_id):
    """Test ending a conversation (set ended_at)."""
    print(f"\n🔧 Ending conversation...\n")

    update_data = {"ended_at": datetime.now(timezone.utc).isoformat()}

    result = test_patch_conversation(conversation_id, update_data)
    return result


def test_update_coherence_scores(conversation_id):
    """Test updating coherence scores for a conversation."""
    print(f"\n📊 Updating coherence scores...\n")

    update_data = {
        "coherence_score_current": 0.82,
        "coherence_score_trend": 0.05,
    }

    result = test_patch_conversation(conversation_id, update_data)
    return result


def test_update_all_fields(conversation_id):
    """Test updating all fields at once."""
    print(f"\n🔧 Updating all fields...\n")

    update_data = {
        "ended_at": datetime.now(timezone.utc).isoformat(),
        "coherence_score_current": 0.75,
        "coherence_score_trend": -0.03,
    }

    result = test_patch_conversation(conversation_id, update_data)
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test PATCH /api/conversations/{id}")
    parser.add_argument("conversation_id", help="Conversation ID to update")
    parser.add_argument(
        "--action",
        choices=["end", "coherence", "all"],
        default="end",
        help="What to update (default: end)",
    )

    args = parser.parse_args()

    if args.action == "end":
        test_end_conversation(args.conversation_id)
    elif args.action == "coherence":
        test_update_coherence_scores(args.conversation_id)
    elif args.action == "all":
        test_update_all_fields(args.conversation_id)
