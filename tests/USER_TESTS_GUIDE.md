# User Endpoints Testing Guide

This guide covers testing the new user management endpoints with pgcrypto encryption support.

## Overview

The user management system includes:

- **User Model** with encrypted personal information (email, phone, address)
- **CRUD Endpoints** for complete user lifecycle management
- **Relationship** between users and conversations
- **pgcrypto Encryption** for sensitive data

## Test Files

### Individual Test Files

1. **test_create_user.py** - POST /api/users/
   - Create new users
   - Test duplicate username validation
   - Create multiple users

2. **test_get_user.py** - GET /api/users/{user_id}
   - Retrieve user details
   - Test non-existent user (404)
   - Verify encrypted fields are NOT exposed in API

3. **test_patch_user.py** - PATCH /api/users/{user_id}
   - Update personal information (email, phone, address)
   - Deactivate/reactivate users
   - Update multiple fields

4. **test_delete_user.py** - DELETE /api/users/{user_id}
   - Delete users
   - Verify deletion

5. **test_user_conversations.py** - GET /api/users/{user_id}/conversations
   - Retrieve all conversations for a user
   - Test user-conversation relationship integration

6. **test_user_encryption.py** - pgcrypto Encryption Verification
   - Create users and verify encryption in database
   - Check that encrypted data is stored as bytes
   - Verify API does not expose encrypted fields

### Master Test Runner

**run_user_tests.py** - Comprehensive test suite

- CRUD workflow
- Encryption demonstration
- Relationship integration
- Multiple users test
- Validation tests

## Running Tests

### Individual Tests

```bash
# Create a single user
python test_create_user.py

# Create multiple users
python test_create_user.py --count 5

# Test duplicate username validation
python test_create_user.py --duplicate

# Get user details
python test_get_user.py <user_id>

# Update user (personal info)
python test_patch_user.py <user_id> --action personal

# Deactivate user
python test_patch_user.py <user_id> --action deactivate

# Reactivate user
python test_patch_user.py <user_id> --action reactivate

# Delete user
python test_delete_user.py <user_id>

# Delete and verify
python test_delete_user.py <user_id> --verify

# Get user conversations
python test_user_conversations.py --user-id <user_id>

# Test relationship integration
python test_user_conversations.py --integration

# Test encryption
python test_user_encryption.py --mode full

# Check encryption in database
python test_user_encryption.py --mode check --user-id <user_id>
```

### Master Test Runner

```bash
# Run all tests (CRUD + encryption + relationships + validation)
python run_user_tests.py

# Run specific test mode
python run_user_tests.py --mode crud
python run_user_tests.py --mode encryption
python run_user_tests.py --mode relationship
python run_user_tests.py --mode validation

# Create multiple users (10 users)
python run_user_tests.py --mode multiple --count 10
```

## API Endpoints

### POST /api/users/ - Create User

