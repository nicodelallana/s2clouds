# Notas de lectura: Krauß (2021)

**Título**: *Extraction of Cloud Heights from Sentinel-2 Multispectral Images*
**Autor**: Thomas Krauß (DLR)
**Publicación**: ISPRS Annals of the Photogrammetry, Remote Sensing and Spatial Information Sciences, Volume V-1-2021, 2021.

## Puntos clave
1. **Mecanismo**: El sensor MSI pushbroom de Sentinel-2 adquiere bandas visibles con intervalos de fracciones de segundo. Debido a la altitud de vuelo orbital (~786 km), objetos por encima del elipsoide/DEM de referencia sufren un paralaje cuantificable.
2. **Bandas**: Se descarta B08 (NIR) debido a que su firma espectral sobre nubes difiere sensiblemente del visible, perjudicando la correlación de imágenes. Solo se usan B02 (azul), B03 (verde) y B04 (rojo).
3. **Inversión detector**: El orden de los detectores en el plano focal se invierte entre detectores pares e impares, lo que altera el signo de la disparidad; por ello se toma el valor absoluto $|d|$.
4. **Viento**: El viento a lo largo de la trayectoria del satélite produce un desplazamiento adicional que se suma o resta al paralaje. Krauß reporta que un viento de 10 m/s genera ~1 px de sesgo (~1000 m de error de cota).
5. **Validación**: Con 7 nubes y sus sombras, obtuvo un error medio de 31 m y una desviación estándar de 137 m.
