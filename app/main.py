"""
Ghana Earth Intelligence -- MVP API

Implements the first milestone from the project spec:
"Given satellite imagery of a selected region in Ghana, detect
significant land-use changes associated with possible mining activity
and display those changes ... with an explainable risk score."

IMPORTANT: All imagery in this MVP is SYNTHETIC (see synthetic_data.py).
No real Sentinel/Landsat ingestion is wired in yet -- that is the
documented next step (see DATA_SOURCES.md, LIMITATIONS.md). This service
never labels anything "illegal"; every alert carries evidence, a
confidence-adjacent risk score, and status REQUIRES_HUMAN_VERIFICATION.

Persistence: writes to Supabase/PostGIS (app/db.py) when SUPABASE_URL +
SUPABASE_SERVICE_ROLE_KEY are set in the environment. Falls back to an
in-memory store otherwise, so this runs and tests cleanly with zero
configuration. The in-memory store is always kept in sync regardless
(see LIMITATIONS.md for what this does and doesn't guarantee).
"""
from __future__ import annotations

import hashlib
from typing import Dict, List

from fastapi import FastAPI, HTTPException

from . import db
from .change_detection import ChangeFeatures, detect_change
from .models import Alert, EvidenceItem, Location, VerificationRecord
from .risk_engine import WEIGHTS, compute_risk
from .synthetic_data import generate_synthetic_scene

app = FastAPI(
    title="Ghana Earth Intelligence -- MVP",
    version="0.1.1",
    description="Galamsey satellite monitor MVP. Synthetic data only -- see DATA_SOURCES.md.",
)

# Demo locations: approximate public-domain town centroids in Ghana's
# mining belt, used only to seed the synthetic generator deterministically.
DEMO_LOCATIONS: List[Location] = [
    Location(id="obuasi", name="Obuasi (Ashanti Region)", lat=6.2027, lon=-1.6708),
    Location(id="tarkwa", name="Tarkwa (Western Region)", lat=5.3017, lon=-1.9911),
    Location(id="prestea", name="Prestea (Western Region)", lat=5.4333, lon=-2.1500),
    Location(id="kenyasi", name="Kenyasi (Ahafo Region)", lat=7.1167, lon=-2.3333),
]

_alerts_store: Dict[str, Alert] = {}
_verifications: Dict[str, List[VerificationRecord]] = {}


def _mock_geospatial_signal(location_id: str, salt: int) -> float:
    """
    Deterministic 0-1 pseudo-value standing in for a real geospatial join
    (proximity to rivers/forests/licensed areas). NOT a real measurement --
    tracked as a Phase 1 gap in LIMITATIONS.md.
    """
    seed = int(hashlib.sha256(location_id.encode()).hexdigest()[:6], 16)
    return ((seed * (salt + 1)) % 97) / 97


def _evidence_from_features(features: ChangeFeatures, location: Location) -> Dict[str, float]:
    return {
        "temporal_disturbance": min(1.0, features.ndvi_drop / 0.30),
        "excavation_probability": min(1.0, features.disturbed_fraction / 0.5),
        "water_proximity": _mock_geospatial_signal(location.id, 1),
        "protected_area_proximity": _mock_geospatial_signal(location.id, 2),
        "historical_mining_evidence": _mock_geospatial_signal(location.id, 3),
        "geospatial_context": _mock_geospatial_signal(location.id, 4),
    }


