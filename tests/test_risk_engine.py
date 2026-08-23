from app.risk_engine import compute_risk, score_bucket


def test_score_bucket_boundaries():
    assert score_bucket(0) == "LOW"
    assert score_bucket(20) == "LOW"
    assert score_bucket(21) == "MODERATE"
    assert score_bucket(60) == "ELEVATED"
    assert score_bucket(61) == "HIGH"
    assert score_bucket(100) == "CRITICAL"


def test_compute_risk_zero_evidence():
    result = compute_risk({})
    assert result.score == 0.0
    assert result.bucket == "LOW"


def test_compute_risk_max_evidence():
    evidence = {
        k: 1.0
        for k in [
            "temporal_disturbance",
            "excavation_probability",
            "water_proximity",
            "protected_area_proximity",
            "historical_mining_evidence",
            "geospatial_context",
        ]
    }
    result = compute_risk(evidence)
    assert result.score == 100.0
    assert result.bucket == "CRITICAL"


def test_compute_risk_contributions_sum_to_score():
    evidence = {"temporal_disturbance": 0.5, "water_proximity": 0.8}
    result = compute_risk(evidence)
    assert abs(sum(result.contributions.values()) - result.score) < 0.01
