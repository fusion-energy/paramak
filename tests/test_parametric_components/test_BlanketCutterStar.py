
import unittest

import paramak
import pytest


class test_BlanketCutterStar(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.BlanketCutterStar(distance=100)

    def test_BlanketCutterStar_creation(self):
        """Creates a solid using the BlanketCutterStar parametric component
        and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_BlanketCutterStar_distance_volume_impact(self):
        """Creates solid using the BlanketCutterStar parametric component
        with different distances and checks that the volume changes accordingly
        ."""

        test_volume = self.test_shape.volume
        self.test_shape.distance=50
        # not quite two times as large as there is overlap in the center
        assert test_volume == pytest.approx(self.test_shape.volume * 2, rel=0.1)
