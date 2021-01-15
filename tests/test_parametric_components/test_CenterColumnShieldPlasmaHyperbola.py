
import unittest

import paramak


class TestCenterColumnShieldPlasmaHyperbola(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.CenterColumnShieldPlasmaHyperbola(
            height=800, inner_radius=100, mid_offset=40, edge_offset=30
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

    def test_creation(self):
        """Creates a center column shield using the
        CenterColumnShieldPlasmaHyperbola parametric component and checks that
        a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_points_calculation(self):
        """Checks that the points used to construct the CenterColumnShieldPlasmaHyperbola
        component are calculated correctly fro the parameters given."""

        assert self.test_shape.points == [
            (100, 0, 'straight'), (100, 400.0, 'straight'), (337.5, 400.0, 'straight'),
            (337.5, 300.0, 'spline'), (260.0, 0.0, 'spline'), (337.5, -300.0, 'straight'),
            (337.5, -400.0, 'straight'), (100, -400.0, 'straight'), (100, 0, 'straight')
        ]

    def test_invalid_parameters_errors(self):
        """Checks that the correct errors are raised when invalid arguments are input as
        shape parameters."""

        def incorrect_inner_radius():
            self.test_shape.inner_radius = 601
            self.test_shape.solid

        def incorrect_height():
            self.test_shape.inner_radius = 100
            self.test_shape.height = 300
            self.test_shape.solid

        self.assertRaises(ValueError, incorrect_inner_radius)
        self.assertRaises(ValueError, incorrect_height)

    def test_faces(self):
        """Creates a center column shield using the CenterColumnShieldPlasmaHyperbola
        parametric component and checks that a solid with the correct number of
        faces is created"""

        assert len(self.test_shape.areas) == 6
        assert len(set([round(i) for i in self.test_shape.areas])) == 4

        self.test_shape.rotation_angle = 180
        assert len(self.test_shape.areas) == 8
        assert len(set([round(i) for i in self.test_shape.areas])) == 5
