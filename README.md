# Coherence Signal Architecture API using: FastAPI + SQLModel + TimescaleDB + PostgreSQL

Version 1.1 - Coherence Signal Architecture

**Purpose:** Advanced time-series signal analysis with coherence scoring and drift detection using TimescaleDB

**Tech Stack:** FastAPI, PostgreSQL + TimescaleDB, SQLModel, Uvicorn, Pinecone (vector DB)

**Latest Updates (Dec 2025):**

- ✨ **NEW:** Bulk Signal Ingestion Endpoint (`POST /api/signals/batch`) - 10-12x performance improvement
- 🧪 **IMPROVED:** Reorganized test suite - 14 simple, focused tests (one per endpoint)
- 📚 **UPDATED:** Unified testing documentation with complete workflow examples
- 🔧 **FIXED:** All user tests working with proper field validation

**Key Features:**

- User management with pgcrypto encrypted personal information
- Signal ingestion from multiple sources (Axis, M, Neo, person, Slack, etc.)
- **Bulk signal ingestion** with ACID transaction support (NEW)
- Vector-native signal capture with Pinecone embedding references
- Conversation/session grouping and tracking with user relationships
- Real-time coherence scoring via drift analysis
- Moving variance computation over sliding time windows
- Signal lineage and source diversity metrics
- REST API for signal CRUD and coherence analytics
- Comprehensive test suite with 14 simple, independent test files

**Data Model:**

- `users`: User profiles with encrypted personal information (email, phone, address)
- `conversations`: Session/timeline grouping for coherence tracking, linked to users
- `signals`: Vector-native signal capture with source, score, and Pinecone vector reference
- `signal_drift_metrics`: Drift measurements (variance) per conversation window
- **Relationships:** Users → Conversations (1:M), Conversations → SignalDriftMetrics (1:M)

**Deployment:** Docker + Docker Compose with TimescaleDB + PostgreSQL

## Docker

Build image

- `docker build -t analytics-api -f Dockerfile.web .`
  Run container
- `docker run analytics-api `

- `docker compose run app /bin/bash` or `docker compose run app python`

# Quick Start

## Prerequisites

- Docker & Docker Compose
- Python 3.13+ (for local development)

## Run with Docker Compose

### Start the API and database

`docker compose up --build`

### Or with hot-reload enabled

`docker compose up --watch`
The API will be available at http://localhost:8002

### Run interactive bash in container

`docker compose run app /bin/bash`

### Or run Python REPL

`docker compose run app python`

### Stop containers

`docker compose down`

### Remove volumes (database data)

`docker compose down -v`

### Test the API:

curl http://localhost:8002/healthz
curl http://localhost:8002/
Clean Up

# API Endpoints

## Health Check

**GET /healthz**

```
Returns: {"status": "ok"}
```

---

## Signal Management

### Create Signals in Batch (High Performance)

**POST /api/signals/batch**

Create multiple signals in a single transaction with ACID guarantees.

Query Parameters:

- `fail_on_error` (boolean, default: false): Operation mode
  - `false`: Best-effort (continue on errors, report per-item status)
  - `true`: All-or-nothing (rollback entire batch on any error)

Request Body:

```json
{
  "signals": [
    {
      "context_window_id": "conv-123",
      "raw_content": "Signal 1 content",
      "signal_source": "Slack",
      "signal_score": 0.85,
      "payload": { "custom": "metadata" }
    },
    {
      "context_window_id": "conv-123",
      "raw_content": "Signal 2 content",
      "signal_source": "Axis",
      "signal_score": 0.72
    }
  ],
  "fail_on_error": false
}
```

Response:

```json
{
  "total_count": 2,
  "successful_count": 2,
  "failed_count": 0,
  "results": [
    {
      "index": 0,
      "success": true,
      "signal_id": 1001,
      "error": null
    },
    {
      "index": 1,
      "success": true,
      "signal_id": 1002,
      "error": null
    }
  ]
}
```

