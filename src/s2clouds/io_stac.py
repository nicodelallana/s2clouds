"""STAC search and Cloud-Optimized GeoTIFF (COG) windowed extraction for Sentinel-2."""

from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.transform import Affine
from rasterio.windows import from_bounds

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

from pystac import Item
from pystac_client import Client

DEFAULT_STAC_URL = "https://earth-search.aws.element84.com/v1"
DEFAULT_COLLECTION = "sentinel-2-l2a"
BAND_ASSET_MAP = {
    "B02": "blue",
    "B03": "green",
    "B04": "red",
    "blue": "blue",
    "green": "green",
    "red": "red",
}


def load_scene_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load scene parameters from a TOML configuration file.

    Args:
        config_path: Path to .toml config file.

    Returns:
        Dictionary containing scene and ROI configuration.
    """
    path = Path(config_path)
    with open(path, "rb") as f:
        config = tomllib.load(f)
    return config


def get_stac_item(
    item_id: str,
    collection: str = DEFAULT_COLLECTION,
    stac_url: str = DEFAULT_STAC_URL,
) -> Item:
    """Retrieve a specific STAC Item by ID.

    Args:
        item_id: Unique STAC item identifier.
        collection: STAC collection name.
        stac_url: STAC API root endpoint.

    Returns:
        pystac.Item object.
    """
    client = Client.open(stac_url)
    search = client.search(collections=[collection], ids=[item_id])
    items = list(search.items())
    if not items:
        raise ValueError(f"Item '{item_id}' not found in collection '{collection}'")
    return items[0]


def extract_solar_angles(item: Item) -> Tuple[float, float]:
    """Extract sun zenith and azimuth angles from STAC Item metadata.

    Args:
        item: STAC Item.

    Returns:
        Tuple of (sun_zenith_deg, sun_azimuth_deg).
    """
    props = item.properties
    sun_azimuth = float(props.get("view:sun_azimuth", 0.0))
    sun_elevation = float(props.get("view:sun_elevation", 0.0))
    sun_zenith = 90.0 - sun_elevation
    return sun_zenith, sun_azimuth


def crop_scene_bands(
    item: Item,
    bands: List[str],
    bbox_wgs84: Tuple[float, float, float, float],
    output_path: Union[str, Path],
) -> Path:
    """Download and crop Sentinel-2 bands from remote COGs using windowed reads.

    Args:
        item: STAC item representing the Sentinel-2 scene.
        bands: List of band identifiers, e.g. ["B02", "B03", "B04"].
        bbox_wgs84: Bounding box in EPSG:4326 (min_lon, min_lat, max_lon, max_lat).
        output_path: Target path for the output multi-band GeoTIFF.

    Returns:
        Path to the saved GeoTIFF file.
    """
    target_path = Path(output_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    min_lon, min_lat, max_lon, max_lat = bbox_wgs84

    # Determine asset keys
    asset_keys = [BAND_ASSET_MAP.get(b, b) for b in bands]

    # Open first band to get coordinate reference system and calculate window
    first_href = item.assets[asset_keys[0]].href
    with rasterio.open(first_href) as ref_ds:
        crs = ref_ds.crs
        # Project bbox to raster CRS if needed
        from rasterio.warp import transform_bounds

        if crs != CRS.from_epsg(4326):
            left, bottom, right, top = transform_bounds(
                CRS.from_epsg(4326),
                crs,
                min_lon,
                min_lat,
                max_lon,
                max_lat,
            )
        else:
            left, bottom, right, top = min_lon, min_lat, max_lon, max_lat

        window = from_bounds(left, bottom, right, top, transform=ref_ds.transform)
        # Round window to integer pixel offsets and size
        window = window.round_offsets().round_lengths()
        win_transform = rasterio.windows.transform(window, ref_ds.transform)
        height = int(window.height)
        width = int(window.width)

    # Read each band inside the window
    data_arrays: List[np.ndarray] = []
    for asset_key in asset_keys:
        if asset_key not in item.assets:
            raise KeyError(f"Asset '{asset_key}' not found in item '{item.id}'")
        href = item.assets[asset_key].href
        with rasterio.open(href) as ds:
            band_data = ds.read(1, window=window)
            data_arrays.append(band_data)

    stacked_data = np.stack(data_arrays, axis=0)

    # Extract metadata tags
    sun_zenith, sun_azimuth = extract_solar_angles(item)
    meta = {
        "driver": "GTiff",
        "dtype": stacked_data.dtype,
        "count": len(bands),
        "height": height,
        "width": width,
        "crs": crs,
        "transform": win_transform,
        "compress": "deflate",
    }

    with rasterio.open(target_path, "w", **meta) as dst:
        dst.write(stacked_data)
        for i, band_name in enumerate(bands, start=1):
            dst.set_band_description(i, band_name)
        dst.update_tags(
            item_id=item.id,
            datetime=str(item.datetime),
            sun_zenith_deg=str(sun_zenith),
            sun_azimuth_deg=str(sun_azimuth),
            cloud_cover=str(item.properties.get("eo:cloud_cover", "")),
        )

    return target_path


def read_crop(
    crop_path: Union[str, Path],
) -> Tuple[np.ndarray, Dict[str, Any], Affine, CRS]:
    """Read cropped multi-band GeoTIFF and its spatial metadata.

    Args:
        crop_path: Path to GeoTIFF file.

    Returns:
        Tuple of (array of shape [bands, rows, cols], tags_dict, Affine transform, CRS).
    """
    path = Path(crop_path)
    if not path.is_file():
        raise FileNotFoundError(f"Crop file '{path}' does not exist")

    with rasterio.open(path) as ds:
        data = ds.read()
        tags = ds.tags()
        transform = ds.transform
        crs = ds.crs
        descriptions = ds.descriptions

    tags["band_descriptions"] = list(descriptions)
    return data, tags, transform, crs
