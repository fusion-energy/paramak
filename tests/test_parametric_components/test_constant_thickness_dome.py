import unittest
import pytest

import paramak


class TestConstantThicknessDome(unittest.TestCase):
    """tests for the ConstantThicknessDome class"""

    def test_volume_increases_with_rotation_angle(self):
        """Tests that the volume doubles when rotation angle doubles"""

        test_shape_1 = paramak.ConstantThicknessDome(rotation_angle=180)
        test_shape_2 = paramak.ConstantThicknessDome(rotation_angle=360)

        assert test_shape_1.volume() * 2 == pytest.approx(test_shape_2.volume())

    def test_upper_lower_flips_points(self):
        """Checks that the coords of the flips version are the same for p1 and p2
        and negative for part of p3"""
        test_shape_1 = paramak.ConstantThicknessDome(upper_or_lower="upper")
        test_shape_2 = paramak.ConstantThicknessDome(upper_or_lower="lower")
        assert test_shape_1.points[0] == test_shape_2.points[0]
        assert test_shape_1.points[1] == test_shape_2.points[1]
        assert test_shape_1.points[2][0] == test_shape_2.points[2][0]
        assert test_shape_1.points[2][1] == -test_shape_2.points[2][1]

        assert test_shape_1.volume() == pytest.approx(test_shape_2.volume())

    def test_invalid_parameters_errors(self):
        """Checks that the correct errors are raised when invalid arguments are
        input as shape parameters."""

        def incorrect_shape_height_width_ratio():
            my_shape = paramak.ConstantThicknessDome(chord_width=10, chord_height=40)
            my_shape.solid

        def incorrect_thickness():
            paramak.ConstantThicknessDome(thickness=-1)

        def incorrect_chord_height():
            paramak.ConstantThicknessDome(chord_height=-1)

        def incorrect_chord_width():
            paramak.ConstantThicknessDome(chord_width=-1)

        self.assertRaises(ValueError, incorrect_shape_height_width_ratio)
        self.assertRaises(ValueError, incorrect_thickness)
        self.assertRaises(ValueError, incorrect_chord_height)
        self.assertRaises(ValueError, incorrect_chord_width)
