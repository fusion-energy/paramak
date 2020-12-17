
import unittest

import paramak


class TestBlanketCutterParallels(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.BlanketCutterParallels(
            thickness=50,
            gap_size=200
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a BlanketCutterParallel are correct."""

        assert self.test_shape.azimuth_placement_angle == [
            0., 36., 72., 108., 144., 180., 216., 252., 288., 324.]
        assert self.test_shape.height == 2000
        assert self.test_shape.width == 2000
        assert self.test_shape.stp_filename == "BlanketCutterParallels.stp"
        assert self.test_shape.stl_filename == "BlanketCutterParallels.stl"
        # assert self.test_shape.name == "blanket_cutter_parallels"
        assert self.test_shape.material_tag == "blanket_cutter_parallels_mat"

    def test_creation(self):
        """Creates solid using the BlanketCutterParallels parametric component
        and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    # def test_BlanketCutterParallels_distance_volume_impact(self):
    #     """Creates solid using the BlanketCutterParallels parametric component
    #     with different distances and checks that the volume changes accordingly
    #     ."""

    #     test_volume = self.test_shape.volume
    #     self.test_shape.thickness=100
    #     assert test_volume < self.test_shape.volume

    def test_cut_modification(self):
        """Creates a BlanketCutterParallels parametric component and with another
        shape cut out and checks that a solid can be produced."""

        cut_shape = paramak.ExtrudeCircleShape(1, 1, points=[(0, 0)])
        self.test_shape.cut = cut_shape
        assert self.test_shape.solid is not None
        assert self.test_shape.solid is not None

    def test_distance_is_modified(self):
        test_shape = paramak.BlanketCutterParallels(
            thickness=50,
            gap_size=50,
        )

        for thickness, gap_size in zip([20, 30, 40], [10, 20, 30]):
            test_shape.thickness = thickness
            test_shape.gap_size = gap_size
            assert test_shape.distance == test_shape.gap_size / 2 + test_shape.thickness

    def test_main_cutting_shape_is_modified(self):
        test_shape = paramak.BlanketCutterParallels(
            thickness=50,
            gap_size=50,
        )

        for gap_size, angles in zip([10, 20, 30], [0, 1, 3]):
            test_shape.gap_size = gap_size
            test_shape.azimuth_placement_angle = angles
            assert test_shape.main_cutting_shape.distance == test_shape.gap_size / 2.0
            assert test_shape.main_cutting_shape.azimuth_placement_angle == test_shape.azimuth_placement_angle
