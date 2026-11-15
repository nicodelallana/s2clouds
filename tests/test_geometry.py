"""Tests for orbital scan direction and rotation geometry (ec. 4 of Krauß 2021)."""

import numpy as np
import pytest

from s2clouds.geometry import (
    rotate_crop,
    satellite_ground_track_heading,
    scan_direction_phi,
    scan_rotation_angle,
    unrotate_crop,
)


def test_scan_direction_phi_bilbao():
    """Test ec. 4 for Bilbao / Cantabrian Sea (43.3 deg N) -> phi ≈ 101.9 deg."""
    phi = scan_direction_phi(43.3)
    assert pytest.approx(phi, abs=0.05) == 101.9
    assert round(phi, 1) == 101.9


def test_scan_direction_phi_frankfurt():
    """Test ec. 4 for Frankfurt (50.11 deg N) -> phi ≈ 103.5 deg (Krauß 2021)."""
    phi = scan_direction_phi(50.11)
    assert pytest.approx(phi, abs=0.05) == 103.5
    assert round(phi, 1) == 103.5


def test_scan_rotation_angle_bilbao():
    """Test rotation angle 90 - phi for Bilbao."""
    phi = scan_direction_phi(43.3)
    rotation_deg = scan_rotation_angle(phi)
    # 90 - 101.9 = -11.9 deg
    assert pytest.approx(rotation_deg, abs=0.1) == -11.9


def test_satellite_ground_track_heading_convention():
    """Contrast flight track phi angle with navigation heading convention."""
    heading = satellite_ground_track_heading(43.3)
    # Heading from North is ~191.9 deg (nominal spherical flight azimuth)
    assert pytest.approx(heading, abs=0.1) == 191.9
    # In s2motion, accounting for Earth's rotation at 43.3 deg N gives ~194.7 deg
    assert pytest.approx(heading, abs=3.5) == 194.7


def test_scan_direction_phi_invalid_latitude():
    """Test error handling when latitude exceeds orbit bounds."""
    with pytest.raises(ValueError, match="Orbit does not reach latitude"):
        scan_direction_phi(85.0)  # Beyond inclination 98.62 limit


def test_rotate_and_unrotate_image_2d():
    """Test 2D image rotation and unrotation cycle."""
    img = np.zeros((100, 100), dtype=float)
    img[40:60, 40:60] = 100.0

    angle_deg = -11.9
    rotated = rotate_crop(img, angle_deg, reshape=False, order=1)
    restored = unrotate_crop(rotated, angle_deg, reshape=False, order=1)

    # In center region, values should be closely preserved
    center_original = img[48:52, 48:52]
    center_restored = restored[48:52, 48:52]
    assert np.allclose(center_original, center_restored, atol=2.0)


def test_rotate_and_unrotate_image_3d():
    """Test multi-band (3, H, W) image rotation."""
    img_3d = np.ones((3, 50, 50), dtype=float) * 50.0
    angle_deg = 15.0

    rotated = rotate_crop(img_3d, angle_deg, reshape=False, order=1)
    assert rotated.shape == (3, 50, 50)
    assert np.allclose(rotated[:, 20:30, 20:30], 50.0, atol=0.1)
