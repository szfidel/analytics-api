"""Test GET /api/conversations/{id} endpoint"""

import requests
import sys

BASE_URL = "http://localhost:8002/api"


def test_get_conversation(conversation_id):
    """Retrieve a conversation by ID."""
    response = requests.get(
        f"{BASE_URL}/conversations/{conversation_id}",
        timeout=10,
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    result = response.json()
    
    # Verify response has required fields
    assert "id" in result, "Response missing 'id' field"
    assert result["id"] == conversation_id, "ID mismatch"
    
    print(f"✓ Conversation retrieved: {conversation_id}", file=sys.stderr)
    return result


if __name__ == "__main__":
    if "--conversation-id" not in sys.argv:
        print("Error: --conversation-id required", file=sys.stderr)
        print("Usage: python test_get_conversation.py --conversation-id <id>", file=sys.stderr)
        sys.exit(1)
    
    try:
        conversation_id = sys.argv[sys.argv.index("--conversation-id") + 1]
        test_get_conversation(conversation_id)
        print("✓ Test passed")
    except Exception as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
