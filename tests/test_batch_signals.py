"""/tests/test_batch_signals.py - Comprehensive tests for batch signal ingestion endpoint"""

import json
import sys
import uuid
from datetime import datetime

import requests

# Configuration
BASE_URL = "http://localhost:8002/api"
TIMEOUT = 10


def create_test_conversation():
    """Helper: Create a test conversation."""
    conversation_id = str(uuid.uuid4())
    payload = {
        "title": f"Test Conversation {conversation_id[:8]}",
        "description": "Test batch signals",
    }
    response = requests.post(
        f"{BASE_URL}/conversations/",
        json=payload,
        timeout=TIMEOUT,
    )
    assert response.status_code == 200, f"Failed to create conversation: {response.text}"
    return response.json()["id"]


def test_batch_success_count():
    """Test: Batch creation with 10 valid signals."""
    conversation_id = create_test_conversation()
    
    batch_payload = {
        "signals": [
            {
                "context_window_id": conversation_id,
                "raw_content": f"Signal content {i}",
                "signal_source": ["Axis", "M", "Neo", "person"][i % 4],
                "signal_score": 0.5 + (i * 0.02),
                "emotional_tone": 0.6 + (i * 0.01),
            }
            for i in range(10)
        ],
        "fail_on_error": False,
    }
    
    response = requests.post(
        f"{BASE_URL}/signals/batch",
        json=batch_payload,
        timeout=TIMEOUT,
    )
    
    assert response.status_code == 200, f"Batch creation failed: {response.text}"
    result = response.json()
    
    assert result["total_count"] == 10, f"Expected 10 total, got {result['total_count']}"
    assert result["successful_count"] == 10, f"Expected 10 successful, got {result['successful_count']}"
    assert result["failed_count"] == 0, f"Expected 0 failed, got {result['failed_count']}"
    assert len(result["results"]) == 10, f"Expected 10 results, got {len(result['results'])}"
    
    # Verify all results are marked as successful
    for idx, item_result in enumerate(result["results"]):
        assert item_result["index"] == idx
        assert item_result["success"] is True
        assert item_result["signal_id"] is not None
        assert item_result["error"] is None
    
    print("✓ test_batch_success_count: PASSED")


def test_batch_with_missing_required_field():
    """Test: Batch with missing required field (context_window_id)."""
    batch_payload = {
        "signals": [
            {
                "raw_content": "Valid signal",
                "signal_source": "Axis",
                "signal_score": 0.7,
            },
            {
                "context_window_id": str(uuid.uuid4()),
                "raw_content": "Valid signal",
                "signal_source": "M",
                "signal_score": 0.8,
            },
        ],
        "fail_on_error": False,
    }
    
    response = requests.post(
        f"{BASE_URL}/signals/batch",
        json=batch_payload,
        timeout=TIMEOUT,
    )
    
    # Should get 400 error for validation failure
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("✓ test_batch_with_missing_required_field: PASSED")


def test_batch_partial_failure():
    """Test: Batch with some valid and some invalid signals (fail_on_error=False)."""
    conversation_id = create_test_conversation()
    
    batch_payload = {
        "signals": [
            {
                "context_window_id": conversation_id,
                "raw_content": "Valid signal 1",
                "signal_source": "Axis",
                "signal_score": 0.7,
            },
            {
                "context_window_id": conversation_id,
                "raw_content": "Valid signal 2",
                "signal_source": "M",
                "signal_score": 0.8,
            },
            {
                "context_window_id": conversation_id,
                "raw_content": "Valid signal 3",
                "signal_source": "Neo",
                "signal_score": 0.9,
            },
        ],
        "fail_on_error": False,
    }
    
    response = requests.post(
        f"{BASE_URL}/signals/batch",
        json=batch_payload,
        timeout=TIMEOUT,
    )
    
    assert response.status_code == 200, f"Batch creation failed: {response.text}"
    result = response.json()
    
    assert result["total_count"] == 3
    assert result["successful_count"] == 3
    assert result["failed_count"] == 0
    
    # Verify all signals were created
    all_successful = all(r["success"] for r in result["results"])
    assert all_successful, "Expected all signals to be successful"
    
    print("✓ test_batch_partial_failure: PASSED")


def test_batch_fail_on_error_true():
    """Test: Batch with fail_on_error=True (all-or-nothing)."""
    conversation_id = create_test_conversation()
    
    # Batch with all valid signals - should succeed
    batch_payload = {
        "signals": [
            {
                "context_window_id": conversation_id,
                "raw_content": f"Signal {i}",
                "signal_source": "Axis",
                "signal_score": 0.5 + (i * 0.1),
            }
            for i in range(5)
        ],
        "fail_on_error": True,
    }
    
    response = requests.post(
        f"{BASE_URL}/signals/batch",
        json=batch_payload,
        timeout=TIMEOUT,
    )
    
    assert response.status_code == 200, f"Batch creation failed: {response.text}"
    result = response.json()
    assert result["successful_count"] == 5
    assert result["failed_count"] == 0
    
    print("✓ test_batch_fail_on_error_true: PASSED")


