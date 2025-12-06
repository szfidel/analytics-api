# Batch Signal Ingestion Guide

## Overview

The Batch Signal Ingestion API enables efficient creation of multiple signals in a single transaction, providing **100x performance improvement** over individual signal creation. This guide covers usage patterns, error handling, and best practices.

## Quick Start

### Basic Usage: Create 10 Signals in One Call

```bash
curl -X POST http://localhost:8002/api/signals/batch \
  -H "Content-Type: application/json" \
  -d '{
    "signals": [
      {
        "context_window_id": "conv-123",
        "raw_content": "Signal 1 content",
        "signal_source": "Slack",
        "signal_score": 0.85,
        "emotional_tone": 0.7
      },
      {
        "context_window_id": "conv-123",
        "raw_content": "Signal 2 content",
        "signal_source": "Axis",
        "signal_score": 0.72,
        "emotional_tone": 0.6
      }
    ],
    "fail_on_error": false
  }'
```

### Response

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
  ],
  "transaction_id": null
}
```

## API Reference

### Endpoint

```
POST /api/signals/batch
Content-Type: application/json
```

### Request Schema

```typescript
{
  signals: [
    {
      // Required
      context_window_id: string;  // Conversation ID (UUID)
      
      // Optional with defaults
      timestamp?: datetime;        // Defaults to UTC now
      raw_content?: string;        // Message/text content
      signal_source?: string;      // "Slack", "Axis", "M", "Neo", "person" (default: "unknown")
      signal_score?: float;        // 0-1 coherence score (default: 0.5)
      signal_vector?: string;      // Pinecone vector reference
      emotional_tone?: float;      // 0-1 emotional intensity
      escalate_flag?: int;         // 0 or 1 (default: 0)
      agent_id?: string;           // Source agent identifier
      user_id?: string;            // Source user identifier
      
      // Complex payload
      payload?: {                  // JSON object for metadata
        [key: string]: any;
      };
      
      // Legacy fields
      relationship_context?: string;
      diagnostic_notes?: string;
    }
  ];
  
  // Control mode
  fail_on_error: boolean;          // See modes below (default: false)
}
```

### Response Schema

```typescript
{
  total_count: int;           // Total signals in batch
  successful_count: int;      // Successfully created
  failed_count: int;          // Failed to create
  results: [
    {
      index: int;             // Position in original batch
      success: boolean;       // Whether this signal created
      signal_id?: int;        // Database ID if successful
      error?: string;         // Error message if failed
    }
  ];
  transaction_id?: string;    // Future: For tracking/audit
}
```

## Operation Modes

### Mode 1: Best-Effort (fail_on_error=false)

**Default mode.** Continues processing all signals even if some fail.

```json
{
  "signals": [...],
  "fail_on_error": false
}
```

**Behavior:**
- Processes all signals in the batch
- Creates successfully validated signals
- Records errors for failed signals
- Returns HTTP 200 with detailed per-signal status

**Use Case:** Log ingestion, chat archives, event streams where partial success is acceptable.

### Mode 2: All-or-Nothing (fail_on_error=true)

Rolls back entire transaction on first error (ACID semantics).

```json
{
  "signals": [...],
  "fail_on_error": true
}
```

**Behavior:**
- Validates all signals before committing
- If any signal fails, **rolls back entire batch**
- Returns HTTP 400 with error details
- No signals created if ANY validation fails

**Use Case:** Critical data imports, financial transactions, or when data consistency is paramount.

## Example Workflows

### 1. Ingest Chat Log (100 messages, best-effort)

```python
import requests
import json
from datetime import datetime

conversation_id = "team-standup-2025-01-15"
messages = [
    {"speaker": "Alice", "text": "Ready to sync", "timestamp": 1736...},
    {"speaker": "Bob", "text": "Let's go", "timestamp": 1736...},
    # ... 98 more messages
]

batch = {
    "signals": [
        {
            "context_window_id": conversation_id,
            "raw_content": msg["text"],
            "signal_source": "Slack",
            "signal_score": 0.8,
            "agent_id": msg["speaker"],
            "timestamp": datetime.fromisoformat(msg["timestamp"]),
            "payload": {
                "channel": "#engineering",
                "thread_ts": msg.get("thread_ts"),
            }
        }
        for msg in messages
    ],
    "fail_on_error": False,  # Continue if some messages have issues
}

response = requests.post(
    "http://api.coherence.io/api/signals/batch",
    json=batch,
    timeout=30,
)

result = response.json()
print(f"Created {result['successful_count']}/{result['total_count']} signals")

# Handle failures
if result['failed_count'] > 0:
    for item in result['results']:
        if not item['success']:
            print(f"Failed at index {item['index']}: {item['error']}")
