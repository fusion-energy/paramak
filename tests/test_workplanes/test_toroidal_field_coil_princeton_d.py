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