**Request:**

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "phone": "555-1234",
  "address": "123 Main St, City, State 12345"
}
```

**Response:**

```json
{
  "id": "5bc6bb20-850b-4c46-a0e5-932d1e020e21",
  "username": "john_doe",
  "created_at": "2025-11-26T01:26:54.800206",
  "is_active": true
}
```

**Note:** Email, phone, and address are encrypted in the database but NOT returned in the API response.

### GET /api/users/{user_id} - Get User

**Response:**

```json
{
  "id": "5bc6bb20-850b-4c46-a0e5-932d1e020e21",
  "username": "john_doe",
  "created_at": "2025-11-26T01:26:54.800206",
  "is_active": true
}
```

### PATCH /api/users/{user_id} - Update User

**Request (update personal info):**

```json
{
  "email": "newemail@example.com",
  "phone": "555-5555",
  "address": "456 New Ave, New City, State 54321"
}
```

**Request (change status):**

```json
{
  "is_active": false
}
```

**Response:**

```json
{
  "id": "5bc6bb20-850b-4c46-a0e5-932d1e020e21",
  "username": "john_doe",
  "created_at": "2025-11-26T01:26:54.800206",
  "is_active": false
}
```

### DELETE /api/users/{user_id} - Delete User

**Response:**

```json
{
  "message": "User deleted successfully",
  "id": "5bc6bb20-850b-4c46-a0e5-932d1e020e21"
}
```

### GET /api/users/{user_id}/conversations - Get User Conversations

**Response:**

```json
{
  "user_id": "5bc6bb20-850b-4c46-a0e5-932d1e020e21",
  "conversation_count": 3,
  "conversations": [
    {
      "id": "a2341424-93a0-4e40-9779-610844ab742c",
      "user_id": "5bc6bb20-850b-4c46-a0e5-932d1e020e21",
      "agent_id": "agent_001",
      "started_at": "2025-11-26T01:27:01.253133",
      "ended_at": null,
      "coherence_score_current": null,
      "coherence_score_trend": null,
      "context_metadata": null
    }
  ]
}
```

## Understanding pgcrypto Encryption

### What Gets Encrypted

Personal information is encrypted at the database level:

- `email_encrypted` - encrypted user email
- `phone_encrypted` - encrypted phone number
- `address_encrypted` - encrypted address

### Encryption Flow

1. **API Request** → Client sends plaintext personal info
2. **Database** → Encrypted using pgcrypto (PostgreSQL extension)
3. **Storage** → Encrypted bytes stored in `bytea` columns
4. **API Response** → Encrypted fields NOT included in response

### Database Column Types

```sql
-- Column definitions in users table
email_encrypted bytea       -- Stores encrypted email
phone_encrypted bytea       -- Stores encrypted phone
address_encrypted bytea     -- Stores encrypted address
```

### Verifying Encryption

To verify data is encrypted, you can:

1. **Use the test script:**

   ```bash
   python test_user_encryption.py --mode full
   ```

2. **Direct database check:**

   ```sql
   -- Connect to PostgreSQL
   SELECT id, username, email_encrypted, phone_encrypted, address_encrypted
   FROM users
   WHERE id = '<user_id>';
   ```

   You'll see encrypted values as bytea (binary data).

3. **Decryption (requires key):**
   ```sql
   -- Using pgp_sym_decrypt (requires the encryption key)
   SELECT pgp_sym_decrypt(email_encrypted, 'your_secret_key'::bytea)
   FROM users
   WHERE id = '<user_id>';
   ```

## Security Features

### ✅ What's Protected

- Personal information encrypted at database level
- Encrypted fields NOT exposed in API responses
- Each field encrypted independently
- Uses PostgreSQL's pgcrypto extension

### ✅ What's Not Encrypted (by design)

- `id` - User UUID (needed for queries)
- `username` - Username (plaintext for authentication)
- `created_at` - Timestamp metadata
- `updated_at` - Timestamp metadata
- `is_active` - User status flag

## Relationships

### User → Conversations

Users can have multiple conversations:

```
User (1) ──────→ (Many) Conversations
   ↓
   └── Linked via: conversations.user_id = users.id
```

**Example:**

```bash
# Create user
user=$(python test_create_user.py | grep "ID:" | awk '{print $2}')

# Create conversations for that user
python test_create_conversation.py

# Retrieve all conversations for user
python test_user_conversations.py --user-id $user
```

## Validation

### Username Validation

- Must be unique
- Cannot create duplicate usernames

### Test:

```bash
python test_create_user.py --duplicate
```

### Non-existent User

- Returns 404 error
- Properly handled in all endpoints

### Test:

```bash
python test_get_user.py 00000000-0000-0000-0000-000000000000
```

## Common Workflows

### Create User, Update Info, Create Conversation

```bash
# 1. Create user
python test_create_user.py
# Output: id = <user_id>, username = test_user_000

# 2. Update user's email (gets encrypted)
python test_patch_user.py <user_id> --action personal

# 3. Create conversation for user
python test_create_conversation.py

# 4. Link conversation to user
python test_create_conversation.py
# (use the user_id from step 1)

# 5. Retrieve user's conversations
python test_user_conversations.py --user-id <user_id>
```

### Test Full Encryption

```bash
# Run full encryption test
python test_user_encryption.py --mode full

# This will:
# 1. Create a user with personal info
# 2. Check database for encrypted bytes
# 3. Verify API doesn't expose encrypted data
```

## Troubleshooting

### ImportError: psycopg

```bash
# Install psycopg for database access
pip install psycopg[binary]
```

### Connection Error to Database

Make sure PostgreSQL is running:

```bash
docker compose ps
```

### User Not Found

Verify user exists:

```bash
# Run integration test to create users
python run_user_tests.py --mode crud
```

## Next Steps

### Implementing pgcrypto Triggers

To fully automate encryption, add PostgreSQL triggers:

```sql
CREATE TRIGGER encrypt_user_email
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION encrypt_email();
```

### Key Management

For production, implement proper key management:

1. Store encryption key securely (not in code)
2. Rotate keys periodically
3. Use environment variables for keys
4. Implement key versioning

### Decryption Endpoint

Next steps adding a secure endpoint for decryption:

```
GET /api/users/{user_id}/personal-info
Authorization: Bearer <admin_token>
```

Returns decrypted personal information (requires admin auth).