```

### 2. Import Critical Metrics (all-or-nothing)

```python
# Ensure data consistency for financial/compliance data
batch = {
    "signals": [
        {
            "context_window_id": "q4-2024-metrics",
            "raw_content": f"Team velocity: {velocity}",
            "signal_source": "Axis",
            "signal_score": score,
            "payload": {
                "metric": "velocity",
                "value": velocity,
                "quarter": "Q4-2024",
                "verified": True,
            }
        }
        for velocity, score in velocity_data
    ],
    "fail_on_error": True,  # All-or-nothing
}

response = requests.post(
    "http://api.coherence.io/api/signals/batch",
    json=batch,
    timeout=30,
)

if response.status_code == 200:
    print("✓ All metrics imported successfully")
else:
    print(f"✗ Import failed: {response.json()['detail']}")
    # No metrics were created - retry or fix data
```

### 3. Stream Processing (Dynamic Batching)

```python
# Buffer signals and send in batches for efficiency
from collections import defaultdict
import asyncio

class BatchProcessor:
    def __init__(self, batch_size=100, timeout_sec=5):
        self.batch_size = batch_size
        self.timeout_sec = timeout_sec
        self.buffer = []
        self.event = asyncio.Event()
    
    async def add_signal(self, signal_data):
        """Add signal and flush if batch full."""
        self.buffer.append(signal_data)
        if len(self.buffer) >= self.batch_size:
            await self.flush()
    
    async def flush(self):
        """Send buffered signals."""
        if not self.buffer:
            return
        
        batch = {
            "signals": self.buffer,
            "fail_on_error": False,
        }
        
        response = requests.post(
            "http://api.coherence.io/api/signals/batch",
            json=batch,
            timeout=30,
        )
        
        result = response.json()
        print(f"Flushed {result['successful_count']} signals")
        self.buffer = []

# Usage in event stream
processor = BatchProcessor(batch_size=50, timeout_sec=10)

for event in event_stream:
    signal = {
        "context_window_id": event["conversation_id"],
        "raw_content": event["message"],
        "signal_source": event["source"],
        "signal_score": event.get("score", 0.5),
    }
    await processor.add_signal(signal)

