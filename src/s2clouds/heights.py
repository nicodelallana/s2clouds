"""Conversion between inter-band disparity and cloud height above ground.

References:
    Krauß, T. (2021). Extraction of Cloud Heights from Sentinel-2 Multispectral Images.
    ISPRS Annals, V-1-2021, pp. 17-23. DOI: 10.5194/isprs-annals-V-1-2021-17-2021
"""

from typing import Union

import numpy as np

from s2clouds.constants import (
    ORBIT_ALTITUDE_M,
    ORBIT_VELOCITY_M_S,
    PIXEL_RESOLUTION_M,
)


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
