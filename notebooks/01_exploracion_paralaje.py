"""Exploration script: RGB composition and visual inspection of inter-band parallax.

Demonstrates the chromatic fringe (red/blue edge split) observed at cloud boundaries
in Sentinel-2 MSI bands B02, B03, B04 due to inter-detector acquisition delay.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio


def make_enhanced_rgb(
    red: np.ndarray,
    green: np.ndarray,
    blue: np.ndarray,
    p_low: float = 2.0,
    p_high: float = 98.0,
) -> np.ndarray:
    """Combine R, G, B channels into a normalized [0, 1] RGB image with percentile stretch."""
    rgb = np.dstack([red, green, blue])
    v_min = np.percentile(rgb, p_low)
    v_max = np.percentile(rgb, p_high)
    rgb_scaled = np.clip((rgb - v_min) / (v_max - v_min), 0.0, 1.0)
    return rgb_scaled


def main() -> None:
    data_path = Path("data/bilbao_crop.tif")
    if not data_path.is_file():
        raise FileNotFoundError(
            f"{data_path} not found. Run 's2clouds download -c examples/bilbao_clouds.toml' first."
        )

    with rasterio.open(data_path) as ds:
        b02 = ds.read(1).astype(float)  # Blue
        b03 = ds.read(2).astype(float)  # Green
        b04 = ds.read(3).astype(float)  # Red

    rgb = make_enhanced_rgb(b04, b03, b02)

    # Cloud window showing the chromatic fringe
    r0, r1 = 300, 420
    c0, c1 = 640, 760
    rgb_zoom = rgb[r0:r1, c0:c1]

    output_dir = Path("docs/img")
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 6))
    plt.imshow(rgb_zoom)
    plt.title("Paralaje entre bandas de Sentinel-2: Franjas en borde de nube")
    plt.xlabel("Columnas (px)")
    plt.ylabel("Filas (px)")
    plt.tight_layout()
    plt.savefig(output_dir / "cantabrico_cloud_fringe_zoom.png", dpi=180)
    plt.close()
    print("Figura guardada en docs/img/cantabrico_cloud_fringe_zoom.png")


if __name__ == "__main__":
    main()
