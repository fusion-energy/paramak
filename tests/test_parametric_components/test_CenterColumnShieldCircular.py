
import unittest

import paramak


class TestCenterColumnShieldCircular(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.CenterColumnShieldCircular(
            height=600, inner_radius=100, mid_radius=150, outer_radius=200
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a CenterColumnShieldCircular are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "CenterColumnShieldCircular.stp"
        assert self.test_shape.stl_filename == "CenterColumnShieldCircular.stl"
        # assert self.test_shape.name == "center_column_shield"
        assert self.test_shape.material_tag == "center_column_shield_mat"

    def test_points_calculation(self):
        """Checks that the points used to construct the CenterColumnShieldCircular components
        are calculated correctly from the parameters given."""

        assert self.test_shape.points == [
            (100, 0, 'straight'), (100, 300.0, 'straight'), (200, 300.0, 'circle'),
            (150, 0, 'circle'), (200, -300.0, 'straight'), (100, -300.0, 'straight'),
            (100, 0, 'straight')
        ]

    def test_creation(self):
        """Creates a center column shield using the CenterColumnShieldCircular
        parametric component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_faces(self):
        """Creates a center column shield using the CenterColumnShieldCircular
        parametric component and checks that a solid is created with the correct
        number of faces"""

        assert len(self.test_shape.areas) == 4
        assert len(set([round(i) for i in self.test_shape.areas])) == 3

        self.test_shape.rotation_angle = 180
        assert len(self.test_shape.areas) == 6
        assert len(set([round(i) for i in self.test_shape.areas])) == 4
