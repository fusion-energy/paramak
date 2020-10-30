
import paramak
import unittest


class test_CenterColumnShieldFlatTopCircular(unittest.TestCase):
    def test_CenterColumnShieldFlatTopCircular_creation(self):
        """Creates a center column shield using the
        CenterColumnShieldFlatTopCircular parametric component and checks that
        a cadquery solid is created."""

        test_shape = paramak.CenterColumnShieldFlatTopCircular(
            height=600,
            arc_height=200,
            inner_radius=100,
            mid_radius=150,
            outer_radius=200,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000
