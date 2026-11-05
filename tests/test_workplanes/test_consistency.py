import pytest

import paramak


@pytest.mark.parametrize(
    "function, kwargs",
    [
        (paramak.cutting_wedge, dict(height=10, radius=100)),
        (paramak.constant_thickness_dome, dict()),
        (paramak.blanket_constant_thickness_arc_h, dict(inner_mid_point=(100, 0), inner_upper_point=(50, 100), inner_lower_point=(50, -100), thickness=10)),
        (paramak.poloidal_field_coil, dict(height=10, width=10, center_point=(100, 0))),
    ],
)
def test_color_is_stored_as_given(function, kwargs):
    assert function(color=(0.1, 0.2, 0.3), **kwargs).color == (0.1, 0.2, 0.3)


def test_unknown_arguments_raise():
    with pytest.raises(TypeError, match="rotation_angel"):
        paramak.constant_thickness_dome(rotation_angel=10)


@pytest.mark.parametrize("function", [paramak.dished_vacuum_vessel, paramak.u_shaped_dome])
def test_vessel_color_and_origin_apply_to_every_part(function):
    parts = function()
    moved = function(origin=(0, 0, 100), color=(1.0, 0.0, 0.0))
    for part, moved_part in zip(parts, moved):
        assert moved_part.color == (1.0, 0.0, 0.0)
        assert moved_part.val().BoundingBox().zmin == pytest.approx(part.val().BoundingBox().zmin + 100, abs=1e-3)
        assert moved_part.val().Volume() == pytest.approx(part.val().Volume(), rel=1e-6)


@pytest.mark.parametrize("function", [paramak.toroidal_field_coil_rectangle, paramak.toroidal_field_coil_princeton_d])
def test_tf_coil_wedge_follows_the_origin(function):
    coil = function(rotation_angle=90, azimuthal_placement_angles=[45])
    moved = function(rotation_angle=90, azimuthal_placement_angles=[45], origin=(0, 0, 100))
    assert moved.val().Volume() == pytest.approx(coil.val().Volume(), rel=1e-4)
