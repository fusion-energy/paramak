import math

import paramak


def test_relative_shape_volume():
    """Creates two blankets using the blanket_constant_thickness_arc_h
    parametric component and checks that their relative volumes and face areas
    are correct."""

    test_shape_360 = paramak.blanket_constant_thickness_arc_h(
        inner_lower_point=(300, -200),
        inner_mid_point=(500, 0),
        inner_upper_point=(300, 200),
        thickness=20,
        rotation_angle=360,
    )

    test_shape_180 = paramak.blanket_constant_thickness_arc_h(
        inner_lower_point=(300, -200),
        inner_mid_point=(500, 0),
        inner_upper_point=(300, 200),
        thickness=20,
        rotation_angle=180,
    )

    assert test_shape_360.val().Volume() > 1000
    assert math.isclose(test_shape_360.val().Volume(), 2 * test_shape_180.val().Volume())

    assert len(test_shape_360.val().Faces()) == 4

    areas = [face.Area() for face in test_shape_360.val().Faces()]
    assert len(set([round(i) for i in areas])) == 3

    areas = [face.Area() for face in test_shape_180.val().Faces()]
    assert len(areas) == 6
    assert len(set([round(i) for i in areas])) == 4
