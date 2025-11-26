"""Test DELETE /api/users/{user_id} endpoint."""

import requests

# Base API configuration
BASE_URL = "http://localhost:8002"
USERS_ENDPOINT = f"{BASE_URL}/api/users"


def test_delete_user(user_id):
    """Test deleting a user via DELETE endpoint."""
    endpoint = f"{USERS_ENDPOINT}/{user_id}"

    try:
        response = requests.delete(endpoint)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ User deleted successfully")
            print(f"   ID: {result.get('id')}")
            print(f"   Message: {result.get('message')}")
            return result
        elif response.status_code == 404:
            print(f"❌ User not found (404)")
            return None
        else:
            print(f"❌ Failed to delete user ({response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return None


def test_delete_and_verify(user_id):
    """Test deleting a user and verifying it's gone."""
    print(f"\n🗑️ Deleting user and verifying...\n")

    # Delete user
    delete_result = test_delete_user(user_id)

    if delete_result:
        print(f"\n   Verifying deletion...\n")
        
        # Try to get the deleted user
        endpoint = f"{USERS_ENDPOINT}/{user_id}"
        response = requests.get(endpoint)
        
        if response.status_code == 404:
            print(f"✅ Verified: User no longer exists in database")
        else:
            print(f"❌ Warning: User still exists (status {response.status_code})")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test DELETE /api/users/{user_id}")
    parser.add_argument("user_id", help="User ID to delete")
    parser.add_argument(
        "--verify", action="store_true", help="Verify deletion after deleting"
    )

    args = parser.parse_args()

    if args.verify:
        test_delete_and_verify(args.user_id)
    else:
        test_delete_user(args.user_id)
