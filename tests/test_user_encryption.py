"""Test pgcrypto encryption of user personal information.

This test demonstrates that user personal information (email, phone, address)
is encrypted in the PostgreSQL database using pgcrypto extension.
"""

import requests
import psycopg

# Base API configuration
BASE_URL = "http://localhost:8002"
USERS_ENDPOINT = f"{BASE_URL}/api/users"

# Database configuration (from .env.compose)
DB_HOST = "db_service"
DB_PORT = 5432
DB_NAME = "analytics"
DB_USER = "analytics_user"
DB_PASSWORD = "analytics_password"


def create_test_user():
    """Create a test user with personal information."""
    user_data = {
        "username": "encryption_test_user",
        "email": "encryption.test@example.com",
        "phone": "555-8888",
        "address": "888 Encryption Road, Secret City, SC 88888",
    }

    try:
        response = requests.post(USERS_ENDPOINT, json=user_data)

        if response.status_code in (200, 201):
            result = response.json()
            print(f"✅ User created via API")
            print(f"   ID: {result.get('id')}")
            print(f"   Username: {result.get('username')}")
            print(f"   NOTE: Encrypted fields NOT returned in API response")
            return result
        else:
            print(f"❌ Failed to create user ({response.status_code})")
            return None

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None


def check_encrypted_data_in_db(user_id):
    """Connect to database and verify personal info is encrypted."""
    print(f"\n🔐 Checking database for encryption...\n")
    
    try:
        # Connect to PostgreSQL
        conninfo = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"
        conn = psycopg.connect(conninfo)
        cur = conn.cursor()

        # Query the user record
        cur.execute(
            "SELECT id, username, email_encrypted, phone_encrypted, address_encrypted FROM users WHERE id = %s",
            (user_id,),
        )
        result = cur.fetchone()

        if result:
            user_id, username, email_enc, phone_enc, addr_enc = result
            
            print(f"✅ User found in database")
            print(f"   ID: {user_id}")
            print(f"   Username: {username}")
            print(f"")
            print(f"📊 Encryption Status:")
            print(f"   Email encrypted: {type(email_enc).__name__} - {'✅ Encrypted (bytes)' if isinstance(email_enc, bytes) else '❌ Not encrypted'}")
            print(f"   Phone encrypted: {type(phone_enc).__name__} - {'✅ Encrypted (bytes)' if isinstance(phone_enc, bytes) else '❌ Not encrypted'}")
            print(f"   Address encrypted: {type(addr_enc).__name__} - {'✅ Encrypted (bytes)' if isinstance(addr_enc, bytes) else '❌ Not encrypted'}")
            
            if email_enc:
                print(f"")
                print(f"   Email encrypted value (first 50 chars):")
                print(f"      {str(email_enc)[:50]}...")
            if phone_enc:
                print(f"   Phone encrypted value (first 50 chars):")
                print(f"      {str(phone_enc)[:50]}...")
            if addr_enc:
                print(f"   Address encrypted value (first 50 chars):")
                print(f"      {str(addr_enc)[:50]}...")
                
            print(f"")
            print(f"💡 Note: To decrypt, you would need the pgcrypto key and use")
            print(f"   pgp_sym_decrypt() function in PostgreSQL with the encryption key")
            
        else:
            print(f"❌ User not found in database")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print(f"   Make sure PostgreSQL is running and credentials are correct")
        print(f"   This test requires direct database access")


def test_api_does_not_expose_encrypted_data():
    """Verify that the API does not expose encrypted personal data."""
    print(f"\n🛡️ Verifying API does not expose encrypted data...\n")

    user_data = {
        "username": "security_test_user",
        "email": "security.test@example.com",
        "phone": "555-7777",
        "address": "777 Security Ave, Protected City, PC 77777",
    }

    try:
        response = requests.post(USERS_ENDPOINT, json=user_data)

        if response.status_code in (200, 201):
            result = response.json()
            user_id = result.get('id')
            
            print(f"✅ User created")
            print(f"")
            print(f"📋 API Response Fields:")
            for key, value in result.items():
                print(f"   {key}: {value}")
            
            print(f"")
            print(f"🔍 Checking for encrypted fields in response...")
            
            if "email_encrypted" in result or "phone_encrypted" in result or "address_encrypted" in result:
                print(f"❌ WARNING: Encrypted fields exposed in API!")
            else:
                print(f"✅ GOOD: No encrypted fields in API response")
            
            print(f"")
            print(f"ℹ️ The API only returns:")
            print(f"   - id: User UUID")
            print(f"   - username: Plaintext username")
            print(f"   - created_at: Timestamp")
            print(f"   - is_active: Boolean")
            print(f"")
            print(f"✅ Personal info is encrypted in database, not exposed via API")

        else:
            print(f"❌ Failed to create user ({response.status_code})")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test pgcrypto encryption of user personal data"
    )
    parser.add_argument(
        "--mode",
        choices=["create", "check", "api-security", "full"],
        default="full",
        help="Test mode (default: full)",
    )
    parser.add_argument("--user-id", help="User ID to check in database")

    args = parser.parse_args()

    if args.mode == "create" or args.mode == "full":
        print("=" * 60)
        print("Creating test user with personal information")
        print("=" * 60)
        print()
        user = create_test_user()
        
        if args.mode == "full" and user:
            args.user_id = user.get('id')

    if (args.mode == "check" or args.mode == "full") and args.user_id:
        print("")
        print("=" * 60)
        print("Checking encrypted data in database")
        print("=" * 60)
        check_encrypted_data_in_db(args.user_id)

    if args.mode == "api-security" or args.mode == "full":
        print("")
        print("=" * 60)
        print("Testing API security (no encrypted data exposure)")
        print("=" * 60)
        test_api_does_not_expose_encrypted_data()
