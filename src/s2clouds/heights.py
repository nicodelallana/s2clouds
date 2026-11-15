"""Conversion between inter-band disparity and cloud height above ground.

References:
    Krauß, T. (2021). Extraction of Cloud Heights from Sentinel-2 Multispectral Images.
    ISPRS Annals, V-1-2021, pp. 17-23. DOI: 10.5194/isprs-annals-V-1-2021-17-2021
    Binet, R., Bergsma, E., & Poulain, V. (2022). Accurate Sentinel-2 Inter-Band Time Delays.
    ISPRS Annals, V-1-2022, pp. 57-66. DOI: 10.5194/isprs-annals-V-1-2022-57-2022
"""

import math
from dataclasses import dataclass
from typing import Tuple, Union

import numpy as np

from s2clouds.constants import (
    ORBIT_ALTITUDE_M,
    ORBIT_VELOCITY_M_S,
    PIXEL_RESOLUTION_M,
)


@dataclass(frozen=True)
class CloudHeightResult:
    """Container for estimated cloud height and propagated uncertainty metrics."""

    height_m: float
    sigma_height_m: float
    disparity_px: float
    sigma_disparity_px: float
    delta_t_s: float
    confidence_interval_68_m: Tuple[float, float]
    confidence_interval_95_m: Tuple[float, float]

    def summary(self) -> str:
        """Format human-readable summary with uncertainty interval."""
        low_68, high_68 = self.confidence_interval_68_m
        low_95, high_95 = self.confidence_interval_95_m
        line1 = f"Cloud Height: {self.height_m:.1f} m ± {self.sigma_height_m:.1f} m"
        line2 = f"68% CI: [{low_68:.1f}, {high_68:.1f}] m"
        line3 = f"95% CI: [{low_95:.1f}, {high_95:.1f}] m"
        return f"{line1} | {line2} | {line3}"


def height_from_disparity(
    disparity_px: Union[float, np.ndarray],
    delta_t_s: float,
    pixel_resolution_m: float = PIXEL_RESOLUTION_M,
    orbit_altitude_m: float = ORBIT_ALTITUDE_M,
    orbit_velocity_m_s: float = ORBIT_VELOCITY_M_S,
) -> Union[float, np.ndarray]:
    """Calculate cloud height above ground from disparity between Sentinel-2 bands.

    Implements equation 6 of Krauß (2021):
        h = |d| * rho * h_o / (v_o * dt)

    The absolute value of disparity is used because band acquisition order
    reverses between odd and even detector modules.

    Args:
        disparity_px: Apparent disparity along the flight track in pixels.
        delta_t_s: Time delay between the two bands in seconds. Must be > 0.
        pixel_resolution_m: Spatial resolution of pixels in meters (nominal 10.0 m/px).
        orbit_altitude_m: Mean orbital altitude of the satellite in meters (nominal 786,000.0 m).
        orbit_velocity_m_s: Orbital flight velocity in meters per second (nominal 7,429.0 m/s).

    Returns:
        Height above ground in meters (same type as disparity_px, float or ndarray).

    Raises:
        ValueError: If delta_t_s is less than or equal to zero.
    """
    if delta_t_s <= 0:
        raise ValueError("delta_t_s must be positive and non-zero")

    abs_disparity_px = np.abs(disparity_px)
    numerator = abs_disparity_px * pixel_resolution_m * orbit_altitude_m
    denominator = orbit_velocity_m_s * delta_t_s
    height_m = numerator / denominator

    if isinstance(disparity_px, (int, float)):
        return float(height_m)
    return height_m


def propagate_height_uncertainty(
    disparity_px: float,
    delta_t_s: float,
    sigma_disparity_px: float = 0.1,
    relative_sigma_delta_t: float = 0.01,
    pixel_resolution_m: float = PIXEL_RESOLUTION_M,
    orbit_altitude_m: float = ORBIT_ALTITUDE_M,
    orbit_velocity_m_s: float = ORBIT_VELOCITY_M_S,
) -> CloudHeightResult:
    """Calculate cloud height and propagate analytical uncertainties.

    Assumes uncorrelated errors between phase correlation subpixel disparity (sigma_disparity_px)
    and nominal inter-band delay error (relative_sigma_delta_t from Binet et al. 2022).

    Uncertainty propagation formula:
        sigma_h = sqrt( (dh/d|d| * sigma_d)^2 + (dh/ddt * sigma_dt)^2 )
        where dh/d|d| = (rho * h_o) / (v_o * dt)
        and dh/ddt = - h / dt

    Args:
        disparity_px: Measured disparity along flight track in pixels.
        delta_t_s: Time delay between the bands in seconds.
        sigma_disparity_px: Subpixel disparity standard error in pixels (nominal ±0.1 px).
        relative_sigma_delta_t: Fractional time delay error (nominal ±0.01, i.e. 1%).
        pixel_resolution_m: Spatial pixel resolution in meters.
        orbit_altitude_m: Orbital altitude in meters.
        orbit_velocity_m_s: Orbital flight velocity in meters per second.

    Returns:
        CloudHeightResult instance with height, uncertainty, and confidence intervals.
    """
    height_m = float(
        height_from_disparity(
            disparity_px,
            delta_t_s,
            pixel_resolution_m=pixel_resolution_m,
            orbit_altitude_m=orbit_altitude_m,
            orbit_velocity_m_s=orbit_velocity_m_s,
        )
    )

    scale_factor = (pixel_resolution_m * orbit_altitude_m) / (orbit_velocity_m_s * delta_t_s)
    variance_from_disparity = (scale_factor * sigma_disparity_px) ** 2

    sigma_delta_t_s = relative_sigma_delta_t * delta_t_s
    variance_from_delta_t = (height_m * (sigma_delta_t_s / delta_t_s)) ** 2

    total_variance = variance_from_disparity + variance_from_delta_t
    sigma_height_m = math.sqrt(total_variance)

    # Confidence intervals (lower bound clipped at 0 meters)
    ci_68_low = max(0.0, height_m - sigma_height_m)
    ci_68_high = height_m + sigma_height_m

    ci_95_low = max(0.0, height_m - 1.96 * sigma_height_m)
    ci_95_high = height_m + 1.96 * sigma_height_m

    return CloudHeightResult(
        height_m=height_m,
        sigma_height_m=sigma_height_m,
        disparity_px=float(abs(disparity_px)),
        sigma_disparity_px=sigma_disparity_px,
        delta_t_s=delta_t_s,
        confidence_interval_68_m=(ci_68_low, ci_68_high),
        confidence_interval_95_m=(ci_95_low, ci_95_high),
    )
