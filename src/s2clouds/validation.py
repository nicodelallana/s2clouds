"""Validation of cloud heights using cloud-shadow geometry and solar zenith angles.

References:
    Krauß, T. (2021). Extraction of Cloud Heights from Sentinel-2 Multispectral Images.
    ISPRS Annals, V-1-2021, pp. 17-23. DOI: 10.5194/isprs-annals-V-1-2021-17-2021
"""

import math
from dataclasses import dataclass
from typing import Tuple

from s2clouds.constants import PIXEL_RESOLUTION_M


@dataclass(frozen=True)
class ShadowValidationResult:
    """Comparison results between parallax height and shadow geometry."""

    parallax_height_m: float
    parallax_sigma_m: float
    shadow_height_m: float
    difference_m: float
    absolute_difference_m: float
    relative_difference_pct: float
    within_uncertainty: bool
    within_literature_tolerance: bool  # Krauß 2021 benchmark: ~150 m

    def summary(self) -> str:
        """Format comparison summary."""
        lines = [
            f"Parallax Height : {self.parallax_height_m:.1f} m ± {self.parallax_sigma_m:.1f} m",
            f"Shadow Height   : {self.shadow_height_m:.1f} m",
            f"Difference (P-S): {self.difference_m:+.1f} m ({self.relative_difference_pct:.1f}%)",
            f"Within 1-sigma uncertainty: {self.within_uncertainty}",
            f"Within literature tolerance (150 m): {self.within_literature_tolerance}",
        ]
        return "\n".join(lines)


def solar_zenith_from_elevation(sun_elevation_deg: float) -> float:
    """Calculate solar zenith angle from sun elevation angle.

    Args:
        sun_elevation_deg: Sun elevation angle in degrees above horizon.

    Returns:
        Solar zenith angle in degrees (90 - elevation).
    """
    if not (0.0 <= sun_elevation_deg <= 90.0):
        raise ValueError(f"Sun elevation must be between 0 and 90 degrees, got {sun_elevation_deg}")
    return 90.0 - sun_elevation_deg


def cloud_height_from_shadow(
    shadow_distance_m: float,
    sun_zenith_deg: float,
    terrain_elevation_shadow_m: float = 0.0,
    terrain_elevation_cloud_m: float = 0.0,
) -> float:
    """Calculate cloud height above ground from cloud-to-shadow ground distance.

    Implements equations 7 and 8 of Krauß (2021):
        tan(s_z) = d / h_s
        h_c = d / tan(s_z) + H_s - H_c

    where:
        d = horizontal distance between cloud and projected shadow on ground
        s_z = solar zenith angle
        h_s = cloud height above the shadow projection ground
        H_s = terrain elevation at shadow location
        H_c = terrain elevation under the cloud

    Args:
        shadow_distance_m: Measured distance between cloud and shadow in meters.
        sun_zenith_deg: Solar zenith angle s_z in degrees.
        terrain_elevation_shadow_m: Topographic elevation H_s at shadow location (m).
        terrain_elevation_cloud_m: Topographic elevation H_c under cloud (m).

    Returns:
        Cloud height h_c above ground in meters.

    Raises:
        ValueError: If sun zenith is not in (0, 90) degrees or distance is negative.
    """
    if shadow_distance_m < 0.0:
        raise ValueError("shadow_distance_m cannot be negative")

    if not (0.0 < sun_zenith_deg < 90.0):
        raise ValueError(
            f"sun_zenith_deg must be strictly between 0 and 90 degrees, got {sun_zenith_deg}"
        )

    sun_zenith_rad = math.radians(sun_zenith_deg)
    tan_s_z = math.tan(sun_zenith_rad)

    h_s = shadow_distance_m / tan_s_z
    h_c = h_s + terrain_elevation_shadow_m - terrain_elevation_cloud_m
    return h_c


def shadow_displacement_vector(
    height_m: float,
    sun_zenith_deg: float,
    sun_azimuth_deg: float,
    pixel_resolution_m: float = PIXEL_RESOLUTION_M,
) -> Tuple[float, float]:
    """Calculate the expected row and column pixel offset from cloud to shadow.

    Shadow is cast in the anti-solar direction (azimuth + 180 deg).

    Args:
        height_m: Cloud height above ground in meters.
        sun_zenith_deg: Solar zenith angle in degrees.
        sun_azimuth_deg: Solar azimuth angle in degrees clockwise from North.
        pixel_resolution_m: Spatial resolution in meters per pixel.

    Returns:
        Tuple of (delta_row_px, delta_col_px) from cloud to shadow.
        In standard image coordinates (row 0 is North, col 0 is West).
    """
    sun_zenith_rad = math.radians(sun_zenith_deg)
    ground_dist_m = height_m * math.tan(sun_zenith_rad)
    ground_dist_px = ground_dist_m / pixel_resolution_m

    # Anti-solar azimuth
    cast_azimuth_deg = (sun_azimuth_deg + 180.0) % 360.0
    cast_azimuth_rad = math.radians(cast_azimuth_deg)

    # In map/raster coordinates: North is negative row, East is positive col
    delta_row_px = -ground_dist_px * math.cos(cast_azimuth_rad)
    delta_col_px = ground_dist_px * math.sin(cast_azimuth_rad)

    return delta_row_px, delta_col_px


def validate_parallax_with_shadow(
    parallax_height_m: float,
    parallax_sigma_m: float,
    shadow_distance_m: float,
    sun_zenith_deg: float,
    terrain_elevation_shadow_m: float = 0.0,
    terrain_elevation_cloud_m: float = 0.0,
    literature_tolerance_m: float = 150.0,
) -> ShadowValidationResult:
    """Compare parallax-derived cloud height against shadow geometry calculation.

    Args:
        parallax_height_m: Height estimated from inter-band disparity.
        parallax_sigma_m: 1-sigma uncertainty of parallax height.
        shadow_distance_m: Distance between cloud and shadow in meters.
        sun_zenith_deg: Solar zenith angle in degrees.
        terrain_elevation_shadow_m: Terrain elevation at shadow.
        terrain_elevation_cloud_m: Terrain elevation under cloud.
        literature_tolerance_m: Acceptable error threshold from Krauß 2021 (150 m).

    Returns:
        ShadowValidationResult with comparative metrics.
    """
    shadow_height_m = cloud_height_from_shadow(
        shadow_distance_m=shadow_distance_m,
        sun_zenith_deg=sun_zenith_deg,
        terrain_elevation_shadow_m=terrain_elevation_shadow_m,
        terrain_elevation_cloud_m=terrain_elevation_cloud_m,
    )

    diff_m = parallax_height_m - shadow_height_m
    abs_diff_m = abs(diff_m)

    ref_denominator = shadow_height_m if shadow_height_m > 0 else 1.0
    rel_diff_pct = (abs_diff_m / ref_denominator) * 100.0

    within_unc = abs_diff_m <= parallax_sigma_m
    within_lit = abs_diff_m <= literature_tolerance_m

    return ShadowValidationResult(
        parallax_height_m=parallax_height_m,
        parallax_sigma_m=parallax_sigma_m,
        shadow_height_m=shadow_height_m,
        difference_m=diff_m,
        absolute_difference_m=abs_diff_m,
        relative_difference_pct=rel_diff_pct,
        within_uncertainty=within_unc,
        within_literature_tolerance=within_lit,
    )
