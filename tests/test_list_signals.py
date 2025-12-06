"""Test GET /api/signals/ endpoint (list with aggregation)"""

import requests
import sys

BASE_URL = "http://localhost:8002/api"


def test_list_signals():
    """List all signals with time-bucketing and aggregation."""
    response = requests.get(
        f"{BASE_URL}/signals/",
        timeout=10,
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    results = response.json()
    
    # Verify response
    assert isinstance(results, list), "Response should be a list"
    
    print(f"✓ Listed {len(results)} signal buckets", file=sys.stderr)
    return results


if __name__ == "__main__":
    try:
        test_list_signals()
        print("✓ Test passed")
    except Exception as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
