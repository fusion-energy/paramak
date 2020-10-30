
import unittest
import numpy as np

from paramak.utils import find_center_point_of_circle


class test_utility_functions(unittest.TestCase):
    def test_find_center_point_of_circle(self):
        """passes three points on a circle to the function and checks that the
        radius and center of the circle is calculated correctly"""

        point_1 = (0, 20)
        point_2 = (20, 0)
        point_3 = (0, -20)

        assert find_center_point_of_circle(
            point_1, point_2, point_3) == (
            (0, 0), 20)

    def test_find_center_point_of_circle_zero_det(self):
        """Checks that None is given if det is zero
        """
        point_1 = (0, 0)
        point_2 = (0, 0)
        point_3 = (0, 0)

        assert find_center_point_of_circle(
            point_1, point_2, point_3) == (
            None, np.inf)
