
import unittest

import paramak


class TestCenterColumnShieldFlatTopHyperbola(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.CenterColumnShieldFlatTopHyperbola(
            height=600, arc_height=400, inner_radius=100, mid_radius=150, outer_radius=200)

    def test_default_parameters(self):
        """Checks that the default parameters of a CenterColumnShieldFlatTopHyperbola are
        correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "CenterColumnShieldFlatTopHyperbola.stp"
        assert self.test_shape.stl_filename == "CenterColumnShieldFlatTopHyperbola.stl"
        # assert self.test_shape.name == "center_column"
        assert self.test_shape.material_tag == "center_column_shield_mat"

    def test_points_calculation(self):
        """Checks that the points used to construct the CenterColumnShieldFlatTopHyperbola
        component are calculated correctly from the parameters given."""

        assert self.test_shape.points == [
            (100, 0, "straight"), (100, 300, "straight"), (200, 300, "straight"),
            (200, 200, "spline"), (150, 0, "spline"), (200, -200, "straight"),
            (200, -300, "straight"), (100, -300, "straight"), (100, 0, "straight")
        ]

    def test_creation(self):
        """Creates a center column shield using the
        CenterColumnShieldFlatTopHyperbola parametric component and checks that
        a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_invalid_parameters_errors(self):
        """Checks that the correct errors are raised when invalid arguments are input as
        shape parameters."""

        def incorrect_inner_radius():
            self.test_shape.inner_radius = 220
            self.test_shape.solid

        def incorrect_mid_radius():
            self.test_shape.inner_radius = 100
            self.test_shape.mid_radius = 250
            self.test_shape.solid

        def incorrect_outer_radius():
            self.test_shape.mid_radius = 150
            self.test_shape.outer_radius = 130
            self.test_shape.solid

        def incorrect_arc_height():
            self.test_shape.outer_radius = 200
            self.test_shape.arc_height = 700
            self.test_shape.solid

        self.assertRaises(ValueError, incorrect_inner_radius)
        self.assertRaises(ValueError, incorrect_mid_radius)
        self.assertRaises(ValueError, incorrect_outer_radius)
        self.assertRaises(ValueError, incorrect_arc_height)

    def test_faces(self):
        """Creates a center column shield using the
        CenterColumnShieldFlatTopHyperbola parametric component and checks
        that a solid is created with the correct number of faces."""

        assert len(self.test_shape.areas) == 6
        assert len(set([round(i) for i in self.test_shape.areas])) == 4

        self.test_shape.rotation_angle = 180
        assert len(self.test_shape.areas) == 8
        assert len(set([round(i) for i in self.test_shape.areas])) == 5