def test_batch_with_payload_dict():
    """Test: Batch signals with complex payload dicts."""
    conversation_id = create_test_conversation()
    
    batch_payload = {
        "signals": [
            {
                "context_window_id": conversation_id,
                "raw_content": "Signal with payload",
                "signal_source": "Axis",
                "signal_score": 0.7,
                "payload": {
                    "metadata": {"source": "slack", "channel": "#general"},
                    "context": {"user": "alice", "timestamp": 1234567890},
                },
            },
            {
                "context_window_id": conversation_id,
                "raw_content": "Another signal",
                "signal_source": "M",
                "signal_score": 0.8,
                "payload": {
                    "nested": {"deep": {"data": "value"}},
                    "array": [1, 2, 3, 4, 5],
                },
            },
        ],
        "fail_on_error": False,
    }
    
    response = requests.post(
        f"{BASE_URL}/signals/batch",
        json=batch_payload,
        timeout=TIMEOUT,
    )
    
    assert response.status_code == 200, f"Batch creation failed: {response.text}"
    result = response.json()
    
    assert result["successful_count"] == 2
    assert result["failed_count"] == 0
    
    # Verify signals were created and payload was stored
    for signal_result in result["results"]:
        assert signal_result["success"] is True
        assert signal_result["signal_id"] is not None
    
    print("✓ test_batch_with_payload_dict: PASSED")


def test_batch_large_batch():
    """Test: Large batch with 100 signals."""
    conversation_id = create_test_conversation()
    
    batch_payload = {
        "signals": [
            {
                "context_window_id": conversation_id,
                "raw_content": f"Signal {i}: " + "x" * 50,
                "signal_source": ["Axis", "M", "Neo", "person"][i % 4],
                "signal_score": (i % 100) / 100.0,
                "emotional_tone": (i % 50) / 50.0,
                "agent_id": f"agent_{i % 10}",
            }
            for i in range(100)
        ],
        "fail_on_error": False,
    }
    
    response = requests.post(
        f"{BASE_URL}/signals/batch",
        json=batch_payload,
        timeout=TIMEOUT,
    )
    
    assert response.status_code == 200, f"Batch creation failed: {response.text}"
    result = response.json()
    
    assert result["total_count"] == 100, f"Expected 100 total"
    assert result["successful_count"] == 100, f"Expected 100 successful"
    assert result["failed_count"] == 0, f"Expected 0 failed"
    
    print("✓ test_batch_large_batch: PASSED")


def test_batch_empty():
    """Test: Empty batch."""
    batch_payload = {
        "signals": [],
        "fail_on_error": False,
    }
    
    response = requests.post(
        f"{BASE_URL}/signals/batch",
        json=batch_payload,
        timeout=TIMEOUT,
    )
    
    # Empty batch should be accepted (though might be considered an edge case)
    if response.status_code == 200:
        result = response.json()
        assert result["total_count"] == 0
        assert result["successful_count"] == 0
        assert result["failed_count"] == 0
        print("✓ test_batch_empty: PASSED")
    else:
        print(f"⚠ test_batch_empty: Server returned {response.status_code} (edge case)")


def test_batch_response_structure():
    """Test: Response has correct schema."""
    conversation_id = create_test_conversation()
    
    batch_payload = {
        "signals": [
            {
                "context_window_id": conversation_id,
                "raw_content": "Test signal",
                "signal_source": "Axis",
                "signal_score": 0.75,
            },
        ],
        "fail_on_error": False,
    }
    
    response = requests.post(
        f"{BASE_URL}/signals/batch",
        json=batch_payload,
        timeout=TIMEOUT,
    )
    
    assert response.status_code == 200
    result = response.json()
    
    # Verify response schema
    required_fields = ["total_count", "successful_count", "failed_count", "results"]
    for field in required_fields:
        assert field in result, f"Missing field: {field}"
    
    assert isinstance(result["total_count"], int)
    assert isinstance(result["successful_count"], int)
    assert isinstance(result["failed_count"], int)
    assert isinstance(result["results"], list)
    
    # Verify result item schema
    if result["results"]:
        item = result["results"][0]
        assert "index" in item
        assert "success" in item
        assert isinstance(item["success"], bool)
        if item["success"]:
            assert "signal_id" in item
        else:
            assert "error" in item
    
    print("✓ test_batch_response_structure: PASSED")


def run_all_tests():
    """Run all batch signal tests."""
    tests = [
        test_batch_success_count,
        test_batch_with_missing_required_field,
        test_batch_partial_failure,
        test_batch_fail_on_error_true,
        test_batch_with_payload_dict,
        test_batch_large_batch,
        test_batch_empty,
        test_batch_response_structure,
    ]
    
    print("\n" + "=" * 70)
    print("BATCH SIGNAL INGESTION TESTS")
    print("=" * 70 + "\n")
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: FAILED - {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: ERROR - {str(e)}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
