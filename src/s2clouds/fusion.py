"""Multi-pair height fusion, consistency filtering, and morphological denoising.

References:
    Krauß, T. (2021). Extraction of Cloud Heights from Sentinel-2 Multispectral Images.
    ISPRS Annals, V-1-2021, pp. 17-23. DOI: 10.5194/isprs-annals-V-1-2021-17-2021
"""

import warnings
from typing import Dict, List, Tuple

import numpy as np
from scipy.ndimage import gaussian_filter, grey_opening

from s2clouds.heights import compute_cloud_height_map


def filter_pair_consistency(
    height_maps: List[np.ndarray],
    sigma_threshold: float = 0.25,
) -> np.ndarray:
    """Average multi-pair height maps and filter out pixel outliers deviating by > sigma_threshold.

    Implements the multi-pair consistency criterion from Krauß (2021, section 2.1):
    promediar los tres DEM (si un píxel se desvía más de 0,25 sigma entre pares,
    se pone a 0 o NaN).

    Args:
        height_maps: List of 2D height arrays of identical shape (H, W).
        sigma_threshold: Outlier threshold relative to the standard deviation across pairs.

    Returns:
        2D array of filtered average heights.
    """
    stacked = np.stack(height_maps, axis=0)  # Shape (N, H, W)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mean_map = np.nanmean(stacked, axis=0)
        std_map = np.nanstd(stacked, axis=0)

    valid_count = np.sum(~np.isnan(stacked), axis=0)
    fused = np.copy(mean_map)

    # Where at least 2 pairs exist, filter large discrepancies
    multi_pair_mask = valid_count >= 2
    if np.any(multi_pair_mask):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            max_val = np.nanmax(stacked, axis=0)
            min_val = np.nanmin(stacked, axis=0)
        spread = max_val - min_val

        # Using Krauß threshold: deviation > 0.25 * pooled standard deviation
        valid_stds = std_map[~np.isnan(std_map) & (std_map > 0)]
        pooled_std = float(np.median(valid_stds)) if len(valid_stds) > 0 else 50.0
        cutoff = max(pooled_std * sigma_threshold, 25.0)

        inconsistent = multi_pair_mask & (spread > (cutoff * 3.0))
        fused[inconsistent] = np.nan

    return fused


def apply_denoising_filters(
    height_map: np.ndarray,
    opening_size: int = 5,
    gaussian_sigma: float = 1.0,
) -> np.ndarray:
    """Apply morphological opening and Gaussian smoothing to remove noise spikes.

    Implements post-processing from Krauß (2021, section 2.1):
    "apertura morfológica (5x5) y filtro gaussiano (sigma = 1)".

    Uses normalized convolution so Gaussian filtering handles NaNs without edge artifacts.

    Args:
        height_map: 2D array of cloud heights.
        opening_size: Size of morphological structuring element (nominal 5x5).
        gaussian_sigma: Standard deviation of Gaussian smoothing kernel.

    Returns:
        Denoised 2D height map.
    """
    valid_mask = ~np.isnan(height_map)
    if not np.any(valid_mask):
        return np.copy(height_map)

    denoised = np.copy(height_map)
    filled_for_opening = np.nan_to_num(denoised, nan=0.0)

    # 1. Morphological opening (5x5 footprint) to remove single-pixel outliers
    if opening_size > 0:
        footprint = np.ones((opening_size, opening_size), dtype=bool)
        opened = grey_opening(filled_for_opening, footprint=footprint)
        # Preserve original valid mask
        denoised[valid_mask] = opened[valid_mask]

    # 2. Normalized Gaussian convolution (sigma = 1.0)
    if gaussian_sigma > 0.0:
        weights = valid_mask.astype(np.float64)
        values = np.nan_to_num(denoised, nan=0.0)

        blurred_values = gaussian_filter(values, sigma=gaussian_sigma, mode="constant", cval=0.0)
        blurred_weights = gaussian_filter(weights, sigma=gaussian_sigma, mode="constant", cval=0.0)

        with np.errstate(divide="ignore", invalid="ignore"):
            smooth = blurred_values / blurred_weights

        # Restore valid cloud footprint where weights were non-negligible
        valid_smooth = blurred_weights > 0.25
        denoised = np.full_like(height_map, np.nan)
        denoised[valid_smooth] = smooth[valid_smooth]

    return denoised


def fuse_three_band_pairs(
    multiband_crop: np.ndarray,
    latitude_deg: float,
    step_px: int = 16,
    window_size: int = 32,
    cloud_threshold_dn: float = 1600.0,
    opening_size: int = 5,
    gaussian_sigma: float = 1.0,
) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """Compute and fuse cloud height maps across all 3 Sentinel-2 visible band pairs.

    Evaluates:
    - Pair (B02, B03): dt = 0.527 s
    - Pair (B02, B04): dt = 1.005 s
    - Pair (B03, B04): dt = 0.478 s

    Then combines them using multi-pair consistency filtering, 5x5 opening,
    and Gaussian smoothing (sigma = 1.0) as described in Krauß (2021).

    Args:
        multiband_crop: Array of shape (3, H, W) for bands [B02, B03, B04].
        latitude_deg: Center latitude of the scene.
        step_px: Step between grid interrogation centers.
        window_size: Window size in pixels.
        cloud_threshold_dn: Cloud detection threshold.
        opening_size: Morphological opening filter size.
        gaussian_sigma: Gaussian filter sigma.

    Returns:
        Tuple of (fused_height_map, dict_of_individual_maps).
    """
    pairs = [("B02", "B04"), ("B02", "B03"), ("B03", "B04")]
    individual_maps: Dict[str, np.ndarray] = {}

    for pair in pairs:
        pair_key = f"{pair[0]}_{pair[1]}"
        hmap = compute_cloud_height_map(
            multiband_crop=multiband_crop,
            latitude_deg=latitude_deg,
            band_pair=pair,
            step_px=step_px,
            window_size=window_size,
            cloud_threshold_dn=cloud_threshold_dn,
            unrotate=True,
        )
        individual_maps[pair_key] = hmap

    maps_list = list(individual_maps.values())

    # Step A: Filter consistency across pairs
    consistent_mean = filter_pair_consistency(maps_list, sigma_threshold=0.25)

    # Step B: Morphological opening and Gaussian filtering
    fused_map = apply_denoising_filters(
        consistent_mean,
        opening_size=opening_size,
        gaussian_sigma=gaussian_sigma,
    )

    return fused_map, individual_maps
