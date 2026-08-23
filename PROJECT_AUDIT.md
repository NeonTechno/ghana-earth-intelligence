# PROJECT_AUDIT.md

**Audit date:** 2026-08-23
**Auditor:** Claude (acting as lead engineer per project master prompt)

## Repository state at audit time

`NeonTechno/ghana-earth-intelligence` was created on 2026-08-23 and was **completely empty** (0 commits, size 0) when this audit was performed. There was no existing architecture, code, models, APIs, database, frontend, GIS functionality, ML pipeline, tests, configuration, Docker setup, or documentation to inspect or preserve.

## Conclusion

Since there was nothing to keep or avoid rewriting, this audit doubles as the Phase 0 kickoff record. Everything added in this initial push is new.

## What was built in this pass (Phase 0 + partial Phase 1/2)

- FastAPI backend skeleton (`app/main.py`)
- NDVI-based temporal change-detection module (`app/change_detection.py`)
- Heuristic mining-disturbance classifier (placeholder for the planned RF/XGBoost model)
- Explainable weighted risk-scoring engine (`app/risk_engine.py`), 0-100 scale with LOW/MODERATE/ELEVATED/HIGH/CRITICAL buckets
- Pydantic schemas for Location, Alert, EvidenceItem, VerificationRecord (`app/models.py`)
- A synthetic (procedurally generated, clearly labeled) raster generator (`app/synthetic_data.py`) so the pipeline is testable end-to-end before real imagery is wired in
- REST endpoints: health, locations, alerts, single alert, ad-hoc risk lookup, verification submission + history, model registry
- pytest suite covering change detection, risk engine, and API behavior
- `DATA_SOURCES.md`, `ARCHITECTURE.md`, `LIMITATIONS.md` reproducibility docs

## Problems / gaps identified

1. No real satellite ingestion (Sentinel-1/2, Landsat) — the sandbox this was built in has no network egress to Copernicus Data Space, AWS Open Data, Sentinel Hub, or Google Earth Engine. This is the single biggest gap before the system produces real signal.
2. No database — everything is in-memory (`_alerts_store`, `_verifications` dicts in `app/main.py`). Restarting the process loses all state. PostGIS schema from the spec (section 15) is not yet implemented.
3. No real geospatial joins — `water_proximity`, `protected_area_proximity`, `historical_mining_evidence`, `geospatial_context` in `app/main.py` are deterministic mock values, not computed from real rivers/forests/protected-area/license datasets.
4. No auth, rate limiting, or audit-trail persistence (spec section 22) — appropriate for an MVP, but must precede any real deployment.
5. No frontend/interactive map yet (spec section 17) — API-only right now.
6. Risk-engine weights and disturbance-classifier thresholds are hand-picked, not empirically fit or cross-validated against ground truth (spec sections 10, 20).

## Recommended architecture (near-term)

Keep the current module boundaries (`synthetic_data` / `change_detection` / `risk_engine` / `models` / `main`) — they map directly onto where real raster I/O, a trained classifier, and a calibrated risk model will slot in later without changing the API contract. Next additions, in order:

1. Swap `synthetic_data.py` for a real raster reader (`rasterio` + a Sentinel-2 source) behind the same `(red, nir) -> ChangeFeatures` interface.
2. Add PostgreSQL + PostGIS and move `_alerts_store` / `_verifications` into it.
3. Replace the mocked geospatial signals in `main.py` with real GeoPandas joins against rivers/forest-reserve/protected-area layers (see `DATA_SOURCES.md`).
4. Add a proper test dataset with hand-labeled disturbance examples to start validating classifier thresholds (spec section 20).

## Immediate implementation priorities

1. Real satellite data source integration (start with one openly accessible source — see `DATA_SOURCES.md`)
2. PostGIS schema + persistence
3. Real geospatial layers for the mocked proximity signals
4. Interactive map frontend (Next.js + MapLibre GL, per spec section 17)
