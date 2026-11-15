# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y el proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-11-15

### Added
- Malla de correlación subpíxel (`compute_disparity_grid`) y máscara de nubes adaptativa (`generate_cloud_mask`).
- Generación de mapas densos de altura de nubes (`compute_cloud_height_map`) con desrotación espacial a coordenadas geográficas.
- Fusión multiespectral de los 3 pares de bandas ((B02,B03), (B02,B04), (B03,B04)) en `fusion.py` siguiendo a Krauß (2021).
- Filtrado de consistencia estadística inter-pares (umbral 0.25σ) y post-procesamiento morfológico (apertura 5x5 + suavizado gaussiano).
- Subcomando CLI `s2clouds heightmap` con opciones de selección de par individual o `--pair fuse`.
- Figuras de validación cartográfica (`cantabrico_cloud_height_map.png` y `cantabrico_three_pairs_fusion.png`).
- Verificación empírica de reducción de ruido en mapa fusionado.

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
