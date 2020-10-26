
import paramak
import unittest
import pytest

class test_BlanketCutterStar(unittest.TestCase):
    def test_BlanketCutterStar_creation(self):
        """creates a solid using the BlanketCutterStar parametric component
        and checks that a cadquery solid is created"""

        test_shape = paramak.BlanketCutterStar(
            distance=100)

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketCutterStar_distance_volume_impact(self):
        """creates solid using the BlanketCutterStar parametric component
        with different distances and checks that the volume changes accordingly
        """

        small_shape = paramak.BlanketCutterStar(distance=50)

        large_shape = paramak.BlanketCutterStar(distance=100)

        # not quite two times as big as there is overlap in the center
        assert 2 * small_shape.volume == pytest.approx(large_shape.volume, rel=0.1)