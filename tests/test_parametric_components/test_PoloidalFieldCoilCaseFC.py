
import math
import unittest

import paramak
import pytest


class TestPoloidalFieldCoilCaseFC(unittest.TestCase):

    def setUp(self):
        self.pf_coil = paramak.PoloidalFieldCoil(
            height=50, width=60, center_point=(1000, 500)
        )

        self.test_shape = paramak.PoloidalFieldCoilCaseFC(
            pf_coil=self.pf_coil, casing_thickness=5
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a PoloidalFieldCoilCaseFC are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "PoloidalFieldCoilCaseFC.stp"
        assert self.test_shape.stl_filename == "PoloidalFieldCoilCaseFC.stl"
        assert self.test_shape.material_tag == "pf_coil_case_mat"

    def test_creation(self):
        """Creates a pf coil case using the PoloidalFieldCoilCaseFC parametric
        component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_absolute_volume(self):
        """Creates a pf coil case using the PoloidalFieldCoilCaseFC parametric
        component and checks that its volume is correct."""

        assert self.test_shape.volume == pytest.approx(
            (math.pi * 2 * 1000) * ((50 * 5 * 2) + (70 * 5 * 2)))

    def test_absolute_areas(self):
        """Creates a pf coil case using the PoloidalFieldCoilCaseFC parametric
        component and checks that the areas of its faces are correct"""

        assert len(self.test_shape.areas) == 8
        assert len(set([round(i) for i in self.test_shape.areas])) == 6
        assert self.test_shape.areas.count(
            pytest.approx(60 * math.pi * 2 * 1000)) == 2
        assert self.test_shape.areas.count(
            pytest.approx(70 * math.pi * 2 * 1000)) == 2
        assert self.test_shape.areas.count(
            pytest.approx(50 * math.pi * 2 * 1030)) == 1
        assert self.test_shape.areas.count(
            pytest.approx(50 * math.pi * 2 * 970)) == 1
        assert self.test_shape.areas.count(
            pytest.approx(60 * math.pi * 2 * 1035)) == 1
        assert self.test_shape.areas.count(
            pytest.approx(60 * math.pi * 2 * 965)) == 1
