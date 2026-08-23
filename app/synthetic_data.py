"""
SYNTHETIC / MOCK DATA GENERATOR
================================
No real satellite imagery is used anywhere in this module. All rasters
are procedurally generated with numpy using a seed derived from
(lat, lon, timestamp label), purely to exercise the change-detection
and risk-scoring pipeline end-to-end before real Sentinel-1/2 ingestion
(see DATA_SOURCES.md) is wired in.

Every artifact produced here MUST be treated as fake. API responses
built from it are tagged `"data_source": "synthetic"` — never presented
as real observations.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np

RASTER_SIZE = 64  # pixels per side, small synthetic tile


def _seed_from_location(lat: float, lon: float, salt: str = "") -> int:
    key = f"{lat:.4f}:{lon:.4f}:{salt}".encode()
    return int(hashlib.sha256(key).hexdigest()[:8], 16)


@dataclass
class SyntheticScene:
    red: np.ndarray
    nir: np.ndarray
    label: str  # ground-truth synthetic scenario, for tests/debugging only


def generate_synthetic_scene(lat: float, lon: float, when: str, disturbed: bool) -> SyntheticScene:
    """
    Produce a fake (red, nir) reflectance band pair for a location + timestamp.

    `disturbed=True` biases the scene toward a low-vegetation / bare-soil
    signature, standing in for a post-disturbance capture in demo alerts.
    This is NOT derived from any real observation — it is a deterministic
    function of (lat, lon, when, disturbed) so the API is reproducible.
    """
    rng = np.random.default_rng(_seed_from_location(lat, lon, when))
    if disturbed:
        red = rng.normal(0.32, 0.05, (RASTER_SIZE, RASTER_SIZE)).clip(0, 1)
        nir = rng.normal(0.28, 0.05, (RASTER_SIZE, RASTER_SIZE)).clip(0, 1)
        label = "synthetic_bare_soil_disturbance"
    else:
        red = rng.normal(0.10, 0.03, (RASTER_SIZE, RASTER_SIZE)).clip(0, 1)
        nir = rng.normal(0.45, 0.05, (RASTER_SIZE, RASTER_SIZE)).clip(0, 1)
        label = "synthetic_healthy_vegetation"
    return SyntheticScene(red=red, nir=nir, label=label)
