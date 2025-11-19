# V1.1 API Usage Examples

This document provides practical examples for using the Coherence Signal Architecture API.

> **💡 Tip:** For testing without writing curl commands, use the test suite in `tests/` directory. See `tests/TEST_GUIDE.md` for comprehensive testing documentation.

## 1. Create a Conversation

```bash
curl -X POST http://localhost:8002/api/conversations/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice-001",
    "agent_id": "gpt4-assistant",
    "started_at": "2024-11-18T10:00:00Z",
    "context_metadata": {"topic": "product strategy", "team": "engineering"}
  }'
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "alice-001",
  "agent_id": "gpt4-assistant",
  "started_at": "2024-11-18T10:00:00Z",
  "ended_at": null,
  "coherence_score_current": null,
  "coherence_score_trend": null
}
```

## 2. Create Signals in the Conversation

```bash
# Signal 1: From Axis source
curl -X POST http://localhost:8002/api/signals/ \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-11-18T10:05:00Z",
    "user_id": "alice-001",
    "agent_id": "gpt4-assistant",
    "raw_content": "We should focus on improving API latency",
    "context_window_id": "550e8400-e29b-41d4-a716-446655440000",
    "signal_source": "Axis",
    "signal_score": 0.85,
    "signal_vector": "pinecone_vec_0001",
    "emotional_tone": 0.7
  }'

# Signal 2: From M source (different perspective)
curl -X POST http://localhost:8002/api/signals/ \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-11-18T10:06:00Z",
    "user_id": "alice-001",
    "agent_id": "gpt4-assistant",
    "raw_content": "API latency is critical, lets prioritize caching",
    "context_window_id": "550e8400-e29b-41d4-a716-446655440000",
    "signal_source": "M",
    "signal_score": 0.82,
    "signal_vector": "pinecone_vec_0002",
    "emotional_tone": 0.75
  }'

# Signal 3: Human perspective (slightly different)
curl -X POST http://localhost:8002/api/signals/ \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-11-18T10:07:00Z",
    "user_id": "bob-002",
    "raw_content": "Security headers are more important than latency",
    "context_window_id": "550e8400-e29b-41d4-a716-446655440000",
    "signal_source": "person",
    "signal_score": 0.65,
    "signal_vector": "pinecone_vec_0003",
    "emotional_tone": 0.6
  }'

# Signal 4: Back to alignment (coherence recovery)
curl -X POST http://localhost:8002/api/signals/ \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-11-18T10:08:00Z",
    "user_id": "alice-001",
    "agent_id": "gpt4-assistant",
    "raw_content": "We can do both - optimize latency AND add security headers",
    "context_window_id": "550e8400-e29b-41d4-a716-446655440000",
    "signal_source": "Axis",
    "signal_score": 0.88,
    "signal_vector": "pinecone_vec_0004",
    "emotional_tone": 0.8
  }'
```

## 3. Get Coherence Metrics

```bash
# Get coherence with 5-minute sliding windows
curl http://localhost:8002/api/conversations/550e8400-e29b-41d4-a716-446655440000/coherence?window_size=5m
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "coherence_score_current": 0.79,
  "coherence_score_trend": null,
  "drift_metrics": [
    {
      "id": 0,
      "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
      "window_start": "2024-11-18T10:00:00Z",
      "window_end": "2024-11-18T10:05:00Z",
      "drift_score": 0.12,
      "signal_count": 1,
      "coherence_trend": null
    },
    {
      "id": 0,
      "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
      "window_start": "2024-11-18T10:05:00Z",
      "window_end": "2024-11-18T10:10:00Z",
      "drift_score": 0.18,
      "signal_count": 3,
      "coherence_trend": null
    }
  ],
  "signal_sources": {
    "Axis": 2,
    "M": 1,
    "person": 1
  },
  "total_signal_count": 4,
  "time_range_start": "2024-11-18T10:05:00Z",
  "time_range_end": "2024-11-18T10:08:00Z"
}
```

## 4. Get Signals by Conversation

```bash
curl 'http://localhost:8002/api/signals/conversation/550e8400-e29b-41d4-a716-446655440000?limit=10'
```

## 5. End Conversation and Update Scores

```bash
curl -X PATCH http://localhost:8002/api/conversations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "ended_at": "2024-11-18T10:30:00Z",
    "coherence_score_current": 0.79,
    "coherence_score_trend": 0.02
  }'
```

## 6. List Aggregated Signals

```bash
# Get hourly aggregation of all signals
curl 'http://localhost:8002/api/signals/?duration=1%20hour'

# Get hourly aggregation filtered by source
curl 'http://localhost:8002/api/signals/?duration=1%20hour&signal_sources=Axis&signal_sources=M'

# Get daily aggregation for specific conversation
curl 'http://localhost:8002/api/signals/?duration=1%20day&context_window_id=550e8400-e29b-41d4-a716-446655440000'
```

## 7. Get Individual Signal

```bash
curl http://localhost:8002/api/signals/1
```

---

## Interpreting Coherence Scores

### Signal Score (0-1)
- **0.9-1.0:** Perfect alignment with conversation direction
- **0.7-0.8:** Good alignment, minor deviations
- **0.5-0.6:** Neutral or tangential signals
- **0.2-0.4:** Contrary to conversation direction
- **0.0-0.2:** Severely misaligned

### Drift Score (0-1, within window)
- **0.0-0.2:** Very low drift → **High coherence** (signals consistent)
- **0.2-0.4:** Low drift → **Good coherence** (mostly consistent)
- **0.4-0.6:** Moderate drift → **Fair coherence** (some variation)
- **0.6-0.8:** High drift → **Low coherence** (inconsistent signals)
- **0.8-1.0:** Very high drift → **Very low coherence** (highly inconsistent)

### Overall Coherence Score (0-1)
- **0.8-1.0:** Conversation is highly aligned, ready for decision
- **0.6-0.8:** Conversation is mostly coherent, minor disagreements
- **0.4-0.6:** Conversation has notable divergence, may need alignment
- **0.2-0.4:** Conversation is quite incoherent, needs facilitation
- **0.0-0.2:** Conversation is fragmented, high misalignment

---

## Window Size Examples

- `window_size=30s` → 30-second windows (fine-grained, real-time)
- `window_size=5m` → 5-minute windows (default, balanced)
- `window_size=15m` → 15-minute windows (session segments)
- `window_size=1h` → hourly windows (high-level overview)

Smaller windows show more volatility. Larger windows show overall trends.

---

## Testing Workflow

1. **Create conversation** → Get conversation_id
2. **Post 3-5 signals** with varying signal_scores (0.3, 0.8, 0.7, 0.9, 0.4)
3. **Query coherence endpoint** → See drift metrics and overall score
4. **Verify calculation**: 
   - Average signal_score ≈ coherence (if no drift metrics computed)
   - Variance of scores = drift_score in window
5. **Try different window_sizes** → See how windows change aggregation
