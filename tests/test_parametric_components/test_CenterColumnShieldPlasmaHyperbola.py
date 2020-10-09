
import paramak
import unittest


class test_CenterColumnShieldPlasmaHyperbola(unittest.TestCase):
    def test_CenterColumnShieldPlasmaHyperbola_creation(self):
        """creates a center column shield using the
        CenterColumnShieldPlasmaHyperbola parametric
        component and checks that a cadquery solid is created"""

        test_shape = paramak.CenterColumnShieldPlasmaHyperbola(
            inner_radius=50, height=800, mid_offset=40, edge_offset=30
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000
