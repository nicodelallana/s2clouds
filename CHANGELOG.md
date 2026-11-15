# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y el proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Módulo `validation.py` con validación geométrica nube-sombra (ec. 7-8 Krauß 2021) y cálculo del vector de proyección de sombra.
- Resultados de validación empírica en escena real de Bilbao anotados en `docs/validation.md` (discrepancia de 4.1 m entre paralaje y sombra).
- Tests para cálculo solar y validación nube-sombra en `tests/test_validation.py`.
- Función `propagate_height_uncertainty` y estructura de datos `CloudHeightResult` con intervalos de confianza al 68% y 95% para propagación analítica de incertidumbres en disparidad y retardos de banda.
- Tests unitarios de propagación de incertidumbre y verificación del rango de alturas en nubes bajas (0 a 3 km).
- Módulo `disparity.py` para cálculo de disparidad subpíxel en ventanas con correlación de fase (`skimage.registration.phase_cross_correlation`) y apodización Tukey.
- Tests de precisión subpíxel sobre datos sintéticos y test de estabilidad bajo jitter de ventana.
- Módulo de geometría orbital `geometry.py`: cálculo del ángulo de escaneo `phi` (ec. 4 Krauß 2021), ángulo de rotación para alineación vertical y funciones de rotación/desrotación de rásteres.
- Tests de verificación para `phi` a 43.3° N (Bilbao, 101.9°) y 50.11° N (Frankfurt, 103.5°).
- Script de exploración y figuras de paralaje (`notebooks/01_exploracion_paralaje.py`, `docs/img/cantabrico_rgb_parallax.png`, `docs/img/cantabrico_cloud_fringe_zoom.png`) mostrando el desplazamiento cromático en bordes de nube.
- Módulo `io_stac` para consulta en STAC (Earth Search) y descarga de recortes en ventana COG con `rasterio`.
- Configuración de escena de ejemplo `examples/bilbao_clouds.toml`.
- Subcomando CLI `s2clouds download` para reproducción de recortes.
- Constantes orbitales y físicas de Sentinel-2 (`src/s2clouds/constants.py`).
- Función `height_from_disparity` para cálculo de altura a partir de disparidad (ec. 6 de Krauß 2021).
- Tests unitarios para constantes y ec. 6 con los pares B02-B04, B02-B03 y B03-B04.
- Configuración inicial del repositorio: `pyproject.toml`, ruff, pytest, CI y estructura de carpetas.
