"""Test POST /api/users/ endpoint"""

import requests
import sys
import uuid

BASE_URL = "http://localhost:8002/api"


def test_create_user():
    """Create a new user and return its ID."""
    payload = {
        "username": f"testuser{uuid.uuid4().hex[:8]}",
        "email": f"test{uuid.uuid4().hex[:8]}@example.com",
    }
    
    response = requests.post(
        f"{BASE_URL}/users/",
        json=payload,
        timeout=10,
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    result = response.json()
    
    # Verify response
    assert "id" in result, "Response missing 'id' field"
    
    user_id = result["id"]
    print(f"✓ User created: {user_id}", file=sys.stderr)
    return user_id


if __name__ == "__main__":
    try:
        user_id = test_create_user()
        print(user_id)  # Print just the ID for use in scripts
    except Exception as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
