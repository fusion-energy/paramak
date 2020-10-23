
import paramak
import pytest
import unittest


class test_ToroidalFieldCoilRectangle(unittest.TestCase):
    def test_ToroidalFieldCoilRectangle_creation(self):
        """creates a tf coil using the ToroidalFieldCoilRectangle parametric
        component and checks that a cadquery solid is created"""

        test_shape = paramak.ToroidalFieldCoilRectangle(
            horizontal_start_point=(100, 700),
            vertical_mid_point=(800, 0),
            thickness=150,
            distance=50,
            number_of_coils=8,
        )
        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_ToroidalFieldCoilRectangle_no_inner_leg_creation(self):
        """creates a tf coil using the ToroidalFieldCoilRectangle without
        the inner leg and checks that a cadquery solid is created"""

        test_shape = paramak.ToroidalFieldCoilRectangle(
            horizontal_start_point=(100, 700),
            vertical_mid_point=(800, 0),
            with_inner_leg=False,
            thickness=150,
            distance=50,
            number_of_coils=8,
        )
        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_ToroidalFieldCoilRectangle_rotation_angle(self):
        """creates a tf coil with a rotation_angle < 360 and checks that the correct
        cut is performed and the volume is correct"""

        test_shape = paramak.ToroidalFieldCoilRectangle(
            horizontal_start_point=(100, 700),
            vertical_mid_point=(800, 0),
            with_inner_leg=False,
            thickness=50,
            distance=50,
            number_of_coils=8,
        )
        test_volume = test_shape.volume

        test_shape.rotation_angle = 180

        assert test_shape.volume == pytest.approx(test_volume * 0.5)
