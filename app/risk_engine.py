"""
Explainable risk-scoring engine (project spec section 10).

Combines evidence signals (each normalized 0-1) into a 0-100 risk score
using a documented, linear, fully-traceable formula. Weights and bucket
thresholds are PROVISIONAL and require empirical validation against
verified ground-truth cases before being relied upon operationally.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

WEIGHTS: Dict[str, float] = {
    "temporal_disturbance": 0.30,
    "excavation_probability": 0.20,
    "water_proximity": 0.15,
    "protected_area_proximity": 0.15,
    "historical_mining_evidence": 0.10,
    "geospatial_context": 0.10,
}

BUCKETS = [
    (0, 20, "LOW"),
    (21, 40, "MODERATE"),
    (41, 60, "ELEVATED"),
    (61, 80, "HIGH"),
    (81, 100, "CRITICAL"),
]


@dataclass
class RiskAssessment:
    score: float
    bucket: str
    contributions: Dict[str, float]
    status: str = "REQUIRES_HUMAN_VERIFICATION"


def score_bucket(score: float) -> str:
    for lo, hi, name in BUCKETS:
        if lo <= score <= hi:
            return name
    return "CRITICAL" if score > 100 else "LOW"


def compute_risk(evidence: Dict[str, float]) -> RiskAssessment:
    """
    `evidence` values must each be in [0, 1]; out-of-range values are
    clipped. Missing keys default to 0. Returns a fully explainable
    breakdown so every point of the score traces back to a named signal
    (project spec section 16, explainable AI).
    """
    contributions: Dict[str, float] = {}
    total = 0.0
    for key, weight in WEIGHTS.items():
        value = max(0.0, min(1.0, evidence.get(key, 0.0)))
        contribution = value * weight * 100
        contributions[key] = round(contribution, 2)
        total += contribution

    total = max(0.0, min(100.0, total))
    return RiskAssessment(score=round(total, 2), bucket=score_bucket(total), contributions=contributions)
