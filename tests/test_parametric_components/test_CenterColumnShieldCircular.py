
import paramak
import unittest


class test_CenterColumnShieldCircular(unittest.TestCase):
    def test_CenterColumnShieldCircular_creation(self):
        """creates a center column shield using the CenterColumnShieldCircular
        parametric component and checks that a cadquery solid is created"""

        test_shape = paramak.CenterColumnShieldCircular(
            height=600, inner_radius=100, mid_radius=150, outer_radius=200
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000
