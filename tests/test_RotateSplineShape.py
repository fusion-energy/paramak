import unittest

import pytest
import numpy as np

from paramak import RotateSplineShape


class test_object_properties(unittest.TestCase):
    def test_absolute_shape_volume(self):
        """creates a rotated shape using spline connections and checks the volume
        is correct"""

        test_shape = RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)])

        test_shape.rotation_angle = 360
        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume > 100

    def test_cut_volume(self):
        """creates a rotated shape using spline connections with another shape cut
        out and checks that the volume is correct"""

        inner_shape = RotateSplineShape(
            points=[(5, 5), (5, 10), (10, 10), (10, 5)], rotation_angle=180
        )

        outer_shape = RotateSplineShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)], rotation_angle=180
        )

        outer_shape_with_cut = RotateSplineShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)],
            cut=inner_shape,
            rotation_angle=180,
        )

        assert inner_shape.volume == pytest.approx(900.88, abs=0.1)
        assert outer_shape.volume == pytest.approx(2881.76, abs=0.1)
        assert outer_shape_with_cut.volume == pytest.approx(
            2881.76 - 900.88, abs=0.2)

    def test_shape_azimuth_placement_angles_iterabel(self):
        """checks that azimuth_placement_angle can take an Iterable
        """
        test_shape = RotateSplineShape(
            points=[(200, 100), (200, 200), (500, 200), (500, 100)],
            azimuth_placement_angle=[0, 180])
        assert test_shape.solid is not None

    def test_incorrect_color_values(self):
            """Checks incorrect argument values for RotateSplineShape"""
            def test_string_color_value():
                """Tries to make a RotateSplineShape is string values for color"""
                test_shape = RotateSplineShape(
                    points=[(200, 100), (200, 200), (500, 200), (500, 100)],
                    azimuth_placement_angle=np.linspace(0,90,2),
                    color=('1','0','1')
                )

            self.assertRaises(
                ValueError,
                test_string_color_value
            )


if __name__ == "__main__":
    unittest.main()
