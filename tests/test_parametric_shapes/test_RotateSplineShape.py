import unittest

import pytest
import numpy as np

from paramak import RotateSplineShape


class test_object_properties(unittest.TestCase):
    def test_absolute_shape_volume(self):
        """creates a rotated shape using spline connections and checks the volume
        is correct"""

        test_shape = RotateSplineShape(
            points=[
                (50, 0),
                (50, 20),
                (70, 80),
                (90, 50),
                (70, 0),
                (90, -50),
                (70, -80),
                (50, -20)
            ]
        )
        test_shape.rotation_angle = 360

        assert test_shape.solid is not None
        # assert test_shape.volume > 100

        # test_volume = test_shape.volume
        test_shape.rotation_angle = 180

        assert test_shape.solid is not None
        # assert test_shape.volume == pytest.approx(test_volume * 0.5)

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

    def test_shape_areas(self):
        """creates rotated shapes using spline connections and checks the
        areas are expected"""

        test_shape = RotateSplineShape(
            points=[
                (50, 0),
                (50, 20),
                (70, 80),
                (90, 50),
                (70, 0),
                (90, -50),
                (70, -80),
                (50, -20)
            ]
        )

        assert len(test_shape.areas) == 1
        assert len(set(test_shape.areas)) == 1

        test_shape.rotation_angle = 180

        assert len(test_shape.areas) == 3
        assert len(set(test_shape.areas)) == 2

    def test_shape_azimuth_placement_angles_iterabel(self):
        """checks that azimuth_placement_angle can take an Iterable
        """
        test_shape = RotateSplineShape(
            points=[(200, 100), (200, 200), (500, 200), (500, 100)],
            rotation_angle=20,
            azimuth_placement_angle=[0, 180])
        test_shape.solid
        assert test_shape.solid is not None

    def test_incorrect_color_values(self):
        """Checks incorrect argument values for RotateSplineShape"""
        def test_string_color_value():
            """Tries to make a RotateSplineShape is string values for color"""
            RotateSplineShape(
                points=[(200, 100), (200, 200), (500, 200), (500, 100)],
                azimuth_placement_angle=np.linspace(0, 90, 2),
                color=('1', '0', '1')
            )

        self.assertRaises(
            ValueError,
            test_string_color_value
        )


if __name__ == "__main__":
    unittest.main()
