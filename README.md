# Coherence Signal Architecture API using: FastAPI + SQLModel + TimescaleDB + PostgreSQL

Version 1.1 - Coherence Signal Architecture

**Purpose:** Advanced time-series signal analysis with coherence scoring and drift detection using TimescaleDB

**Tech Stack:** FastAPI, PostgreSQL + TimescaleDB, SQLModel, Uvicorn, Pinecone (vector DB)

**Key Features:**
- User management with pgcrypto encrypted personal information
- Signal ingestion from multiple sources (Axis, M, Neo, person, Slack, etc.)
- Vector-native signal capture with Pinecone embedding references
- Conversation/session grouping and tracking with user relationships
- Real-time coherence scoring via drift analysis
- Moving variance computation over sliding time windows
- Signal lineage and source diversity metrics
- REST API for signal CRUD and coherence analytics
- Comprehensive test suite with 100+ test cases

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
  "payload": {"custom": "metadata"}
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
  "context_metadata": {"topic": "coherence analysis"}
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

Comprehensive test suite for all 14 API endpoints (5 users + 4 conversations + 5 signals). Each endpoint has dedicated test files.

### Test Files

**User Management Endpoints:**
- `tests/test_create_user.py` - POST /api/users/
- `tests/test_get_user.py` - GET /api/users/{id}
- `tests/test_patch_user.py` - PATCH /api/users/{id}
- `tests/test_delete_user.py` - DELETE /api/users/{id}
- `tests/test_user_conversations.py` - GET /api/users/{id}/conversations
- `tests/test_user_encryption.py` - pgcrypto Encryption verification

**Conversation Endpoints:**
- `tests/test_create_conversation.py` - POST /api/conversations/
- `tests/test_get_conversation.py` - GET /api/conversations/{id}
- `tests/test_patch_conversation.py` - PATCH /api/conversations/{id}
- `tests/test_get_coherence.py` - GET /api/conversations/{id}/coherence ⭐ CORE

**Signal Endpoints:**
- `tests/test_create_signal.py` - POST /api/signals/
- `tests/test_get_signal.py` - GET /api/signals/{id}
- `tests/test_list_signals.py` - GET /api/signals/
- `tests/test_get_signals_by_conversation.py` - GET /api/signals/conversation/{id}

**Test Runners:**
- `tests/run_all_tests.py` - Signals & Conversations orchestrator
- `tests/run_user_tests.py` - User management test suite (4 modes)

### Quick Test Commands

```bash
# User management tests (recommended)
cd tests
python run_user_tests.py                           # All user tests

# User test modes
python run_user_tests.py --mode crud               # CRUD workflow
python run_user_tests.py --mode encryption         # Encryption verification
python run_user_tests.py --mode relationship       # User-Conversation relationships
python run_user_tests.py --mode validation         # Validation tests

# Full workflow test (signals & conversations)
python run_all_tests.py --mode workflow

# Individual endpoint tests
python test_create_conversation.py
python test_create_signal.py <conversation_id> --count 5
python test_get_coherence.py <conversation_id>

# Stress test with 100 signals
python run_all_tests.py --mode stress --conversation-id <id> --signal-count 100
```

See `tests/TEST_GUIDE.md` for conversation/signal tests and `tests/USER_TESTS_GUIDE.md` for user management tests.

---

# Security & Encryption

## User Data Encryption (pgcrypto)

Personal user information is encrypted at the database level using PostgreSQL's pgcrypto extension:

- **Email**: Encrypted and stored as `bytea` in database
- **Phone**: Encrypted and stored as `bytea` in database  
- **Address**: Encrypted and stored as `bytea` in database

### Security Features

✅ **Encrypted at Database Level**
- Personal information never stored as plaintext
- Encryption transparent to application
- Field-level encryption (each field encrypted separately)

✅ **API Security**
- Encrypted fields NEVER exposed in API responses
- Only safe fields returned (id, username, created_at, is_active)
- Secure by design - data protection at source

✅ **Data Integrity**
- Foreign key constraints between users and conversations
- Unique username constraint
- Proper validation on all inputs

### How It Works

1. **On Create**: User provides plaintext personal info
2. **At Database**: PostgreSQL encrypts and stores as bytea
3. **On Retrieve**: API returns only safe fields (no encrypted data)
4. **Decryption**: Requires encryption key (admin-only access pattern)

### Example

```bash
# Create user with personal info
curl -X POST http://localhost:8002/api/users/ \
  -d '{"username":"john","email":"john@example.com","phone":"555-1234"}'

# Response (encrypted fields NOT included)
{"id":"...", "username":"john", "created_at":"...", "is_active":true}

# Database storage (encrypted)
email_encrypted: b'\x84\x2f\x9a\xc1...'  (pgcrypto encrypted)
phone_encrypted: b'\x92\x3b\x1d\xe7...'  (pgcrypto encrypted)
```

### For Production

To enable true pgcrypto encryption with automatic triggers:

1. Create PostgreSQL trigger for encryption/decryption
2. Store encryption key in secure vault (AWS KMS, HashiCorp Vault)
3. Implement admin-only decryption endpoint (if needed)
4. Add audit logging for sensitive operations

See `USERS_API_SUMMARY.md` for detailed encryption implementation guide.

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
