"""Test GET /api/conversations/{id} endpoint."""

import requests

# Base API configuration
BASE_URL = "http://localhost:8002"
CONVERSATIONS_ENDPOINT = f"{BASE_URL}/api/conversations"


def test_get_conversation(conversation_id):
    """Test retrieving a conversation by ID."""
    endpoint = f"{CONVERSATIONS_ENDPOINT}/{conversation_id}"

    try:
        response = requests.get(endpoint)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Conversation retrieved successfully")
            print(f"   ID: {result.get('conversation_id')}")
            print(f"   User: {result.get('user_id')}")
            print(f"   Agent: {result.get('agent_id')}")
            print(f"   Started: {result.get('started_at')}")
            print(f"   Ended: {result.get('ended_at')}")
            print(f"   Coherence Score: {result.get('coherence_score_current')}")
            print(f"   Coherence Trend: {result.get('coherence_score_trend')}")
            return result
        elif response.status_code == 404:
            print(f"❌ Conversation not found (404)")
            print(f"   ID: {conversation_id}")
            return None
        else:
            print(f"❌ Failed to retrieve conversation ({response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error retrieving conversation: {e}")
        return None


def test_get_nonexistent_conversation():
    """Test retrieving a non-existent conversation (should return 404)."""
    fake_id = "00000000-0000-0000-0000-000000000000"

    print(f"\n📋 Testing non-existent conversation (expecting 404)...\n")
    result = test_get_conversation(fake_id)

    if result is None:
        print(f"✅ Correctly handled non-existent conversation")
    else:
        print(f"⚠️ Unexpected: conversation should not exist")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test GET /api/conversations/{id}")
    parser.add_argument("conversation_id", help="Conversation ID to retrieve")

    args = parser.parse_args()

    test_get_conversation(args.conversation_id)
