
import paramak
import unittest


class test_BlanketCutterParallels(unittest.TestCase):
    def test_BlanketCutterParallels_creation(self):
        """creates solid using the BlanketCutterParallels parametric component
        and checks that a cadquery solid is created"""

        test_shape = paramak.BlanketCutterParallels(
            thickness=50,
            gap_size=200)

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketCutterParallels_distance_volume_impact(self):
        """creates solid using the BlanketCutterParallels parametric component
        with different distances and checks that the volume changes accordingly
        """

        small_shape = paramak.BlanketCutterParallels(
            thickness=50,
            gap_size=200)

        large_shape = paramak.BlanketCutterParallels(
            thickness=100,
            gap_size=200,
        )

        assert small_shape.volume < large_shape.volume

    def test_BlanketCutterParallels_modif(self):
        test_shape = paramak.BlanketCutterParallels(
            thickness=50,
            gap_size=200)
        test_shape.solid

        test_shape.thickness = 53
        assert test_shape.solid is not None
