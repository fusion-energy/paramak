
import unittest

import paramak


class test_InnerTfCoilsFlat(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.InnerTfCoilsFlat(
            height=500,
            inner_radius=50,
            outer_radius=150,
            number_of_coils=6,
            gap_size=5
        )
    
    def test_InnerTfCoilsFlat_creation(self):
        """Creates an inner tf coil using the InnerTFCoilsFlat parametric
        component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_InnerTfCoilsFlat_azimuth_offset(self):
        """Creates an inner tf coil using the InnerTfCoilsFlat parametric
        component and checks that the azimuthal start angle can be changed
        correctly."""

        assert self.test_shape.azimuth_placement_angle == [
            0, 60, 120, 180, 240, 300]
        self.test_shape.azimuth_start_angle = 20
        assert self.test_shape.azimuth_placement_angle == [
            20, 80, 140, 200, 260, 320]

    def test_InnerTfCoilsFlat_attributes(self):
        """Checks that changing the attributes of InnerTfCoilsFlat affects the
        cadquery solid produced."""

        test_volume = self.test_shape.volume

        self.test_shape.height = 1000
        assert test_volume == self.test_shape.volume * 0.5
        self.test_shape.height = 500
        self.test_shape.inner_radius = 30
        assert test_volume < self.test_shape.volume
        self.test_shape.inner_radius = 50
        self.test_shape.outer_radius = 170
        assert test_volume < self.test_shape.volume

    def test_InnerTfCoilsFlat_gap_size(self):
        """Checks that a ValueError is raised when a too large gap_size is
        used."""

        def test_InnerTfCoilsFlat_incorrect_gap_size():
            self.test_shape.inner_radius = 20
            self.test_shape.outer_radius = 40
            self.test_shape.gap_size = 50
            self.test_shape.solid

        self.assertRaises(
            ValueError,
            test_InnerTfCoilsFlat_incorrect_gap_size
        )
