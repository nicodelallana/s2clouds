"""Tests for multi-pair height fusion and denoising (Krauß 2021)."""

from pathlib import Path

import numpy as np

from s2clouds.fusion import (
    apply_denoising_filters,
    filter_pair_consistency,
    fuse_three_band_pairs,
)
from s2clouds.io_stac import read_crop


def test_filter_pair_consistency_removes_outliers():
    """Verify consistency filtering across 3 pairs."""
    shape = (50, 50)
    # Pair 1: nominal height ~1000m
    p1 = np.full(shape, 1000.0, dtype=float)
    # Pair 2: slight noise ~1020m
    p2 = np.full(shape, 1020.0, dtype=float)
    # Pair 3: consistent ~990m, but has severe outlier spike at (25, 25)
    p3 = np.full(shape, 990.0, dtype=float)
    p3[25, 25] = 4500.0  # Massive outlier

    fused = filter_pair_consistency([p1, p2, p3], sigma_threshold=0.25)

    # In regular regions, fused should be near mean(1000, 1020, 990) = 1003.3
    assert abs(fused[10, 10] - 1003.3) < 5.0
    # At the outlier spike, pixel should be rejected (NaN)
    assert np.isnan(fused[25, 25])


def test_apply_denoising_filters_morphological_and_gaussian():
    """Verify 5x5 opening removes isolated spike and Gaussian smooths."""
    img = np.full((40, 40), 500.0, dtype=float)
    # Add isolated single pixel spike
    img[20, 20] = 3000.0

    denoised = apply_denoising_filters(img, opening_size=5, gaussian_sigma=1.0)

    # Spike should be eliminated by 5x5 opening
    assert abs(denoised[20, 20] - 500.0) < 50.0


def test_fuse_three_band_pairs_noise_reduction():
    """Verify that fused map has less spatial noise than individual pairs."""
    crop_path = Path("tests/data/test_crop.tif")
    data, tags, transform, crs = read_crop(crop_path)

    fused, individual = fuse_three_band_pairs(
        multiband_crop=data,
        latitude_deg=43.3,
        step_px=8,
        window_size=16,
        cloud_threshold_dn=1000.0,
    )

    assert set(individual.keys()) == {"B02_B04", "B02_B03", "B03_B04"}
    assert fused.shape == (64, 64)

    # Compare local noise (spatial gradient variance) on valid cloud region
    valid_common = (
        ~np.isnan(fused) & ~np.isnan(individual["B02_B04"]) & ~np.isnan(individual["B03_B04"])
    )

    assert np.sum(valid_common) > 20

    # Local variance / gradient in fused vs noisy short-delay pair (B03-B04)
    # Short-delay pair is inherently noisier due to smaller dt (0.478 s)
    std_fused = np.nanstd(fused[valid_common])
    std_noisy_pair = np.nanstd(individual["B03_B04"][valid_common])

    # Fused map should be smoother / less noisy than short-delay pair
    assert std_fused <= std_noisy_pair + 1e-3
