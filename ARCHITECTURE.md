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

Only the **Environmental Intelligence** branch's MVP slice: Satellite Analysis (synthetic) -> Change Detection -> a minimal Risk/Prospectivity Engine -> Alerts -> Human Verification (write path real, read-back partial). Mineral Intelligence tables exist in the DB schema but no pipeline populates them yet -- that's Phase 5.

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
                    |            \
                    |             +--> app/db.py --> Supabase/PostGIS   <- REAL persistence (spec section 15)
                    |
         POST /api/verification              <- "Human Verification" (writes to DB when configured)
```

## Module responsibilities

- **`app/synthetic_data.py`** -- deterministic fake raster generator. Replace with a real Sentinel-2 reader (rasterio) behind the same interface when ready.
- **`app/change_detection.py`** -- pure functions over numpy arrays: NDVI, temporal disturbance features, heuristic classification. No I/O, no framework dependencies -- easy to unit test and easy to swap the classifier for a trained model later.
- **`app/risk_engine.py`** -- pure function mapping an evidence dict to a score + bucket + per-signal breakdown. Weights are named constants (`WEIGHTS`) so they're trivially tunable/auditable.
- **`app/db.py`** -- Supabase/PostGIS client wrapper. No-ops safely when unconfigured; every write is exception-safe so a DB outage degrades gracefully instead of crashing the API.
- **`app/models.py`** -- Pydantic schemas shared by the API layer.
- **`app/main.py`** -- FastAPI app; wires the above together, owns the in-memory read cache, and delegates persistence to `db.py`.

## Database (live)

Supabase project `ghana-earth-intelligence` (`eu-west-1`, free tier, org `DeRi`). Full PostGIS schema per spec section 15 is applied via migration; RLS is enabled on every table with public-read / service-role-write policies (spec section 22). See `LIMITATIONS.md` for exactly what is and isn't wired end-to-end yet.

## Roadmap (from the master project spec, condensed)

- **Phase 0 -- Research** (done): audit, data source research, architecture docs.
- **Phase 1 -- Geospatial foundation** (mostly done): PostGIS schema + RLS live; real satellite ingestion still pending.
- **Phase 2 -- Galamsey MVP** (done, synthetic-data version): temporal comparison, disturbance classifier, risk scoring, now with real persistence.
- **Phase 3 -- Dashboard**: interactive map (Next.js + MapLibre GL), alerts UI, evidence panel.
- **Phase 4 -- Field verification**: GPS/photo field observations, full verification workflow (table exists, no UI/API yet).
- **Phase 5 -- Mineral intelligence**: gold prospectivity modeling (tables exist, no pipeline yet).
- **Phase 6 -- Agentic AI**: specialized Geological/Satellite/Environmental/Mining/Verification agents.
- **Phase 7 -- Advanced research**: foundation models, active learning, uncertainty estimation, GNNs, Bayesian/physics-informed ML.
