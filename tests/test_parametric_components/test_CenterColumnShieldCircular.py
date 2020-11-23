
import unittest

import paramak


class test_CenterColumnShieldCircular(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.CenterColumnShieldCircular(
            height=600, inner_radius=100, mid_radius=150, outer_radius=200
        )

    def test_CenterColumnShieldCircular_creation(self):
        """Creates a center column shield using the CenterColumnShieldCircular
        parametric component and checks that a cadquery solid is created."""

        test_shape = paramak.CenterColumnShieldCircular(
            height=600, inner_radius=100, mid_radius=150, outer_radius=200
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_CenterColumnShieldCircular_faces(self):
        """Creates a center column shield using the CenterColumnShieldCircular
        parametric component and checks that a solid is created with the correct
        number of faces"""

        test_shape = paramak.CenterColumnShieldCircular(
            height=600,
            inner_radius=100,
            mid_radius=150,
            outer_radius=200,
            rotation_angle=360)
        assert len(test_shape.areas) == 4
        assert len(set([round(i) for i in test_shape.areas])) == 3

        test_shape.rotation_angle = 180
        assert len(test_shape.areas) == 6
        assert len(set([round(i) for i in test_shape.areas])) == 4
