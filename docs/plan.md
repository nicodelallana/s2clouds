# Altura de nubes por paralaje entre bandas de Sentinel-2 (`s2clouds`)

> Plan de proyecto, borrador v0.1. Basado en Krauß (2021) y Binet et al. (2022).

---

## 1. Qué se pretende hacer

Medir la **altura de nubes** sobre el Cantábrico a partir del desplazamiento (paralaje) que se ve entre las bandas B02 (azul), B03 (verde) y B04 (rojo) de Sentinel-2, y **validarla con una fuente externa** (sombras de las nubes y radiosondeo).

Es el mismo efecto físico que `s2motion` (retardo entre detectores del sensor *pushbroom*), pero aplicado a objetos que **no están en el suelo y casi no se mueven**, así que lo que se mide es la altura y no la velocidad.

**Entregables**
- Paquete Python `s2clouds` con una CLI sencilla.
- Mapa de alturas de una escena real, con incertidumbre.
- README al estilo de `s2motion`: hipótesis física, tabla de validación y limitaciones honestas.

---

## 2. Base científica

### 2.1 Krauß (2021): extracción de alturas de nubes

- Las bandas de 10 m **B02, B03, B04** tienen un retardo temporal entre sí. Los productos L1C/L2A se ortorrectifican con un DEM del **suelo**, así que lo que está por encima del suelo (nubes) queda desplazado entre bandas.
- Retardos (tabla 1 del paper, referidos a B02): B02 = 0,000 s, B08 = 0,264 s, B03 = 0,527 s, B04 = 1,005 s.
- Pares útiles y su Δt: **(B02,B03) = 0,527 s**, **(B02,B04) = 1,005 s**, **(B03,B04) = 0,478 s**. **No se usa B08 (NIR)**: correlaciona mal con las demás bandas.
- Fórmula de altura (ec. 6 del paper):

```text
h = |d| * rho * h_o / (v_o * dt)

h    altura sobre el suelo (m)
d    disparidad (px)
rho  resolución = 10 m/px
h_o  altura de la órbita = 786 km
v_o  velocidad orbital = 7,429 km/s   (2*pi*(R_E + h_o) / periodo)
dt   retardo entre las dos bandas (s)
```

- Con (B02,B04): **1 px de desplazamiento ≈ 1053 m de altura**. Con ec. 6 salen también ≈ 2008 m/px para (B02,B03) y ≈ 2213 m/px para (B03,B04). Una nube baja típica da 1 a 3 px en B02-B04.
- Dirección de escaneo (ec. 4): `cos(phi) = cos(alpha) / cos(lambda)`, con alpha = 98,62° (inclinación) y lambda = latitud de la escena. Se rota la imagen `90° - phi` para que el desplazamiento quede en vertical. Para Frankfurt sale 103,5°; para Bilbao (43,3° N) debería salir **≈ 101,9°** (dato para un test).
- Pipeline del paper: dividir en teselas de 1000×1000 px → rotar → disparidad con SGM (coste Census, rango ±20 px) para cada par → convertir a altura → **promediar los tres DEM** (si un píxel se desvía más de 0,25σ entre pares, se pone a 0) → apertura morfológica (5×5) y filtro gaussiano (σ = 1) → deshacer la rotación.
- Como el orden de bandas se invierte entre detectores pares e impares, la disparidad sale con signo cambiado en unas zonas, y se usa el **valor absoluto**.
- Validación del paper: distancia nube-sombra + ángulo cenital solar (ec. 7 y 8):

```text
tan(s_z) = d / h_s
h_c = d / tan(s_z) + H_s - H_c
```

  En 7 puntos de una escena: error medio 31 m, desviación típica 137 m. Resumen del paper: ≈ 150 m de error a 1500 m.
- Limitaciones que reconoce: **el viento de las nubes** (10 m/s ≈ 1 px extra ⇒ error de ±1000 m), ruido fuera de las nubes, cirros muy perforados y que **no se pueden sacar alturas de edificios**.

### 2.2 Binet et al. (2022): retardos precisos entre bandas

