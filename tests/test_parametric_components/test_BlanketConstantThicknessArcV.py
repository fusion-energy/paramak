
import unittest

import paramak
import pytest


class test_BlanketConstantThicknessArcV(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.BlanketConstantThicknessArcH(
            inner_lower_point=(300, -200),
            inner_mid_point=(500, 0),
            inner_upper_point=(300, 200),
            thickness=20,
            rotation_angle=180,
        )
    
    def test_default_parameters(self):
        """Checks that the default parameters of a BlanketConstantThicknessArcV are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "BlanketConstantThicknessArcV.stp"
        assert self.test_shape.stl_filename == "BlanketConstantThicknessArcV.stl"
        assert self.test_shape.material_tag == "blanket_mat"
    
    def test_points_calculation(self):
        """Checks that the points used to construct the BlanketConstantThicknessArcH component
        are calculated correctly from the parameters given."""

        assert self.test_shape.points == [
            (300, 200, 'circle'), 
            (500, 0, 'circle'), 
            (300, -200, 'straight'), 
            (320, -200, 'circle'), 
            (520, 0, 'circle'), 
            (320, 200, 'straight'), 
            (300, 200, 'circle')
        ]

    def test_BlanketConstantThickness_creation(self):
        """Creates a blanket using the BlanketConstantThicknessArcV parametric
        component and checks that a cadquery solid is created."""

        test_shape = paramak.BlanketConstantThicknessArcV(
            inner_lower_point=(300, -200),
            inner_mid_point=(500, 0),
            inner_upper_point=(300, 200),
            thickness=20,
            rotation_angle=180,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketConstantThickness_relative_volume(self):
        """creates two blankets using the BlanketConstantThicknessArcV parametric
        component and checks that their relative volumes are correct"""

        # rotation_angle
        test_shape = paramak.BlanketConstantThicknessArcV(
            inner_lower_point=(300, -200),
            inner_mid_point=(500, 0),
            inner_upper_point=(300, 200),
            thickness=20,
            rotation_angle=360,
        )
        test_shape_volume = test_shape.volume

        test_shape.rotation_angle = 180
        assert test_shape.volume == pytest.approx(test_shape_volume * 0.5)

    def test_BlanketConstantThickness_faces(self):
        """creates a blanket using the BlanketConstantThicknessArcV parametric
        component and checks that a solid with the correct number of faces is produced"""

        test_shape = paramak.BlanketConstantThicknessArcV(
            inner_lower_point=(300, -200),
            inner_mid_point=(500, 0),
            inner_upper_point=(300, 200),
            thickness=20,
            rotation_angle=360,
        )
        assert len(test_shape.areas) == 4
        assert len(set(test_shape.areas)) == 3

        test_shape.rotation_angle = 180
        assert len(test_shape.areas) == 6
        assert len(set(test_shape.areas)) == 4
