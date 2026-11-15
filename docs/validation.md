# Protocolo de Validación y Métricas de `s2clouds`

## 1. Estado Epistémico de las Hipótesis

Siguiendo el estándar de validación científica de `s2motion`:

| Hipótesis / Parámetro | Método de Verificación | Criterio de Aceptación | Estado |
|:---|:---|:---|:---|
| **Retardos $\Delta t$ entre detectores** | Literatura (Krauß 2021, Binet 2022) | Coherencia con la geometría del plano focal MSI | **Respaldada por literatura** |
| **Conversión $d \to h$ (ec. 6)** | Física orbital y proyección ortográfica | Escala nominal $\approx 1053\text{ m/px}$ para (B02, B04) | **Respaldada por literatura** |
| **Ángulo de escaneo $\phi$ (ec. 4)** | Mecánica orbital Kepleriana retrógrada | $\phi \approx 101.9^\circ$ a $43.3^\circ\text{ N}$ | **Coherente internamente** |
| **Altura por paralaje vs sombras** | Trigonometría solar (ec. 7 y 8) | Error medio $< 50\text{ m}$, desviación $< 150\text{ m}$ | **Validada empíricamente** |
| **Consistencia multi-par** | Fusión de DEMs B02-B03, B02-B04, B03-B04 | Desviación del mapa fusionado menor que cada par | **Validada empíricamente** |
| **Separación de advección (viento)** | Análisis de disparidad en sombras terrestres | Desacople vector viento vs paralaje | *Hipótesis no validada (trabajo futuro)* |

---

## 2. Tabla de Validación Multi-Escena (Cantábrico)

Comparación empírica entre la cota calculada por paralaje inter-banda $h_{\text{paralaje}}$ y la cota geométrica derivada de la proyección de sombra solar $h_{\text{sombra}}$:

| Escena STAC | Fecha | Ubicación | Tipo Nuboso | $d_{\text{sombra}}$ (m) | $s_z$ (deg) | $h_{\text{sombra}}$ (m) | $h_{\text{paralaje}}$ (m) | Error $\Delta h$ (m) | Error Rel. (%) |
|:---|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `S2B_30TWN_20230831` | 2023-08-31 | Bilbao Abra (P4) | Cumulus humilis | 144.2 | 36.68 | 193.6 | $189.5 \pm 105.8$ | **-4.1** | 2.1% |
| `S2B_30TWN_20230831` | 2023-08-31 | Bilbao Costa (P5) | Cumulus fractus | 147.0 | 36.68 | 197.3 | $200.0 \pm 106.0$ | **+2.7** | 1.4% |
| `S2B_30TWN_20230831` | 2023-08-31 | Abra Interior (P3) | Stratus marinus | 35.8 | 36.68 | 48.1 | $42.1 \pm 105.3$ | **-6.0** | 12.5% |
| `S2B_30TVN_20230831` | 2023-08-31 | Bahía de Santander | Stratocumulus | 885.0 | 36.36 | 1202.1 | $1178.5 \pm 106.5$ | **-23.6** | 2.0% |
| `S2A_30TVP_20230819` | 2023-08-19 | Golfo de Vizcaya | Cumulus congestus | 1045.0 | 33.32 | 1590.2 | $1631.8 \pm 108.0$ | **+41.6** | 2.6% |
| `S2A_30TWP_20230819` | 2023-08-19 | Cantabria Offshore | Cumulus mediocris | 580.0 | 33.32 | 882.6 | $894.8 \pm 106.0$ | **+12.2** | 1.4% |

### Métricas Estadísticas Globales

- **Error Medio (Sesgo / Bias)**: **$+3.8\text{ m}$** *(referencia Krauß 2021: $+31.0\text{ m}$)*
- **Error Medio Absoluto (MAE)**: **$15.0\text{ m}$**
- **Error Cuadrático Medio (RMSE)**: **$20.4\text{ m}$**
- **Desviación Típica ($\sigma$)**: **$22.4\text{ m}$** *(referencia Krauß 2021: $137.0\text{ m}$)*

Todos los casos analizados se encuentran holgadamente dentro del umbral de incertidumbre analítica y de la tolerancia experimental de la literatura ($150\text{ m}$).
