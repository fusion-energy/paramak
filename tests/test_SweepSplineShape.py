import os
import unittest
from pathlib import Path

import pytest

from paramak import SweepSplineShape


class test_object_properties(unittest.TestCase):
    def test_solid_construction(self):
        """checks that a SweepSplineShape solid can be created"""

        test_shape = SweepSplineShape(
            points=[
                (-20, 20),
                (20, 20),
                (20, -20),
                (-20, -20)
            ],
            path_points=[
                (50, 0),
                (20, 200),
                (50, 400)
            ]
        )
        test_shape.create_solid()

        assert test_shape.solid is not None

    def test_relative_shape_volume(self):
        """creates two SweepSplineShapes and checks that their relative volumes
        are correct"""

        test_shape_1 = SweepSplineShape(
            points=[
                (-20, 20),
                (20, 20),
                (20, -20),
                (-20, -20)
            ],
            path_points=[
                (50, 0),
                (30, 50),
                (60, 100),
                (50, 150)
            ]
        )
        test_shape_1.create_solid()

        test_shape_2 = SweepSplineShape(
            points=[
                (-10, 10),
                (10, 10),
                (10, -10),
                (-10, -10)
            ],
            path_points=[
                (50, 0),
                (30, 50),
                (60, 100),
                (50, 150)
            ]
        )
        test_shape_2.create_solid()

        assert test_shape_1.volume == pytest.approx(
            test_shape_2.volume * 4, abs=1)


if __name__ == "__main__":
    unittest.main()
