# LIMITATIONS.md

A blunt list of what is and is not real in this codebase right now. Read this before citing any output from this repo as evidence of anything.

## What is real

- The NDVI math, the change-detection feature extraction, and the risk-scoring arithmetic (`app/change_detection.py`, `app/risk_engine.py`) are real, tested implementations of the formulas described in the project spec.
- The FastAPI service, its endpoints, and its Pydantic schemas are real and runnable (`uvicorn app.main:app`).
- The test suite (`tests/`) genuinely exercises this code and passes against it.

## What is NOT real (yet)

1. **All imagery is synthetic.** `app/synthetic_data.py` generates procedurally-random numpy arrays, not satellite pixels. No Sentinel-1, Sentinel-2, or Landsat data has been fetched or used anywhere in this repo.
2. **The disturbance classifier is a hand-written heuristic**, not a trained model. `classify_disturbance()` uses fixed NDVI-drop thresholds picked for demonstration, not fit on labeled data.
3. **Four of the six risk-engine evidence signals are mocked.** `water_proximity`, `protected_area_proximity`, `historical_mining_evidence`, and `geospatial_context` in `app/main.py` are deterministic pseudo-random values keyed off the location id — not computed from any real river, protected-area, license, or contextual dataset.
4. **No database.** Alerts and verifications live in process memory (`_alerts_store`, `_verifications` in `app/main.py`) and are lost on restart. The PostGIS schema from the spec (section 15) does not exist yet.
5. **No authentication, authorization, or rate limiting.** Do not expose this service publicly as-is.
6. **Risk-engine weights and disturbance thresholds are unvalidated.** They were chosen to be directionally sensible, not fit or cross-validated against any ground-truth dataset (spec section 20 calls this out explicitly as required future work).
7. **No interactive map / frontend yet.** This is an API-only service.

## What this means for interpreting output

Every `Alert` returned by this API is explicitly `"data_source": "synthetic"` and `"status": "REQUIRES_HUMAN_VERIFICATION"`. Nothing produced by this code should be treated as evidence of real mining activity, environmental harm, or illegal activity at any real location, even when a demo location's name matches a real place in Ghana — the coordinates are only used as a seed for fake data.
