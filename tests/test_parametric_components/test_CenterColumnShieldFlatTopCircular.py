
import unittest

import paramak


class test_CenterColumnShieldFlatTopCircular(unittest.TestCase):
    def test_CenterColumnShieldFlatTopCircular_creation(self):
        """Creates a center column shield using the
        CenterColumnShieldFlatTopCircular parametric component and checks that
        a cadquery solid is created."""

        test_shape = paramak.CenterColumnShieldFlatTopCircular(
            height=600,
            arc_height=400,
            inner_radius=100,
            mid_radius=150,
            outer_radius=200,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_CenterColumnShieldFlatTopCircular_faces(self):
        """Creates a center column shield using the
        CenterColumnShieldFlatTopCircular parametric component and checks that
        a solid is created with the correct number of faces"""

        test_shape = paramak.CenterColumnShieldFlatTopCircular(
            height=600,
            arc_height=400,
            inner_radius=100,
            mid_radius=150,
            outer_radius=200,
        )

        assert len(test_shape.areas) == 6
        # assert len(set(test_shape.areas)) == 4

        test_shape.rotation_angle = 180
        assert len(test_shape.areas) == 8
        assert len(set(test_shape.areas)) == 5
