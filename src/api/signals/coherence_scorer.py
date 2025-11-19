"""/src/api/signals/coherence_scorer.py

Coherence scoring based on signal lineage and drift metrics.
Measures discourse alignment and signal stability over time.
"""


def compute_coherence_from_drift(
    drift_metrics: list[dict],
    signals=None,
) -> float:
    """Compute coherence score from drift metrics.
    
    Simple formula: coherence = 1 - avg(drift_scores)
    
    High drift (variance) → low coherence
    Low drift (consistency) → high coherence
    
    Parameters:
        drift_metrics: List of drift metric dicts with 'drift_score' key
        signals: Optional list of SignalModel for fallback calculation
    
    Returns:
        Coherence score (0-1)
    """
    if not drift_metrics or len(drift_metrics) == 0:
        # If no drift metrics, use average signal score as fallback
        if signals and len(signals) > 0:
            avg_signal_score = sum(s.signal_score for s in signals) / len(signals)
            return avg_signal_score
        return 0.5
    
    avg_drift = sum(m.get('drift_score', 0.0) for m in drift_metrics) / len(drift_metrics)
    coherence = max(0.0, min(1.0, 1.0 - avg_drift))
    
    return coherence


def compute_coherence_trend(
    coherence_scores: list[float],
) -> float:
    """Compute trend of coherence over time (simple linear slope).
    
    Positive trend = coherence improving
    Negative trend = coherence degrading
    
    Parameters:
        coherence_scores: List of coherence values over time
    
    Returns:
        Trend slope (unbounded, typically -1 to 1)
    """
    if not coherence_scores or len(coherence_scores) < 2:
        return 0.0
    
    # Simple linear regression slope
    n = len(coherence_scores)
    x_values = list(range(n))
    
    mean_x = sum(x_values) / n
    mean_y = sum(coherence_scores) / n
    
    numerator = sum(
        (x_values[i] - mean_x) * (coherence_scores[i] - mean_y)
        for i in range(n)
    )
    denominator = sum((x - mean_x) ** 2 for x in x_values)
    
    if denominator == 0:
        return 0.0
    
    slope = numerator / denominator
    return slope


def score_signal_source_diversity(signal_sources: dict[str, int]) -> float:
    """Score coherence boost from diverse signal sources.
    
    Multiple sources reduce groupthink and improve coherence.
    Single source reduces score.
    
    Parameters:
        signal_sources: Dict mapping source name to signal count
    
    Returns:
        Diversity bonus (0-0.2)
    """
    if not signal_sources:
        return 0.0
    
    num_sources = len(signal_sources)
    total_signals = sum(signal_sources.values())
    
    # More sources = higher diversity
    # Ideally distributed across sources
    diversity_score = min(1.0, (num_sources - 1) / 4)  # 4 sources = max diversity
    
    # Check distribution balance (penalize if heavily skewed to one source)
    if total_signals > 0:
        max_source_ratio = max(signal_sources.values()) / total_signals
        balance_penalty = (max_source_ratio - 0.25)  # Penalize >25% from one source
        diversity_score *= max(0.5, 1.0 - balance_penalty)
    
    return diversity_score * 0.2  # Cap bonus at 0.2


def compute_weighted_coherence(
    base_coherence: float,
    drift_metrics: list[dict],
    signal_sources: dict[str, int],
) -> float:
    """Compute weighted coherence with multiple factors.
    
    Factors:
    - Base coherence (from drift): 70%
    - Source diversity: 30%
    
    Parameters:
        base_coherence: Coherence from drift (0-1)
        drift_metrics: List of drift metrics
        signal_sources: Dict of signal sources
    
    Returns:
        Weighted coherence score (0-1)
    """
    diversity_bonus = score_signal_source_diversity(signal_sources)
    
    # 70% base coherence, 30% diversity bonus
    weighted = (base_coherence * 0.7) + diversity_bonus
    
    return max(0.0, min(1.0, weighted))
