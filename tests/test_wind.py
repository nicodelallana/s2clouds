"""Tests for cloud advection (wind) estimation and height correction."""

import pytest

from s2clouds.wind import (
    correct_height_for_wind,
    correct_height_using_shadow_disparity,
    estimate_cross_track_wind_velocity,
)


def test_estimate_cross_track_wind_velocity():
    """Verify cross-track wind speed: v = (dx * rho) / dt."""
    # 0.5 px cross-track shift with dt = 1.005s and rho = 10m/px
    # v = (0.5 * 10) / 1.005 = 5.0 / 1.005 = 4.975 m/s (~18 km/h)
    v_wind = estimate_cross_track_wind_velocity(
        shift_cross_track_px=0.5,
        delta_t_s=1.005,
    )
    assert pytest.approx(v_wind, abs=0.01) == 4.98


def test_correct_height_for_wind_krauss_ten_ms_benchmark():
    """Verify Krauß (2021) observation: 10 m/s wind contributes ~1 px extra (~1000 m error)."""
    # Total measured disparity: 2.0 px
    # Along-track wind: 10.0 m/s (in flight direction)
    delta_t_s = 1.005
    h_uncorr, h_corr, diff_m = correct_height_for_wind(
        total_along_track_disparity_px=2.0,
        wind_along_track_m_s=10.0,
        delta_t_s=delta_t_s,
    )

    # 10 m/s over 1.005 s is 10.05 m = 1.005 px
    # Parallax is 2.0 - 1.005 = 0.995 px
    # Uncorrected height: ~2105 m; Corrected height: ~1047 m
    # Discrepancy is ~1058 m (≈ 1000 m as stated in Krauß 2021)
    assert pytest.approx(h_uncorr, abs=10.0) == 2105.0
    assert pytest.approx(h_corr, abs=10.0) == 1047.0
    assert pytest.approx(abs(diff_m), abs=20.0) == 1058.0


def test_correct_height_using_shadow_disparity():
    """Verify wind correction using shadow as ground reference."""
    delta_t_s = 1.005
    # Cloud moves by 0.2 px wind + 1.0 px parallax = 1.2 px
    cloud_shift = 1.2
    # Shadow on ground experiences 0 parallax, only 0.2 px wind
    shadow_shift = 0.2

    h_uncorr, h_corr, diff = correct_height_using_shadow_disparity(
        cloud_along_track_shift_px=cloud_shift,
        shadow_along_track_shift_px=shadow_shift,
        delta_t_s=delta_t_s,
    )

    # Pure parallax = 1.0 px -> exactly 1053 m
    assert pytest.approx(h_corr, abs=1.0) == 1053.0
    assert pytest.approx(h_uncorr, abs=1.0) == 1263.0
    assert pytest.approx(diff, abs=1.0) == -210.0
