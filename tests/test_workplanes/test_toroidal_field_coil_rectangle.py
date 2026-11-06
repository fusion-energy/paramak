import math

import pytest

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


def test_diagonal_coils_are_not_clipped_by_the_wedge():
    "coils between the x and y axes reach further from the Z axis than their x or y extent"

    kwargs = dict(horizontal_start_point=(100, 100), vertical_mid_point=(300, 0), thickness=10, distance=10)
    whole = paramak.toroidal_field_coil_rectangle(azimuthal_placement_angles=[35, 55], **kwargs)
    cut = paramak.toroidal_field_coil_rectangle(azimuthal_placement_angles=[35, 55], rotation_angle=90, **kwargs)
    assert sum(solid.Volume() for solid in cut.vals()) == pytest.approx(whole.val().Volume(), rel=1e-4)


@pytest.mark.parametrize("mid_z", [0, 150, -50])
def test_coil_is_symmetric_about_the_vertical_mid_point(mid_z):
    coil = paramak.toroidal_field_coil_rectangle(
        horizontal_start_point=(20, 200), vertical_mid_point=(350, mid_z), thickness=30
    )
    bb = coil.val().BoundingBox()
    assert bb.zmax == pytest.approx(230, abs=1e-3)
    assert (bb.zmax + bb.zmin) / 2 == pytest.approx(mid_z, abs=1e-3)
