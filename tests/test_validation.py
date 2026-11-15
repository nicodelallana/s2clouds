"""Tests for cloud shadow geometry and validation (ec. 7-8 of Krauß 2021)."""

import math

import pytest

from s2clouds.validation import (
    ShadowValidationResult,
    cloud_height_from_shadow,
    shadow_displacement_vector,
    solar_zenith_from_elevation,
    validate_parallax_with_shadow,
)


def test_solar_zenith_from_elevation():
    """Verify solar zenith angle derivation."""
    assert solar_zenith_from_elevation(90.0) == 0.0
    assert solar_zenith_from_elevation(0.0) == 90.0
    assert pytest.approx(solar_zenith_from_elevation(53.32), abs=0.01) == 36.68

    with pytest.raises(ValueError):
        solar_zenith_from_elevation(-5.0)
    with pytest.raises(ValueError):
        solar_zenith_from_elevation(95.0)


def test_cloud_height_from_shadow_flat_terrain():
    """Verify ec. 7: tan(s_z) = d / h_s on flat terrain (H_s = H_c)."""
    # For sun zenith = 45 deg, tan(45) = 1.0 -> h = d
    h = cloud_height_from_shadow(shadow_distance_m=1000.0, sun_zenith_deg=45.0)
    assert pytest.approx(h, abs=1e-3) == 1000.0

    # Scene value: d = 144.2 m, s_z = 36.68 deg -> h ≈ 193.6 m
    h_scene = cloud_height_from_shadow(shadow_distance_m=144.2, sun_zenith_deg=36.68)
    assert pytest.approx(h_scene, abs=0.5) == 193.6


def test_cloud_height_from_shadow_with_topography():
    """Verify ec. 8: h_c = d / tan(s_z) + H_s - H_c with DEM elevation difference."""
    # Shadow falls on a hill at 50 m, cloud is over sea level (0 m)
    h_c = cloud_height_from_shadow(
        shadow_distance_m=1000.0,
        sun_zenith_deg=45.0,
        terrain_elevation_shadow_m=50.0,
        terrain_elevation_cloud_m=0.0,
    )
    assert pytest.approx(h_c, abs=1e-3) == 1050.0


def test_shadow_displacement_vector():
    """Verify anti-solar shadow casting vector."""
    height_m = 193.6
    sun_zenith = 36.68
    sun_azimuth = 154.5  # Sun in SSE -> Shadow in NNW

    delta_row_px, delta_col_px = shadow_displacement_vector(
        height_m=height_m,
        sun_zenith_deg=sun_zenith,
        sun_azimuth_deg=sun_azimuth,
        pixel_resolution_m=10.0,
    )

    # Shadow should be north (negative row) and west (negative col)
    assert delta_row_px < 0.0
    assert delta_col_px < 0.0

    total_dist_px = math.hypot(delta_row_px, delta_col_px)
    assert pytest.approx(total_dist_px, abs=0.5) == 14.42


def test_validate_parallax_with_shadow_real_scene():
    """Verify validation comparison between parallax and shadow."""
    parallax_h = 189.5
    parallax_sigma = 105.8
    shadow_dist = 144.2
    sun_zenith = 36.68

    val = validate_parallax_with_shadow(
        parallax_height_m=parallax_h,
        parallax_sigma_m=parallax_sigma,
        shadow_distance_m=shadow_dist,
        sun_zenith_deg=sun_zenith,
    )

    assert isinstance(val, ShadowValidationResult)
    assert pytest.approx(val.shadow_height_m, abs=0.5) == 193.6
    assert pytest.approx(val.absolute_difference_m, abs=0.5) == 4.1
    assert val.within_uncertainty is True
    assert val.within_literature_tolerance is True
    assert "Difference (P-S): -4.1 m" in val.summary()
