import pytest

import paramak
from paramak.utils import (
    ValidationError,
    validate_non_negative,
    validate_number,
    validate_plasma_radial_build,
    validate_positive,
    validate_rotation_angle,
)

RADIAL_BUILD = [
    (paramak.LayerType.GAP, 10),
    (paramak.LayerType.SOLID, 30),
    (paramak.LayerType.SOLID, 50),
    (paramak.LayerType.SOLID, 10),
    (paramak.LayerType.SOLID, 120),
    (paramak.LayerType.SOLID, 20),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.PLASMA, 300),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.SOLID, 20),
    (paramak.LayerType.SOLID, 120),
    (paramak.LayerType.SOLID, 10),
]


@pytest.mark.parametrize("value", ["10", None, True, [1]])
def test_validate_number_rejects_non_numbers(value):
    with pytest.raises(TypeError, match="height must be a number"):
        validate_number(value, "height")


@pytest.mark.parametrize("value", [1, 0.5, 1e9])
def test_validate_positive_accepts_positive_numbers(value):
    validate_positive(value, "height")


@pytest.mark.parametrize("value", [0, -1, -0.1])
def test_validate_positive_rejects_zero_and_negative(value):
    with pytest.raises(ValueError, match="height must be positive"):
        validate_positive(value, "height")


def test_validate_non_negative():
    validate_non_negative(0, "inner_radius")
    with pytest.raises(ValueError, match="inner_radius must be zero or positive"):
        validate_non_negative(-1, "inner_radius")


@pytest.mark.parametrize("rotation_angle", [0, -30, 360.1, 400])
def test_validate_rotation_angle_out_of_range(rotation_angle):
    with pytest.raises(ValueError, match="rotation_angle must be above 0 and at most 360"):
        validate_rotation_angle(rotation_angle)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
@pytest.mark.parametrize("validator", [validate_number, validate_positive, validate_non_negative])
def test_validators_reject_non_finite_numbers(validator, value):
    with pytest.raises(ValueError, match="height must be a finite number"):
        validator(value, "height")


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_validate_rotation_angle_rejects_non_finite_numbers(value):
    with pytest.raises(ValueError, match="rotation_angle must be a finite number"):
        validate_rotation_angle(value)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_validate_plasma_radial_build_rejects_non_finite_thickness(value):
    radial_build = [
        (paramak.LayerType.GAP, 1),
        (paramak.LayerType.PLASMA, 100),
        (paramak.LayerType.GAP, 1),
        (paramak.LayerType.SOLID, value),
    ]
    with pytest.raises(ValidationError, match=f"Non-finite value '{value}' at index 3 of the radial_build"):
        validate_plasma_radial_build(radial_build)


@pytest.mark.parametrize("function", [paramak.tokamak_from_plasma, paramak.spherical_tokamak_from_plasma])
@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_reactor_rejects_non_finite_layer_thickness(function, value):
    radial_build = list(RADIAL_BUILD)
    radial_build[-2] = (paramak.LayerType.SOLID, value)
    with pytest.raises(ValueError, match=f"Non-finite value '{value}' at index 10 of the radial_build"):
        function(radial_build=radial_build, rotation_angle=90)


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_workplane_rejects_non_finite_values(value):
    with pytest.raises(ValueError, match="height must be a finite number"):
        paramak.poloidal_field_coil(height=value, width=10, center_point=(100, 0))


def test_validation_error_is_a_value_error():
    assert issubclass(ValidationError, ValueError)


@pytest.mark.parametrize("function", [paramak.tokamak_from_plasma, paramak.spherical_tokamak_from_plasma])
@pytest.mark.parametrize("thickness", [0, -120])
def test_reactor_rejects_non_positive_layer_thickness(function, thickness):
    radial_build = list(RADIAL_BUILD)
    radial_build[-2] = (paramak.LayerType.SOLID, thickness)
    with pytest.raises(ValueError, match=f"Non-positive value '{thickness}' at index 10 of the radial_build"):
        function(radial_build=radial_build, rotation_angle=90)


def test_reactor_rejects_bad_vertical_build():
    vertical_build = [
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.GAP, 50),
        (paramak.LayerType.PLASMA, 700),
        (paramak.LayerType.GAP, -60),
        (paramak.LayerType.SOLID, 15),
    ]
    with pytest.raises(ValueError, match="Non-positive value '-60' at index 3 of the vertical_build"):
        paramak.tokamak(radial_build=RADIAL_BUILD, vertical_build=vertical_build, rotation_angle=90)


