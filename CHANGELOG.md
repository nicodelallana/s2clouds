# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y el proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Constantes orbitales y físicas de Sentinel-2 (`src/s2clouds/constants.py`).
- Función `height_from_disparity` para cálculo de altura a partir de disparidad (ec. 6 de Krauß 2021).
- Tests unitarios para constantes y ec. 6 con los pares B02-B04, B02-B03 y B03-B04.
- Configuración inicial del repositorio: `pyproject.toml`, ruff, pytest, CI y estructura de carpetas.
