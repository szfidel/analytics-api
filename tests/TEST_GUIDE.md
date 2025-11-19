# V1.1 Coherence Signal Architecture - Test Guide

This directory contains comprehensive tests for all API endpoints in the V1.1 release.

## Test Files

### Conversation Endpoints

1. **test_create_conversation.py**
   - Tests: `POST /api/conversations/`
   - Creates new conversation/session
   - Usage: `python test_create_conversation.py --count 3`

2. **test_get_conversation.py**
   - Tests: `GET /api/conversations/{id}`
   - Retrieves conversation by ID
   - Usage: `python test_get_conversation.py <conversation_id>`

3. **test_patch_conversation.py**
   - Tests: `PATCH /api/conversations/{id}`
   - Updates conversation (end_at, coherence scores)
   - Usage: `python test_patch_conversation.py <conversation_id> --action end`
   - Options: `--action [end|coherence|all]`

4. **test_get_coherence.py** ⭐ **CORE ENDPOINT**
   - Tests: `GET /api/conversations/{id}/coherence`
   - Computes coherence metrics with drift analysis
   - Usage: `python test_get_coherence.py <conversation_id> --window-size 5m`
   - Options: `--test-windows` (test multiple window sizes)

### Signal Endpoints

5. **test_create_signal.py**
   - Tests: `POST /api/signals/`
   - Creates signals in a conversation
   - Usage: `python test_create_signal.py <conversation_id> --count 5`
   - Options: `--varying-scores` (create signals with different score ranges)

6. **test_get_signal.py**
   - Tests: `GET /api/signals/{id}`
   - Retrieves single signal by ID
   - Usage: `python test_get_signal.py <signal_id>`

7. **test_list_signals.py**
   - Tests: `GET /api/signals/`
   - Lists signals with time-bucketing and aggregation
   - Usage: `python test_list_signals.py --duration "1 day"`
   - Options: `--test-durations` (test multiple bucket sizes)
   - Options: `--sources Axis M Neo` (filter by sources)

8. **test_get_signals_by_conversation.py**
   - Tests: `GET /api/signals/conversation/{context_window_id}`
   - Gets all signals in a conversation
   - Usage: `python test_get_signals_by_conversation.py <conversation_id> --limit 50`

### Master Test Runner

9. **run_all_tests.py**
   - Runs complete test workflows
   - Usage: `python run_all_tests.py --mode workflow`
   - Modes:
     - `workflow`: Full end-to-end test (create conversation → signals → coherence)
     - `endpoints`: Test all GET endpoints
     - `stress`: Create many signals (requires `--conversation-id`)

## Quick Start

### 1. Full Workflow Test (Recommended)
```bash
# Creates conversation, signals, and analyzes coherence
python run_all_tests.py --mode workflow
```

### 2. Manual Testing

Step by step testing:

```bash
# Step 1: Create a conversation
CONV_ID=$(python test_create_conversation.py | grep "ID:" | awk '{print $3}')
echo "Created conversation: $CONV_ID"

# Step 2: Create signals in the conversation
python test_create_signal.py $CONV_ID --count 5

# Step 3: Get signals for the conversation
python test_get_signals_by_conversation.py $CONV_ID

# Step 4: Get coherence metrics (CORE)
python test_get_coherence.py $CONV_ID

# Step 5: Update conversation (end it)
python test_patch_conversation.py $CONV_ID --action end

# Step 6: Verify update
python test_get_conversation.py $CONV_ID
```

## Test Scenarios

### Scenario 1: Basic Signal Workflow
```bash
# Test basic signal ingestion and coherence analysis
python test_create_conversation.py
python test_create_signal.py <conv_id> --count 3
python test_get_coherence.py <conv_id>
```

### Scenario 2: Varying Signal Scores
```bash
# Test coherence with signals of different quality
python test_create_conversation.py
python test_create_signal.py <conv_id> --varying-scores
python test_get_coherence.py <conv_id> --detailed
```

### Scenario 3: Multiple Window Sizes
```bash
# Analyze coherence with different time windows
python test_create_conversation.py
python test_create_signal.py <conv_id> --count 10
python test_get_coherence.py <conv_id> --test-windows
```

### Scenario 4: Stress Test
```bash
# Test with large number of signals
python test_create_conversation.py
python run_all_tests.py --mode stress --conversation-id <conv_id> --signal-count 100
```

### Scenario 5: Signal Source Analysis
```bash
# Analyze signals by source
python test_create_signal.py <conv_id> --count 20
python test_list_signals.py --conversation-id <conv_id> --test-sources
```

## Understanding Test Output

### Coherence Interpretation

The `test_get_coherence.py` output shows:

```
Coherence Score: 0.943 (94.3% coherent)
├─ Excellent alignment (0.8-1.0)
├─ Good alignment (0.6-0.8)
├─ Fair alignment (0.4-0.6)
└─ Poor alignment (0.0-0.4)
```

### Drift Score Interpretation

Drift = Moving Variance of Signal Scores

```
Drift: 0.057 (5.7%)
├─ Very low drift (0.0-0.1) → Highly coherent
├─ Low drift (0.1-0.3) → Coherent
├─ Moderate drift (0.3-0.6) → Some variation
└─ High drift (0.6-1.0) → Incoherent
```

Coherence Formula:
```
Coherence = 1 - Average(Drift Scores)
Example: 1 - 0.057 = 0.943
```

## Troubleshooting

### "Connection refused" error
- Ensure Docker containers are running: `docker compose ps`
- Start containers: `docker compose up -d`

### "Conversation not found (404)"
- Use valid conversation IDs from recent test runs
- Create a new conversation first: `python test_create_conversation.py`

### "Signal not found (404)"
- Create signals first: `python test_create_signal.py <conversation_id>`
- Get the signal ID from the creation response

### Empty coherence metrics
- Need signals with timestamps in the window
- Create signals first before querying coherence
- Check window size matches signal timestamps

## Performance Notes

- Creating 50+ signals: ~5-10 seconds
- Computing coherence with 100 signals: ~1-2 seconds
- List signals aggregation: Depends on time range

## Testing Best Practices

1. **Always create conversation first** - Signals need a conversation_id
2. **Use timestamps close to now** - Drift calculation uses actual times
3. **Create multiple signals** - Coherence needs variance to compute
4. **Test with different window sizes** - Windows affect drift aggregation
5. **Check database directly** - Verify data persists:
   ```bash
   docker compose exec db_service psql -U postgres -d analytics -c \
     "SELECT COUNT(*) FROM signals;"
   ```

## Next Steps

After running tests:

1. Review coherence scores
2. Adjust signal_score values to see coherence changes
3. Test with real signal sources (Axis, M, Neo, etc.)
4. Implement Pinecone vector search
5. Add real-time alerting based on coherence drops

## Documentation

For more details, see:
- `README.md` - Full API documentation
- `API_EXAMPLES.md` - Practical examples and usage patterns
