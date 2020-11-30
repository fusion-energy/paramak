
import unittest

import numpy as np
import paramak
from paramak.utils import (EdgeLengthSelector, FaceAreaSelector,
                           find_center_point_of_circle)


class TestUtilityFunctions(unittest.TestCase):

    def test_find_center_point_of_circle(self):
        """passes three points on a circle to the function and checks that the
        radius and center of the circle is calculated correctly"""

        point_1 = (0, 20)
        point_2 = (20, 0)
        point_3 = (0, -20)

        assert find_center_point_of_circle(
            point_1, point_2, point_3) == (
            (0, 0), 20)

    def test_EdgeLengthSelector_with_fillet_areas(self):
        """tests the filleting of a RotateStraightShape results in an extra
        surface area"""

        test_shape = paramak.RotateStraightShape(
            points=[(1, 1), (2, 1), (2, 2)])

        assert len(test_shape.areas) == 3

        test_shape.solid = test_shape.solid.edges(
            EdgeLengthSelector(6.28)).fillet(0.1)

        assert len(test_shape.areas) == 4

    def test_FaceAreaSelector_with_fillet_areas(self):
        """tests the filleting of a ExtrudeStraightShape"""

        test_shape = paramak.ExtrudeStraightShape(
            distance=5, points=[(1, 1), (2, 1), (2, 2)])

        assert len(test_shape.areas) == 5

        test_shape.solid = test_shape.solid.faces(
            FaceAreaSelector(0.5)).fillet(0.1)

        assert len(test_shape.areas) == 11

    def test_find_center_point_of_circle_zero_det(self):
        """Checks that None is given if det is zero
        """
        point_1 = (0, 0)
        point_2 = (0, 0)
        point_3 = (0, 0)

        assert find_center_point_of_circle(
            point_1, point_2, point_3) == (
            None, np.inf)
