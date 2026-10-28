# LIMITATIONS.md

A blunt list of what is and is not real in this codebase right now. Read this before citing any output from this repo as evidence of anything.

## What is real

- The NDVI math, the change-detection feature extraction, and the risk-scoring arithmetic (`app/change_detection.py`, `app/risk_engine.py`) are real, tested implementations of the formulas described in the project spec.
- The FastAPI service, its endpoints, and its Pydantic schemas are real and runnable (`uvicorn app.main:app`).
- **The dashboard frontend exists.** The `frontend/` directory contains a Next.js App Router UI with a MapLibre map, risk markers, alert details, an evidence breakdown, and a human-verification submission form. It is a demo UI; its alerts still come from the synthetic-data backend described below.
- **The database is real.** A Supabase Postgres+PostGIS project (`ghana-earth-intelligence`, org `DeRi`, `eu-west-1`) is provisioned with the full schema from spec section 15, RLS enabled on every table (spec section 22), and the backend (`app/db.py`) writes real `land_change_events` / `environmental_alerts` / `verification_records` rows when `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` are set. Every `Alert` response has a `persisted` flag telling you whether that particular write actually landed.
- The test suite (`tests/`) exercises the API and core calculations, including a fallback-path test for when the DB isn't configured. Re-run the tests in the current checkout before relying on this statement as a current test result.

## What is NOT real (yet)

1. **All imagery is synthetic.** `app/synthetic_data.py` generates procedurally-random numpy arrays, not satellite pixels. No Sentinel-1, Sentinel-2, or Landsat data has been fetched or used anywhere in this repo.
2. **The disturbance classifier is a hand-written heuristic**, not a trained model. `classify_disturbance()` uses fixed NDVI-drop thresholds picked for demonstration, not fit on labeled data.
3. **Four of the six risk-engine evidence signals are mocked.** `water_proximity`, `protected_area_proximity`, `historical_mining_evidence`, and `geospatial_context` in `app/main.py` are deterministic pseudo-random values keyed off the location id -- not computed from any real river, protected-area, license, or contextual dataset.
4. **Database persistence depends on deployment configuration.** The schema is provisioned, but the API needs `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` configured in its runtime environment for writes to persist. Check each response's `persisted` flag; do not assume persistence is active just because the database exists.
5. **Alert reads are not fully database-backed.** `GET /api/alerts` recomputes alerts rather than reading stored alerts from Postgres; `GET /api/verification/{id}` reads verification history from Postgres when configured.
6. **No authentication, authorization, or rate limiting** is implemented at the FastAPI layer. Database RLS does not replace API authentication. Do not expose this service publicly as-is.
7. **Risk-engine weights and disturbance thresholds are unvalidated.** They were chosen to be directionally sensible, not fit or cross-validated against any ground-truth dataset (spec section 20 calls this out explicitly as required future work).
8. **The dashboard is not a production geospatial monitoring system.** It is a frontend demo connected to an API whose imagery and several evidence signals are synthetic. It does not yet provide live satellite observations or verified mining detections.

## What this means for interpreting output

Every synthetic `Alert` returned by the API is explicitly labeled with `"data_source": "synthetic"` and `"status": "REQUIRES_HUMAN_VERIFICATION"`. Nothing produced by the synthetic pipeline should be treated as evidence of real mining activity, environmental harm, or illegal activity at any real location, even when a demo location's name matches a real place in Ghana. A `persisted` flag only tells you whether that alert record was saved to a real database; it does not make the underlying synthetic observation real.
