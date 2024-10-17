import math

from cadquery import exporters

import paramak


def test_construction():
    poloidal_field_coil = paramak.poloidal_field_coil(height=20, width=10, center_point=(100, 50), rotation_angle=360)

    exporters.export(poloidal_field_coil, "poloidal_field_coil.step")


def test_volume_rotation_angle():
    poloidal_field_coil = paramak.poloidal_field_coil(height=20, width=10, center_point=(100, 50), rotation_angle=360)
    half_poloidal_field_coil = paramak.poloidal_field_coil(
        height=20, width=10, center_point=(100, 50), rotation_angle=180
    )

    assert math.isclose(half_poloidal_field_coil.val().Volume(), poloidal_field_coil.val().Volume() / 2)
