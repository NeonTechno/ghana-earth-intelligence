# LIMITATIONS.md

A blunt list of what is and is not real in this codebase right now. Read this before citing any output from this repo as evidence of anything.

## What is real

- The NDVI math, the change-detection feature extraction, and the risk-scoring arithmetic (`app/change_detection.py`, `app/risk_engine.py`) are real, tested implementations of the formulas described in the project spec.
- The FastAPI service, its endpoints, and its Pydantic schemas are real and runnable (`uvicorn app.main:app`).
- **The database is real.** A Supabase Postgres+PostGIS project (`ghana-earth-intelligence`, org `DeRi`, `eu-west-1`) is provisioned with the full schema from spec section 15, RLS enabled on every table (spec section 22), and the backend (`app/db.py`) writes real `land_change_events` / `environmental_alerts` / `verification_records` rows when `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` are set. Every `Alert` response has a `persisted` flag telling you whether that particular write actually landed.
- The test suite (`tests/`) genuinely exercises this code, including a fallback-path test for when the DB isn't configured, and passes against it (16/16, run locally before each push).

## What is NOT real (yet)

1. **All imagery is synthetic.** `app/synthetic_data.py` generates procedurally-random numpy arrays, not satellite pixels. No Sentinel-1, Sentinel-2, or Landsat data has been fetched or used anywhere in this repo.
2. **The disturbance classifier is a hand-written heuristic**, not a trained model. `classify_disturbance()` uses fixed NDVI-drop thresholds picked for demonstration, not fit on labeled data.
3. **Four of the six risk-engine evidence signals are mocked.** `water_proximity`, `protected_area_proximity`, `historical_mining_evidence`, and `geospatial_context` in `app/main.py` are deterministic pseudo-random values keyed off the location id -- not computed from any real river, protected-area, license, or contextual dataset.
4. **The `service_role` key is not deployed anywhere.** The DB schema and RLS are live, but no running instance of this API currently has network access to Supabase *and* the service_role key configured, so in practice every deployed/local run today still falls back to in-memory storage (`persisted: false` on every alert) until someone sets `SUPABASE_SERVICE_ROLE_KEY` in a real deployment environment with outbound network access to `*.supabase.co`.
5. **Reads are still served from the in-memory cache**, not queried back from Postgres, even when writes succeed. `GET /api/alerts` always recomputes + re-persists rather than reading existing rows; `GET /api/verification/{id}` does read from Postgres when configured. Full read-from-DB for alerts is the next step.
6. **No authentication, authorization, or rate limiting** on the API itself (the DB has RLS, but the FastAPI layer has none). Do not expose this service publicly as-is.
7. **Risk-engine weights and disturbance thresholds are unvalidated.** They were chosen to be directionally sensible, not fit or cross-validated against any ground-truth dataset (spec section 20 calls this out explicitly as required future work).
8. **No interactive map / frontend yet.** This is an API-only service.

## What this means for interpreting output

Every `Alert` returned by this API is explicitly `"data_source": "synthetic"` and `"status": "REQUIRES_HUMAN_VERIFICATION"`. Nothing produced by this code should be treated as evidence of real mining activity, environmental harm, or illegal activity at any real location, even when a demo location's name matches a real place in Ghana -- the coordinates are only used as a seed for fake data, and even the `persisted` flag only tells you whether a *fake* alert was saved to a real database.
