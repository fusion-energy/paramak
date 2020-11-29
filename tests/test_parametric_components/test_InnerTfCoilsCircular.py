
import unittest

import paramak


class TestInnerTfCoilsCircular(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.InnerTfCoilsCircular(
            height=500,
            inner_radius=50,
            outer_radius=150,
            number_of_coils=6,
            gap_size=5
        )

    def test_default_parameters(self):
        """Checks that the default parameters of an InnerTfCoilsCircular are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.azimuth_start_angle == 0
        assert self.test_shape.stp_filename == "InnerTfCoilsCircular.stp"
        assert self.test_shape.stl_filename == "InnerTfCoilsCircular.stl"
        assert self.test_shape.material_tag == "inner_tf_coil_mat"
        assert self.test_shape.workplane == "XY"
        assert self.test_shape.rotation_axis == "Z"

    def test_points_calculation(self):
        """Checks that the points used to construct the InnerTFCoilsCircular component
        are calculated correctly from the parameters given."""

        assert self.test_shape.points == [
            (49.937460888595446, 2.5, 'circle'),
            (43.300748759659555, 25.000903120744287, 'circle'),
            (27.1320420790315, 41.99824154201773, 'straight'),
            (77.154447582418, 128.6358861991937, 'circle'),
            (129.90375269002172, 75.00010024693078, 'circle'),
            (149.97916521970643, 2.5, 'straight'),
            (49.937460888595446, 2.5, 'circle')
        ]

    def test_creation(self):
        """Creates an inner tf coil using the InnerTfCoilsCircular parametric
        component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_azimuth_offset(self):
        """Creates an inner tf coil using the InnerTfCoilsCircular parametric
        component and checks that the azimuthal start angle can be changed
        correctly."""

        assert self.test_shape.azimuth_placement_angle == [
            0, 60, 120, 180, 240, 300]
        self.test_shape.azimuth_start_angle = 20
        assert self.test_shape.azimuth_placement_angle == [
            20, 80, 140, 200, 260, 320]

    def test_attributes(self):
        """Checks that changing the attributes of InnerTfCoilsCircular affects
        the cadquery solid produced."""

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
