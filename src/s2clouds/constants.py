"""Constants for Sentinel-2 cloud height extraction.

References:
    Krauß, T. (2021). Extraction of Cloud Heights from Sentinel-2 Multispectral Images.
    ISPRS Annals, V-1-2021, pp. 17-23. DOI: 10.5194/isprs-annals-V-1-2021-17-2021
"""

from typing import Final

# Orbit altitude h_o (meters) - Krauß 2021, ec. 6
ORBIT_ALTITUDE_M: Final[float] = 786_000.0

# Orbit velocity v_o (meters per second) - Krauß 2021, ec. 6
ORBIT_VELOCITY_M_S: Final[float] = 7_429.0

# Spatial resolution rho for 10m bands (meters per pixel) - Krauß 2021, ec. 6
PIXEL_RESOLUTION_M: Final[float] = 10.0

# Orbit inclination alpha (degrees) - Krauß 2021, ec. 4
ORBIT_INCLINATION_DEG: Final[float] = 98.62

# Nominal acquisition delays relative to band B02 (seconds) - Krauß 2021, Tabla 1
DELTA_T_B02_S: Final[float] = 0.000
DELTA_T_B08_S: Final[float] = 0.264
DELTA_T_B03_S: Final[float] = 0.527
DELTA_T_B04_S: Final[float] = 1.005

# Useful band pairs and their inter-band time delays delta_t (seconds) - Krauß 2021
BAND_PAIRS_DELTA_T_S: Final[dict[tuple[str, str], float]] = {
    ("B02", "B03"): 0.527,
    ("B02", "B04"): 1.005,
    ("B03", "B04"): 0.478,
}

__all__ = [
    "ORBIT_ALTITUDE_M",
    "ORBIT_VELOCITY_M_S",
    "PIXEL_RESOLUTION_M",
    "ORBIT_INCLINATION_DEG",
    "DELTA_T_B02_S",
    "DELTA_T_B08_S",
    "DELTA_T_B03_S",
    "DELTA_T_B04_S",
    "BAND_PAIRS_DELTA_T_S",
]
