
import unittest

import paramak


class test_CenterColumnShieldPlasmaHyperbola(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.CenterColumnShieldPlasmaHyperbola(
            height=600, inner_radius=100, mid_offset=40, edge_offset=30
        )
    
    def test_default_parameters(self):
        """Checks that the default parameters of a CenterColumnShieldPlasmaHyperbola are
        correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.major_radius == 450
        assert self.test_shape.minor_radius == 150
        assert self.test_shape.triangularity == 0.55
        assert self.test_shape.elongation == 2
        assert self.test_shape.stp_filename == "CenterColumnShieldPlasmaHyperbola.stp"
        assert self.test_shape.stl_filename == "CenterColumnShieldPlasmaHyperbola.stl"
        # assert self.test_shape.name == "center_column"
        assert self.test_shape.material_tag == "center_column_shield_mat"

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
