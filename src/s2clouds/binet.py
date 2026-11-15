"""High-precision inter-band delay correction based on satellite orbital ephemerides.

References:
    Binet, R., Bergsma, E., & Poulain, V. (2022). Accurate Sentinel-2 Inter-Band Time Delays.
    ISPRS Annals of the Photogrammetry, Remote Sensing and Spatial Information Sciences,
    V-1-2022, pp. 57-66. DOI: 10.5194/isprs-annals-V-1-2022-57-2022
"""

from typing import Final

from s2clouds.constants import ORBIT_ALTITUDE_M

NOMINAL_GROUND_VELOCITY_M_S: Final[float] = 6_890.0


def corrected_interband_delay(
    delta_t_ref_s: float,
    satellite_altitude_m: float,
    reference_altitude_m: float = ORBIT_ALTITUDE_M,
    ground_velocity_m_s: float = NOMINAL_GROUND_VELOCITY_M_S,
    reference_ground_velocity_m_s: float = NOMINAL_GROUND_VELOCITY_M_S,
) -> float:
    """Calculate corrected inter-band time delay based on orbital state.

    Implements equation 12 of Binet et al. (2022):
        dt = dt_ref * (H_sat / H_sat_ref) * (V_ground_ref / V_ground)

    Accounts for satellite orbital altitude variations (varying from ~788 km to ~818 km)
    which alter the ground track velocity and inter-detector acquisition timings.

    Args:
        delta_t_ref_s: Reference inter-band time delay from nominal ESA table (seconds).
        satellite_altitude_m: Instantaneous satellite altitude during acquisition (meters).
        reference_altitude_m: Reference orbital altitude (nominal 786,000 m).
        ground_velocity_m_s: Instantaneous ground velocity of sub-satellite point (m/s).
        reference_ground_velocity_m_s: Reference ground track velocity (m/s).

    Returns:
        Corrected inter-band delay dt in seconds.
    """
    if delta_t_ref_s <= 0.0:
        raise ValueError("delta_t_ref_s must be positive and non-zero")
    if satellite_altitude_m <= 0.0:
        raise ValueError("satellite_altitude_m must be positive")

    altitude_ratio = satellite_altitude_m / reference_altitude_m
    velocity_ratio = reference_ground_velocity_m_s / ground_velocity_m_s
    dt_corrected = delta_t_ref_s * altitude_ratio * velocity_ratio
    return dt_corrected
