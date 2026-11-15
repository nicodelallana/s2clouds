# Fundamentos Metodológicos de `s2clouds`

Basado en Krauß (2021) (*Extraction of Cloud Heights from Sentinel-2 Multispectral Images*) y Binet et al. (2022) (*Accurate Sentinel-2 Inter-Band Time Delays*).

---

## 1. Paralaje inter-banda en Sentinel-2

El instrumento MSI de Sentinel-2 cuenta con 12 detectores en disposición escalonada (*staggered*) a lo largo del plano focal. Las bandas se adquieren secuencialmente a medida que el satélite viaja a lo largo de su trayectoria orbital:

- Bandas de 10 m de resolución: B02 (azul, 490 nm), B03 (verde, 560 nm), B04 (rojo, 665 nm), B08 (NIR, 842 nm).
- Retardo temporal nominal relativo a B02:
  - B02: $0.000\text{ s}$
  - B08: $0.264\text{ s}$
  - B03: $0.527\text{ s}$
  - B04: $1.005\text{ s}$
- Pares útiles (evitando B08 por pobre correlación radiométrica con las bandas visibles):
  - $(B02, B03): \Delta t = 0.527\text{ s}$
  - $(B02, B04): \Delta t = 1.005\text{ s}$
  - $(B03, B04): \Delta t = 0.478\text{ s}$

---

## 2. Ecuación de altura (Krauß 2021, ec. 6)

Durante el procesado L1C/L2A, las imágenes se proyectan ortográficamente sobre un modelo digital de elevación (DEM) de la superficie terrestre. Los objetos situados a una altura $h$ sobre el terreno experimentan un desplazamiento aparente (disparidad $d$) en la dirección del vuelo del satélite:

$$h = \frac{|d| \cdot \rho \cdot h_o}{v_o \cdot \Delta t}$$

Donde:
- $h$: altura del objeto sobre el suelo $[\text{m}]$.
- $d$: disparidad medida $[\text{px}]$.
- $\rho$: resolución espacial del píxel ($10\text{ m/px}$).
- $h_o$: altitud media orbital ($786\text{ km} = 786{,}000\text{ m}$).
- $v_o$: velocidad orbital del satélite ($7.429\text{ km/s} = 7{,}429\text{ m/s}$).
- $\Delta t$: retardo temporal entre las bandas $[\text{s}]$.

### Factores de escala por píxel:
- Para $(B02, B04)$: $\approx 1052.75\text{ m/px} \approx 1053\text{ m/px}$.
- Para $(B02, B03)$: $\approx 2007.62\text{ m/px} \approx 2008\text{ m/px}$.
- Para $(B03, B04)$: $\approx 2213.42\text{ m/px} \approx 2213\text{ m/px}$.

---

## 3. Ángulo de escaneo y orientación (Krauß 2021, ec. 4)

La dirección del escaneo respecto al meridiano depende de la inclinación orbital $\alpha = 98.62^\circ$ y la latitud $\lambda$:

$$\cos(\phi) = \frac{\cos(\alpha)}{\cos(\lambda)}$$

La rotación para alinear el desplazamiento con las columnas verticales de la matriz es:
$$\theta_{\text{rot}} = 90^\circ - \phi$$

Para latitudes típicas:
- Frankfurt ($50.1^\circ\text{ N}$): $\phi \approx 103.5^\circ$
- Bilbao / Cantábrico ($43.3^\circ\text{ N}$): $\phi \approx 101.9^\circ$

---

## 4. Validación geométrica con sombras (Krauß 2021, ec. 7-8)

A partir de la distancia horizontal proyectada $d_{\text{sombra}}$ entre el centro de la nube y su sombra proyectada en el suelo, y del ángulo cenital solar $s_z$:

$$\tan(s_z) = \frac{d_{\text{sombra}}}{h_s}$$

## 5. Corrección de Retardos de Binet et al. (2022, ec. 12)

La órbita de Sentinel-2 oscila en altitud a lo largo de su paso orbital entre $\approx 788\text{ km}$ y $818\text{ km}$. La variación de la velocidad del subpunto satelital en tierra y de la escala focal induce una pequeña variación en el retardo entre bandas:

$$\Delta t_{\text{corregido}} = \Delta t_{\text{ref}} \cdot \left(\frac{H_{\text{sat}}}{H_{\text{sat, ref}}}\right) \cdot \left(\frac{V_{\text{ground, ref}}}{V_{\text{ground}}}\right)$$

## 6. Tratamiento del Viento y Advección (Krauß 2021)

El desplazamiento a lo largo de la órbita mezcla paralaje y advección de la masa de aire:
$$d_{\text{total, along}} = d_{\text{paralaje}} + d_{\text{viento, along}} = d_{\text{paralaje}} + \frac{v_{\text{viento, along}} \cdot \Delta t}{\rho}$$

Krauß (2021) documenta que una componente de viento de solo $10\text{ m/s}$ a lo largo de la traza agrega $\approx 1\text{ px}$ de sesgo ($\approx 1000\text{ m}$ de error de cota).

`s2clouds` proporciona dos métodos de desacople:
1. **Componente transversal libre de paralaje**: El desplazamiento a través de la traza ($d_{\text{cross}}$) no tiene paralaje geométrico, por lo que permite calcular la componente ortogonal del viento: $v_{\text{viento, cross}} = (d_{\text{cross}} \cdot \rho) / \Delta t$.
2. **Referencia en sombras terrestres**: La sombra proyectada en el suelo ($h = 0$) tiene paralaje nulo ($d_{\text{paralaje, sombra}} = 0$). Cualquier desplazamiento medido en la sombra corresponde al movimiento de la nube ($d_{\text{sombra}} = d_{\text{viento}}$), permitiendo calcular el paralaje puro restando: $d_{\text{paralaje}} = d_{\text{nube}} - d_{\text{sombra}}$.


