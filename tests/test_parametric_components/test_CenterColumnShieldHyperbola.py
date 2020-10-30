
import paramak
import unittest


class test_CenterColumnShieldHyperbola(unittest.TestCase):
    def test_CenterColumnShieldHyperbola_creation(self):
        """Creates a center column shield using the
        CenterColumnShieldHyperbola parametric component and checks that a
        cadquery solid is created."""

        test_shape = paramak.CenterColumnShieldHyperbola(
            height=100, inner_radius=50, mid_radius=80, outer_radius=100
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_CenterColumnShieldHyperbola_error(self):
        def incorrect_inner_radius1():
            test_shape = paramak.CenterColumnShieldHyperbola(
                height=100, inner_radius=81, mid_radius=80, outer_radius=100
            )
            test_shape.solid

        def incorrect_inner_radius2():
            test_shape = paramak.CenterColumnShieldHyperbola(
                height=100, inner_radius=50, mid_radius=80, outer_radius=49
            )
            test_shape.solid

        self.assertRaises(ValueError, incorrect_inner_radius1)
        self.assertRaises(ValueError, incorrect_inner_radius2)
