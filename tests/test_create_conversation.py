"""Test POST /api/conversations/ endpoint"""

import requests
import sys
import uuid

BASE_URL = "http://localhost:8002/api"


def test_create_conversation():
    """Create a new conversation and return its ID."""
    payload = {
        "title": f"Test Conversation {uuid.uuid4().hex[:8]}",
        "description": "Testing conversation creation endpoint",
    }
    
    response = requests.post(
        f"{BASE_URL}/conversations/",
        json=payload,
        timeout=10,
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    result = response.json()
    
    # Verify response has required fields
    assert "id" in result, "Response missing 'id' field"
    assert "started_at" in result, "Response missing 'started_at' field"
    
    conversation_id = result["id"]
    print(f"✓ Conversation created: {conversation_id}", file=sys.stderr)
    return conversation_id


if __name__ == "__main__":
    try:
        conversation_id = test_create_conversation()
        print(conversation_id)  # Print just the ID for use in scripts
    except Exception as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
