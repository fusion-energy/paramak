import os
import unittest
from pathlib import Path

import pytest

from paramak import SweepMixedShape


class test_object_properties(unittest.TestCase):
    def test_solid_construction(self):
        """checks that a SweepMixedShape solid can be created"""

        test_shape = SweepMixedShape(
            points=[
                (-10, -10, "straight"),
                (-10, 10, "spline"),
                (0, 20, "spline"),
                (10, 10, "circle"),
                (0, 0, "circle"),
                (10, -10, "straight")
            ],
            path_points=[
                (50, 0),
                (20, 50),
                (50, 100)
            ]
        )
        test_shape.create_solid()

        assert test_shape.solid is not None

    def test_solid_construction(self):
        """checks that a SweepMixedShape solid can be created with workplane
        YZ"""

        test_shape = SweepMixedShape(
            points=[
                (-10, -10, "straight"),
                (-10, 10, "spline"),
                (0, 20, "spline"),
                (10, 10, "circle"),
                (0, 0, "circle"),
                (10, -10, "straight")
            ],
            path_points=[
                (50, 0),
                (20, 50),
                (50, 100)
            ],
            workplane='YZ',
            path_workplane="YX"
        )

        assert test_shape.solid is not None

    def test_solid_construction_workplane_XZ(self):
        """checks that a SweepMixedShape solid can be created with workplane
        XZ"""

        test_shape = SweepMixedShape(
            points=[
                (-10, -10, "straight"),
                (-10, 10, "spline"),
                (0, 20, "spline"),
                (10, 10, "circle"),
                (0, 0, "circle"),
                (10, -10, "straight")
            ],
            path_points=[
                (50, 0),
                (20, 50),
                (50, 100)
            ],
            workplane='XZ',
            path_workplane="XY"
        )

        assert test_shape.solid is not None

    def test_relative_shape_volume(self):
        """creates two SweepMixedShapes and checks that their relative volumes
        are correct"""

        test_shape_1 = SweepMixedShape(
            points=[
                (-10, -10, "straight"),
                (-10, 10, "spline"),
                (0, 20, "spline"),
                (10, 10, "circle"),
                (0, 0, "circle"),
                (10, -10, "straight")
            ],
            path_points=[
                (50, 0),
                (30, 50),
                (50, 100)
            ]
        )
        test_shape_1.create_solid()

        test_shape_2 = SweepMixedShape(
            points=[
                (-20, -20, "straight"),
                (-20, 20, "spline"),
                (0, 40, "spline"),
                (20, 20, "circle"),
                (0, 0, "circle"),
                (20, -20, "straight")
            ],
            path_points=[
                (50, 0),
                (30, 50),
                (50, 100)
            ]
        )
        test_shape_2.create_solid()

        assert test_shape_1.volume == pytest.approx(
            test_shape_2.volume * 0.25, rel=0.01)

    def test_iterable_azimuthal_placement(self):
        """checks that swept solids can be placed at multiple azimuth placement angles"""

        test_shape = SweepMixedShape(
            points=[
                (-10, -10, "straight"),
                (-10, 10, "spline"),
                (0, 20, "spline"),
                (10, 10, "circle"),
                (0, 0, "circle"),
                (10, -10, "straight")
            ],
            path_points=[
                (50, 0),
                (30, 50),
                (60, 100),
                (50, 150)
            ]
        )
        test_shape.create_solid()

        test_volume = test_shape.volume

        test_shape.azimuth_placement_angle = [0, 90, 180, 270]

        assert test_shape.volume == pytest.approx(test_volume * 4, rel=0.01)

    def test_workplane_path_workplane_error_raises(self):
        """checks that errors are raised when disallowed workplane and path_workplane
        combinations are used"""

        def workplane_and_path_workplane_equal():
            test_shape = SweepMixedShape(
                points=[
                    (-10, -10, "straight"),
                    (-10, 10, "spline"),
                    (0, 20, "spline"),
                    (10, 10, "circle"),
                    (0, 0, "circle"),
                    (10, -10, "straight")
                ],
                path_points=[(50, 0), (30, 50), (60, 100), (50, 150)],
                workplane="XZ",
                path_workplane="XZ"
            )

        def invalid_relative_workplane_and_path_workplane():
            test_shape = SweepMixedShape(
                points=[
                    (-10, -10, "straight"),
                    (-10, 10, "spline"),
                    (0, 20, "spline"),
                    (10, 10, "circle"),
                    (0, 0, "circle"),
                    (10, -10, "straight")
                ],
                path_points=[(50, 0), (30, 50), (60, 100), (50, 150)],
                workplane="XZ",
                path_workplane="YZ"
            )

        self.assertRaises(ValueError, workplane_and_path_workplane_equal)
        self.assertRaises(
            ValueError,
            invalid_relative_workplane_and_path_workplane)

    def test_workplane_opposite_direction(self):
        """Checks that a solid can be created with workplane XZ and path_workplane XY"""

        test_shape = SweepMixedShape(
            points = [
                (-10, -10, "straight"),
                (-10, 10, "spline"),
                (0, 20, "spline"),
                (10, 10, "circle"),
                (0, 0, "circle"),
                (10, -10, "straight")
            ],
            path_points = [
                (50, 0), (30, 50), (50, 100)
            ],
            workplane = "XZ",
            path_workplane = "XY"
        )

        assert test_shape.solid is not None


if __name__ == "__main__":
    unittest.main()