**Performance:** 10-12x improvement over single signal creation (400+ signals/sec vs 40 sig/sec)

**Use Cases:**

- Chat log imports (1000+ messages in seconds)
- Event stream processing (high-throughput ingestion)
- Database migrations and bulk operations
- API integrations with batch requirements

See `tests/BATCH_INGESTION_GUIDE.md` for detailed batch API documentation.

### List Signals (Time-Bucketed Aggregation)

**GET /api/signals/**

Query Parameters:

- `duration` (string, default: "1 day"): Time bucket duration (e.g., "1 hour", "7 days")
- `context_window_id` (string, optional): Filter by conversation ID
- `signal_sources` (array, optional): Filter by signal sources (e.g., "Axis", "M", "Neo", "person")

Response:

```json
[
  {
    "bucket": "2024-11-18T00:00:00Z",
    "signal_source": "Axis",
    "agent_id": "agent-123",
    "avg_signal_score": 0.75,
    "avg_emotional_tone": 0.65,
    "total_count": 42
  }
]
```

### Create Signal

**POST /api/signals/**

Request Body:

```json
{
  "timestamp": "2024-11-18T10:30:00Z",
  "user_id": "user-123",
  "agent_id": "agent-123",
  "raw_content": "This is the signal text",
  "context_window_id": "conv-abc123",
  "signal_source": "Axis",
  "signal_score": 0.85,
  "signal_vector": "pinecone_vector_id_12345",
  "emotional_tone": 0.7,
  "escalate_flag": 0,
  "payload": { "custom": "metadata" }
}
```

### Get Signal by ID

**GET /api/signals/{signal_id}**

Returns a single signal with all details.

### Get Signals by Conversation

**GET /api/signals/conversation/{context_window_id}**

Query Parameters:

- `limit` (int, default: 100): Maximum signals to return

Returns list of signals in a conversation, ordered by timestamp.

---

## Conversation Management

### Create Conversation

**POST /api/conversations/**

Request Body:

```json
{
  "user_id": "user-123",
  "agent_id": "agent-123",
  "started_at": "2024-11-18T10:00:00Z",
  "context_metadata": { "topic": "coherence analysis" }
}
```

Response:

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "agent_id": "agent-123",
  "started_at": "2024-11-18T10:00:00Z",
  "ended_at": null,
  "coherence_score_current": null,
  "coherence_score_trend": null
}
```

### Get Conversation

**GET /api/conversations/{conversation_id}**

Returns conversation details and metadata.

### Update Conversation

**PATCH /api/conversations/{conversation_id}**

Request Body:

```json
{
  "ended_at": "2024-11-18T11:30:00Z",
  "coherence_score_current": 0.82,
  "coherence_score_trend": 0.05
}
```

### Get Coherence Metrics (Core Endpoint)

**GET /api/conversations/{conversation_id}/coherence**

Query Parameters:

- `window_size` (string, default: "5m"): Drift calculation window (e.g., "5m", "1h", "30s")

Response:

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "coherence_score_current": 0.82,
  "coherence_score_trend": 0.05,
  "drift_metrics": [
    {
      "id": 1,
      "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
      "window_start": "2024-11-18T10:00:00Z",
      "window_end": "2024-11-18T10:05:00Z",
      "drift_score": 0.15,
      "signal_count": 8,
      "coherence_trend": null
    }
  ],
  "signal_sources": {
    "Axis": 15,
    "M": 12,
    "person": 8
  },
  "total_signal_count": 35,
  "time_range_start": "2024-11-18T10:00:00Z",
  "time_range_end": "2024-11-18T11:30:00Z"
}
```

---

## User Management

### Create User

**POST /api/users/**

Request Body:

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "phone": "555-1234",
  "address": "123 Main St, City, State 12345"
}
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "created_at": "2024-11-26T12:00:00Z",
  "is_active": true
}
```

**Note:** Personal information (email, phone, address) is encrypted in the database but NOT returned in API responses for security.

### Get User

**GET /api/users/{user_id}**

Returns user details without exposing encrypted personal information.

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "created_at": "2024-11-26T12:00:00Z",
  "is_active": true
}
```

### Update User

**PATCH /api/users/{user_id}**

Request Body (all fields optional):

```json
{
  "email": "newemail@example.com",
  "phone": "555-5555",
  "address": "456 New Ave, New City, State 54321",
  "is_active": false
}
```

Response: Updated user object

### Delete User

**DELETE /api/users/{user_id}**

Permanently deletes a user from the system.

Response:

```json
{
  "message": "User deleted successfully",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Get User's Conversations

**GET /api/users/{user_id}/conversations**

Retrieves all conversations associated with a user (via foreign key relationship).

Response:

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "conversation_count": 3,
  "conversations": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "agent_id": "agent-123",
      "started_at": "2024-11-26T10:00:00Z",
      "ended_at": null,
      "coherence_score_current": 0.82,
      "coherence_score_trend": 0.05
    }
  ]
}
```

---

## Core Concepts

### Signal

Vector-native representation of discourse elements:

- `raw_content`: Text/message content
- `context_window_id`: Link to parent conversation
- `signal_source`: Source identifier (Axis, M, Neo, person, Slack, etc.)
- `signal_score`: Coherence strength (0-1)
- `signal_vector`: Reference to Pinecone embedding

### Conversation

Temporal grouping of signals for coherence analysis:

- Tracks session start/end times
- Maintains current coherence score and trend
- Groups signals for drift analysis

### Drift Score

Moving variance of signal_scores within a time window:

- High drift (0.7-1.0) = low coherence (inconsistent signals)
- Low drift (0.0-0.3) = high coherence (consistent signals)
- Computed over sliding windows (default: 5-minute windows)

### Coherence Score

Derived from drift and signal diversity:

- Formula: `coherence = 1 - avg(drift_scores)` (baseline)
- Adjusted for: source diversity, signal stability, temporal trend
- Range: 0-1 (1.0 = perfect coherence, 0.0 = complete incoherence)

# Testing

## Test Suite

Comprehensive test suite with **14 simple, focused test files** - one per endpoint. Each test is independent and can be run individually with clear, simple arguments.

### Test Files (14 total)

**Conversation Endpoints (3 tests):**

- `test_create_conversation.py` - POST /api/conversations/ (standalone)
- `test_get_conversation.py` - GET /api/conversations/{id} (--conversation-id)
- `test_patch_conversation.py` - PATCH /api/conversations/{id} (--conversation-id)

**Signal Endpoints (5 tests):**

- `test_create_signal.py` - POST /api/signals/ (--conversation-id)
- `test_get_signal.py` - GET /api/signals/{id} (--signal-id)
- `test_batch_signals.py` - POST /api/signals/batch (--conversation-id)
- `test_list_signals.py` - GET /api/signals/ (standalone)
- `test_get_signals_by_conversation.py` - GET /api/signals/conversation/{id} (--conversation-id)

**Coherence Endpoint (1 test):**

- `test_get_coherence.py` - GET /api/conversations/{id}/coherence ⭐ CORE (--conversation-id)

**User Endpoints (5 tests):**

- `test_create_user.py` - POST /api/users/ (standalone)
- `test_get_user.py` - GET /api/users/{id} (--user-id)
- `test_patch_user.py` - PATCH /api/users/{id} (--user-id)
- `test_delete_user.py` - DELETE /api/users/{id} (--user-id)
- `test_user_conversations.py` - GET /api/users/{id}/conversations (--user-id)

### Quick Test Commands

```bash
cd tests

# Simple: Run any test standalone
python test_create_conversation.py

# With arguments: Tests that need data
python test_get_conversation.py --conversation-id <id>
python test_create_signal.py --conversation-id <id>
python test_get_coherence.py --conversation-id <id>

# Complete workflow
conversation_id=$(python test_create_conversation.py)
signal_id=$(python test_create_signal.py --conversation-id $conversation_id)
python test_get_signal.py --signal-id $signal_id
python test_batch_signals.py --conversation-id $conversation_id
python test_get_coherence.py --conversation-id $conversation_id

# User tests
user_id=$(python test_create_user.py)
python test_get_user.py --user-id $user_id
python test_user_conversations.py --user-id $user_id
python test_delete_user.py --user-id $user_id
```

### Documentation

- `tests/TEST_GUIDE.md` - Complete testing guide with all 14 endpoints and examples
- `tests/BATCH_INGESTION_GUIDE.md` - Detailed batch signals API reference

### Key Features

✅ **Simple Execution:** `python test_xxx.py` (no complex runners or modes)
✅ **Clear Arguments:** `--conversation-id`, `--user-id`, `--signal-id` (explicit dependencies)
✅ **Return IDs:** Tests that create data return IDs for use in other tests
✅ **Exit Codes:** 0 = success, 1 = failure (scriptable)
✅ **All Working:** 14/14 tests verified with real API

---

# Security & Encryption

## User Data Encryption (pgcrypto)

Personal user information is **automatically encrypted** at the database level using PostgreSQL's pgcrypto extension with BEFORE INSERT/UPDATE triggers:

- **Email**: Encrypted with `pgp_sym_encrypt()` and stored as `bytea` in database
- **Phone**: Encrypted with `pgp_sym_encrypt()` and stored as `bytea` in database
- **Address**: Encrypted with `pgp_sym_encrypt()` and stored as `bytea` in database

### Automatic Encryption Trigger

The system implements a PostgreSQL trigger that automatically encrypts personal information when data is inserted or updated:

```sql
-- Trigger fires BEFORE INSERT OR UPDATE on users table
CREATE TRIGGER users_encrypt_trigger
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION encrypt_user_fields();
```

**How it works:**

1. Application sends plaintext data to API (email, phone, address)
2. Data is stored as encoded bytes in database
3. **BEFORE INSERT trigger fires** and encrypts the bytes using `pgp_sym_encrypt()`
4. Encrypted bytea is stored in database
5. API response returns only safe fields (no encrypted data exposed)

### Security Features

✅ **Automatic Encryption at Database Level**

- Encryption happens transparently at database level
- Personal information never stored as plaintext
- Works automatically on INSERT and UPDATE operations
- Field-level encryption (each field encrypted separately)

✅ **Key Management via Environment Variables**

- Encryption key stored in `PGCRYPTO_KEY` environment variable
- Uses `python-decouple` for secure configuration management
- Key never hardcoded or exposed in application code
- Validated at application startup (fails if not set)

✅ **API Security**

- Encrypted fields NEVER exposed in API responses
- Only safe fields returned (id, username, created_at, is_active)
- Secure by design - data protection at source
- `UserReadSchema` excludes all encrypted fields

✅ **Data Integrity**

- Foreign key constraints between users and conversations
- Unique username constraint
- Proper validation on all inputs
- ORM works transparently with encrypted fields

### How It Works

1. **Configuration** (`.env.compose`):

   ```env
   PGCRYPTO_KEY=your-key
   ```

2. **On Create** (User sends plaintext):

   ```bash
   POST /api/users/
   {
     "username": "john_doe",
     "email": "john@example.com",
     "phone": "555-1234",
     "address": "123 Main St"
   }
   ```

3. **At Database** (Trigger encrypts automatically):
   - Application: Stores as bytes
   - Trigger: Converts bytes to text with `convert_from()`
   - Trigger: Encrypts with `pgp_sym_encrypt(plaintext, key)`
   - Database: Stores encrypted bytea

4. **On Retrieve** (API returns safe data):

   ```json
   {
     "id": "uuid",
     "username": "john_doe",
     "created_at": "2025-11-27T03:00:00Z",
     "is_active": true
   }
   ```

   Note: email, phone, address NOT included

5. **Decryption** (Admin access pattern):
   ```sql
   SELECT pgp_sym_decrypt(email_encrypted, 'encryption-key') AS email
   FROM users WHERE id = 'user-id';
   ```

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│ API Request (plaintext email, phone, address)           │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────┐
        │  .encode() → bytes      │
        └──────────┬──────────────┘
                   │
                   ▼
        ┌─────────────────────────────────────────┐
        │ PostgreSQL INSERT/UPDATE Statement      │
        └──────────────┬──────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────────────┐
        │ BEFORE INSERT/UPDATE Trigger Fires           │
        │ encrypt_user_fields() function               │
        ├──────────────────────────────────────────────┤
        │ 1. Read encryption key: app.pgcrypto_key     │
        │ 2. Convert bytes → UTF-8 text                │
        │ 3. pgp_sym_encrypt(plaintext, key)           │
        │ 4. Return encrypted bytea                    │
        └──────────────┬───────────────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────────────┐
        │ Store encrypted bytea in database       │
        │ email_encrypted: b'\xc3\r\x04\x07...'   │
        │ phone_encrypted: b'\xc3\r\x04\x07...'   │
        │ address_encrypted: b'\xc3\r\x04\x07...' │
        └─────────────────────────────────────────┘
```

### Implementation Files

- **`src/api/db/triggers.sql`** - PostgreSQL trigger function and definition
- **`src/api/db/config.py`** - PGCRYPTO_KEY configuration via decouple
- **`src/api/db/session.py`** - `init_pgcrypto_trigger()` initializes at startup
- **`src/api/users/routing.py`** - API routes with `.encode()` for bytes storage
- **`tests/test_user_encryption.py`** - Comprehensive encryption test suite

### Testing Encryption

Run the encryption test suite to verify the trigger is working:

```bash
cd tests
python test_user_encryption.py --mode full
```

Test modes:

```bash
python test_user_encryption.py --mode create       # Create user via API
python test_user_encryption.py --mode check        # Verify database encryption
python test_user_encryption.py --mode api-security # Verify API security
python test_user_encryption.py --mode full         # All tests (default)
```

### Example Test Output

```
✅ User created via API
   ID: 8a13a064-eb53-4bda-b423-1e517a1d4bc7
   Username: encryption_test_user_1764214243085

✅ Email encrypted: bytes (b'\xc3\r\x04\x07\x03\x02...')
✅ Phone encrypted: bytes (b'\xc3\r\x04\x07\x03\x02...')
✅ Address encrypted: bytes (b'\xc3\r\x04\x07\x03\x02...')

✅ API Response: No encrypted fields exposed
   - Only returns: id, username, created_at, is_active
```

### Decryption Example

To decrypt personal information (admin-only pattern):

```sql
-- Decrypt a user's email
SELECT
  id,
  username,
  pgp_sym_decrypt(email_encrypted, 'your-encryption-key') AS email,
  pgp_sym_decrypt(phone_encrypted, 'your-encryption-key') AS phone,
  pgp_sym_decrypt(address_encrypted, 'your-encryption-key') AS address
FROM users
WHERE username = 'john_doe';
```

Result:

```
id                   | username  | email            | phone    | address
─────────────────────┼───────────┼──────────────────┼──────────┼─────────────
8a13a064-eb53-4bd... | john_doe  | john@example.com | 555-1234 | 123 Main St
```

---

# Dependencies

See requirements.txt:

- **fastapi:** Web framework
- **uvicorn:** ASGI server
- **sqlmodel:** SQLAlchemy ORM with Pydantic validation
- **timescaledb:** TimescaleDB Python client
- **psycopg:** PostgreSQL adapter (v3)
- **python-decouple:** Environment configuration
- **requests:** HTTP client (for tests)