- El retardo real **no es constante** respecto a la tabla de ESA. Varía por la distorsión óptica (≈ 3,2 % a lo ancho de la franja) y por la altura del satélite (hasta ≈ 4,2 % a lo largo de la órbita; la altura va de ≈ 788 a 818 km).
- Con la tabla de ESA, el error máximo es 2,5 % y el rms 1 %.
- Corrección propuesta para productos L1C (ec. 12), con el retardo de referencia de un producto L1B:

```text
dt = dt_ref * (H_sat / H_sat_ref) * (V_ground_ref / V_ground)
```

  Con ella: error máximo 1 % y rms 0,28 %. Necesita las efemérides del *datastrip* y la máscara de detectores `MSK_DETFOO`.
- Para este proyecto es una **mejora opcional**: un 2 % sobre 1500 m son ≈ 30 m, bastante menos que el error esperado por el viento (cientos de metros).

---

## 3. Hipótesis de trabajo

1. La disparidad entre bandas de una nube, en la dirección de escaneo, es proporcional a su altura (ec. 6).
2. Los tres pares de bandas dan alturas compatibles entre sí, con ruido distinto (el de Δt corto es peor).
3. Las alturas medidas concuerdan con las que salen de la geometría nube-sombra dentro de ≈ 150 m (nivel del paper, a comprobar).
4. **Problema abierto**: el viento. El desplazamiento a lo largo de la órbita mezcla paralaje y movimiento de la nube, y **ambos son proporcionales a Δt**, así que los pares de bandas por sí solos no los separan. Opciones para tratarlo:
   - Medir la disparidad también en las **sombras** (están en el suelo: no tienen paralaje, solo movimiento), como sugiere Krauß.
   - Usar la componente **perpendicular** a la órbita, que no tiene paralaje y da el viento en esa dirección.
   - Comparar con el viento de un radiosondeo cercano.

---

## 4. Alcance

**MVP (v0.1)**: una escena, una ventana pequeña, un número de altura con incertidumbre, validado con una sombra.

**v0.2**: malla de ventanas, mapa de alturas y fusión de los tres pares.

**v1.0**: varias escenas, tabla de validación, README final.

**Extras (si hay tiempo)**: corrección de Binet, separación del viento con sombras, comparación con radiosondeo.

**Fuera de alcance**: cirros finos, edificios, nubes sobre mar sin referencia de sombra, procesado a gran escala.

---

## 5. Fases

Cada fase vive en su propia rama `feature/...` (ver sección 8).

| Fase | Rama | Qué se hace | Hecho cuando |
|:---:|:---|:---|:---|
| 0 | `feature/00-setup` | Repo, `pyproject.toml`, ruff, pytest, CI y estructura de carpetas | `pytest` y `ruff` pasan en CI |
| 1 | `feature/01-constantes` | `constants.py` con Δt, `h_o`, `v_o`, `rho`; función `height_from_disparity` (ec. 6) | Test: 1 px con Δt = 1,005 s da ≈ 1053 m |
| 2 | `feature/02-descarga-stac` | Descargar un recorte de B02, B03, B04 vía STAC (AWS Earth Search) y COG con `rasterio` (usar `sentinel-2-l1c` si está disponible, si no `l2a`) | Recorte guardado y reproducible con una orden |
| 3 | `feature/03-exploracion` | Escena con nubes bajas sobre el Cantábrico. Composición RGB y ver a ojo el desplazamiento de color en los bordes | Imagen en `docs/img/` donde se aprecia la franja de color |
| 4 | `feature/04-direccion-escaneo` | Calcular `phi` (ec. 4) y rotar el recorte | Test: `phi` ≈ 101,9° a 43,3° N. Contrastar el convenio del ángulo con el rumbo del satélite que ya usas en `s2motion` (194,7°) |
| 5 | `feature/05-disparidad-ventana` | Disparidad entre dos bandas en **una sola ventana** con correlación de fase subpíxel (`skimage.registration.phase_cross_correlation`) | Un número en píxeles, estable al mover un poco la ventana |
| 6 | `feature/06-altura-una-ventana` | Pasar la disparidad a altura y propagar la incertidumbre (±0,1 px de disparidad, ±1 % de Δt) | Altura con intervalo. Debe estar entre 0 y 3 km para nubes bajas |
| 7 | `feature/07-validacion-sombras` | Medir `d` nube-sombra a mano, calcular el ángulo cenital solar y aplicar ec. 7 y 8 con un DEM (SRTM o Copernicus DEM) | Diferencia entre altura por paralaje y por sombra, anotada |
| 8 | `feature/08-malla-de-ventanas` | Repetir la medida en una malla y construir el mapa de alturas | Mapa con máscara de nubes y sin ruido evidente fuera de ellas |
| 9 | `feature/09-fusion-tres-pares` | Pares (2,3), (2,4) y (3,4); promedio con el criterio de 0,25σ; apertura morfológica y gaussiano | El mapa fusionado tiene menos ruido que cada par por separado |
| 10 | `feature/10-validacion-varias-escenas` | Varias escenas y fechas; tabla de validación con error medio y desviación | Tabla en el README |
| 11 | `feature/11-extra-binet` *(opcional)* | Corrección del retardo con la altura del satélite (ec. 12) | Cambio en altura < 2 %, documentado |
| 12 | `feature/12-extra-viento` *(opcional)* | Separar el viento con las sombras y/o el radiosondeo | Altura corregida frente a la no corregida |

