
import math
import pytest
import paramak
import unittest


class test_PoloidalFieldCoil(unittest.TestCase):
    def test_PoloidalFieldCoil_creation(self):
        """Creates a pf coil using the PoloidalFieldCoil parametric component
        and checks that a cadquery solid is created."""

        test_shape = paramak.PoloidalFieldCoil(
            height=50, width=60, center_point=(1000, 500)
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_PoloidalFieldCoil_absolute_volume(self):
        """Creates a pf coil using the PoloidalFieldCoil parametric component
        and checks that the volume is correct"""

        test_shape = paramak.PoloidalFieldCoil(
            height=50, width=60, center_point=(1000, 500)
        )

        assert test_shape.volume == pytest.approx(50 * 60 * math.pi * 2 * 1000)

    def test_PoloidalFieldCoil_absolute_areas(self):
        """Creates a pf coil using the PoloidalFieldCoil parametric component
        and checks that the areas are correct"""

        test_shape = paramak.PoloidalFieldCoil(
            height=50, width=60, center_point=(1000, 500)
        )

        assert len(test_shape.areas) == 4
        # assert len(set(test_shape.areas)) == 3
        assert test_shape.areas.count(
            pytest.approx(60 * math.pi * 2 * 1000)) == 2
        assert test_shape.areas.count(
            pytest.approx(50 * math.pi * 2 * 970)) == 1
        assert test_shape.areas.count(
            pytest.approx(50 * math.pi * 2 * 1030)) == 1
