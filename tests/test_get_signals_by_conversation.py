"""Test GET /api/signals/conversation/{context_window_id} endpoint"""

import requests
import sys

BASE_URL = "http://localhost:8002/api"


def test_get_signals_by_conversation(conversation_id):
    """Retrieve all signals in a conversation."""
    response = requests.get(
        f"{BASE_URL}/signals/conversation/{conversation_id}",
        timeout=10,
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    results = response.json()
    
    # Verify response
    assert isinstance(results, list), "Response should be a list"
    
    print(f"✓ Retrieved {len(results)} signals for conversation {conversation_id}", file=sys.stderr)
    return results


if __name__ == "__main__":
    if "--conversation-id" not in sys.argv:
        print("Error: --conversation-id required", file=sys.stderr)
        print("Usage: python test_get_signals_by_conversation.py --conversation-id <id>", file=sys.stderr)
        sys.exit(1)
    
    try:
        conversation_id = sys.argv[sys.argv.index("--conversation-id") + 1]
        test_get_signals_by_conversation(conversation_id)
        print("✓ Test passed")
    except Exception as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
