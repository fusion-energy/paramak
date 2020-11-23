
import unittest

import paramak


class test_InnerTfCoilsCircular(unittest.TestCase):
    def test_InnerTfCoilsCircular_creation(self):
        """Creates an inner tf coil using the InnerTfCoilsCircular parametric
        component and checks that a cadquery solid is created."""

        test_shape = paramak.InnerTfCoilsCircular(
            height=500,
            inner_radius=50,
            outer_radius=150,
            number_of_coils=6,
            gap_size=5,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_InnerTfCoilsCircular_azimuth_offset(self):
        """Creates an inner tf coil using the InnerTfCoilsCircular parametric
        component and checks that the azimuthal start angle can be changed
        correctly."""

        test_shape = paramak.InnerTfCoilsCircular(
            height=500,
            inner_radius=50,
            outer_radius=150,
            number_of_coils=6,
            gap_size=5
        )

        assert test_shape.azimuth_placement_angle == [
            0, 60, 120, 180, 240, 300]
        test_shape.azimuth_start_angle = 20
        assert test_shape.azimuth_placement_angle == [
            20, 80, 140, 200, 260, 320]

    def test_InnerTfCoilsCircular_attributes(self):
        """Checks that changing the attributes of InnerTfCoilsCircular affects
        the cadquery solid produced."""

        test_shape = paramak.InnerTfCoilsCircular(
            height=500,
            inner_radius=50,
            outer_radius=150,
            number_of_coils=6,
            gap_size=5
        )
        test_shape_volume = test_shape.volume

        test_shape.height = 1000
        assert test_shape_volume == test_shape.volume * 0.5
        test_shape.height = 500
        test_shape.inner_radius = 30
        assert test_shape_volume < test_shape.volume
        test_shape.inner_radius = 50
        test_shape.outer_radius = 170
        assert test_shape_volume < test_shape.volume

    def test_InnerTfCoilsCircular_gap_size(self):
        """Checks that a ValueError is raised when a too large gap_size is
        used."""

        def test_InnerTfCoilsCircular_incorrect_gap_size():
            paramak.InnerTfCoilsCircular(
                height=100,
                inner_radius=20,
                outer_radius=40,
                number_of_coils=8,
                gap_size=20
            ).solid

        self.assertRaises(
            ValueError,
            test_InnerTfCoilsCircular_incorrect_gap_size
        )
