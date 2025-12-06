"""Test GET /api/signals/{id} endpoint"""

import requests
import sys

BASE_URL = "http://localhost:8002/api"


def test_get_signal(signal_id):
    """Retrieve a signal by ID."""
    response = requests.get(
        f"{BASE_URL}/signals/{signal_id}",
        timeout=10,
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    result = response.json()
    
    # Verify response
    assert "id" in result, "Response missing 'id' field"
    assert result["id"] == int(signal_id), "ID mismatch"
    
    print(f"✓ Signal retrieved: {signal_id}", file=sys.stderr)
    return result


if __name__ == "__main__":
    if "--signal-id" not in sys.argv:
        print("Error: --signal-id required", file=sys.stderr)
        print("Usage: python test_get_signal.py --signal-id <id>", file=sys.stderr)
        sys.exit(1)
    
    try:
        signal_id = sys.argv[sys.argv.index("--signal-id") + 1]
        test_get_signal(signal_id)
        print("✓ Test passed")
    except Exception as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
