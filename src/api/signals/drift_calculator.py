"""/src/api/signals/drift_calculator.py

Drift calculator for moving variance of signal scores.
Core component of the Coherence Signal Architecture.
"""

from datetime import datetime, timedelta


def compute_variance(values: list[float]) -> float:
    """Compute variance of a list of values, normalized to 0-1.

    Variance measures the spread of signal_scores. Higher variance indicates
    more inconsistency (lower coherence). Normalized to 0-1 range for
    coherence scoring.

    Parameters:
        values: List of signal scores (0-1)

    Returns:
        Normalized variance value (0-1)
    """
    if not values or len(values) < 2:
        return 0.0

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)

    # Normalize to 0-1 (max variance is 0.25 for uniform 0-1 distribution)
    # Clamp between 0 and 1
    normalized_variance = min(1.0, variance * 4)
    return normalized_variance


def parse_window_size(window_str: str) -> int:
    """Parse window size string into seconds.

    Supports format: '5m' (5 minutes), '1h' (1 hour), '30s' (30 seconds)

    Parameters:
        window_str: Window size string (e.g., '5m', '1h', '30s')

    Returns:
        Window size in seconds

    Raises:
        ValueError: If format is invalid
    """
    window_str = window_str.strip().lower()

    if window_str.endswith("m"):
        return int(window_str[:-1]) * 60
    elif window_str.endswith("h"):
        return int(window_str[:-1]) * 3600
    elif window_str.endswith("s"):
        return int(window_str[:-1])
    else:
        raise ValueError(f"Invalid window size format: {window_str}")


def compute_drift_over_windows(
    signals,
    window_seconds: int,
) -> list[dict]:
    """Compute drift metrics over sliding windows.

    Drift = moving variance of signal_scores within each time window.

    Parameters:
        signals: List of SignalModel objects with time and signal_score
        window_seconds: Window size in seconds

    Returns:
        List of drift metrics with structure:
        {
            'window_start': datetime,
            'window_end': datetime,
            'drift_score': float,
            'signal_count': int
        }
    """
    if not signals:
        return []

    metrics = []
    first_time = signals[0].time
    last_time = signals[-1].time

    # Create sliding windows
    current_start = first_time
    while current_start < last_time:
        current_end = current_start + timedelta(seconds=window_seconds)

        # Get signals in this window
        window_signals = [s for s in signals if current_start <= s.time < current_end]

        if window_signals:
            # Compute variance of signal_scores
            signal_scores = [s.signal_score for s in window_signals]
            drift = compute_variance(signal_scores)

            metric = {
                "window_start": current_start,
                "window_end": current_end,
                "drift_score": drift,
                "signal_count": len(window_signals),
            }
            metrics.append(metric)

        current_start = current_end

    return metrics