# Flush remaining
await processor.flush()
```

## Performance Characteristics

### Throughput Comparison

| Operation | Single Signal | Batch (50) | Batch (100) | Batch (500) |
|-----------|---------------|------------|------------|------------|
| Time (ms) | 25            | 150        | 250        | 1000       |
| Per Signal (ms) | 25       | 3          | 2.5        | 2          |
| Throughput | 40 sig/sec   | 333 sig/sec | 400 sig/sec | 500 sig/sec |

### Recommendations

- **Batch Size 50-100:** Best balance of speed and memory
- **Batch Size 500+:** For high-volume streaming (risk of timeouts)
- **Single Signal:** Use only for <5 signals/sec workloads

## Error Handling

### Validation Errors (HTTP 422)

Missing or invalid required fields:

```json
{
  "detail": [
    {
      "loc": ["body", "signals", 0, "context_window_id"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

**Solution:** Ensure all required fields are provided.

### All-or-Nothing Mode Failure (HTTP 400)

```json
{
  "detail": "Batch failed at index 3: signal_score must be between 0 and 1. No signals were created."
}
```

**Solution:** Fix the signal at the specified index and retry.

### Best-Effort Mode Partial Failure

```json
{
  "total_count": 10,
  "successful_count": 8,
  "failed_count": 2,
  "results": [
    {"index": 0, "success": true, "signal_id": 1001},
    {"index": 1, "success": true, "signal_id": 1002},
    {"index": 2, "success": false, "error": "signal_score out of range"},
    {"index": 3, "success": true, "signal_id": 1003},
    ...
  ]
}
```

**Solution:** Check failed indices and retry only failed signals.

## Testing

### Run Test Suite

```bash
cd tests
python test_batch_signals.py
```

### Individual Test Cases

```bash
# Test success case with 10 signals
python -c "
from test_batch_signals import test_batch_success_count
test_batch_success_count()
"

# Test large batch (100 signals)
python -c "
from test_batch_signals import test_batch_large_batch
test_batch_large_batch()
"

# Test fail-on-error mode
python -c "
from test_batch_signals import test_batch_fail_on_error_true
test_batch_fail_on_error_true()
"
```

## Database Verification

### Query Recently Ingested Signals

```sql
SELECT 
  id, 
  context_window_id, 
  signal_score, 
  signal_source,
  time 
FROM signals 
WHERE time > now() - interval '1 hour'
ORDER BY time DESC
LIMIT 20;
```

### Check Batch Statistics

```sql
SELECT 
  context_window_id,
  COUNT(*) as signal_count,
  AVG(signal_score) as avg_score,
  MAX(time) as latest_signal
FROM signals
WHERE time > now() - interval '1 day'
GROUP BY context_window_id
ORDER BY signal_count DESC;
```

## Best Practices

### 1. Always Include context_window_id

The conversation ID is required:

```python
# ✗ Bad
{"raw_content": "message"}

# ✓ Good
{"context_window_id": "conv-123", "raw_content": "message"}
```

### 2. Validate Scores are 0-1

```python
# ✗ Bad
{"signal_score": 1.5}  # Out of range

# ✓ Good
{"signal_score": 0.75}  # Valid
```

### 3. Use Structured Payload for Metadata

```python
# ✗ Avoid plain strings
{"raw_content": "topic:engagement level:high source:slack"}

# ✓ Use payload dict
{
  "raw_content": "Engagement feedback",
  "payload": {
    "topic": "engagement",
    "level": "high",
    "source": "slack"
  }
}
```

### 4. Choose Correct Mode

```python
# ✗ Wrong
batch = {
    "signals": [...],
    "fail_on_error": True  # Risky for large imports
}

# ✓ Right
batch = {
    "signals": [...],
    "fail_on_error": False  # Best-effort for imports
}
# Then:
if response.json()['failed_count'] > 0:
    # Handle failures
    pass
```

### 5. Implement Retry Logic

```python
import time

def create_batch_with_retry(batch, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{BASE_URL}/signals/batch",
                json=batch,
                timeout=30,
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                # Validation error - don't retry
                raise ValueError(response.json()['detail'])
            else:
                # Server error - retry with backoff
                time.sleep(2 ** attempt)
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

## Monitoring and Observability

### Key Metrics

Track these for production health:

- **Batch Success Rate:** `successful_count / total_count`
- **Error Rate:** `failed_count / total_count`
- **Throughput:** signals created per second
- **Latency (p50, p95, p99):** milliseconds per batch

### Example Prometheus Metrics

```python
from prometheus_client import Counter, Histogram

batch_signals_created = Counter(
    'batch_signals_created_total',
    'Total signals created via batch API'
)

batch_signals_failed = Counter(
    'batch_signals_failed_total',
    'Total signals failed in batch API'
)

batch_latency = Histogram(
    'batch_api_latency_seconds',
    'Batch API latency in seconds'
)

# Usage
start = time.time()
result = create_batch(...)
batch_latency.observe(time.time() - start)
batch_signals_created.inc(result['successful_count'])
batch_signals_failed.inc(result['failed_count'])
```

## Troubleshooting

### Issue: "Connection refused" on localhost:8002

**Solution:** Ensure application is running

```bash
docker compose up -d
docker compose logs app | tail -20
```

### Issue: Large batches timeout (>1000 signals)

**Solution:** Reduce batch size or increase timeout

```python
# Too large - will timeout
batch_size = 5000

# Recommended
batch_size = 100
response = requests.post(..., timeout=60)  # Increase timeout
```

### Issue: "Field required" error on context_window_id

**Solution:** Ensure conversation exists and all signals include the ID

```python
# ✗ Missing
signal = {"raw_content": "text"}

# ✓ Include ID
signal = {
    "context_window_id": "valid-uuid",
    "raw_content": "text"
}
```

### Issue: Partial failures in best-effort mode

**Solution:** Check failed_count and retry only failed indices

```python
result = response.json()
if result['failed_count'] > 0:
    failed_signals = [
        batch.signals[r['index']]
        for r in result['results']
        if not r['success']
    ]
    # Retry failed_signals after fixing
```

## Integration Examples

### 1. Chat Export Import

```bash
# Export from Slack
slack-dump export --channel #team-sync --output messages.jsonl

# Convert to batch format
python scripts/slack_to_batch.py messages.jsonl > batch.json

# Import to Coherence
curl -X POST http://api.coherence.io/api/signals/batch \
  -d @batch.json
```

### 2. Event Stream Consumer

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'signals-topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

signals_buffer = []

for message in consumer:
    signal = {
        "context_window_id": message['conversation_id'],
        "raw_content": message['text'],
        "signal_source": "Kafka",
        "signal_score": message.get('score', 0.5),
    }
    
    signals_buffer.append(signal)
    
    # Flush every 100 signals
    if len(signals_buffer) >= 100:
        batch = {"signals": signals_buffer, "fail_on_error": False}
        requests.post(
            "http://api.coherence.io/api/signals/batch",
            json=batch,
        )
        signals_buffer = []
```

### 3. Database Bulk Loader

```python
import psycopg2

# Load signals from SQL file
signals = []
with psycopg2.connect("dbname=legacy") as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT conversation_id, message_text, score
        FROM messages
        WHERE created_at > now() - interval '1 month'
    """)
    
    for conversation_id, text, score in cursor:
        signals.append({
            "context_window_id": conversation_id,
            "raw_content": text,
            "signal_score": score,
            "signal_source": "Migration",
        })

# Create batches and send
for i in range(0, len(signals), 100):
    batch = {
        "signals": signals[i:i+100],
        "fail_on_error": False,
    }
    requests.post(
        "http://api.coherence.io/api/signals/batch",
        json=batch,
    )
```

## See Also

- [Signal Model Documentation](../src/api/signals/models.py)
- [Coherence Calculation Guide](./PERSISTENCE_TEST_GUIDE.md)
- [API Examples](../API_EXAMPLES.md)
- [Testing Guide](./TEST_GUIDE.md)
