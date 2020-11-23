
import unittest

import paramak


class test_CenterColumnShieldHyperbola(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.CenterColumnShieldHyperbola(
            height=600, inner_radius=100, mid_radius=150, outer_radius=200
        )
    
    def test_CenterColumnShieldHyperbola_creation(self):
        """Creates a center column shield using the
        CenterColumnShieldHyperbola parametric component and checks that a
        cadquery solid is created."""

        assert self.test_shape.solid is not None 
        assert self.test_shape.volume > 1000

    def test_CenterColumnShieldHyperbola_invalid_parameters_errors(self):
        """Checks that the correct errors are raised when invalid arguments are input
        as shape parameters."""

        def incorrect_inner_radius():
            self.test_shape.inner_radius = 180
            self.test_shape.solid

        def incorrect_mid_radius():
            self.test_shape.mid_radius = 80
            self.test_shape.solid
        
        def incorrect_outer_radius():
            self.test_shape.outer_radius = 130
            self.test_shape.solid

        self.assertRaises(ValueError, incorrect_inner_radius)
        self.assertRaises(ValueError, incorrect_mid_radius)
        self.assertRaises(ValueError, incorrect_outer_radius)

    def test_CenterColumnShieldHyperbola_faces(self):
        """Creates a center column shield using the CenterColumnShieldHyperbola
        parametric component and checks that a solid with the correct number of
        faces is created"""

        assert len(self.test_shape.areas) == 4
        assert len(set([round(i) for i in self.test_shape.areas])) == 3

        self.test_shape.rotation_angle = 180
        assert len(self.test_shape.areas) == 6
        assert len(set([round(i) for i in self.test_shape.areas])) == 4
