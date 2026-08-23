"""
Change-detection module (project spec section 9).

Implements the MVP workflow:
    preprocessing -> spectral indices (NDVI) -> difference features -> classification

Currently operates ONLY on synthetic rasters (see synthetic_data.py) since
no live satellite ingestion pipeline exists yet (tracked in DATA_SOURCES.md
and LIMITATIONS.md). The function signatures take raw (red, nir) arrays
so a real Sentinel-2 raster reader can be substituted later without
changing any caller.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def compute_ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """Normalized Difference Vegetation Index. Values in roughly [-1, 1]."""
    denom = nir + red
    denom = np.where(denom == 0, 1e-6, denom)
    return (nir - red) / denom


@dataclass
class ChangeFeatures:
    mean_ndvi_t1: float
    mean_ndvi_t2: float
    ndvi_drop: float          # mean_ndvi_t1 - mean_ndvi_t2, floored at 0
    disturbed_fraction: float  # fraction of pixels whose NDVI drop exceeds threshold
    disturbance_class: str    # heuristic label — NOT a legal/factual determination


def detect_change(
    red_t1: np.ndarray,
    nir_t1: np.ndarray,
    red_t2: np.ndarray,
    nir_t2: np.ndarray,
    drop_threshold: float = 0.15,
) -> ChangeFeatures:
    ndvi_t1 = compute_ndvi(red_t1, nir_t1)
    ndvi_t2 = compute_ndvi(red_t2, nir_t2)

    pixel_drop = ndvi_t1 - ndvi_t2
    mean_t1 = float(np.mean(ndvi_t1))
    mean_t2 = float(np.mean(ndvi_t2))
    ndvi_drop = max(0.0, mean_t1 - mean_t2)
    disturbed_fraction = float(np.mean(pixel_drop > drop_threshold))

    disturbance_class = classify_disturbance(ndvi_drop, disturbed_fraction)

    return ChangeFeatures(
        mean_ndvi_t1=mean_t1,
        mean_ndvi_t2=mean_t2,
        ndvi_drop=ndvi_drop,
        disturbed_fraction=disturbed_fraction,
        disturbance_class=disturbance_class,
    )


def classify_disturbance(ndvi_drop: float, disturbed_fraction: float) -> str:
    """
    Heuristic placeholder classifier. Stands in for the RF/XGBoost
    disturbance classifier planned in the roadmap (to be trained on
    labeled Sentinel-1/2 change pairs once real data is wired in).
    Thresholds are provisional and unvalidated — see LIMITATIONS.md.

    Output must never be described as a determination of illegal activity.
    """
    if disturbed_fraction < 0.05:
        return "no_significant_change"
    if ndvi_drop >= 0.20 and disturbed_fraction >= 0.35:
        return "mining_disturbance_candidate"
    if 0.08 <= ndvi_drop < 0.20:
        return "vegetation_loss_ambiguous"  # could be agriculture, construction, or natural
    return "natural_variation_candidate"
