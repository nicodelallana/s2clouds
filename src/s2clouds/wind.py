"""Separation of cloud advection (wind) and orbital parallax.

References:
    Krauß, T. (2021). Extraction of Cloud Heights from Sentinel-2 Multispectral Images.
    ISPRS Annals, V-1-2021, pp. 17-23. DOI: 10.5194/isprs-annals-V-1-2021-17-2021
"""

from typing import Tuple

from s2clouds.constants import PIXEL_RESOLUTION_M
from s2clouds.heights import height_from_disparity


def estimate_cross_track_wind_velocity(
    shift_cross_track_px: float,
    delta_t_s: float,
    pixel_resolution_m: float = PIXEL_RESOLUTION_M,
) -> float:
    """Calculate the cross-track cloud wind component from horizontal displacement.

    Because orbital parallax occurs exclusively along the satellite flight track
    (when rotated), any cross-track shift between bands is caused by cloud advection (wind).

    Formula:
        v_cross = (shift_cross_track_px * rho) / dt

    Args:
        shift_cross_track_px: Measured displacement perpendicular to flight track in pixels.
        delta_t_s: Inter-band time delay in seconds.
        pixel_resolution_m: Spatial resolution in meters per pixel.

    Returns:
        Cross-track cloud speed in meters per second (m/s).
    """
    if delta_t_s <= 0.0:
        raise ValueError("delta_t_s must be positive and non-zero")
    return (shift_cross_track_px * pixel_resolution_m) / delta_t_s


def correct_height_for_wind(
    total_along_track_disparity_px: float,
    wind_along_track_m_s: float,
    delta_t_s: float,
    pixel_resolution_m: float = PIXEL_RESOLUTION_M,
) -> Tuple[float, float, float]:
    """Correct cloud height for along-track cloud advection (wind).

    Krauß (2021) observes that along-track cloud motion mixes with parallax:
        d_total = d_parallax + d_wind
        d_wind = (v_wind_along * dt) / rho

    Therefore, knowing the along-track wind speed (e.g. from atmospheric sounding or shadows):
        d_parallax = d_total - d_wind

    Args:
        total_along_track_disparity_px: Measured total inter-band shift along flight track.
        wind_along_track_m_s: Along-track wind velocity component (m/s).
        delta_t_s: Inter-band time delay in seconds.
        pixel_resolution_m: Pixel spatial resolution in meters.

    Returns:
        Tuple of (uncorrected_height_m, corrected_height_m, height_difference_m).
    """
    if delta_t_s <= 0.0:
        raise ValueError("delta_t_s must be positive and non-zero")

    wind_displacement_px = (wind_along_track_m_s * delta_t_s) / pixel_resolution_m
    corrected_disparity_px = total_along_track_disparity_px - wind_displacement_px

    h_uncorrected = float(height_from_disparity(abs(total_along_track_disparity_px), delta_t_s))
    h_corrected = float(height_from_disparity(abs(corrected_disparity_px), delta_t_s))
    diff_m = h_corrected - h_uncorrected

    return h_uncorrected, h_corrected, diff_m


def correct_height_using_shadow_disparity(
    cloud_along_track_shift_px: float,
    shadow_along_track_shift_px: float,
    delta_t_s: float,
) -> Tuple[float, float, float]:
    """Correct cloud parallax using the inter-band shift of the cloud's ground shadow.

    Because the shadow is projected on the ground (elevation h = 0), it experiences zero
    orbital parallax. Any inter-band shift observed on the shadow is due exclusively
    to cloud movement (wind advection).

    Parallax subtraction:
        d_parallax = d_cloud - d_shadow

    Args:
        cloud_along_track_shift_px: Inter-band shift measured on cloud top.
        shadow_along_track_shift_px: Inter-band shift measured on cloud shadow.
        delta_t_s: Inter-band time delay in seconds.

    Returns:
        Tuple of (uncorrected_height_m, corrected_height_m, height_difference_m).
    """
    pure_parallax_px = cloud_along_track_shift_px - shadow_along_track_shift_px

    h_uncorrected = float(height_from_disparity(abs(cloud_along_track_shift_px), delta_t_s))
    h_corrected = float(height_from_disparity(abs(pure_parallax_px), delta_t_s))
    diff_m = h_corrected - h_uncorrected

    return h_uncorrected, h_corrected, diff_m
