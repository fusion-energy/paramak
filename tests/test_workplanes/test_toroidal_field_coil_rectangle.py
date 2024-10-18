import math

from cadquery import exporters

import paramak


def test_construction():
    toroidal_field_coil_rectangle = paramak.toroidal_field_coil_rectangle(azimuthal_placement_angles=[0, 90, 180])

    exporters.export(toroidal_field_coil_rectangle, "toroidal_field_coil_rectangle.step")


def test_volume_rotation_angle():
    toroidal_field_coil_rectangle = paramak.toroidal_field_coil_rectangle(
        azimuthal_placement_angles=[0, 90], horizontal_start_point=(50, 200)
    )
    half_toroidal_field_coil_rectangle = paramak.toroidal_field_coil_rectangle(
        azimuthal_placement_angles=[0], horizontal_start_point=(50, 200)
    )

    assert math.isclose(
        half_toroidal_field_coil_rectangle.val().Volume(), toroidal_field_coil_rectangle.val().Volume() / 2
    )


def test_rotation_angle():
    solid_360_uncut = paramak.toroidal_field_coil_rectangle(azimuthal_placement_angles=[0, 180], rotation_angle=360)
    solid_180_uncut = paramak.toroidal_field_coil_rectangle(azimuthal_placement_angles=[0, 180], rotation_angle=360)
    solid_180_cut = paramak.toroidal_field_coil_rectangle(azimuthal_placement_angles=[0, 180], rotation_angle=180)

    assert solid_360_uncut.val().Volume() == solid_180_uncut.val().Volume()
    # checks relative volume difference
    assert (
        abs(solid_180_cut.val().Volume() - 0.5 * solid_180_uncut.val().Volume())
        / (0.5 * solid_180_uncut.val().Volume())
        < 0.00001
    )
