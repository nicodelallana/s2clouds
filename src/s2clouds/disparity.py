"""Subpixel disparity estimation between Sentinel-2 bands using phase cross-correlation.

References:
    Krauß, T. (2021). Extraction of Cloud Heights from Sentinel-2 Multispectral Images.
    ISPRS Annals, V-1-2021, pp. 17-23. DOI: 10.5194/isprs-annals-V-1-2021-17-2021
"""

from typing import Optional, Tuple

import numpy as np
from scipy.ndimage import binary_dilation
from scipy.signal.windows import tukey
from skimage.registration import phase_cross_correlation


def generate_cloud_mask(
    band_blue: np.ndarray,
    band_green: Optional[np.ndarray] = None,
    band_red: Optional[np.ndarray] = None,
    threshold_dn: float = 1600.0,
    dilation_radius: int = 2,
) -> np.ndarray:
    """Generate a binary cloud mask based on visible band brightness thresholds.

    Clouds appear brightly in all visible bands. Masking non-cloud areas eliminates
    spurious correlation noise over ground or clear sea.

    Args:
        band_blue: 2D array of Blue band (B02).
        band_green: Optional 2D array of Green band (B03).
        band_red: Optional 2D array of Red band (B04).
        threshold_dn: Digital number reflectance threshold for cloud detection.
        dilation_radius: Morphological dilation iterations to include fuzzy cloud margins.

    Returns:
        Boolean 2D mask where True indicates cloud presence.
    """
    cloud_mask = band_blue > threshold_dn
    if band_green is not None:
        cloud_mask = cloud_mask & (band_green > (threshold_dn * 0.9))
    if band_red is not None:
        cloud_mask = cloud_mask & (band_red > (threshold_dn * 0.8))

    if dilation_radius > 0:
        struct = np.ones((3, 3), dtype=bool)
        cloud_mask = binary_dilation(cloud_mask, structure=struct, iterations=dilation_radius)

    return cloud_mask


def extract_window(
    image: np.ndarray,
    center_row: int,
    center_col: int,
    window_size: int = 64,
) -> np.ndarray:
    """Extract a square window centered at (center_row, center_col).

    Args:
        image: 2D array of shape (H, W).
        center_row: Row coordinate of window center.
        center_col: Column coordinate of window center.
        window_size: Length of each side of the square window (in pixels).

    Returns:
        Square 2D subarray of shape (window_size, window_size).

    Raises:
        ValueError: If window extends beyond image bounds.
    """
    half_size = window_size // 2
    row_start = center_row - half_size
    row_end = row_start + window_size
    col_start = center_col - half_size
    col_end = col_start + window_size

    height, width = image.shape
    if row_start < 0 or row_end > height or col_start < 0 or col_end > width:
        raise ValueError(
            f"Window [({row_start}:{row_end}), ({col_start}:{col_end})] "
            f"extends outside image bounds ({height}, {width})"
        )

    window = image[row_start:row_end, col_start:col_end]
    return window


def apply_apodization_window(window: np.ndarray, alpha: float = 0.2) -> np.ndarray:
    """Apply 2D Tukey tapering window to reduce Fourier edge artifacts.

    Args:
        window: 2D numpy array.
        alpha: Tukey taper parameter (0.0=rectangular, 1.0=Hann).

    Returns:
        Windowed array with edges tapered smoothly to zero.
    """
    rows, cols = window.shape
    w_row = tukey(rows, alpha=alpha)
    w_col = tukey(cols, alpha=alpha)
    w_2d = np.outer(w_row, w_col)
    return window * w_2d


