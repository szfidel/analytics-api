"""Test GET /api/conversations/{id}/coherence endpoint"""

import requests
import sys

BASE_URL = "http://localhost:8002/api"


def test_get_coherence(conversation_id):
    """Retrieve coherence metrics for a conversation.
    
    This endpoint computes:
    - Drift metrics (moving variance)
    - Overall coherence score
    - Signal sources breakdown
    - Time range analysis
    """
    response = requests.get(
        f"{BASE_URL}/conversations/{conversation_id}/coherence",
        timeout=10,
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    result = response.json()
    
    # Verify response has required fields
    assert "id" in result, "Response missing 'id' field"
    assert result["id"] == conversation_id, "ID mismatch"
    
    print(f"✓ Coherence metrics retrieved for {conversation_id}", file=sys.stderr)
    print(f"  Coherence Score: {result.get('coherence_score_current')}", file=sys.stderr)
    return result


if __name__ == "__main__":
    if "--conversation-id" not in sys.argv:
        print("Error: --conversation-id required", file=sys.stderr)
        print("Usage: python test_get_coherence.py --conversation-id <id>", file=sys.stderr)
        sys.exit(1)
    
    try:
        conversation_id = sys.argv[sys.argv.index("--conversation-id") + 1]
        test_get_coherence(conversation_id)
        print("✓ Test passed")
    except Exception as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
