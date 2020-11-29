
import unittest

import paramak
import pytest


class TestBlanketCutterStar(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.BlanketCutterStar(distance=100)

    def test_default_parameters(self):
        """Checks that the default parameters of a BlanketCutterStar are correct."""

        assert self.test_shape.azimuth_placement_angle == [
            0., 36., 72., 108., 144., 180., 216., 252., 288., 324.]
        assert self.test_shape.height == 2000
        assert self.test_shape.width == 2000
        assert self.test_shape.stp_filename == "BlanketCutterStar.stp"
        assert self.test_shape.stl_filename == "BlanketCutterStar.stl"
        assert self.test_shape.name == "blanket_cutter_star"
        assert self.test_shape.material_tag == "blanket_cutter_star_mat"

    def test_points_calculation(self):
        """Checks that the points used to construct the BlanketCutterStar component
        are calculated correctly from the parameters given."""

        assert self.test_shape.points == [(0, -
                                           1000, "straight"), (2000, -
                                                               1000, "straight"), (2000, 1000, "straight"), (0, 1000, "straight"), (0, -
                                                                                                                                    1000, "straight")]

    def test_creation(self):
        """Creates a solid using the BlanketCutterStar parametric component
        and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_distance_volume_impact(self):
        """Creates solid using the BlanketCutterStar parametric component
        with different distances and checks that the volume changes accordingly
        ."""

        test_volume = self.test_shape.volume
        self.test_shape.distance = 50
        # not quite two times as large as there is overlap in the center
        assert test_volume == pytest.approx(
            self.test_shape.volume * 2, rel=0.1)
