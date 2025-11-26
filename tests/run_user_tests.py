"""Master test runner for user endpoints - tests CRUD and relationships."""

import sys
from test_create_user import test_create_user, test_create_multiple_users, test_duplicate_username
from test_get_user import test_get_user, test_get_nonexistent_user
from test_patch_user import (
    test_update_personal_info,
    test_deactivate_user,
    test_reactivate_user,
)
from test_delete_user import test_delete_user, test_delete_and_verify
from test_user_conversations import test_relationship_integration, test_get_user_conversations


def run_user_crud_workflow():
    """Run a complete user CRUD workflow:
    1. Create a user
    2. Get user details
    3. Update user personal info
    4. Update user status (deactivate/reactivate)
    5. Delete user
    """
    print("=" * 80)
    print("👤 USER CRUD WORKFLOW TEST")
    print("=" * 80)

    # Step 1: Create user
    print("\n\n📌 STEP 1: Create User")
    print("-" * 80)
    user = test_create_user()
    if not user:
        print("❌ Failed to create user. Aborting.")
        return False

    user_id = user.get("id")
    print(f"\n✅ User created: {user_id}")

    # Step 2: Get user details
    print("\n\n📌 STEP 2: Get User Details")
    print("-" * 80)
    retrieved_user = test_get_user(user_id)
    if not retrieved_user:
        print("⚠️ Failed to retrieve user")
    else:
        print(f"\n✅ User retrieved successfully")

    # Step 3: Update personal info
    print("\n\n📌 STEP 3: Update Personal Information (encrypted)")
    print("-" * 80)
    updated_user = test_update_personal_info(user_id)
    if not updated_user:
        print("⚠️ Failed to update personal info")
    else:
        print(f"\n✅ Personal info updated (encrypted in DB)")

    # Step 4: Deactivate user
    print("\n\n📌 STEP 4: Deactivate User")
    print("-" * 80)
    deactivated_user = test_deactivate_user(user_id)
    if not deactivated_user:
        print("⚠️ Failed to deactivate user")
    else:
        print(f"\n✅ User deactivated")

    # Step 5: Reactivate user
    print("\n\n📌 STEP 5: Reactivate User")
    print("-" * 80)
    reactivated_user = test_reactivate_user(user_id)
    if not reactivated_user:
        print("⚠️ Failed to reactivate user")
    else:
        print(f"\n✅ User reactivated")

    # Step 6: Delete user
    print("\n\n📌 STEP 6: Delete User")
    print("-" * 80)
    deleted_user = test_delete_and_verify(user_id)

    print("\n\n" + "=" * 80)
    print("✅ USER CRUD WORKFLOW TEST COMPLETED")
    print("=" * 80)

    return True


def run_encryption_demonstration():
    """Run tests to demonstrate pgcrypto encryption."""
    print("=" * 80)
    print("🔐 PGCRYPTO ENCRYPTION DEMONSTRATION")
    print("=" * 80)

    try:
        from test_user_encryption import (
            create_test_user as create_enc_user,
            test_api_does_not_expose_encrypted_data,
        )

        print("\n\n📌 STEP 1: Create User with Personal Info")
        print("-" * 80)
        user = create_enc_user()
        if not user:
            print("⚠️ Failed to create user")
            return False

        print("\n\n📌 STEP 2: Verify API Does Not Expose Encrypted Data")
        print("-" * 80)
        test_api_does_not_expose_encrypted_data()

        print("\n\n" + "=" * 80)
        print("✅ ENCRYPTION DEMONSTRATION COMPLETED")
        print("=" * 80)
        return True

    except ImportError as e:
        print(f"⚠️ Could not run encryption test: {e}")
        print("   Make sure psycopg is installed: pip install psycopg[binary]")
        return False


def run_relationship_workflow():
    """Run user-conversation relationship integration test."""
    print("=" * 80)
    print("🔗 USER-CONVERSATION RELATIONSHIP WORKFLOW")
    print("=" * 80)

    test_relationship_integration()

    return True


def run_multiple_users_test(count=3):
    """Test creating multiple users."""
    print("=" * 80)
    print(f"👥 CREATING {count} USERS TEST")
    print("=" * 80)

    users = test_create_multiple_users(count)

    if users:
        print(f"\n\n✅ Successfully created {len(users)} users")
        print("\nUser IDs:")
        for i, user in enumerate(users, 1):
            print(f"  {i}. {user.get('id')} - {user.get('username')}")
    else:
        print(f"\n\n❌ Failed to create users")

    return bool(users)


def run_validation_tests():
    """Run validation tests (duplicate username, etc)."""
    print("=" * 80)
    print("✔️ VALIDATION TESTS")
    print("=" * 80)

    # Test duplicate username
    print("\n\n📌 TEST: Duplicate Username Rejection")
    print("-" * 80)
    test_duplicate_username()

    # Test non-existent user
    print("\n\n📌 TEST: Non-Existent User (404)")
    print("-" * 80)
    test_get_nonexistent_user()

    print("\n\n" + "=" * 80)
    print("✅ VALIDATION TESTS COMPLETED")
    print("=" * 80)

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Master test runner for user endpoints")
    parser.add_argument(
        "--mode",
        choices=["crud", "encryption", "relationship", "multiple", "validation", "all"],
        default="all",
        help="Test mode to run (default: all)",
    )
    parser.add_argument(
        "--count", type=int, default=3, help="Number of users to create in multiple test"
    )

    args = parser.parse_args()

    success = True

    if args.mode in ("crud", "all"):
        success = run_user_crud_workflow() and success

    if args.mode in ("encryption", "all"):
        success = run_encryption_demonstration() and success

    if args.mode in ("relationship", "all"):
        success = run_relationship_workflow() and success

    if args.mode in ("multiple", "all"):
        success = run_multiple_users_test(args.count) and success

    if args.mode in ("validation", "all"):
        success = run_validation_tests() and success

    sys.exit(0 if success else 1)
