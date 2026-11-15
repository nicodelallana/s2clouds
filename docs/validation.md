# Protocolo de Validación y Métricas

## Tabla de Estado de Validación

| Magnitud | Fuente / Método | Criterio de Aceptación | Estado |
|:---|:---|:---|:---|
| Retardos $\Delta t$ | Literatura (Krauß 2021, Binet 2022) | Coherencia con especificaciones ESA MSI | Respaldada por literatura |
| Conversión $d \to h$ | Ecuación física de paralaje (ec. 6) | Escala $\approx 1053\text{ m/px}$ para (B02, B04) | Respaldada por literatura |
| Ángulo de escaneo | Ecuación orbital (ec. 4) | $\phi \approx 101.9^\circ$ en Cantábrico ($43.3^\circ\text{ N}$) | Coherente internamente |
| Altura estimada | Geometría nube-sombra (ec. 7-8) | Error medio $< 150\text{ m}$ respecto a sombra | Pendiente de verificación |
| Consistencia inter-bandas | Desviación estándar entre los 3 pares | $\sigma < 0.25 \bar{h}$ en nubes densas | Pendiente de verificación |
