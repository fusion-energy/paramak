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


if __name__ == "__main__":
    unittest.main()
    