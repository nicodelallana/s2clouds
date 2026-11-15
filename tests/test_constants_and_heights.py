"""Tests for constants and height_from_disparity equation (ec. 6 of Krauß 2021)."""

import numpy as np
import pytest

from s2clouds.constants import (
    BAND_PAIRS_DELTA_T_S,
    DELTA_T_B02_S,
    DELTA_T_B03_S,
    DELTA_T_B04_S,
    DELTA_T_B08_S,
    ORBIT_ALTITUDE_M,
    ORBIT_INCLINATION_DEG,
    ORBIT_VELOCITY_M_S,
    PIXEL_RESOLUTION_M,
)
from s2clouds.heights import height_from_disparity


def test_sentinel2_constants_values():
    """Verify nominal physical constants against Krauß (2021)."""
    assert ORBIT_ALTITUDE_M == 786_000.0
    assert ORBIT_VELOCITY_M_S == 7_429.0
    assert PIXEL_RESOLUTION_M == 10.0
    assert ORBIT_INCLINATION_DEG == 98.62

    # Krauß 2021 Table 1 delays relative to B02
    assert DELTA_T_B02_S == 0.000
    assert DELTA_T_B08_S == 0.264
    assert DELTA_T_B03_S == 0.527
    assert DELTA_T_B04_S == 1.005

    # Band pair delays
    assert BAND_PAIRS_DELTA_T_S[("B02", "B04")] == 1.005
    assert BAND_PAIRS_DELTA_T_S[("B02", "B03")] == 0.527
    assert pytest.approx(BAND_PAIRS_DELTA_T_S[("B03", "B04")], abs=1e-3) == 0.478


def test_height_from_disparity_b02_b04():
    """Test ec. 6: 1 px disparity with dt=1.005 s gives ~1053 m (Krauß 2021)."""
    delta_t_s = BAND_PAIRS_DELTA_T_S[("B02", "B04")]
    disparity_px = 1.0

    height_m = height_from_disparity(disparity_px, delta_t_s)

    # 10 * 786000 / (7429 * 1.005) = 7860000 / 7466.145 = 1052.7523... m
    assert pytest.approx(height_m, abs=1.0) == 1053.0
    assert round(height_m) == 1053


def test_height_from_disparity_b02_b03():
    """Test ec. 6: 1 px disparity with dt=0.527 s gives ~2008 m (Krauß 2021)."""
    delta_t_s = BAND_PAIRS_DELTA_T_S[("B02", "B03")]
    disparity_px = 1.0

    height_m = height_from_disparity(disparity_px, delta_t_s)

    # 10 * 786000 / (7429 * 0.527) = 7860000 / 3915.083 = 2007.62... m
    assert pytest.approx(height_m, abs=1.0) == 2008.0
    assert round(height_m) == 2008


def test_height_from_disparity_b03_b04():
    """Test ec. 6: 1 px disparity with dt=0.478 s gives ~2213 m (Krauß 2021)."""
    delta_t_s = BAND_PAIRS_DELTA_T_S[("B03", "B04")]
    disparity_px = 1.0

    height_m = height_from_disparity(disparity_px, delta_t_s)

    # 10 * 786000 / (7429 * 0.478) = 7860000 / 3551.062 = 2213.42... m
    assert pytest.approx(height_m, abs=1.0) == 2213.0
    assert round(height_m) == 2213


def test_height_from_disparity_absolute_value():
    """Test that parity reversal between detectors is handled by absolute value."""
    delta_t_s = 1.005
    height_positive = height_from_disparity(2.5, delta_t_s)
    height_negative = height_from_disparity(-2.5, delta_t_s)

    assert height_positive == height_negative
    assert height_positive > 0


def test_height_from_disparity_numpy_array():
    """Test that height_from_disparity operates element-wise on numpy arrays."""
    delta_t_s = 1.005
    disparities = np.array([0.0, 1.0, 2.0, -1.5])

    heights = height_from_disparity(disparities, delta_t_s)

    assert isinstance(heights, np.ndarray)
    assert heights.shape == (4,)
    assert heights[0] == 0.0
    assert pytest.approx(heights[1], abs=1.0) == 1053.0
    assert pytest.approx(heights[2], abs=1.0) == 2106.0


def test_height_from_disparity_invalid_delta_t():
    """Test error handling when delta_t_s is <= 0."""
    with pytest.raises(ValueError, match="positive and non-zero"):
        height_from_disparity(1.0, 0.0)

    with pytest.raises(ValueError, match="positive and non-zero"):
        height_from_disparity(1.0, -1.0)
