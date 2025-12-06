# Test Guide - Coherence Signal Architecture

This directory contains **14 simple, focused test scripts** - one per API endpoint. Each test can be run independently.

## Quick Start

### Run a Single Test

```bash
# Create a conversation (returns conversation_id)
python test_create_conversation.py

# Then use the ID to test other endpoints
python test_get_conversation.py --conversation-id <id>
```

## Available Tests

| File | Endpoint | Method | Prerequisites |
|------|----------|--------|---|
| **test_create_conversation.py** | `/api/conversations/` | POST | None |
| **test_get_conversation.py** | `/api/conversations/{id}` | GET | `--conversation-id` |
| **test_patch_conversation.py** | `/api/conversations/{id}` | PATCH | `--conversation-id` |
| **test_create_signal.py** | `/api/signals/` | POST | `--conversation-id` |
| **test_get_signal.py** | `/api/signals/{id}` | GET | `--signal-id` |
| **test_batch_signals.py** | `/api/signals/batch` | POST | `--conversation-id` |
| **test_list_signals.py** | `/api/signals/` | GET | None |
| **test_get_signals_by_conversation.py** | `/api/signals/conversation/{id}` | GET | `--conversation-id` |
| **test_get_coherence.py** ⭐ | `/api/conversations/{id}/coherence` | GET | `--conversation-id` |
| **test_create_user.py** | `/api/users/` | POST | None |
| **test_get_user.py** | `/api/users/{id}` | GET | `--user-id` |
| **test_patch_user.py** | `/api/users/{id}` | PATCH | `--user-id` |
| **test_delete_user.py** | `/api/users/{id}` | DELETE | `--user-id` |
| **test_user_conversations.py** | `/api/users/{id}/conversations` | GET | `--user-id` |

## Usage Examples

### Example 1: Test Conversation Endpoints

```bash
# Create a conversation
conversation_id=$(python test_create_conversation.py)

# Get the conversation
python test_get_conversation.py --conversation-id $conversation_id

# Update the conversation
python test_patch_conversation.py --conversation-id $conversation_id
```

### Example 2: Test Signal Endpoints

```bash
# First create a conversation
conversation_id=$(python test_create_conversation.py)

# Create a signal
signal_id=$(python test_create_signal.py --conversation-id $conversation_id)

# Get the signal
python test_get_signal.py --signal-id $signal_id

# List all signals
python test_list_signals.py

# Get signals for that conversation
python test_get_signals_by_conversation.py --conversation-id $conversation_id

# Test batch signal creation
python test_batch_signals.py --conversation-id $conversation_id

# Test coherence calculation (CORE ENDPOINT)
python test_get_coherence.py --conversation-id $conversation_id
```

### Example 3: Test User Endpoints

```bash
# Create a user
user_id=$(python test_create_user.py)

# Get the user
python test_get_user.py --user-id $user_id

# Update the user
python test_patch_user.py --user-id $user_id

# Get user's conversations
python test_user_conversations.py --user-id $user_id

# Delete the user
python test_delete_user.py --user-id $user_id
```

## Test Output

Each test prints one of two outputs:

**Success:**
```
✓ Conversation created: abc-123
abc-123
```

**Failure:**
```
✗ Test failed: Expected 200, got 404: {"detail":"Conversation not found"}
```

Tests return IDs or data to stdout (for piping), errors to stderr (for visibility).

## Complete Workflow

```bash
# Setup
conversation_id=$(python test_create_conversation.py)
user_id=$(python test_create_user.py)

# Test conversation operations
python test_get_conversation.py --conversation-id $conversation_id
python test_patch_conversation.py --conversation-id $conversation_id

# Create signals
signal_id=$(python test_create_signal.py --conversation-id $conversation_id)

# Test signal operations
python test_get_signal.py --signal-id $signal_id
python test_list_signals.py
python test_get_signals_by_conversation.py --conversation-id $conversation_id
python test_batch_signals.py --conversation-id $conversation_id

# Test core endpoint
python test_get_coherence.py --conversation-id $conversation_id

# Test user operations
python test_get_user.py --user-id $user_id
python test_patch_user.py --user-id $user_id
python test_user_conversations.py --user-id $user_id
python test_delete_user.py --user-id $user_id
```

## Understanding Each Test

### Conversation Tests

- **test_create_conversation.py**: Creates a new conversation, returns its ID
- **test_get_conversation.py**: Retrieves a conversation's details
- **test_patch_conversation.py**: Updates conversation data
- **test_get_coherence.py** ⭐: **CORE ENDPOINT** - Calculates coherence metrics, persists drift metrics

### Signal Tests

- **test_create_signal.py**: Creates a single signal in a conversation
- **test_get_signal.py**: Retrieves a signal by ID
- **test_batch_signals.py**: Creates multiple signals in one transaction
- **test_list_signals.py**: Lists signals with time-bucketing (aggregation)
- **test_get_signals_by_conversation.py**: Retrieves all signals in a conversation

### User Tests

- **test_create_user.py**: Creates a new user, returns its ID
- **test_get_user.py**: Retrieves a user's details
- **test_patch_user.py**: Updates user data
- **test_delete_user.py**: Deletes a user
- **test_user_conversations.py**: Lists conversations for a user

## Troubleshooting

### Connection Refused

```
Error: HTTPConnectionPool ... Failed to establish a new connection
```

**Solution**: Start the API server

```bash
docker compose up -d
docker compose logs app  # Check server logs
```

### Required Arguments

```
Error: --conversation-id required
Usage: python test_get_conversation.py --conversation-id <id>
```

**Solution**: Some tests need data from other tests

```bash
# First create data
conversation_id=$(python test_create_conversation.py)

# Then test with that ID
python test_get_conversation.py --conversation-id $conversation_id
```

### 404 Errors

```
Expected 200, got 404: {"detail":"Conversation not found"}
```

**Solution**: The ID doesn't exist. Create it first or verify it's correct

```bash
conversation_id=$(python test_create_conversation.py)
python test_get_conversation.py --conversation-id $conversation_id
```

## Database Verification

After running tests, verify data in the database:

```bash
# Connect to database
docker compose exec -T db_service psql -U time-user -d timescaledb

# List conversations
SELECT id, title FROM conversations LIMIT 10;

# List signals
SELECT id, context_window_id, signal_score FROM signals LIMIT 10;

# List users
SELECT id, name, email FROM users LIMIT 10;

# Check drift metrics (persisted by coherence endpoint)
SELECT conversation_id, window_start, drift_score FROM signal_drift_metrics LIMIT 10;
```

## Additional Resources

- **Batch Signals**: See `BATCH_INGESTION_GUIDE.md` for detailed batch API usage
- **API Examples**: See `../API_EXAMPLES.md` for curl examples
- **Architecture**: See `../README.md` for system overview

## Notes

- All tests use simple `--argument-name <value>` syntax (no complex modes)
- Tests are independent - run any test without running others first
- Tests that create data return the ID for use in other tests
- Tests that need data take `--conversation-id`, `--user-id`, `--signal-id` arguments
- All tests print success/failure and exit with status 0 (success) or 1 (failure)
