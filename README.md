# Ghana Earth Intelligence (GEI)

AI-powered geospatial intelligence platform for Ghana: mineral prospectivity + galamsey (illegal/environmentally destructive mining) monitoring, inspired by systems like Earth AI.

**Mission:** DISCOVER -> MONITOR -> VERIFY -> PROTECT -> RESTORE

> This project produces evidence and risk/prospectivity scores for **human verification**. It never issues automated legal or enforcement determinations. See `LIMITATIONS.md` and `PROJECT_AUDIT.md` before relying on any output.

## Current status: MVP + real database (Phase 1/2 of the roadmap)

The first working milestone, per the project spec:

> Given satellite imagery of a selected region in Ghana, detect significant land-use changes associated with possible mining activity and display those changes with an explainable risk score.

**Important:** the imagery is still **synthetic** (procedurally generated) -- see `app/synthetic_data.py` and `LIMITATIONS.md`. What's now real is the **database**: a Supabase Postgres + PostGIS project with the full schema from the spec, RLS security, and a persistence layer (`app/db.py`) that writes real rows for every alert and verification when configured.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # optional: add SUPABASE_SERVICE_ROLE_KEY to enable real persistence
uvicorn app.main:app --reload
```

Then visit `http://localhost:8000/docs` for interactive OpenAPI docs.

Without any `.env`, the app runs entirely in-memory (no DB writes) -- useful for local dev and exactly what the test suite does. With `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` set (see `.env.example`), `GET /api/alerts` and `POST /api/verification` write real rows to Postgres, and each `Alert.persisted` field tells you whether it landed.

## Run tests

```bash
pytest -v
```

16 tests, all passing without any environment configuration.

## API surface (MVP)

| Endpoint | Description |
|---|---|
| `GET /api/health` | liveness check; also reports `database_configured` |
| `GET /api/locations` | demo Ghana mining-belt locations |
| `GET /api/alerts` | runs the pipeline on all demo locations, returns risk-scored alerts (persists to Postgres if configured) |
| `GET /api/alerts/{id}` | fetch a single alert |
| `GET /api/risk?lat=&lon=&name=` | run the pipeline on an arbitrary coordinate |
| `POST /api/verification` | record a human verification decision on an alert (persists if configured) |
| `GET /api/verification/{alert_id}` | list verification history for an alert (reads from Postgres if configured) |
| `GET /api/models` | model registry / versions |

## Architecture (MVP scope)

```
synthetic raster (t1, t2)
        |
   NDVI computation           app/change_detection.py
        |
   change / disturbance features
        |
   heuristic disturbance classifier
        |
   evidence vector (6 signals, 0-1 each)
        |
   explainable risk engine      app/risk_engine.py
        |
   0-100 score -> LOW/MODERATE/ELEVATED/HIGH/CRITICAL
        |
   Alert (JSON, via FastAPI)    app/main.py  ---->  app/db.py  ---->  Supabase/PostGIS
```

See `ARCHITECTURE.md` for how this maps onto the full long-term system, `PROJECT_AUDIT.md` for the state of the repo when this MVP was added, `DATA_SOURCES.md` for real datasets researched but not yet ingested, and `LIMITATIONS.md` for a blunt list of what is and isn't real right now.

## Database

Supabase project `ghana-earth-intelligence` (org `DeRi`, `eu-west-1`, free tier). Full PostGIS schema (locations, satellite_observations, land_change_events, environmental_alerts, geological_features, mineral_occurrences, prospectivity_predictions, field_observations, verification_records, model_versions) with row-level security on every table -- public read, service-role-only write.

## Ethical constraints (non-negotiable)

- No automated "illegal activity" determinations -- outputs use `mining-risk`, `mining_disturbance_candidate`, `REQUIRES_HUMAN_VERIFICATION`, never "illegal" or "confirmed crime".
- Every prediction carries evidence + confidence, never a bare assertion.
- No fabricated satellite observations, licenses, or geological data. Where real data isn't wired in, it's synthetic and labeled as such -- never silently substituted.

## License

Not yet specified -- add one before any external contribution or deployment.
