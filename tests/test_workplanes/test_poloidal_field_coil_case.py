import math

from cadquery import exporters

import paramak


def test_construction():
    poloidal_field_coil_case = paramak.poloidal_field_coil_case(
        coil_height=20, coil_width=10, center_point=(100, 50), rotation_angle=360, casing_thickness=10
    )

    exporters.export(poloidal_field_coil_case, "poloidal_field_coil_case.step")


def test_volume_rotation_angle():
    poloidal_field_coil_case = paramak.poloidal_field_coil_case(
        coil_height=20, coil_width=10, center_point=(100, 50), casing_thickness=10, rotation_angle=360
    )
    half_poloidal_field_coil_case = paramak.poloidal_field_coil_case(
        coil_height=20, coil_width=10, center_point=(100, 50), casing_thickness=10, rotation_angle=180
    )

    assert math.isclose(half_poloidal_field_coil_case.val().Volume(), poloidal_field_coil_case.val().Volume() / 2)
