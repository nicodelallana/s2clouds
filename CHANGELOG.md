# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y el proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Módulo `fusion.py` para fusión multiespectral de los 3 pares de bandas ((B02,B03), (B02,B04), (B03,B04)).
- Filtrado de consistencia según criterio de Krauß (2021) de 0.25σ.
- Denoising mediante apertura morfológica 5x5 y convolución gaussiana normalizada (σ = 1.0).
- Soporte para `--pair fuse` en CLI `s2clouds heightmap`.
- Figura comparativa de los tres pares y mapa fusionado en `docs/img/cantabrico_three_pairs_fusion.png`.
- Tests unitarios en `tests/test_fusion.py` demostrando reducción de ruido en el mapa fusionado.
- Funciones `compute_disparity_grid` y `generate_cloud_mask` en `disparity.py`.
- Función `compute_cloud_height_map` en `heights.py` para generación de mapas de altura densos con enmascaramiento estricto de nubes y desrotación a coordenadas originales.
- Subcomando CLI `s2clouds heightmap`.
- Figura del mapa de alturas en escena del Cantábrico en `docs/img/cantabrico_cloud_height_map.png`.
- Tests unitarios en `tests/test_height_map.py`.

## [0.1.0] - 2026-11-15

### Added
- Módulo `constants.py` con constantes físicas y orbitales del instrumento Sentinel-2 MSI (Krauß 2021).
- Función `height_from_disparity` para conversión de disparidad a altura sobre el terreno (ec. 6 Krauß 2021).
- Módulo `io_stac.py` para consulta de escenas STAC (AWS Earth Search) y descarga de recortes multiespectrales en ventana COG con `rasterio`.
- Configuración de escena de ejemplo `examples/bilbao_clouds.toml`.
- Subcomando CLI `s2clouds download` para adquisición reproducible de recortes.
- Cuaderno de exploración y figuras de paralaje (`docs/img/cantabrico_rgb_parallax.png`, `docs/img/cantabrico_cloud_fringe_zoom.png`).
- Módulo `geometry.py`: cálculo del ángulo de escaneo `phi` (ec. 4 Krauß 2021), ángulo de alineación vertical y funciones de rotación/desrotación.
- Módulo `disparity.py`: estimación de disparidad subpíxel mediante correlación de fase y apodización Tukey.
- Función `propagate_height_uncertainty` y estructura de datos `CloudHeightResult` con intervalos de confianza al 68% y 95%.
- Módulo `validation.py`: cálculo de altura mediante geometría nube-sombra (ec. 7-8 Krauß 2021) y vector de proyección solar.
- Validación empírica documentada en `docs/validation.md` en escena del Cantábrico (discrepancia de 4.1 m).
- Suite de tests unitarios (31 tests en pytest) y pipeline de integración continua CI en GitHub Actions.
