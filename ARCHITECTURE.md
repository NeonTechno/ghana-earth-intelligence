# ARCHITECTURE.md

## Long-term system (from the project spec)

```
                    GHANA EARTH INTELLIGENCE
                              |
              +---------------+---------------+
              |                               |
              v                               v
       MINERAL INTELLIGENCE             ENVIRONMENTAL
              |                         INTELLIGENCE
              v                               v
      Geological/Geochemical/           Satellite Analysis
      Geophysical Analysis               Change Detection
      Prospectivity ML                   Mining Detection
              |                          Water Monitoring
              +---------------+---------------+
                              |
                              v
                     GEOSPATIAL FUSION
                              |
                              v
                RISK / PROSPECTIVITY ENGINE
                              |
                +-------------+-------------+
                v                           v
          Exploration Map             Galamsey Alerts
                |                           |
                v                           v
             Research                 Human Verification
```

## What this repo currently implements

Only the **Environmental Intelligence** branch's MVP slice: Satellite Analysis (synthetic) -> Change Detection -> a minimal Risk/Prospectivity Engine -> Alerts -> (stubbed) Human Verification. Mineral Intelligence is out of scope until Phase 5 of the roadmap below.

```
            app/synthetic_data.py           <- stand-in for "Satellite Analysis"
         (generate_synthetic_scene)
                    |
            app/change_detection.py         <- "Change Detection" / "Mining Detection"
              (compute_ndvi,
               detect_change,
               classify_disturbance)
                    |
     app/main.py: _evidence_from_features    <- "Geospatial Fusion" (partially mocked)
                    |
            app/risk_engine.py               <- "Risk / Prospectivity Engine"
              (compute_risk)
                    |
            app/models.py: Alert             <- API contract
                    |
            app/main.py (FastAPI)            <- "Exploration Map" / "Galamsey Alerts" (API only, no map UI yet)
                    |
         POST /api/verification              <- "Human Verification" (in-memory, no persistence)
```

## Module responsibilities

- **`app/synthetic_data.py`** — deterministic fake raster generator. Replace with a real Sentinel-2 reader (rasterio) behind the same interface when ready.
- **`app/change_detection.py`** — pure functions over numpy arrays: NDVI, temporal disturbance features, heuristic classification. No I/O, no framework dependencies — easy to unit test and easy to swap the classifier for a trained model later.
- **`app/risk_engine.py`** — pure function mapping an evidence dict to a score + bucket + per-signal breakdown. Weights are named constants (`WEIGHTS`) so they're trivially tunable/auditable.
- **`app/models.py`** — Pydantic schemas shared by the API layer.
- **`app/main.py`** — FastAPI app; wires the above together and owns the (currently in-memory) alert/verification stores.

## Roadmap (from the master project spec, condensed)

- **Phase 0 — Research** (this push): audit, data source research, architecture docs.
- **Phase 1 — Geospatial foundation**: PostGIS, real satellite ingestion.
- **Phase 2 — Galamsey MVP** (this push, synthetic-data version): temporal comparison, disturbance classifier, risk scoring.
- **Phase 3 — Dashboard**: interactive map (Next.js + MapLibre GL), alerts UI, evidence panel.
- **Phase 4 — Field verification**: GPS/photo field observations, verification workflow with persistence.
- **Phase 5 — Mineral intelligence**: gold prospectivity modeling.
- **Phase 6 — Agentic AI**: specialized Geological/Satellite/Environmental/Mining/Verification agents.
- **Phase 7 — Advanced research**: foundation models, active learning, uncertainty estimation, GNNs, Bayesian/physics-informed ML.
