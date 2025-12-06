"""Test POST /api/signals/ endpoint"""

import requests
import sys

BASE_URL = "http://localhost:8002/api"


def test_create_signal(conversation_id):
    """Create a new signal and return its ID."""
    payload = {
        "context_window_id": conversation_id,
        "raw_content": "Test signal content",
        "signal_source": "test",
        "signal_score": 0.85,
    }
    
    response = requests.post(
        f"{BASE_URL}/signals/",
        json=payload,
        timeout=10,
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    result = response.json()
    
    # Verify response
    assert "id" in result, "Response missing 'id' field"
    
    signal_id = result["id"]
    print(f"✓ Signal created: {signal_id}", file=sys.stderr)
    return signal_id


if __name__ == "__main__":
    if "--conversation-id" not in sys.argv:
        print("Error: --conversation-id required", file=sys.stderr)
        print("Usage: python test_create_signal.py --conversation-id <id>", file=sys.stderr)
        sys.exit(1)
    
    try:
        conversation_id = sys.argv[sys.argv.index("--conversation-id") + 1]
        signal_id = test_create_signal(conversation_id)
        print(signal_id)  # Print just the ID for use in scripts
    except Exception as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