**Regla de trabajo**: no pasar a la fase siguiente hasta que la anterior tenga test o figura que la respalde.

---

## 6. Validación y métricas

| Magnitud | Cómo se valida | Métrica |
|:---|:---|:---|
| Retardos entre bandas | Literatura (Krauß 2021, Binet 2022) | Valores de la tabla, con ±1 % de incertidumbre |
| Altura por paralaje | Geometría nube-sombra (ec. 7-8) | Error medio y desviación típica en m; referencia del paper: ≈ 31 m y 137 m (n = 7) |
| Altura por paralaje | Radiosondeo más cercano (Santander), si hay uno ese día | Altura de la capa nubosa frente a la medida |
| Viento | Radiosondeo y/o sombras | Diferencia de velocidad |
| Consistencia entre pares | Comparar los tres mapas | Desviación entre pares por píxel |

Mantener una tabla de **estado de validación** como la de `s2motion`: *respaldada por literatura*, *coherente internamente*, *hipótesis no validada*.

---

## 7. Riesgos y limitaciones

1. **Viento**: puede aportar ±1000 m a 10 m/s (Krauß). Elegir días y capas con poco viento y estimarlo con radiosondeo.
2. **Señal pequeña**: 1 a 3 px en nubes bajas. Hace falta subpíxel y el error relativo es alto en nubes muy bajas.
3. **Ruido fuera de las nubes**: enmascarar con una máscara de nube.
4. **Elegir las escenas a mano** sin una tasa de falsos positivos conocida (como ya declaras en `s2motion`).
5. **Convenio de ejes y ángulos**: errores de signo al rotar. Cubrirlo con tests.
6. **Cirros**: el DEM sale muy perforado; fuera de alcance.
7. **Datos**: L1C puede no estar en el catálogo para todas las fechas.
8. **Orden de bandas según el detector**: el orden se invierte entre detectores pares e impares. En nubes se resuelve con el valor absoluto, pero es un dato a tener en cuenta en `s2motion` (ver `MSK_DETFOO`).

---

## 8. Git y flujo de trabajo

### 8.1 Ramas (Git flow simplificado)

```text
main                  estable, solo recibe releases (tags v0.1.0, v0.2.0, ...)
develop               integración; aquí se juntan las features
feature/<nn>-<tema>   una por fase del plan (sección 5)
release/vX.Y.Z        congelar y revisar antes de publicar
hotfix/<tema>         arreglo urgente sobre main
```

### 8.2 Reglas

