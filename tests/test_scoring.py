from __future__ import annotations

from core.scorer import calculate_risk_score, get_risk_label


def test_rule_and_ml_combination_yields_critical_score() -> None:
    score = calculate_risk_score(-0.45, ["DoS / DDoS Attack"], True)
    label, _ = get_risk_label(score)

    assert score >= 80
    assert label == "CRITICAL"


def test_clean_event_remains_safe_or_low() -> None:
    score = calculate_risk_score(0.35, [], False)
    label, _ = get_risk_label(score)

    assert score < 20
    assert label == "SAFE"
