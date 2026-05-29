import cadquery as cq
import pytest

import paramak


def test_creation():
    points = [
        (300, -700, "straight"),
        (300, -300, "spline"),
        (470, -240, "spline"),
        (600, -700, "straight"),
    ]
    test_shape = paramak.revolved_shape(points=points, rotation_angle=180)

    assert test_shape.val().isValid()
    assert test_shape.val().Volume() > 0
    cq.exporters.export(test_shape, "revolved_shape.step")


def test_rotation_angle():
    # a rectangular profile away from the axis, so volume scales with angle
    points = [
        (300, -700, "straight"),
        (300, -300, "straight"),
        (600, -300, "straight"),
        (600, -700, "straight"),
    ]
    half = paramak.revolved_shape(points=points, rotation_angle=180)
    full = paramak.revolved_shape(points=points, rotation_angle=360)

    assert full.val().Volume() == pytest.approx(2 * half.val().Volume(), rel=0.01)


def test_name_and_color():
    points = [
        (300, -700, "straight"),
        (300, -300, "straight"),
        (600, -300, "straight"),
        (600, -700, "straight"),
    ]
    test_shape = paramak.revolved_shape(points=points, name="my_divertor", color=(0.1, 0.2, 0.3))

    assert test_shape.name == "my_divertor"
    assert test_shape.color == (0.1, 0.2, 0.3)


def test_too_few_points_raises():
    with pytest.raises(ValueError):
        paramak.revolved_shape(points=[(0, 0, "straight"), (1, 1, "straight")])
