import pytest

import paramak


def test_creation_of_inner_leg():
    solid_without_inner_leg = paramak.toroidal_field_coil_princeton_d(with_inner_leg=False)
    solid_with_inner_leg = paramak.toroidal_field_coil_princeton_d(with_inner_leg=True)

    assert solid_without_inner_leg.val().Volume() < solid_with_inner_leg.val().Volume()


def test_rotation_angle():
    solid_360_uncut = paramak.toroidal_field_coil_princeton_d(azimuthal_placement_angles=[0, 180], rotation_angle=360)
    solid_180_uncut = paramak.toroidal_field_coil_princeton_d(azimuthal_placement_angles=[0, 180], rotation_angle=360)
    solid_180_cut = paramak.toroidal_field_coil_princeton_d(azimuthal_placement_angles=[0, 180], rotation_angle=180)

    assert solid_360_uncut.val().Volume() == solid_180_uncut.val().Volume()
    # checks relative volume difference
    assert (
        abs(solid_180_cut.val().Volume() - 0.5 * solid_180_uncut.val().Volume())
        / (0.5 * solid_180_uncut.val().Volume())
        < 0.00001
    )


def test_no_integration_warnings():
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        paramak.toroidal_field_coil_princeton_d()


def test_r2_must_be_beyond_the_inner_leg():
    with pytest.raises(ValueError, match="r2 .120. must be greater than r1 . thickness .130."):
        paramak.toroidal_field_coil_princeton_d(r1=100, r2=120, thickness=30)


def test_coil_extends_from_r1_to_r2_plus_thickness():
    bb = paramak.toroidal_field_coil_princeton_d(r1=100, r2=300, thickness=30).val().BoundingBox()
    assert bb.xmin == pytest.approx(100, abs=1e-3)
    assert bb.xmax == pytest.approx(330, rel=0.01)
