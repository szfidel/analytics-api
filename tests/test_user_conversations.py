"""Test GET /api/users/{user_id}/conversations endpoint"""

import requests
import sys

BASE_URL = "http://localhost:8002/api"


def test_user_conversations(user_id):
    """Retrieve conversations for a user."""
    response = requests.get(
        f"{BASE_URL}/users/{user_id}/conversations",
        timeout=10,
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    result = response.json()
    
    # Verify response
    assert isinstance(result, dict), "Response should be a dict"
    assert "conversations" in result, "Response missing 'conversations' field"
    assert isinstance(result["conversations"], list), "Conversations should be a list"
    
    conversations = result["conversations"]
    print(f"✓ Retrieved {len(conversations)} conversations for user {user_id}", file=sys.stderr)
    return conversations


if __name__ == "__main__":
    if "--user-id" not in sys.argv:
        print("Error: --user-id required", file=sys.stderr)
        print("Usage: python test_user_conversations.py --user-id <id>", file=sys.stderr)
        sys.exit(1)
    
    try:
        user_id = sys.argv[sys.argv.index("--user-id") + 1]
        test_user_conversations(user_id)
        print("✓ Test passed")
    except Exception as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
