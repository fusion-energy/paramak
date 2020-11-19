
import math
import unittest

import paramak
import pytest


class test_PoloidalFieldCoilCaseFC(unittest.TestCase):
    def test_PoloidalFieldCoilCaseFC_creation(self):
        """Creates a pf coil case using the PoloidalFieldCoilCaseFC parametric
        component and checks that a cadquery solid is created."""

        pf_coil = paramak.PoloidalFieldCoil(
            height=50, width=60, center_point=(1000, 500)
        )

        test_shape = paramak.PoloidalFieldCoilCaseFC(
            pf_coil=pf_coil, casing_thickness=5
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_PoloidalFieldCoilCaseFC_absolute_volume(self):
        """Creates a pf coil case using the PoloidalFieldCoilCaseFC parametric
        component and checks that its volume is correct"""

        pf_coil = paramak.PoloidalFieldCoil(
            height=50, width=60, center_point=(1000, 500)
        )

        test_shape = paramak.PoloidalFieldCoilCaseFC(
            pf_coil=pf_coil, casing_thickness=5
        )

        assert test_shape.volume == pytest.approx(
            (math.pi * 2 * 1000) * ((50 * 5 * 2) + (70 * 5 * 2)))

    def test_PoloidalFieldCoilCaseFC_absolute_areas(self):
        """Creates a pf coil case using the PoloidalFieldCoilCaseFC parametric
        component and checks that the areas of its faces are correct"""

        pf_coil = paramak.PoloidalFieldCoil(
            height=50, width=60, center_point=(1000, 500)
        )

        test_shape = paramak.PoloidalFieldCoilCaseFC(
            pf_coil=pf_coil, casing_thickness=5
        )

        assert len(test_shape.areas) == 8
        # assert len(set(test_shape.areas)) == 6
        assert test_shape.areas.count(
            pytest.approx(60 * math.pi * 2 * 1000)) == 2
        assert test_shape.areas.count(
            pytest.approx(70 * math.pi * 2 * 1000)) == 2
        assert test_shape.areas.count(
            pytest.approx(50 * math.pi * 2 * 1030)) == 1
        assert test_shape.areas.count(
            pytest.approx(50 * math.pi * 2 * 970)) == 1
        assert test_shape.areas.count(
            pytest.approx(60 * math.pi * 2 * 1035)) == 1
        assert test_shape.areas.count(
            pytest.approx(60 * math.pi * 2 * 965)) == 1
