
import unittest

import paramak
import pytest


class TestInnerTfCoilsFlat(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.InnerTfCoilsFlat(
            height=500,
            inner_radius=50,
            outer_radius=150,
            number_of_coils=6,
            gap_size=5
        )

        self.test_shape2 = paramak.InnerTfCoilsFlat(
            height=500,
            inner_radius=50,
            outer_radius=150,
            number_of_coils=6,
            gap_size=5,
            radius_type='straight'
        )

        # hexagon with 0 inner radius
        self.test_shape_3 = paramak.InnerTfCoilsFlat(
            height=10,
            inner_radius=0,
            outer_radius=20,
            number_of_coils=6,
            gap_size=0,
            radius_type='straight',
        )

    def test_default_parameters(self):
        """Checks that the default parameters of an InnerTfCoilsFlat are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.azimuth_start_angle == 0
        assert self.test_shape.stp_filename == "InnerTfCoilsFlat.stp"
        assert self.test_shape.stl_filename == "InnerTfCoilsFlat.stl"
        assert self.test_shape.material_tag == "inner_tf_coil_mat"
        assert self.test_shape.workplane == "XY"
        assert self.test_shape.rotation_axis == "Z"
        assert self.test_shape.radius_type == "corner"

    def test_points_calculation(self):
        """Checks that the points used to construct the InnerTfCoilsFlat
        component are calculated correctly from the parameters given."""

        assert self.test_shape.points == [
            (49.937460888595446, 2.5),
            (27.1320420790315, 41.99824154201773),
            (77.154447582418, 128.6358861991937),
            (149.97916521970643, 2.5)
        ]

    def test_processed_points_calculation(self):
        """Checks that the points used to construct the InnerTfCoilsFlat
        component are calculated correctly from the parameters given."""

        assert self.test_shape.processed_points == [
            (49.937460888595446, 2.5, 'straight'),
            (27.1320420790315, 41.99824154201773, 'straight'),
            (77.154447582418, 128.6358861991937, 'straight'),
            (149.97916521970643, 2.5, 'straight'),
            (49.937460888595446, 2.5, 'straight')
        ]

    def test_creation(self):
        """Creates an inner tf coil using the InnerTFCoilsFlat parametric
        component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_azimuth_offset(self):
        """Creates an inner tf coil using the InnerTfCoilsFlat parametric
        component and checks that the azimuthal start angle can be changed
        correctly."""

        assert self.test_shape.azimuth_placement_angle == [
            0, 60, 120, 180, 240, 300]
        self.test_shape.azimuth_start_angle = 20
        assert self.test_shape.azimuth_placement_angle == [
            20, 80, 140, 200, 260, 320]

    def test_attributes(self):
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

    def test_gap_size(self):
        """Checks that a ValueError is raised when a too large gap_size is
        used."""

        def test_incorrect_gap_size():
            self.test_shape.inner_radius = 20
            self.test_shape.outer_radius = 40
            self.test_shape.gap_size = 50
            self.test_shape.solid

        self.assertRaises(
            ValueError,
            test_incorrect_gap_size
        )

    def test_radius_type(self):
        """Checks that a ValueError is raised when radius_type is not a
        valid option."""

        def test_incorrect_radius_type():
            self.test_shape.radius_type = 'coucou'

        self.assertRaises(
            ValueError,
            test_incorrect_radius_type
        )

    def test_volume_changes_with_radius_type(self):
        """Checks the analytical volume of the hex shaped extrusion and
        that adding a hole reduces voulume."""

        hex_volume = self.test_shape_3.volume
        hex_with_hole = self.test_shape_3
        hex_with_hole.inner_radius = 1

        assert hex_volume > hex_with_hole.volume
        assert pytest.approx(hex_volume, abs=0.5) == 1385.6 * 10

    def test_volume_changes_with_radius_type_for_corners(self):
        """Checks the analytical volume of the hex shaped extrusion and
        that adding a hole reduces voulume when the radius is to the corners."""

        hex_shape = self.test_shape_3
        hex_shape.radius_type = 'corner'
        hex_volume = hex_shape.volume

        assert pytest.approx(hex_volume, abs=0.5) == 1039.2 * 10

        hex_with_hole = self.test_shape_3
        hex_with_hole.radius_type = 'corner'
        hex_with_hole.inner_radius = 2

        assert hex_volume > hex_with_hole.volume
