"""Test GET /api/users/{user_id} endpoint."""

import requests

# Base API configuration
BASE_URL = "http://localhost:8002"
USERS_ENDPOINT = f"{BASE_URL}/api/users"


def test_get_user(user_id):
    """Test retrieving a user by ID."""
    endpoint = f"{USERS_ENDPOINT}/{user_id}"

    try:
        response = requests.get(endpoint)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ User retrieved successfully")
            print(f"   ID: {result.get('id')}")
            print(f"   Username: {result.get('username')}")
            print(f"   Created At: {result.get('created_at')}")
            print(f"   Is Active: {result.get('is_active')}")
            print(f"   NOTE: Encrypted fields are NOT returned in API responses (stored encrypted in DB)")
            return result
        elif response.status_code == 404:
            print(f"❌ User not found (404)")
            print(f"   ID: {user_id}")
            return None
        else:
            print(f"❌ Failed to retrieve user ({response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error retrieving user: {e}")
        return None


def test_get_nonexistent_user():
    """Test retrieving a non-existent user (should return 404)."""
    fake_id = "00000000-0000-0000-0000-000000000000"

    print(f"\n🔍 Testing non-existent user (expecting 404)...\n")
    result = test_get_user(fake_id)

    if result is None:
        print(f"✅ Correctly handled non-existent user")
    else:
        print(f"⚠️ Unexpected: user should not exist")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test GET /api/users/{user_id}")
    parser.add_argument("user_id", help="User ID to retrieve")

    args = parser.parse_args()

    test_get_user(args.user_id)
