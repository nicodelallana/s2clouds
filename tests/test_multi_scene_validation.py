"""Tests for multi-scene validation table and statistical metrics."""

import numpy as np

from s2clouds.validation import (
    ShadowValidationResult,
    validate_parallax_with_shadow,
)

# Multi-scene validation points across Cantabrian Sea acquisitions
VALIDATION_TARGETS = [
    {
        "scene_id": "S2B_30TWN_20230831_0_L2A",
        "date": "2023-08-31",
        "location": "Bilbao Abra / Patch 4",
        "cloud_type": "Cumulus humilis",
        "parallax_h_m": 189.5,
        "parallax_sigma_m": 105.8,
        "shadow_dist_m": 144.2,
        "sun_zenith_deg": 36.68,
    },
    {
        "scene_id": "S2B_30TWN_20230831_0_L2A",
        "date": "2023-08-31",
        "location": "Bilbao Coast / Patch 5",
        "cloud_type": "Cumulus",
        "parallax_h_m": 200.0,
        "parallax_sigma_m": 106.0,
        "shadow_dist_m": 147.0,
        "sun_zenith_deg": 36.68,
    },
    {
        "scene_id": "S2B_30TWN_20230831_0_L2A",
        "date": "2023-08-31",
        "location": "Bilbao Abra / Patch 3",
        "cloud_type": "Stratus marinus",
        "parallax_h_m": 42.1,
        "parallax_sigma_m": 105.3,
        "shadow_dist_m": 35.8,
        "sun_zenith_deg": 36.68,
    },
    {
        "scene_id": "S2B_30TVN_20230831_0_L2A",
        "date": "2023-08-31",
        "location": "Santander Bay",
        "cloud_type": "Stratocumulus",
        "parallax_h_m": 1178.5,
        "parallax_sigma_m": 106.5,
        "shadow_dist_m": 885.0,
        "sun_zenith_deg": 36.36,
    },
    {
        "scene_id": "S2A_30TVP_20230819_0_L2A",
        "date": "2023-08-19",
        "location": "Gulf of Biscay",
        "cloud_type": "Cumulus congestus",
        "parallax_h_m": 1631.8,
        "parallax_sigma_m": 108.0,
        "shadow_dist_m": 1045.0,
        "sun_zenith_deg": 33.32,
    },
    {
        "scene_id": "S2A_30TWP_20230819_0_L2A",
        "date": "2023-08-19",
        "location": "Cantabria Offshore",
        "cloud_type": "Cumulus mediocris",
        "parallax_h_m": 894.8,
        "parallax_sigma_m": 106.0,
        "shadow_dist_m": 580.0,
        "sun_zenith_deg": 33.32,
    },
]


def test_multi_scene_validation_statistics():
    """Verify statistical metrics across multi-scene cloud targets."""
    differences = []
    abs_errors = []

    for target in VALIDATION_TARGETS:
        val: ShadowValidationResult = validate_parallax_with_shadow(
            parallax_height_m=target["parallax_h_m"],
            parallax_sigma_m=target["parallax_sigma_m"],
            shadow_distance_m=target["shadow_dist_m"],
            sun_zenith_deg=target["sun_zenith_deg"],
        )
        differences.append(val.difference_m)
        abs_errors.append(val.absolute_difference_m)
        # Every target must be within the literature tolerance (150m from Krauß 2021)
        assert val.within_literature_tolerance is True

    diffs = np.array(differences)
    mean_bias = float(np.mean(diffs))
    rmse = float(np.sqrt(np.mean(diffs**2)))
    std_err = float(np.std(diffs))

    # Mean error should be well under 30 m (Krauß 2021 reference: 31 m)
    assert abs(mean_bias) < 30.0
    # Standard deviation should be well under 137 m (Krauß 2021 reference: 137 m)
    assert std_err < 100.0
    assert rmse < 100.0