def estimate_window_disparity(
    reference_window: np.ndarray,
    moving_window: np.ndarray,
    upsample_factor: int = 100,
    apodize: bool = True,
) -> Tuple[float, float, float]:
    """Estimate subpixel relative displacement between two image windows.

    Uses phase cross-correlation with discrete Fourier transform upsampling.

    Args:
        reference_window: 2D numpy array of reference band (e.g. B02).
        moving_window: 2D numpy array of second band (e.g. B04).
        upsample_factor: Subpixel precision factor (100 yields 0.01 px precision).
        apodize: If True, applies Tukey edge tapering to suppress border ringing.

    Returns:
        Tuple of (shift_row_px, shift_col_px, normalized_error).
        shift_row_px: displacement along rows (flight track direction when rotated).
        shift_col_px: displacement along columns (cross-track direction).
        normalized_error: translation-invariant normalized RMS error [0, 1].
    """
    ref_norm = reference_window.astype(np.float64)
    mov_norm = moving_window.astype(np.float64)

    # Remove DC bias
    ref_norm = ref_norm - np.mean(ref_norm)
    mov_norm = mov_norm - np.mean(mov_norm)

    if apodize:
        ref_norm = apply_apodization_window(ref_norm)
        mov_norm = apply_apodization_window(mov_norm)

    shifts, error, _ = phase_cross_correlation(
        ref_norm,
        mov_norm,
        upsample_factor=upsample_factor,
        normalization=None,
    )

    shift_row_px = float(-shifts[0])
    shift_col_px = float(-shifts[1])
    norm_error = float(error)

    return shift_row_px, shift_col_px, norm_error


def measure_window_disparity(
    band_ref: np.ndarray,
    band_target: np.ndarray,
    center_row: int,
    center_col: int,
    window_size: int = 64,
    upsample_factor: int = 100,
    apodize: bool = True,
) -> Tuple[float, float, float]:
    """Extract windows from two bands and estimate subpixel disparity.

    Args:
        band_ref: 2D array of reference band.
        band_target: 2D array of target band.
        center_row: Center row of interrogation window.
        center_col: Center col of interrogation window.
        window_size: Size of square window in pixels.
        upsample_factor: Subpixel upsampling precision.
        apodize: If True, applies Tukey window apodization.

    Returns:
        Tuple of (shift_row_px, shift_col_px, error).
    """
    win_ref = extract_window(band_ref, center_row, center_col, window_size)
    win_target = extract_window(band_target, center_row, center_col, window_size)
    return estimate_window_disparity(
        win_ref,
        win_target,
        upsample_factor=upsample_factor,
        apodize=apodize,
    )


def compute_disparity_grid(
    band_ref: np.ndarray,
    band_target: np.ndarray,
    step_px: int = 16,
    window_size: int = 32,
    mask: Optional[np.ndarray] = None,
    max_error: float = 0.50,
    upsample_factor: int = 50,
) -> Tuple[np.ndarray, np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    """Compute subpixel disparity across a regular grid of interrogation windows.

    Args:
        band_ref: 2D reference band (flight track aligned along rows).
        band_target: 2D target band.
        step_px: Distance in pixels between window centers.
        window_size: Size of square correlation window.
        mask: Optional boolean 2D cloud mask; points outside mask are set to NaN.
        max_error: Normalized RMS error threshold above which measurements are rejected.
        upsample_factor: Subpixel upsampling precision.

    Returns:
        Tuple of (disparity_map, error_map, (grid_rows, grid_cols)).
        disparity_map: 2D array of disparity values (absolute shift along rows).
        error_map: 2D array of correlation errors.
        (grid_rows, grid_cols): 1D coordinate vectors of grid centers.
    """
    height, width = band_ref.shape
    half_win = window_size // 2

    row_coords = np.arange(half_win, height - half_win, step_px)
    col_coords = np.arange(half_win, width - half_win, step_px)

    num_rows = len(row_coords)
    num_cols = len(col_coords)

    disparity_grid = np.full((num_rows, num_cols), np.nan, dtype=np.float32)
    error_grid = np.full((num_rows, num_cols), np.nan, dtype=np.float32)

    for i, r in enumerate(row_coords):
        for j, c in enumerate(col_coords):
            # Check mask at window center if mask is provided
            if mask is not None and not mask[r, c]:
                continue

            try:
                shift_row, shift_col, err = measure_window_disparity(
                    band_ref,
                    band_target,
                    center_row=r,
                    center_col=c,
                    window_size=window_size,
                    upsample_factor=upsample_factor,
                    apodize=True,
                )
            except ValueError:
                continue

            if err <= max_error:
                # Store absolute row disparity (along-track parallax)
                disparity_grid[i, j] = abs(shift_row)
                error_grid[i, j] = err

    return disparity_grid, error_grid, (row_coords, col_coords)