- Nunca se trabaja directamente en `main` ni en `develop`.
- Cada feature nace de `develop` y vuelve a `develop` con **Pull Request** (aunque trabajes solo, deja historia revisable).
- PR pequeñas: una fase o parte de ella.
- Antes de abrir la PR: `ruff check`, `ruff format` y `pytest` en verde.
- Fusionar con `--no-ff` para conservar la rama en el historial.
- Borrar la rama `feature/...` tras fusionar.

### 8.3 Commits (Conventional Commits)

```text
feat:      nueva funcionalidad            feat: add height_from_disparity
fix:       corrección de un error         fix: sign of rotation angle
test:      tests                          test: phi at 43.3N is about 101.9
docs:      documentación                  docs: add validation table
refactor:  cambio interno sin efecto      refactor: split io_stac module
chore:     tareas de mantenimiento        chore: add ruff config
```

### 8.4 Versiones y releases

- `v0.1.0`: MVP (fases 0 a 7).
- `v0.2.0`: mapa de alturas (fases 8 y 9).
- `v1.0.0`: validación con varias escenas y README final (fase 10).
- Cada release se etiqueta en `main` con un tag anotado y un `CHANGELOG.md` corto.

### 8.5 Datos y archivos grandes

- Los rásteres **no se suben**: `data/` y `outputs/` en `.gitignore`.
- Solo recortes minúsculos para los tests, en `tests/data/`.
- Los recortes se regeneran con la CLI a partir de la fecha y el identificador de escena, que sí se guardan en un `.toml` (como `examples/*.toml` de `s2motion`).

### 8.6 Issues y organización

- Un *issue* por fase, con el criterio de "hecho cuando" de la tabla.
- Etiquetas: `fase`, `bug`, `validación`, `docs`, `extra`.
- Un *milestone* por versión (v0.1, v0.2, v1.0).

---

## 9. Estructura del repositorio

```text
s2clouds/
├── README.md
├── CHANGELOG.md
├── pyproject.toml
├── .gitignore
├── docs/
│   ├── plan.md                  este documento
│   ├── method.md                derivaciones y ecuaciones
│   ├── validation.md            criterios a priori y resultados
│   ├── papers/                  notas de lectura (no los PDF si hay copyright)
│   └── img/
├── src/s2clouds/
│   ├── constants.py             Δt, h_o, v_o, rho
│   ├── io_stac.py               descarga de recortes
│   ├── geometry.py              ángulo de escaneo y rotación
│   ├── disparity.py             correlación de fase, SGM
│   ├── heights.py               disparidad -> altura, incertidumbre
│   ├── validation.py            sombras, ángulo solar
│   └── cli.py
├── examples/                    escenas en .toml
├── notebooks/                   exploración (no es código final)
└── tests/
    └── data/
```

---

## 10. Convenciones de código

- Python ≥ 3.10, igual que `s2motion`.
- **Código simple**: funciones pequeñas, **un cálculo por línea**, sin `lambda` ni construcciones rebuscadas.
- Nombres con la magnitud y la unidad: `disparity_px`, `height_m`, `delta_t_s`.
- Cada función que implementa una ecuación cita su número en el docstring (por ejemplo "ec. 6 de Krauß 2021").
- Tests con `pytest` para cada fórmula, con valores del paper cuando existan.
- Formato y lint con `ruff`.

---

## 11. Referencias

- **Krauß, T. (2021)**. *Extraction of Cloud Heights from Sentinel-2 Multispectral Images*. ISPRS Annals, V-1-2021, pp. 17-23. DOI: 10.5194/isprs-annals-V-1-2021-17-2021
- **Binet, R., Bergsma, E., & Poulain, V. (2022)**. *Accurate Sentinel-2 Inter-Band Time Delays*. ISPRS Annals, V-1-2022, pp. 57-66. DOI: 10.5194/isprs-annals-V-1-2022-57-2022
- **Hirschmüller, H. (2005)**. Semi-global matching and mutual information. CVPR, 2, 807-814.
- ESA, *Sentinel-2 MSI instrument*: https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-2-msi/msi-instrument
