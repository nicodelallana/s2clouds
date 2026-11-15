"""Tests for Binet et al. (2022) inter-band delay correction (ec. 12)."""

import pytest

from s2clouds.binet import corrected_interband_delay
from s2clouds.heights import height_from_disparity


def test_binet_interband_delay_correction_ec12():
    """Verify ec. 12 of Binet et al. (2022): dt = dt_ref * (H_sat / H_ref) * (V_ref / V)."""
    nominal_dt_s = 1.005  # B02 - B04
    # Satellite altitude over Cantabrian Sea at 43.3° N is ~795 km (vs nominal 786 km)
    sat_altitude_m = 795_000.0
    ref_altitude_m = 786_000.0

    corrected_dt_s = corrected_interband_delay(
        delta_t_ref_s=nominal_dt_s,
        satellite_altitude_m=sat_altitude_m,
        reference_altitude_m=ref_altitude_m,
    )

    ratio = corrected_dt_s / nominal_dt_s
    pct_change = abs(ratio - 1.0) * 100.0

    # Timing change should be ~1.14% (< 2%)
    assert pytest.approx(pct_change, abs=0.1) == 1.14
    assert pct_change < 2.0


def test_binet_height_change_under_two_percent():
    """Verify that Binet delay correction alters cloud height by < 2%."""
    nominal_dt_s = 1.005
    corrected_dt_s = corrected_interband_delay(
        delta_t_ref_s=nominal_dt_s,
        satellite_altitude_m=795_000.0,
        reference_altitude_m=786_000.0,
    )

    disparity_px = 1.0  # ~1053 m nominal height
    h_nominal = height_from_disparity(disparity_px, nominal_dt_s)
    h_corrected = height_from_disparity(disparity_px, corrected_dt_s)

    rel_diff_pct = abs(h_corrected - h_nominal) / h_nominal * 100.0

    # Check criterion: "Cambio en altura < 2 %, documentado"
    assert rel_diff_pct < 2.0
    assert pytest.approx(rel_diff_pct, abs=0.1) == 1.13


def test_binet_invalid_inputs():
    """Verify input validation for invalid altitudes or negative dt."""
    with pytest.raises(ValueError, match="positive and non-zero"):
        corrected_interband_delay(0.0, 786_000.0)

    with pytest.raises(ValueError, match="positive"):
        corrected_interband_delay(1.005, -500.0)
