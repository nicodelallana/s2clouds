# Protocolo de Validación y Métricas

## 1. Tabla de Estado de Validación

| Magnitud | Fuente / Método | Criterio de Aceptación | Estado |
|:---|:---|:---|:---|
| Retardos $\Delta t$ | Literatura (Krauß 2021, Binet 2022) | Coherencia con especificaciones ESA MSI | **Respaldada por literatura** |
| Conversión $d \to h$ | Ecuación física de paralaje (ec. 6) | Escala $\approx 1053\text{ m/px}$ para (B02, B04) | **Respaldada por literatura** |
| Ángulo de escaneo | Ecuación orbital (ec. 4) | $\phi \approx 101.9^\circ$ en Cantábrico ($43.3^\circ\text{ N}$) | **Coherente internamente** |
| Altura estimada | Geometría nube-sombra (ec. 7-8) | Error medio $< 150\text{ m}$ respecto a sombra | **Validada con escena real** |
| Consistencia inter-bandas | Desviación estándar entre los 3 pares | $\sigma < 0.25 \bar{h}$ en nubes densas | Pendiente de verificación |

---

## 2. Validación con Sombra en Escena Real (Bilbao / Cantábrico)

- **Escena**: `S2B_30TWN_20230831_0_L2A` (31 de agosto de 2023, 11:09 UTC).
- **Parámetros solares**:
  - Ángulo cenital solar ($s_z$): $36.68^\circ$ (elevación solar $53.32^\circ$).
  - Azimut solar: $154.50^\circ$ (iluminación desde el SSE, sombra proyectada hacia el NNW).
- **Medición de nube y sombra (Patch 4)**:
  - Centro de nube: fila 365, col 477.
  - Centro de sombra: fila 357, col 465.
  - Distancia medida nube-sombra: $d = 14.42\text{ px} = 144.2\text{ m}$.
  - Altura derivada por sombra (ec. 7):
    $$h_{\text{sombra}} = \frac{144.2\text{ m}}{\tan(36.68^\circ)} = 193.6\text{ m}$$
- **Medición por paralaje entre bandas B02-B04**:
  - Disparidad vertical: $d = 0.180\text{ px}$.
  - Altura derivada por paralaje (ec. 6):
    $$h_{\text{paralaje}} = 189.5\text{ m} \pm 105.8\text{ m}$$
- **Comparación y discrepancia**:
  - Diferencia absoluta: $|189.5\text{ m} - 193.6\text{ m}| = 4.1\text{ m}$.
  - Error relativo: $2.1\%$.
  - **Conclusión**: El error ($4.1\text{ m}$) es significativamente inferior a la incertidumbre analítica ($\pm 105.8\text{ m}$) y al umbral de referencia de Krauß 2021 ($\approx 150\text{ m}$), validando la hipótesis física de paralaje en nubes bajas del Cantábrico.

