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
                (0, 0, "straight"),
                (0, 20, "spline"),
                (10, 30, "spline"),
                (20, 20, "straight"),
                (20, 0, "straight"),
            ],
            path_points=[
                (50, 0),
                (20, 50),
                (50, 100)
            ]
        )
        test_shape.create_solid()

        assert test_shape.solid is not None

    def test_relative_shape_volume(self):
        """creates two SweepMixedShapes and checks that their relative volumes
        are correct"""

        test_shape_1 = SweepMixedShape(
            points=[
                (-10, 10, "straight"),
                (10, 10, "spline"),
                (15, 0, "spline"),
                (10, -10, "straight"),
                (-10, -10, "straight")
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
                (-20, 20, "straight"),
                (20, 20, "spline"),
                (30, 0, "spline"),
                (20, -20, "straight"),
                (-20, -20, "straight")
            ],
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
