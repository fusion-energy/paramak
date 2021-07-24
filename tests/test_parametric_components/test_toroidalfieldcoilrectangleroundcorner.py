
from math import pi

import pytest
from attr.setters import NO_OP
from paramak import ToroidalFieldCoilRectangleRoundCorners

obj = ToroidalFieldCoilRectangleRoundCorners(
    lower_inner_coordinates=(50, 0),
    mid_point_coordinates=(100, 100),
    thickness=20,
    distance=10,
    number_of_coils=1,
    with_inner_leg=False
)

obj2 = ToroidalFieldCoilRectangleRoundCorners(
    lower_inner_coordinates=(50, 0),
    mid_point_coordinates=(100, 100),
    thickness=20,
    distance=10,
    number_of_coils=1,
    with_inner_leg=True
)


def surface_area(
        lower_left,
        middle_right,
        thickness,
        extrusion_length,
        with_inner_leg=False,
        xz_face_only=False,
        extrusion_area_only=False):
    """
    Function calculates the total surface area of the TF coil from the
    coordinates given in the find_points function
    """
    test_object = ToroidalFieldCoilRectangleRoundCorners(
        lower_inner_coordinates=lower_left,
        mid_point_coordinates=middle_right,
        thickness=thickness,
        distance=extrusion_length,
        number_of_coils=1,
        with_inner_leg=with_inner_leg
    )

    analyse_attributes = test_object.analyse_attributes

    base, height, inner_rad, outter_rad = analyse_attributes

    # The surface area of the face in XZ plane is divisible into 5 segments
    base_segment_area = thickness * (base - inner_rad)
    vertical_segment_area = thickness * (height - (inner_rad * 2))
    corner_area = (pi / 4) * (outter_rad**2 - inner_rad**2)

    # XZ plane face area
    total_face_area = base_segment_area * 2 + \
        vertical_segment_area + corner_area * 2
    # The surface area of the planes in YZ plane
    contour_length = inner_rad * \
        (pi - 8) + pi * outter_rad + 2 * (2 * base + thickness + height)
    extrusion_area = contour_length * extrusion_length
    # Total Area
    total_bounding_surface = total_face_area * 2 + extrusion_area

    if with_inner_leg:
        # XZ plane face area
        total_face_area += thickness * height
        print(total_face_area)
        total_leg_surface_area = 2 * height * thickness + 2 * \
            extrusion_length * height + 2 * extrusion_length * thickness

        # Total bounding surface
        total_bounding_surface += total_leg_surface_area
        print("Face area: {}\nExtrusion Ares: {}\ntotal bounding area: {}"
              .format(total_face_area, extrusion_area, total_bounding_surface))

    if xz_face_only:
        return total_face_area

    if extrusion_area_only:
        return extrusion_area

    return total_bounding_surface


def volume(
        lower_left,
        middle_right,
        thickness,
        extrusion_length,
        with_inner_leg=False,
):
    """
    The function calculates the volume from the given coordinates used for
    parametarising the component in find_points function in core module it
    takes an additional variable for extrusion length which is the thickness
    of the coil
    """

    face_area = surface_area(
        lower_left,
        middle_right,
        thickness,
        extrusion_length,
        xz_face_only=True,
        with_inner_leg=with_inner_leg)
    print(face_area)
    total_shape_volume = face_area * extrusion_length

    return total_shape_volume


# Parametric Tests

@pytest.mark.parametric
def test_parametric_surface_area_with_leg():
    paramak_area = obj2.area
    package_area = surface_area(
        (50, 0), (100, 100), 20, 10, with_inner_leg=True)
    assert pytest.approx(package_area) == paramak_area


@pytest.mark.parametric
def test_parametric_volume_with_leg():
    paramak_vol = obj2.volume
    package_vol = volume((50, 0), (100, 100), 20, 10, with_inner_leg=True)
    assert pytest.approx(package_vol) == paramak_vol


@pytest.mark.parametric
def test_parametric_surface_area():
    paramak_area = obj.area
    package_area = surface_area((50, 0), (100, 100), 20, 10)
    assert pytest.approx(package_area) == paramak_area


@pytest.mark.parametric
def test_parametric_volume():
    paramak_vol = obj.volume
    package_vol = volume((50, 0), (100, 100), 20, 10)
    assert pytest.approx(package_vol) == paramak_vol


# Analytical Tests

@pytest.mark.analytical
def test_manual_area():
    analytical = 19872.92
    computational = surface_area((50, 0), (100, 100), 20, 10)
    assert pytest.approx(computational) == analytical


@pytest.mark.analytical
def test_manual_volume():
    analytical = 64909.73
    computational = volume((50, 0), (100, 100), 20, 10)
    assert pytest.approx(computational) == analytical


# Input Parameter Tests
# Lower Point Coordinate

@pytest.mark.dtype
def test_input_param_lower_inner():
    with pytest.raises(TypeError):
        test_object = ToroidalFieldCoilRectangleRoundCorners(
            lower_inner_coordinates=1,
            mid_point_coordinates=(100, 100),
            thickness=20,
            distance=10,
            number_of_coils=1,
        )
        assert test_object.solid is not None


@pytest.mark.length
def test_input_lower_point_tuple():
    with pytest.raises(ValueError):
        test_object = ToroidalFieldCoilRectangleRoundCorners(
            lower_inner_coordinates=(50, 0, 5),
            mid_point_coordinates=(100, 100),
            thickness=20,
            distance=10,
            number_of_coils=1,
        )
        assert test_object.solid is not None


