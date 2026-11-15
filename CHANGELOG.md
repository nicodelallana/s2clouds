# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y el proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Script de exploración y figuras de paralaje (`notebooks/01_exploracion_paralaje.py`, `docs/img/cantabrico_rgb_parallax.png`, `docs/img/cantabrico_cloud_fringe_zoom.png`) mostrando el desplazamiento cromático en bordes de nube.
- Módulo `io_stac` para consulta en STAC (Earth Search) y descarga de recortes en ventana COG con `rasterio`.
- Configuración de escena de ejemplo `examples/bilbao_clouds.toml`.
- Subcomando CLI `s2clouds download` para reproducción de recortes.
- Constantes orbitales y físicas de Sentinel-2 (`src/s2clouds/constants.py`).
- Función `height_from_disparity` para cálculo de altura a partir de disparidad (ec. 6 de Krauß 2021).
- Tests unitarios para constantes y ec. 6 con los pares B02-B04, B02-B03 y B03-B04.
- Configuración inicial del repositorio: `pyproject.toml`, ruff, pytest, CI y estructura de carpetas.
