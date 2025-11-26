"""Test POST /api/users/ endpoint."""

import requests

# Base API configuration
BASE_URL = "http://localhost:8002"
ENDPOINT = f"{BASE_URL}/api/users/"


def generate_user(index=0):
    """Generate a user payload with personal information."""
    return {
        "username": f"test_user_{index:03d}",
        "email": f"user_{index:03d}@example.com",
        "phone": f"555-{1000 + index:04d}",
        "address": f"{100 + index} Test Street, City, State 12345",
    }


def test_create_user():
    """Test creating a new user via POST endpoint."""
    user_data = generate_user()

    try:
        response = requests.post(ENDPOINT, json=user_data)

        if response.status_code in (200, 201):
            result = response.json()
            print(f"✅ User created successfully")
            print(f"   ID: {result.get('id')}")
            print(f"   Username: {result.get('username')}")
            print(f"   Created At: {result.get('created_at')}")
            print(f"   Is Active: {result.get('is_active')}")
            print(f"   NOTE: Encrypted fields (email, phone, address) are encrypted in database")
            return result
        else:
            print(f"❌ Failed to create user ({response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None


def test_create_multiple_users(count=3):
    """Test creating multiple users."""
    print(f"\n👥 Creating {count} users...\n")

    users = []
    for i in range(count):
        user = test_create_user()
        if user:
            users.append(user)

        if i < count - 1:
            print()

    return users


def test_duplicate_username():
    """Test that duplicate usernames are rejected."""
    print(f"\n🔄 Testing duplicate username rejection...\n")
    
    user_data = generate_user(999)
    
    # Create first user
    response1 = requests.post(ENDPOINT, json=user_data)
    
    if response1.status_code in (200, 201):
        print(f"✅ First user created")
        user1 = response1.json()
        print(f"   ID: {user1.get('id')}")
        print(f"   Username: {user1.get('username')}")
        
        # Try to create second user with same username
        print(f"\n   Attempting to create duplicate username...")
        response2 = requests.post(ENDPOINT, json=user_data)
        
        if response2.status_code == 400:
            print(f"✅ Correctly rejected duplicate username (400)")
            print(f"   Error: {response2.json().get('detail')}")
        else:
            print(f"❌ Expected 400, got {response2.status_code}")
            print(f"   Response: {response2.text}")
    else:
        print(f"❌ Failed to create first user ({response1.status_code})")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test POST /api/users/")
    parser.add_argument(
        "--count", type=int, default=1, help="Number of users to create"
    )
    parser.add_argument(
        "--duplicate", action="store_true", help="Test duplicate username rejection"
    )

    args = parser.parse_args()

    if args.duplicate:
        test_duplicate_username()
    elif args.count == 1:
        test_create_user()
    else:
        test_create_multiple_users(args.count)
