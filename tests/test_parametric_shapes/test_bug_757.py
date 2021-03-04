
import unittest

import pytest
from paramak import RotateSplineShape, ExtrudeSplineShape


class TestBug(unittest.TestCase):
    def test_default_parameters(self):
        """Checks bug of issue #757."""
        shape1 = RotateSplineShape(
            points=[
                (1.1 + 0, 0),
                (1.1 + 0.5, 0),
                (1.1 + 0.5, 0.5),
                (1.1 + 0, 0.5),
            ],
            rotation_angle=360
        )

        shape2 = ExtrudeSplineShape(
            points=[
                (0 + 1, 0),
                (1 + 1, 0),
                (1 + 1, 1),
                (0 + 1, 1),
            ],
            distance=0.5,
            azimuth_placement_angle=0,
            cut=shape1
        )

        shape2.solid

if __name__ == "__main__":
    unittest.main()
