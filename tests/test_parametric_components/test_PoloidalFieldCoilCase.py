
import paramak
import unittest
import pytest
import math


class test_PoloidalFieldCoilCase(unittest.TestCase):
    def test_PoloidalFieldCoilCase_creation(self):
        """Creates a pf coil case using the PoloidalFieldCoilCase parametric
        component and checks that a cadquery solid is created."""

        test_shape = paramak.PoloidalFieldCoilCase(
            casing_thickness=5,
            coil_height=50,
            coil_width=50,
            center_point=(1000, 500)
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_PoloidalFieldCoilCase_absolute_volume(self):
        """Creates a pf coil case using the PoloidalFieldCoilCase parametric
        component and checks that its volume is correct"""

        test_shape = paramak.PoloidalFieldCoilCase(
            casing_thickness=5,
            coil_height=50,
            coil_width=50,
            center_point=(1000, 500)
        )

        assert test_shape.volume == pytest.approx(
            (math.pi * 2 * 1000) * ((60 * 5 * 2) + (50 * 5 * 2)))

    def test_PoloidalFieldCoilCase_absolute_areas(self):
        """Creates a pf coil case using the PoloidalFieldCoilCase parametric
        component and checks that the areas of its faces are correct"""

        test_shape = paramak.PoloidalFieldCoilCase(
            casing_thickness=5,
            coil_height=50,
            coil_width=50,
            center_point=(1000, 500)
        )

        assert len(test_shape.areas) == 8
        # assert len(set(test_shape.areas)) == 6
        assert test_shape.areas.count(
            pytest.approx(50 * math.pi * 2 * 1000)) == 2
        assert test_shape.areas.count(
            pytest.approx(60 * math.pi * 2 * 1000)) == 2
        assert test_shape.areas.count(
            pytest.approx(50 * math.pi * 2 * 1025)) == 1
        assert test_shape.areas.count(
            pytest.approx(50 * math.pi * 2 * 975)) == 1
        assert test_shape.areas.count(
            pytest.approx(60 * math.pi * 2 * 1030)) == 1
        assert test_shape.areas.count(
            pytest.approx(60 * math.pi * 2 * 970)) == 1
