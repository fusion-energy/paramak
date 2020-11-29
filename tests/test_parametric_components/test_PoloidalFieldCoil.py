
import math
import unittest

import paramak
import pytest


class TestPoloidalFieldCoil(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.PoloidalFieldCoil(
            height=50, width=60, center_point=(1000, 500)
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a PoloidalFieldCoil are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.stp_filename == "PoloidalFieldCoil.stp"
        assert self.test_shape.stl_filename == "PoloidalFieldCoil.stl"
        # assert self.test_shape.name == "pf_coil"
        assert self.test_shape.material_tag == "pf_coil_mat"

    def test_points_calculation(self):
        """Checks that the points used to construct the PoloidalFieldCoil are calculated
        correctly from the parameters given."""

        assert self.test_shape.points == [
            (1030.0, 525.0, 'straight'), (1030.0, 475.0, 'straight'),
            (970.0, 475.0, 'straight'), (970.0, 525.0, 'straight'),
            (1030.0, 525.0, 'straight')
        ]

    def test_creation(self):
        """Creates a pf coil using the PoloidalFieldCoil parametric component
        and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_absolute_volume(self):
        """Creates a pf coil using the PoloidalFieldCoil parametric component
        and checks that the volume is correct"""

        assert self.test_shape.volume == pytest.approx(
            50 * 60 * math.pi * 2 * 1000)

    def test_absolute_areas(self):
        """Creates a pf coil using the PoloidalFieldCoil parametric component
        and checks that the areas are correct"""

        assert len(self.test_shape.areas) == 4
        assert len(set([round(i) for i in self.test_shape.areas])) == 3
        assert self.test_shape.areas.count(
            pytest.approx(60 * math.pi * 2 * 1000)) == 2
        assert self.test_shape.areas.count(
            pytest.approx(50 * math.pi * 2 * 970)) == 1
        assert self.test_shape.areas.count(
            pytest.approx(50 * math.pi * 2 * 1030)) == 1