@pytest.mark.dtype
def test_input_tuple_element_type_lower_point():
    with pytest.raises(TypeError):
        test_object = ToroidalFieldCoilRectangleRoundCorners(
            lower_inner_coordinates=(50, "string"),
            mid_point_coordinates=(100, 100),
            thickness=20,
            distance=10,
            number_of_coils=1,
        )
        assert test_object.solid is not None


@pytest.mark.dtype
def test_setter_lower_point():
    with pytest.raises(TypeError):
        obj2.lower_inner_coordinates = 1


@pytest.mark.length
def test_input_lower_point_tuple_length_with_setter():
    with pytest.raises(ValueError):
        obj2.lower_inner_coordinates = (0, 0, 0)


@pytest.mark.dtype
def test_lower_point_setter_elements_z():
    with pytest.raises(TypeError):
        obj.lower_inner_coordinates = (10, "string")


@pytest.mark.dtype
def test_lower_point_setter_elements_x():
    with pytest.raises(TypeError):
        obj.lower_inner_coordinates = ("string", 10)


# Mid Point Coordinate

@pytest.mark.dtype
def test_input_param_mid_point():
    with pytest.raises(TypeError):
        test_object = ToroidalFieldCoilRectangleRoundCorners(
            lower_inner_coordinates=(50, 0),
            mid_point_coordinates=1,
            thickness=20,
            distance=10,
            number_of_coils=1,
        )
        assert test_object.solid is not None


@pytest.mark.length
def test_input_tuple2():
    with pytest.raises(ValueError):
        test_object = ToroidalFieldCoilRectangleRoundCorners(
            lower_inner_coordinates=(50, 0),
            mid_point_coordinates=(100, 100, 100),
            thickness=20,
            distance=10,
            number_of_coils=1,
        )
        assert test_object.solid is not None


@pytest.mark.dtype
def test_input_tuple_element_type_mid_point():
    with pytest.raises(TypeError):
        test_object = ToroidalFieldCoilRectangleRoundCorners(
            lower_inner_coordinates=(50, 0),
            mid_point_coordinates=(100, "string"),
            thickness=20,
            distance=10,
            number_of_coils=1,
        )
        assert test_object.solid is not None


@pytest.mark.dtype
def test_setter_mid_point():
    with pytest.raises(TypeError):
        obj.mid_point_coordinates = 1


@pytest.mark.length
def test_input_mid_point_tuple_length_with_setter():
    with pytest.raises(ValueError):
        obj2.mid_point_coordinates = (0, 0, 0)


@pytest.mark.dtype
def test_mid_point_setter_elements_z():
    with pytest.raises(TypeError):
        obj.mid_point_coordinates = (10, "string")


@pytest.mark.dtype
def test_mid_point_setter_elements_x():
    with pytest.raises(TypeError):
        obj.mid_point_coordinates = ("string", 10)


# Coordinate Comparison

@pytest.mark.value
def test_input_x_coordinates():
    with pytest.raises(ValueError):
        test_object = ToroidalFieldCoilRectangleRoundCorners(
            lower_inner_coordinates=(50, 0),
            mid_point_coordinates=(0, 100),
            thickness=20,
            distance=10,
            number_of_coils=1,
        )
        assert test_object.solid is not None


@pytest.mark.value
def test_x_coords_with_setters():
    with pytest.raises(ValueError):
        obj.lower_inner_coordinates = (150, 0)
        obj.mid_point_coordinates = (100, 0)


# Thickness Parameter

@pytest.mark.dtype
def test_input_param_thickness():
    with pytest.raises(TypeError):
        test_object = ToroidalFieldCoilRectangleRoundCorners(
            lower_inner_coordinates=(50, 0),
            mid_point_coordinates=(100, 100),
            thickness="fail",
            distance=10,
            number_of_coils=1,
        )
        assert test_object.solid is not None


@pytest.mark.dtype
def test_input_param_thickness2():
    test_object = ToroidalFieldCoilRectangleRoundCorners(
        lower_inner_coordinates=(50, 0),
        mid_point_coordinates=(100, 100),
        thickness=50,
        distance=10,
        number_of_coils=1,
    )
    inner_radius = test_object.analyse_attributes[2]
    outer_radius = test_object.analyse_attributes[3]

    check_inner = 50 * 0.1
    check_outer = 50 * 1.1
    assert inner_radius == check_inner
    assert outer_radius == check_outer


@pytest.mark.dtype
def test_thickness_setter():
    with pytest.raises(TypeError):
        obj.thickness = "string"


# Extrusion Distance

@pytest.mark.dtype
def test_input_param_distance():
    with pytest.raises(TypeError):
        test_object = ToroidalFieldCoilRectangleRoundCorners(
            lower_inner_coordinates=(50, 0),
            mid_point_coordinates=(100, 100),
            thickness=20,
            distance="fail",
            number_of_coils=1,
        )
        assert test_object.solid is not None


@pytest.mark.dtype
def test_distance_setter():
    with pytest.raises(TypeError):
        obj.distance = "string"


# Number of Coils

@pytest.mark.value
def test_input_num_coils():
    with pytest.raises(TypeError):
        test_object = ToroidalFieldCoilRectangleRoundCorners(
            lower_inner_coordinates=(50, 0),
            mid_point_coordinates=(100, 100),
            thickness=20,
            distance=10,
            number_of_coils=1.5,
        )
        assert test_object.solid is not None


@pytest.mark.dtype
def test_num_coil_setter():
    with pytest.raises(TypeError):
        obj2.number_of_coils = 1.4