def test_reactor_rejects_malformed_layer():
    radial_build = list(RADIAL_BUILD)
    radial_build[-1] = (paramak.LayerType.SOLID,)
    with pytest.raises(ValueError, match="should be a tuple of"):
        paramak.tokamak_from_plasma(radial_build=radial_build, rotation_angle=90)


@pytest.mark.parametrize("function", [paramak.tokamak_from_plasma, paramak.spherical_tokamak_from_plasma])
@pytest.mark.parametrize("rotation_angle", [0, 400])
def test_reactor_rejects_rotation_angle_out_of_range(function, rotation_angle):
    with pytest.raises(ValueError, match="rotation_angle must be above 0 and at most 360"):
        function(radial_build=RADIAL_BUILD, rotation_angle=rotation_angle)


WORKPLANES = [
    (
        paramak.blanket_constant_thickness_arc_h,
        dict(inner_mid_point=(100, 0), inner_upper_point=(50, 100), inner_lower_point=(50, -100), thickness=10),
    ),
    (paramak.blanket_from_plasma, dict(thickness=20, start_angle=-90, stop_angle=90)),
    (paramak.center_column_shield_cylinder, dict(height=100, inner_radius=10, thickness=10)),
    (paramak.constant_thickness_dome, dict()),
    (paramak.cutting_wedge, dict(height=10, radius=100)),
    (paramak.dished_vacuum_vessel, dict()),
    (paramak.plasma_simplified, dict()),
    (paramak.poloidal_field_coil, dict(height=10, width=10, center_point=(100, 0))),
    (paramak.poloidal_field_coil_case, dict(coil_height=10, coil_width=10, casing_thickness=2, center_point=(100, 0))),
    (paramak.revolved_shape, dict(points=[(10, 0, "straight"), (20, 0, "straight"), (20, 10, "straight")])),
    (paramak.toroidal_field_coil_princeton_d, dict()),
    (paramak.toroidal_field_coil_rectangle, dict()),
    (paramak.u_shaped_dome, dict()),
]


@pytest.mark.parametrize("function, kwargs", WORKPLANES)
@pytest.mark.parametrize("rotation_angle", [0, -30, 361])
def test_workplane_rejects_rotation_angle_out_of_range(function, kwargs, rotation_angle):
    with pytest.raises(ValueError, match="rotation_angle must be above 0 and at most 360"):
        function(rotation_angle=rotation_angle, **kwargs)


@pytest.mark.parametrize(
    "function, kwargs, name",
    [
        (
            paramak.blanket_constant_thickness_arc_h,
            dict(inner_mid_point=(100, 0), inner_upper_point=(50, 100), inner_lower_point=(50, -100), thickness=-10),
            "thickness",
        ),
        (paramak.cutting_wedge, dict(height=0, radius=100), "height"),
        (paramak.cutting_wedge, dict(height=10, radius=-1), "radius"),
        (
            paramak.poloidal_field_coil_case,
            dict(coil_height=10, coil_width=10, casing_thickness=0, center_point=(100, 0)),
            "casing_thickness",
        ),
        (paramak.plasma_simplified, dict(num_points=0), "num_points"),
        (paramak.u_shaped_dome, dict(dish_height=-5), "dish_height"),
        (paramak.dished_vacuum_vessel, dict(radius=-300), "radius"),
    ],
)
def test_workplane_rejects_non_positive_values(function, kwargs, name):
    with pytest.raises(ValueError, match=f"{name} must be positive"):
        function(**kwargs)


def test_workplane_rejects_non_numbers():
    with pytest.raises(TypeError, match="height must be a number, not str"):
        paramak.poloidal_field_coil(height="10", width=10, center_point=(100, 0))


def test_center_column_accepts_zero_inner_radius():
    paramak.center_column_shield_cylinder(height=100, inner_radius=0, thickness=10)
    with pytest.raises(ValueError, match="inner_radius must be zero or positive"):
        paramak.center_column_shield_cylinder(height=100, inner_radius=-1, thickness=10)


@pytest.mark.parametrize("function", [paramak.plasma_simplified, paramak.blanket_from_plasma])
def test_num_points_must_be_an_integer(function):
    kwargs = dict(thickness=20, start_angle=-90, stop_angle=90) if function is paramak.blanket_from_plasma else {}
    with pytest.raises(TypeError, match="num_points must be an integer"):
        function(num_points=50.5, **kwargs)


def test_numpy_numbers_are_accepted():
    import numpy as np

    paramak.center_column_shield_cylinder(
        height=np.float64(100),
        inner_radius=np.int64(10),
        thickness=np.int64(10),
        reference_point=("lower", np.int64(0)),
    )
    paramak.plasma_simplified(num_points=np.int64(50))
