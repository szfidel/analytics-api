"""Test PATCH /api/users/{user_id} endpoint"""

import requests
import sys

BASE_URL = "http://localhost:8002/api"


def test_patch_user(user_id):
    """Update a user."""
    payload = {
        "name": "Updated User Name",
    }
    
    response = requests.patch(
        f"{BASE_URL}/users/{user_id}",
        json=payload,
        timeout=10,
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    result = response.json()
    
    # Verify response
    assert "id" in result, "Response missing 'id' field"
    assert result["id"] == user_id, "ID mismatch"
    
    print(f"✓ User updated: {user_id}", file=sys.stderr)
    return result


if __name__ == "__main__":
    if "--user-id" not in sys.argv:
        print("Error: --user-id required", file=sys.stderr)
        print("Usage: python test_patch_user.py --user-id <id>", file=sys.stderr)
        sys.exit(1)
    
    try:
        user_id = sys.argv[sys.argv.index("--user-id") + 1]
        test_patch_user(user_id)
        print("✓ Test passed")
    except Exception as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
