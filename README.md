# Ghana Earth Intelligence (GEI)

AI-powered geospatial intelligence platform for Ghana: mineral prospectivity + galamsey (illegal/environmentally destructive mining) monitoring, inspired by systems like Earth AI.

**Mission:** DISCOVER -> MONITOR -> VERIFY -> PROTECT -> RESTORE

> This project produces evidence and risk/prospectivity scores for **human verification**. It never issues automated legal or enforcement determinations. See `LIMITATIONS.md` and `PROJECT_AUDIT.md` before relying on any output.

## Current status: MVP (Phase 1 of the roadmap)

The first working milestone, per the project spec:

> Given satellite imagery of a selected region in Ghana, detect significant land-use changes associated with possible mining activity and display those changes with an explainable risk score.

**Important:** this MVP runs entirely on **synthetic (fake, procedurally generated) raster data** — see `app/synthetic_data.py`. No real Sentinel-1/2 or Landsat imagery is ingested yet. Every API response is tagged `"data_source": "synthetic"` so this is never ambiguous. Real ingestion is the documented next step in `DATA_SOURCES.md`.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then visit `http://localhost:8000/docs` for interactive OpenAPI docs.

## Run tests

```bash
pytest -v
```

## API surface (MVP)

| Endpoint | Description |
|---|---|
| `GET /api/health` | liveness check |
| `GET /api/locations` | demo Ghana mining-belt locations |
| `GET /api/alerts` | runs the pipeline on all demo locations, returns risk-scored alerts |
| `GET /api/alerts/{id}` | fetch a single alert |
| `GET /api/risk?lat=&lon=&name=` | run the pipeline on an arbitrary coordinate |
| `POST /api/verification` | record a human verification decision on an alert |
| `GET /api/verification/{alert_id}` | list verification history for an alert |
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
   Alert (JSON, via FastAPI)    app/main.py
```

See `ARCHITECTURE.md` for how this maps onto the full long-term system, `PROJECT_AUDIT.md` for the state of the repo when this MVP was added, `DATA_SOURCES.md` for real datasets researched but not yet wired in, and `LIMITATIONS.md` for a blunt list of what is and isn't real right now.

## Ethical constraints (non-negotiable)

- No automated "illegal activity" determinations — outputs use `mining-risk`, `mining_disturbance_candidate`, `REQUIRES_HUMAN_VERIFICATION`, never "illegal" or "confirmed crime".
- Every prediction carries evidence + confidence, never a bare assertion.
- No fabricated satellite observations, licenses, or geological data. Where real data isn't wired in, it's synthetic and labeled as such — never silently substituted.

## License

Not yet specified — add one before any external contribution or deployment.
