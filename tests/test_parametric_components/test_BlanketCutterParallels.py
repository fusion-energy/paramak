
import unittest

import paramak


class test_BlanketCutterParallels(unittest.TestCase):
    def test_BlanketCutterParallels_creation(self):
        """Creates solid using the BlanketCutterParallels parametric component
        and checks that a cadquery solid is created."""

        test_shape = paramak.BlanketCutterParallels(
            thickness=50,
            gap_size=200)

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketCutterParallels_distance_volume_impact(self):
        """Creates solid using the BlanketCutterParallels parametric component
        with different distances and checks that the volume changes accordingly
        ."""

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

        cut_shape = paramak.ExtrudeCircleShape(1, 1, points=[(0, 0)])
        test_shape.cut = cut_shape
        test_shape.solid

        assert test_shape.solid is not None

        test_shape.cut = [cut_shape]
        test_shape.solid

        assert test_shape.solid is not None

    def test_distance_is_modified(self):
        test_shape = paramak.BlanketCutterParallels(
            thickness=50,
            gap_size=50,
        )

        for thickness, gap_size in zip([20, 30, 40], [10, 20, 30]):
            test_shape.thickness = thickness
            test_shape.gap_size = gap_size
            assert test_shape.distance == test_shape.gap_size/2 + test_shape.thickness
