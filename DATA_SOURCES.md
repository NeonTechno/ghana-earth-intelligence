# DATA_SOURCES.md

Datasets researched for Ghana Earth Intelligence. **None of these are wired into the current MVP** — the running code uses only synthetic data (see `LIMITATIONS.md`). This document exists so the next integration step is a lookup, not a research project.

> This environment's outbound network access does not currently reach any of the domains below (only package registries and github.com are reachable from the build sandbox), so none of these were live-tested from here. URLs and general characteristics are documented from public, well-established knowledge of these services; verify current terms/quotas directly before integrating.

## Satellite imagery

| Source | URL | License | Resolution | Coverage | Auth required |
|---|---|---|---|---|---|
| Sentinel-2 (ESA Copernicus) | https://dataspace.copernicus.eu | Free, open (Copernicus license) | 10-60m multispectral, ~5 day revisit | Global, incl. Ghana | Yes (free account) |
| Sentinel-1 (ESA Copernicus, SAR) | https://dataspace.copernicus.eu | Free, open | 5-20m SAR (C-band) | Global | Yes (free account) |
| Landsat 8/9 | https://earthexplorer.usgs.gov | Free, open (USGS) | 15-30m multispectral, 16 day revisit | Global | Yes (free account) |
| Sentinel Hub | https://www.sentinel-hub.com | Free tier + paid | Same underlying Sentinel/Landsat data, easier API | Global | Yes (API key) |
| Google Earth Engine | https://earthengine.google.com | Free for research/nonprofit | Catalog of the above + derived products | Global | Yes (GEE account) |
| Microsoft Planetary Computer | https://planetarycomputer.microsoft.com | Free, open | STAC catalog of Sentinel/Landsat | Global | API key for some collections |

**Recommendation for next integration step:** Sentinel-2 via the Copernicus Data Space Ecosystem (free tier, STAC API, no card required) as the primary source, since it directly supports NDVI/NDWI/NDBI/Bare Soil Index computation already stubbed out in `app/change_detection.py`.

## Ghana institutional / geological data

| Institution | Relevance | Notes |
|---|---|---|
| Ghana Geological Survey Authority (GhGSA) | Geological formations, historical exploration data | Public data availability and API access need direct verification; likely PDF/report-based rather than API-first |
| Minerals Commission of Ghana | Mining licenses, concessions | Some concession data has been published via the Ghana Cadastre / mining portal in past initiatives; verify current public access before relying on it, and never assume a lack of listed license implies illegality |
| Environmental Protection Agency (EPA Ghana) | Environmental permits, protected-area status | Verify current public data portal |
| Forestry Commission of Ghana | Forest reserve boundaries | Forest reserve boundary shapefiles have historically been available through Ghana's open data / Global Forest Watch partnerships |
| Water Resources Commission | River basins, water body boundaries | Verify current public data portal |

## Open geographic datasets (not Ghana-specific, but cover Ghana)

| Dataset | URL | Use |
|---|---|---|
| OpenStreetMap (Ghana extract) | https://download.geofabrik.de/africa/ghana.html | Roads, admin boundaries, settlements, some water features |
| HydroSHEDS | https://www.hydrosheds.org | Rivers, watersheds |
| Global Forest Watch / Hansen Global Forest Change | https://www.globalforestwatch.org | Forest cover, forest loss (useful as an independent cross-check for the disturbance classifier) |
| Protected Planet (WDPA) | https://www.protectedplanet.net | Protected area boundaries, incl. Ghana forest reserves and national parks |
| GADM | https://gadm.org | Administrative boundaries |
| SRTM / Copernicus DEM | via Copernicus Data Space or USGS | Elevation, for geophysical/geological features |

## Integration priority (for the mocked signals in `app/main.py`)

1. `water_proximity` -> HydroSHEDS rivers layer, distance-to-nearest-river computed with GeoPandas/Shapely
2. `protected_area_proximity` -> Protected Planet WDPA + Forestry Commission reserve boundaries
3. `historical_mining_evidence` -> Minerals Commission concession data (where publicly available) + Global Forest Watch historical loss near known mining belts
4. `geospatial_context` -> composite of the above plus GADM administrative context

Each of these is a straightforward GeoPandas spatial join once the corresponding shapefile/GeoJSON is downloaded — no ML required for this step.
