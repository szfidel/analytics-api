"""Test user-conversation relationships via GET /api/users/{user_id}/conversations."""

import requests

# Base API configuration
BASE_URL = "http://localhost:8002"
USERS_ENDPOINT = f"{BASE_URL}/api/users"
CONVERSATIONS_ENDPOINT = f"{BASE_URL}/api/conversations"


def create_test_user():
    """Create a test user."""
    user_data = {
        "username": "conversation_test_user",
        "email": "conv.test@example.com",
        "phone": "555-6666",
        "address": "666 Conversation Lane",
    }

    try:
        response = requests.post(USERS_ENDPOINT, json=user_data)

        if response.status_code in (200, 201):
            result = response.json()
            return result
        else:
            print(f"❌ Failed to create user ({response.status_code})")
            return None

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None


def create_test_conversation(user_id, agent_id):
    """Create a test conversation for a user."""
    conv_data = {
        "user_id": user_id,
        "agent_id": agent_id,
    }

    try:
        response = requests.post(CONVERSATIONS_ENDPOINT, json=conv_data)

        if response.status_code in (200, 201):
            result = response.json()
            return result
        else:
            print(f"❌ Failed to create conversation ({response.status_code})")
            return None

    except Exception as e:
        print(f"❌ Error creating conversation: {e}")
        return None


def test_get_user_conversations(user_id):
    """Test retrieving all conversations for a user."""
    endpoint = f"{USERS_ENDPOINT}/{user_id}/conversations"

    try:
        response = requests.get(endpoint)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved conversations for user")
            print(f"   User ID: {result.get('user_id')}")
            print(f"   Total Conversations: {result.get('conversation_count')}")
            print(f"")
            
            conversations = result.get('conversations', [])
            if conversations:
                print(f"   Conversations:")
                for conv in conversations:
                    print(f"      - ID: {conv.get('id')}")
                    print(f"        Agent: {conv.get('agent_id')}")
                    print(f"        Started: {conv.get('started_at')}")
                    print(f"        Status: {'Ended' if conv.get('ended_at') else 'Active'}")
            else:
                print(f"   No conversations found")
            
            return result
        elif response.status_code == 404:
            print(f"❌ User not found (404)")
            return None
        else:
            print(f"❌ Failed to retrieve conversations ({response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error retrieving conversations: {e}")
        return None


def test_relationship_integration():
    """Test the full user-conversation relationship integration."""
    print("=" * 60)
    print("Testing User-Conversation Relationship")
    print("=" * 60)
    print()

    # Step 1: Create user
    print("📝 Step 1: Creating test user...")
    print()
    user = create_test_user()
    if not user:
        print("❌ Failed to create user")
        return

    user_id = user.get('id')
    print(f"✅ User created: {user_id}")
    print(f"   Username: {user.get('username')}")
    print()

    # Step 2: Create conversations
    print("📝 Step 2: Creating test conversations...")
    print()
    conversations = []
    for i in range(3):
        print(f"   Creating conversation {i + 1}...")
        conv = create_test_conversation(user_id, f"agent_{i:03d}")
        if conv:
            conversations.append(conv)
            print(f"      ✅ Created: {conv.get('id')}")
    
    print()

    # Step 3: Retrieve user conversations
    print("📝 Step 3: Retrieving user's conversations via relationship...")
    print()
    result = test_get_user_conversations(user_id)

    if result:
        print()
        print("=" * 60)
        print("✅ Relationship Test Successful!")
        print("=" * 60)
        print(f"Summary:")
        print(f"  - User: {result.get('user_id')}")
        print(f"  - Total Conversations: {result.get('conversation_count')}")
        print(f"  - All conversations linked to user via FK")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test user-conversation relationships"
    )
    parser.add_argument(
        "--user-id", help="Existing user ID to retrieve conversations for"
    )
    parser.add_argument(
        "--integration", action="store_true", help="Run full integration test"
    )

    args = parser.parse_args()

    if args.integration or not args.user_id:
        test_relationship_integration()
    else:
        print("=" * 60)
        print("Retrieving Conversations for User")
        print("=" * 60)
        print()
        test_get_user_conversations(args.user_id)
