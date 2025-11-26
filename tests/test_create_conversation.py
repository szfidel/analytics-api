"""Test POST /api/conversations/ endpoint."""

import json
from datetime import datetime, timezone

import requests

# Base API configuration
BASE_URL = "http://localhost:8002"
ENDPOINT = f"{BASE_URL}/api/conversations/"


def generate_conversation():
    """Generate a conversation payload."""
    import json
    
    metadata = {
        "topic": "test conversation",
        "environment": "testing",
    }
    
    return {
        "user_id": "test_user_001",
        "agent_id": "test_agent_001",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }


def test_create_conversation():
    """Test creating a new conversation via POST endpoint."""
    conversation_data = generate_conversation()

    try:
        response = requests.post(ENDPOINT, json=conversation_data)

        if response.status_code in (200, 201):
            result = response.json()
            print(f"✅ Conversation created successfully")
            print(f"   ID: {result.get('id')}")
            print(f"   User: {result.get('user_id')}")
            print(f"   Agent: {result.get('agent_id')}")
            print(f"   Started: {result.get('started_at')}")
            print(f"   Coherence Score: {result.get('coherence_score_current')}")
            return result
        else:
            print(f"❌ Failed to create conversation ({response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error creating conversation: {e}")
        return None


def test_create_multiple_conversations(count=3):
    """Test creating multiple conversations."""
    print(f"\n📊 Creating {count} conversations...\n")

    conversations = []
    for i in range(count):
        conv_data = generate_conversation()
        conv_data["user_id"] = f"user_{i:03d}"
        conv_data["agent_id"] = f"agent_{i:03d}"

        conv = test_create_conversation()
        if conv:
            conversations.append(conv)

        if i < count - 1:
            print()

    return conversations


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test POST /api/conversations/")
    parser.add_argument(
        "--count", type=int, default=1, help="Number of conversations to create"
    )

    args = parser.parse_args()

    if args.count == 1:
        test_create_conversation()
    else:
        test_create_multiple_conversations(args.count)
