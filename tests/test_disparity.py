"""Tests for subpixel window disparity estimation."""

import numpy as np
import pytest
from scipy.ndimage import fourier_shift

from s2clouds.disparity import (
    estimate_window_disparity,
    extract_window,
    measure_window_disparity,
)
from s2clouds.io_stac import read_crop


def test_extract_window_shape_and_bounds():
    """Verify window extraction and boundary validation."""
    img = np.arange(10000, dtype=float).reshape(100, 100)
    win = extract_window(img, center_row=50, center_col=50, window_size=32)

    assert win.shape == (32, 32)
    assert win[16, 16] == img[50, 50]

    with pytest.raises(ValueError, match="extends outside image bounds"):
        extract_window(img, center_row=10, center_col=50, window_size=32)


def test_estimate_window_disparity_synthetic_subpixel():
    """Test phase cross-correlation subpixel accuracy on synthetic data with known shift."""
    y, x = np.mgrid[-32:32, -32:32]
    base_window = 50.0 * np.exp(-(x**2 + y**2) / (2 * 10.0**2))

    true_shift_row = 1.45
    true_shift_col = -0.72

    # Shift using Fourier phase ramp
    fft_base = np.fft.fftn(base_window)
    fft_shifted = fourier_shift(fft_base, [true_shift_row, true_shift_col])
    shifted_window = np.fft.ifftn(fft_shifted).real

    shift_row, shift_col, error = estimate_window_disparity(
        base_window,
        shifted_window,
        upsample_factor=100,
        apodize=False,
    )

    assert pytest.approx(shift_row, abs=0.03) == true_shift_row
    assert pytest.approx(shift_col, abs=0.03) == true_shift_col
    assert error < 0.05


def test_window_disparity_stability_under_window_jitter():
    """Test stability when window center is jittered by +/- 1 to 3 pixels."""
    crop_data, _, _, _ = read_crop("tests/data/test_crop.tif")
    b02 = crop_data[0]
    b04 = crop_data[2]

    # Measure at center (32, 32) and small perturbations
    disparities = []
    for d_row in [-2, 0, 2]:
        for d_col in [-2, 0, 2]:
            s_row, s_col, err = measure_window_disparity(
                b02,
                b04,
                center_row=32 + d_row,
                center_col=32 + d_col,
                window_size=32,
                upsample_factor=100,
            )
            disparities.append(abs(s_row))

    disparities = np.array(disparities)
    # Standard deviation across jittered windows should be small (< 0.25 px)
    assert np.std(disparities) < 0.25
