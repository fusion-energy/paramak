import cadquery as cq

import paramak


def test_creation():
    test_shape = paramak.center_column_shield_cylinder(height=100, inner_radius=10, thickness=20, rotation_angle=90)

    cq.exporters.export(test_shape, "center_column_shield_cylinder.step")


def test_reference_point():
    test_shape = paramak.center_column_shield_cylinder(
        height=100, inner_radius=10, thickness=20, rotation_angle=90, reference_point=("center", 0)
    )
    assert test_shape.val().BoundingBox().zmin == -50
    assert test_shape.val().BoundingBox().zmax == 50

    test_shape = paramak.center_column_shield_cylinder(
        height=100, inner_radius=10, thickness=20, rotation_angle=90, reference_point=("lower", 200)
    )
    assert test_shape.val().BoundingBox().zmin == 200
    assert test_shape.val().BoundingBox().zmax == 300

    test_shape = paramak.center_column_shield_cylinder(
        height=100, inner_radius=10, thickness=20, rotation_angle=90, reference_point=("center", -200)
    )
    assert test_shape.val().BoundingBox().zmin == -250
    assert test_shape.val().BoundingBox().zmax == -150
