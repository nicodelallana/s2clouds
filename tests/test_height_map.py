"""Tests for grid disparity measurement and full cloud height mapping."""

from pathlib import Path

import numpy as np

from s2clouds.cli import create_parser
from s2clouds.disparity import compute_disparity_grid, generate_cloud_mask
from s2clouds.heights import compute_cloud_height_map
from s2clouds.io_stac import read_crop


def test_generate_cloud_mask():
    """Verify cloud mask generation and morphological dilation."""
    b02 = np.array([[500, 2000], [400, 300]], dtype=float)
    mask = generate_cloud_mask(b02, threshold_dn=1500.0, dilation_radius=0)

    assert mask.shape == (2, 2)
    assert mask[0, 1] is np.True_ or mask[0, 1] == 1
    assert mask[0, 0] is np.False_ or mask[0, 0] == 0


def test_compute_disparity_grid():
    """Verify grid disparity calculation over interrogation grid."""
    ref = np.zeros((64, 64), dtype=float)
    target = np.zeros((64, 64), dtype=float)

    # Put a textured spot
    ref[20:44, 20:44] = 2000.0
    target[22:46, 20:44] = 2000.0  # Shifted by 2 pixels along rows

    mask = np.ones((64, 64), dtype=bool)

    disp_grid, err_grid, (r_coords, c_coords) = compute_disparity_grid(
        band_ref=ref,
        band_target=target,
        step_px=16,
        window_size=32,
        mask=mask,
        max_error=0.8,
    )

    assert disp_grid.shape == (len(r_coords), len(c_coords))
    assert not np.all(np.isnan(disp_grid))


def test_compute_cloud_height_map_on_crop():
    """Verify end-to-end height map calculation on test GeoTIFF crop."""
    crop_path = Path("tests/data/test_crop.tif")
    data, tags, transform, crs = read_crop(crop_path)

    hmap = compute_cloud_height_map(
        multiband_crop=data,
        latitude_deg=43.3,
        band_pair=("B02", "B04"),
        step_px=8,
        window_size=16,
        cloud_threshold_dn=1000.0,
    )

    assert hmap.shape == (64, 64)
    # Check that non-cloud pixels are NaN (no noise outside clouds)
    assert np.isnan(hmap).any()
    # Check that cloud pixels have realistic positive altitudes (< 3000 m)
    valid_pixels = hmap[~np.isnan(hmap)]
    assert len(valid_pixels) > 0
    assert (valid_pixels >= 0.0).all()
    assert (valid_pixels <= 3000.0).all()


def test_cli_heightmap_parser():
    """Verify CLI parser for heightmap subcommand."""
    parser = create_parser()
    args = parser.parse_args(["heightmap", "-i", "data/crop.tif", "--pair", "B02-B04"])

    assert args.subcommand == "heightmap"
    assert str(args.input) == "data/crop.tif"
    assert args.pair == "B02-B04"
    assert args.step == 16
