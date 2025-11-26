"""Test PATCH /api/users/{user_id} endpoint."""

import requests

# Base API configuration
BASE_URL = "http://localhost:8002"
USERS_ENDPOINT = f"{BASE_URL}/api/users"


def test_patch_user(user_id, update_data):
    """Test updating a user via PATCH endpoint."""
    endpoint = f"{USERS_ENDPOINT}/{user_id}"

    try:
        response = requests.patch(endpoint, json=update_data)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ User updated successfully")
            print(f"   ID: {result.get('id')}")
            print(f"   Username: {result.get('username')}")
            print(f"   Is Active: {result.get('is_active')}")
            print(f"   Updated At: {result.get('updated_at')}")
            return result
        elif response.status_code == 404:
            print(f"❌ User not found (404)")
            return None
        else:
            print(f"❌ Failed to update user ({response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error updating user: {e}")
        return None


def test_update_personal_info(user_id):
    """Test updating personal information (will be encrypted)."""
    print(f"\n✏️ Updating personal information...\n")

    update_data = {
        "email": "newemail@example.com",
        "phone": "555-9999",
        "address": "999 Updated Ave, New City, New State 99999",
    }

    result = test_patch_user(user_id, update_data)
    if result:
        print(f"   NOTE: Personal info is encrypted before storage in pgcrypto")
    return result


def test_deactivate_user(user_id):
    """Test deactivating a user."""
    print(f"\n🔒 Deactivating user...\n")

    update_data = {"is_active": False}

    result = test_patch_user(user_id, update_data)
    return result


def test_reactivate_user(user_id):
    """Test reactivating a user."""
    print(f"\n🔓 Reactivating user...\n")

    update_data = {"is_active": True}

    result = test_patch_user(user_id, update_data)
    return result


def test_update_multiple_fields(user_id):
    """Test updating multiple fields at once."""
    print(f"\n🔄 Updating multiple fields...\n")

    update_data = {
        "email": "multi@example.com",
        "phone": "555-5555",
        "is_active": True,
    }

    result = test_patch_user(user_id, update_data)
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test PATCH /api/users/{user_id}")
    parser.add_argument("user_id", help="User ID to update")
    parser.add_argument(
        "--action",
        choices=["personal", "deactivate", "reactivate", "all"],
        default="personal",
        help="What to update (default: personal)",
    )

    args = parser.parse_args()

    if args.action == "personal":
        test_update_personal_info(args.user_id)
    elif args.action == "deactivate":
        test_deactivate_user(args.user_id)
    elif args.action == "reactivate":
        test_reactivate_user(args.user_id)
    elif args.action == "all":
        test_update_multiple_fields(args.user_id)
