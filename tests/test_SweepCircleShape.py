import os
import math
import unittest
from pathlib import Path

import pytest

from paramak import SweepCircleShape


class test_object_properties(unittest.TestCase):
    def test_solid_construction(self):
        """checks that a SweepCircleShape solid can be created"""

        test_shape = SweepCircleShape(
            radius=10,
            path_points=[
                (50, 0),
                (30, 50),
                (50, 100)
            ]
        )
        test_shape.create_solid()

        assert test_shape.solid is not None

    def test_absolute_shape_volume(self):
        """creates a SweepCircleshape and checks that the volume is correct"""

        test_shape = SweepCircleShape(
            radius=10,
            path_points=[
                (50, 0),
                (50, 50),
                (50, 100)
            ]
        )
        test_shape.create_solid()

        assert test_shape.volume == pytest.approx(math.pi * 10**2 * 100)

    def test_relative_shape_volume(self):
        """creates two SweepCircleShapes and checks that their relative volumes
        are correct"""

        test_shape_1 = SweepCircleShape(
            radius=10,
            path_points=[
                (50, 0),
                (30, 50),
                (50, 100)
            ]
        )
        test_shape_1.create_solid()

        test_shape_2 = SweepCircleShape(
            radius=20,
            path_points=[
                (50, 0),
                (30, 50),
                (50, 100)
            ]
        )
        test_shape_2.create_solid()

        assert test_shape_1.volume == pytest.approx(test_shape_2.volume * 0.25)

    def test_iterable_azimuthal_placement(self):
        """checks that swept solids can be placed at multiple azimuth placement angles"""

        test_shape = SweepCircleShape(
            radius=10,
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
            test_shape = SweepCircleShape(
                radius=20,
                path_points=[(50, 0), (30, 50), (60, 100), (50, 150)],
                workplane="XZ",
                path_workplane="XZ"
            )

        def invalid_relative_workplane_and_path_workplane():
            test_shape = SweepCircleShape(
                radius=20,
                path_points=[(50, 0), (30, 50), (60, 100), (50, 150)],
                workplane="XZ",
                path_workplane="YZ"
            )

        self.assertRaises(ValueError, workplane_and_path_workplane_equal)
        self.assertRaises(ValueError, invalid_relative_workplane_and_path_workplane)


if __name__ == "__main__":
    unittest.main()