def _build_alert(location: Location) -> Alert:
    t1 = generate_synthetic_scene(location.lat, location.lon, "t1", disturbed=False)
    t2 = generate_synthetic_scene(location.lat, location.lon, "t2", disturbed=True)
    features = detect_change(t1.red, t1.nir, t2.red, t2.nir)

    evidence = _evidence_from_features(features, location)
    risk = compute_risk(evidence)

    evidence_items = [
        EvidenceItem(signal=k, value=round(v, 3), contribution_points=risk.contributions[k])
        for k, v in evidence.items()
    ]
    evidence_payload = [item.model_dump() for item in evidence_items]

    fallback_id = f"{location.id}-demo"
    persisted = False
    alert_id = fallback_id

    if db.is_configured():
        # db.py already swallows its own exceptions and returns None/False on
        # failure (e.g. only the anon key is configured and RLS rejects the
        # write) -- this stays defensive against any future change there too,
        # so a DB hiccup degrades to "not persisted" rather than a 500.
        try:
            db_location_id = db.upsert_location(location.id, location.name, location.lat, location.lon)
            db_alert_id = db.persist_alert(
                location_id=db_location_id,
                ndvi_drop=features.ndvi_drop,
                disturbed_fraction=features.disturbed_fraction,
                disturbance_class=features.disturbance_class,
                risk_score=risk.score,
                risk_bucket=risk.bucket,
                evidence=evidence_payload,
            )
        except Exception:  # noqa: BLE001
            db_alert_id = None
        if db_alert_id:
            alert_id = db_alert_id
            persisted = True

    return Alert(
        id=alert_id,
        location=location,
        disturbance_class=features.disturbance_class,
        ndvi_drop=round(features.ndvi_drop, 4),
        disturbed_fraction=round(features.disturbed_fraction, 4),
        risk_score=risk.score,
        risk_bucket=risk.bucket,
        evidence=evidence_items,
        persisted=persisted,
    )


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "ghana-earth-intelligence-mvp",
        "database_configured": db.is_configured(),
    }


@app.get("/api/locations", response_model=List[Location])
def list_locations():
    return DEMO_LOCATIONS


@app.get("/api/alerts", response_model=List[Alert])
def list_alerts():
    for loc in DEMO_LOCATIONS:
        alert = _build_alert(loc)
        _alerts_store[alert.id] = alert
    return list(_alerts_store.values())


@app.get("/api/alerts/{alert_id}", response_model=Alert)
def get_alert(alert_id: str):
    if alert_id not in _alerts_store:
        matching = [loc for loc in DEMO_LOCATIONS if f"{loc.id}-demo" == alert_id]
        if not matching:
            raise HTTPException(status_code=404, detail="alert not found")
        _alerts_store[alert_id] = _build_alert(matching[0])
    return _alerts_store[alert_id]


@app.get("/api/risk", response_model=Alert)
def get_risk(lat: float, lon: float, name: str = "custom-location"):
    location = Location(id="custom", name=name, lat=lat, lon=lon)
    alert = _build_alert(location)
    _alerts_store[alert.id] = alert
    return alert


@app.post("/api/verification", response_model=VerificationRecord)
def submit_verification(record: VerificationRecord):
    if record.alert_id not in _alerts_store:
        raise HTTPException(status_code=404, detail="unknown alert_id -- call /api/alerts first")
    _verifications.setdefault(record.alert_id, []).append(record)
    try:
        db.persist_verification(record.alert_id, record.verdict, record.notes, record.verified_by)
    except Exception:  # noqa: BLE001
        pass
    return record


@app.get("/api/verification/{alert_id}", response_model=List[VerificationRecord])
def get_verifications(alert_id: str):
    if db.is_configured():
        try:
            rows = db.fetch_verifications(alert_id)
        except Exception:  # noqa: BLE001
            rows = []
        if rows:
            return [
                VerificationRecord(
                    alert_id=row["alert_id"],
                    verdict=row["verdict"],
                    notes=row.get("notes"),
                    verified_by=row["verified_by"],
                    verified_at=row["verified_at"],
                )
                for row in rows
            ]
    return _verifications.get(alert_id, [])


@app.get("/api/models")
def list_models():
    return {
        "models": [
            {
                "name": "gei-mvp-change-detector",
                "version": "0.1.0",
                "type": "heuristic (NDVI-threshold)",
                "weights": WEIGHTS,
                "status": "MVP placeholder -- not trained on real labeled data",
            }
        ]
    }
