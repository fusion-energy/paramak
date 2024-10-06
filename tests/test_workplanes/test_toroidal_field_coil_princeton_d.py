
import paramak

def test_creation_of_inner_leg():
    solid_without_inner_leg = paramak.toroidal_field_coil_princeton_d(with_inner_leg=False)
    solid_with_inner_leg = paramak.toroidal_field_coil_princeton_d(with_inner_leg=True)

    assert solid_without_inner_leg.val().Volume() < solid_with_inner_leg.val().Volume()