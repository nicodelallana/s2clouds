"""Orbital geometry, flight track angle, and image rotation.

References:
    Krauß, T. (2021). Extraction of Cloud Heights from Sentinel-2 Multispectral Images.
    ISPRS Annals, V-1-2021, pp. 17-23. DOI: 10.5194/isprs-annals-V-1-2021-17-2021
"""

import math

import numpy as np
from scipy.ndimage import rotate

from s2clouds.constants import ORBIT_INCLINATION_DEG


def scan_direction_phi(
    latitude_deg: float,
    inclination_deg: float = ORBIT_INCLINATION_DEG,
) -> float:
    """Calculate the scanning flight direction angle phi relative to the meridian.

    Implements equation 4 of Krauß (2021):
        cos(phi) = cos(alpha) / cos(lambda)

    where alpha is the orbital inclination (98.62 deg for Sentinel-2)
    and lambda is the latitude of the scene.

    Args:
        latitude_deg: Latitude of the scene center in decimal degrees (North positive).
        inclination_deg: Satellite orbital inclination in degrees (nominal 98.62 deg).

    Returns:
        Flight direction angle phi in degrees.

    Raises:
        ValueError: If the scene latitude exceeds the orbital inclination bounds.
    """
    alpha_rad = math.radians(inclination_deg)
    lambda_rad = math.radians(latitude_deg)

    cos_alpha = math.cos(alpha_rad)
    cos_lambda = math.cos(lambda_rad)

    if abs(cos_lambda) < 1e-6:
        raise ValueError("Latitude too close to pole")

    ratio = cos_alpha / cos_lambda
    if abs(ratio) > 1.0:
        raise ValueError(f"Orbit does not reach latitude {latitude_deg} deg (ratio={ratio:.4f})")

    phi_rad = math.acos(ratio)
    phi_deg = math.degrees(phi_rad)
    return phi_deg


def scan_rotation_angle(phi_deg: float) -> float:
    """Calculate the rotation angle required to align flight direction with image vertical.

    Following Krauß (2021, section 2.1):
        theta_rot = 90 deg - phi

    Rotating the image by theta_rot aligns the satellite flight track along image columns,
    so parallax disparity occurs purely in the vertical direction.

    Args:
        phi_deg: Flight direction angle phi in degrees.

    Returns:
        Rotation angle in degrees.
    """
    rotation_deg = 90.0 - phi_deg
    return rotation_deg


def satellite_ground_track_heading(
    latitude_deg: float,
    inclination_deg: float = ORBIT_INCLINATION_DEG,
) -> float:
    """Calculate the satellite ground track heading azimuth from True North.

    Contrasts Krauß phi angle with the standard navigation heading convention
    (0 = North, 90 = East, 180 = South, 270 = West).
    For descending passes in the Cantabrian Sea (~43.3 N), heading is ~194.7 deg.

    Args:
        latitude_deg: Scene latitude in degrees.
        inclination_deg: Orbit inclination in degrees.

    Returns:
        Satellite flight track azimuth in degrees clockwise from North.
    """
    phi_deg = scan_direction_phi(latitude_deg, inclination_deg)
    heading_deg = 90.0 + phi_deg
    return heading_deg


def rotate_crop(
    image: np.ndarray,
    angle_deg: float,
    reshape: bool = False,
    order: int = 1,
    cval: float = 0.0,
) -> np.ndarray:
    """Rotate an image array by the specified angle in degrees.

    Args:
        image: 2D array (H, W) or 3D array (C, H, W).
        angle_deg: Rotation angle in degrees (counter-clockwise is positive).
        reshape: If True, output shape is adapted so the whole input is contained.
        order: Spline interpolation order (0=nearest, 1=bilinear, 3=bicubic).
        cval: Fill value for points outside boundaries.

    Returns:
        Rotated image array.
    """
    if image.ndim == 2:
        return rotate(
            image,
            angle_deg,
            reshape=reshape,
            order=order,
            mode="constant",
            cval=cval,
        )
    elif image.ndim == 3:
        # Multi-band raster (C, H, W) -> rotate axes (1, 2)
        return rotate(
            image,
            angle_deg,
            axes=(1, 2),
            reshape=reshape,
            order=order,
            mode="constant",
            cval=cval,
        )
    else:
        raise ValueError(f"Expected 2D or 3D array, got {image.ndim}D")


def unrotate_crop(
    image: np.ndarray,
    angle_deg: float,
    reshape: bool = False,
    order: int = 1,
    cval: float = 0.0,
) -> np.ndarray:
    """Undo the rotation by rotating back by -angle_deg.

    Args:
        image: 2D array (H, W) or 3D array (C, H, W).
        angle_deg: Original forward rotation angle in degrees.
        reshape: Whether to reshape the output.
        order: Spline interpolation order.
        cval: Fill value.

    Returns:
        Unrotated image array.
    """
    return rotate_crop(
        image,
        -angle_deg,
        reshape=reshape,
        order=order,
        cval=cval,
    )
