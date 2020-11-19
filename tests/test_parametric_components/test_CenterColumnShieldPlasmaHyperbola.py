
import unittest

import paramak


class test_CenterColumnShieldPlasmaHyperbola(unittest.TestCase):
    def test_CenterColumnShieldPlasmaHyperbola_creation(self):
        """Creates a center column shield using the
        CenterColumnShieldPlasmaHyperbola parametric component and checks that
        a cadquery solid is created."""

        test_shape = paramak.CenterColumnShieldPlasmaHyperbola(
            inner_radius=50, height=800, mid_offset=40, edge_offset=30
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_CenterColumnShieldPlasmaHyperbola_error(self):
        def incorrect_inner_radius():
            test_shape = paramak.CenterColumnShieldPlasmaHyperbola(
                inner_radius=601, height=800, mid_offset=40, edge_offset=30
            )
            test_shape.solid

        def incorrect_inner_height():
            test_shape = paramak.CenterColumnShieldPlasmaHyperbola(
                inner_radius=50, height=301, mid_offset=40, edge_offset=30
            )
            test_shape.solid

        self.assertRaises(ValueError, incorrect_inner_radius)
        self.assertRaises(ValueError, incorrect_inner_height)

    def test_CenterColumnShieldPlasmaHyperbola_faces(self):
        """Creates a center column shield using the CenterColumnShieldPlasmaHyperbola
        parametric component and checks that a solid with the correct number of
        faces is created"""

        test_shape = paramak.CenterColumnShieldPlasmaHyperbola(
            inner_radius=200, height=800, mid_offset=40, edge_offset=30
        )

        assert len(test_shape.areas) == 6
        # assert len(set(test_shape.areas)) == 4

        test_shape.rotation_angle = 180
        assert len(test_shape.areas) == 8
        # assert len(set(test_shape.areas)) == 5
