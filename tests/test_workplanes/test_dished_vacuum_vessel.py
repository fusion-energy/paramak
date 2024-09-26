import cadquery as cq

import paramak


def test_creation():
    lower_dome_section, cylinder_section, upper_dome_section = paramak.dished_vacuum_vessel()
    cq.exporters.export(lower_dome_section, "lower_dome_section.step")
    cq.exporters.export(cylinder_section, "cylinder_section.step")
    cq.exporters.export(upper_dome_section, "upper_dome_section.step")


def test_reference_point():
    lower_dome_section, cylinder_section, upper_dome_section = paramak.dished_vacuum_vessel(
        dish_height=(50, 50), cylinder_height=400, thickness=15, reference_point=("center", 0)
    )
    assert lower_dome_section.val().BoundingBox().zmin == -265
    assert upper_dome_section.val().BoundingBox().zmax == 265

    lower_dome_section, cylinder_section, upper_dome_section = paramak.dished_vacuum_vessel(
        dish_height=(50, 50), cylinder_height=400, thickness=15, reference_point=("lower", 200)
    )
    assert lower_dome_section.val().BoundingBox().zmin == 200
    assert upper_dome_section.val().BoundingBox().zmax == 730

    lower_dome_section, cylinder_section, upper_dome_section = paramak.dished_vacuum_vessel(
        dish_height=(50, 50), cylinder_height=400, thickness=15, reference_point=("center", -200)
    )
    assert lower_dome_section.val().BoundingBox().zmin == -465
    assert upper_dome_section.val().BoundingBox().zmax == 65
