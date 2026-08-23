import numpy as np

from app.change_detection import classify_disturbance, compute_ndvi, detect_change


def test_compute_ndvi_range():
    red = np.full((4, 4), 0.1)
    nir = np.full((4, 4), 0.4)
    ndvi = compute_ndvi(red, nir)
    assert np.all(ndvi > 0.5)


def test_detect_change_flags_disturbance():
    red_t1 = np.full((8, 8), 0.10)
    nir_t1 = np.full((8, 8), 0.45)
    red_t2 = np.full((8, 8), 0.32)
    nir_t2 = np.full((8, 8), 0.28)

    features = detect_change(red_t1, nir_t1, red_t2, nir_t2)
    assert features.ndvi_drop > 0.2
    assert features.disturbance_class == "mining_disturbance_candidate"


def test_detect_change_no_change():
    red = np.full((8, 8), 0.10)
    nir = np.full((8, 8), 0.45)
    features = detect_change(red, nir, red, nir)
    assert features.disturbance_class == "no_significant_change"
    assert features.disturbed_fraction == 0.0


def test_classify_disturbance_thresholds():
    assert classify_disturbance(0.01, 0.01) == "no_significant_change"
    assert classify_disturbance(0.25, 0.5) == "mining_disturbance_candidate"
    assert classify_disturbance(0.10, 0.10) == "vegetation_loss_ambiguous"
