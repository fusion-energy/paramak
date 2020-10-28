
import paramak
import unittest


class test_CenterColumnShieldFlatTopHyperbola(unittest.TestCase):
    def test_CenterColumnShieldFlatTopHyperbola_creation(self):
        """creates a center column shield using the CenterColumnShieldFlatTopHyperbola parametric
        component and checks that a cadquery solid is created"""

        test_shape = paramak.CenterColumnShieldFlatTopHyperbola(
            height=500,
            arc_height=300,
            inner_radius=50,
            mid_radius=100,
            outer_radius=150,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_CenterColumnShieldFlatTopHyperbola_error(self):
        def incorrect_inner_radius():
            test_shape = paramak.CenterColumnShieldFlatTopHyperbola(
                height=500,
                arc_height=300,
                inner_radius=200,
                mid_radius=100,
                outer_radius=150,
            )
            test_shape.solid

        def incorrect_mid_radius():
            test_shape = paramak.CenterColumnShieldFlatTopHyperbola(
                height=500,
                arc_height=300,
                inner_radius=50,
                mid_radius=200,
                outer_radius=150,
            )
            test_shape.solid

        def incorrect_arc_height():
            test_shape = paramak.CenterColumnShieldFlatTopHyperbola(
                height=500,
                arc_height=600,
                inner_radius=50,
                mid_radius=100,
                outer_radius=150,
            )
            test_shape.solid
        self.assertRaises(ValueError, incorrect_inner_radius)
        self.assertRaises(ValueError, incorrect_mid_radius)
        self.assertRaises(ValueError, incorrect_arc_height)
