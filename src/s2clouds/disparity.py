"""Subpixel disparity estimation between Sentinel-2 bands using phase cross-correlation.

References:
    Krauß, T. (2021). Extraction of Cloud Heights from Sentinel-2 Multispectral Images.
    ISPRS Annals, V-1-2021, pp. 17-23. DOI: 10.5194/isprs-annals-V-1-2021-17-2021
"""

from typing import Tuple

import numpy as np
from scipy.signal.windows import tukey
from skimage.registration import phase_cross_correlation


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

    # Convention: shift required to move ref to target is -shifts
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
