"""Tests for STAC IO and raster loading."""

from pathlib import Path
from unittest.mock import MagicMock

from s2clouds.cli import create_parser
from s2clouds.io_stac import (
    extract_solar_angles,
    load_scene_config,
    read_crop,
)


def test_load_scene_config():
    """Verify loading of example TOML configuration."""
    config_path = Path("examples/bilbao_clouds.toml")
    config = load_scene_config(config_path)

    assert "scene" in config
    assert config["scene"]["id"] == "S2B_30TWN_20230831_0_L2A"
    assert config["roi"]["bbox"] == [-3.15, 43.30, -3.00, 43.42]
    assert config["bands"]["names"] == ["B02", "B03", "B04"]


def test_read_crop():
    """Verify reading of test GeoTIFF crop."""
    crop_path = Path("tests/data/test_crop.tif")
    data, tags, transform, crs = read_crop(crop_path)

    assert data.ndim == 3
    assert data.shape[0] == 3  # 3 bands
    assert data.shape[1] == 64
    assert data.shape[2] == 64
    assert tags["item_id"] == "S2B_30TWN_20230831_0_L2A"
    assert "sun_zenith_deg" in tags
    assert "sun_azimuth_deg" in tags
    assert crs.to_epsg() == 32630


def test_extract_solar_angles():
    """Verify solar zenith and azimuth extraction from STAC Item."""
    mock_item = MagicMock()
    mock_item.properties = {
        "view:sun_azimuth": 154.5,
        "view:sun_elevation": 53.3,
    }

    sun_zenith, sun_azimuth = extract_solar_angles(mock_item)

    assert sun_azimuth == 154.5
    assert round(sun_zenith, 2) == 36.7


def test_cli_download_parser():
    """Verify CLI parser for download subcommand."""
    parser = create_parser()
    args = parser.parse_args(["download", "--config", "examples/bilbao_clouds.toml"])

    assert args.subcommand == "download"
    assert str(args.config) == "examples/bilbao_clouds.toml"
    assert str(args.output) == "data/crop.tif"
