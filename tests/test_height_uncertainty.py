"""Tests for height calculation and uncertainty propagation."""

import pytest

from s2clouds.constants import BAND_PAIRS_DELTA_T_S
from s2clouds.disparity import measure_window_disparity
from s2clouds.geometry import rotate_crop, scan_direction_phi, scan_rotation_angle
from s2clouds.heights import (
    CloudHeightResult,
    propagate_height_uncertainty,
)
from s2clouds.io_stac import read_crop


def test_propagate_height_uncertainty_b02_b04():
    """Test uncertainty propagation for B02-B04 pair."""
    delta_t_s = BAND_PAIRS_DELTA_T_S[("B02", "B04")]
    disparity_px = 1.0
    sigma_d_px = 0.1
    rel_sigma_dt = 0.01

    res = propagate_height_uncertainty(
        disparity_px=disparity_px,
        delta_t_s=delta_t_s,
        sigma_disparity_px=sigma_d_px,
        relative_sigma_delta_t=rel_sigma_dt,
    )

    assert isinstance(res, CloudHeightResult)
    # Height should be ~1053 m
    assert pytest.approx(res.height_m, abs=1.0) == 1053.0

    # Uncertainty: sqrt((1052.75 * 0.1)^2 + (1052.75 * 0.01)^2) = sqrt(105.28^2 + 10.53^2) ≈ 105.8 m
    assert pytest.approx(res.sigma_height_m, abs=1.0) == 105.8

    # 68% confidence interval
    low_68, high_68 = res.confidence_interval_68_m
    assert low_68 < res.height_m < high_68
    assert pytest.approx(high_68 - low_68, abs=2.0) == 2 * res.sigma_height_m

    # 95% confidence interval
    low_95, high_95 = res.confidence_interval_95_m
    assert low_95 < low_68
    assert high_95 > high_68

    summary = res.summary()
    assert "Cloud Height: 1052.8 m ± 105.8 m" in summary


def test_propagate_height_uncertainty_low_clouds_in_range():
    """Verify that typical low cloud disparities (0.5 to 2.5 px) stay within 0 to 3 km."""
    delta_t_s = BAND_PAIRS_DELTA_T_S[("B02", "B04")]

    for d_px in [0.2, 0.5, 1.0, 1.5, 2.0, 2.5]:
        res = propagate_height_uncertainty(d_px, delta_t_s)
        assert 0.0 <= res.height_m <= 3000.0
        assert res.confidence_interval_68_m[0] >= 0.0
        assert res.confidence_interval_68_m[1] <= 3500.0


def test_measure_height_on_test_crop_window():
    """Test measuring height on rotated test crop window."""
    data, tags, _, _ = read_crop("tests/data/test_crop.tif")
    rot_deg = scan_rotation_angle(scan_direction_phi(43.3))
    rotated = rotate_crop(data, rot_deg)

    b02 = rotated[0]
    b04 = rotated[2]

    # Interrogation window at center
    s_row, s_col, err = measure_window_disparity(
        b02,
        b04,
        center_row=32,
        center_col=32,
        window_size=32,
    )

    delta_t_s = BAND_PAIRS_DELTA_T_S[("B02", "B04")]
    result = propagate_height_uncertainty(abs(s_row), delta_t_s)

    # Must be within 0 to 3000 m for low maritime cloud
    assert 0.0 <= result.height_m <= 3000.0
    assert result.sigma_height_m > 0.0
