
import unittest

import paramak
import pytest


class TestToroidalFieldCoilCoatHanger(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.ToroidalFieldCoilCoatHanger(
            horizontal_start_point=(200, 500),
            horizontal_length=400,
            vertical_mid_point=(700, 0),
            vertical_length=500,
            thickness=50,
            distance=30,
            number_of_coils=1,
            with_inner_leg=True
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a ToroidalFieldCoilCoatHanger are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.with_inner_leg
        assert self.test_shape.stp_filename == "ToroidalFieldCoilCoatHanger.stp"
        assert self.test_shape.stl_filename == "ToroidalFieldCoilCoatHanger.stl"
        assert self.test_shape.material_tag == "outer_tf_coil_mat"

    def test_points_calculation(self):
        """Checks that the points used to construct the ToroidalFieldCoilCoatHanger are
        calculated correctly from the parameters given."""

        assert self.test_shape.points == [
            (200, 500, 'straight'), (600, 500, 'straight'), (700, 250.0, 'straight'),
            (700, -250.0, 'straight'), (600, -500, 'straight'), (200, -500, 'straight'),
            (200, -550, 'straight'), (600, -550, 'straight'),
            (646.423834544263, -518.5695338177052, 'straight'),
            (746.423834544263, -268.5695338177052, 'straight'), (750, -250.0, 'straight'),
            (750, 250.0, 'straight'), (746.423834544263, 268.5695338177052, 'straight'),
            (646.423834544263, 518.5695338177052, 'straight'), (600, 550, 'straight'),
            (200, 550, 'straight'), (200, 500, 'straight')
        ]

    def test_creation_with_inner_leg(self):
        """Creates a tf coil with inner leg using the ToroidalFieldCoilCoatHanger
        parametric component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000
        assert self.test_shape.inner_leg_connection_points is not None

        test_inner_leg = paramak.ExtrudeStraightShape(
            points=self.test_shape.inner_leg_connection_points, distance=30
        )
        assert test_inner_leg.solid is not None

    def test_creation_with_inner_leg_with_overlap(self):
        """Creates tf coils with overlapping inner legs using the ToroidalFieldCoilCoatHanger
        parametric component and checks that a cadquery solid is created correctly."""

        self.test_shape.horizontal_start_point = (0, 500)
        self.test_shape.number_of_coils = 8
        assert self.test_shape.solid is not None

        with_inner_leg_volume = self.test_shape.volume

        self.test_shape.with_inner_leg = False
        without_inner_leg_volume = self.test_shape.volume

        assert self.test_shape.solid is not None

        test_inner_leg = paramak.ExtrudeStraightShape(
            points=[
                (0, 500), (50, 500), (50, -500), (0, -500)
            ], distance=30,
            azimuth_placement_angle=[0, 45, 90, 135, 180, 225, 270, 315]
        )
        inner_leg_volume = test_inner_leg.volume

        assert with_inner_leg_volume == pytest.approx(
            without_inner_leg_volume + inner_leg_volume)

    def test_creation_no_inner_leg(self):
        """Creates a tf coil with no inner leg using the ToroidalFieldCoilRectangle
        parametric component and checks that a cadquery solid is created."""

        test_volume = self.test_shape.volume

        test_inner_leg = paramak.ExtrudeStraightShape(
            points=self.test_shape.inner_leg_connection_points, distance=30
        )
        inner_leg_volume = test_inner_leg.volume

        self.test_shape.with_inner_leg = False

        assert self.test_shape.solid is not None
        assert self.test_shape.volume == pytest.approx(
            test_volume - inner_leg_volume)

    def test_absolute_volume(self):
        """Creates a tf coil using the ToroidalFieldCoilCoatHanger parametric
        component and checks that the volume is correc."""

        assert self.test_shape.volume == pytest.approx((400 * 50 * 30 * 2) +
                                                       ((50 * 50 * 30 / 2) * 2) + (50 * 500 * 30) +
                                                       (((150 * 250 * 30) - (((100 * 250) / 2) * 30) -
                                                         (((100 * 250) / 2) * 30)) * 2) + (50 * 1000 * 30), rel=0.1)

        self.test_shape.with_inner_leg = False
        assert self.test_shape.volume == pytest.approx((400 * 50 * 30 * 2) +
                                                       ((50 * 50 * 30 / 2) * 2) +
                                                       (50 * 500 * 30) + (((150 * 250 * 30) -
                                                                           (((100 * 250) / 2) * 30) -
                                                                           (((100 * 250) / 2) * 30)) * 2), rel=0.1)

        self.test_shape.with_inner_leg = True
        self.test_shape.number_of_coils = 8
        assert self.test_shape.volume == pytest.approx(((400 * 50 * 30 * 2) +
                                                        ((50 * 50 * 30 / 2) * 2) + (50 * 500 * 30) +
                                                        (((150 * 250 * 30) - (((100 * 250) / 2) * 30) -
                                                          (((100 * 250) / 2) * 30)) * 2) + (50 * 1000 * 30)) * 8, rel=0.1)

        self.test_shape.with_inner_leg = False
        assert self.test_shape.volume == pytest.approx(((400 * 50 * 30 * 2) +
                                                        ((50 * 50 * 30 / 2) * 2) + (50 * 500 * 30) +
                                                        (((150 * 250 * 30) - (((100 * 250) / 2) * 30) -
                                                          (((100 * 250) / 2) * 30)) * 2)) * 8, rel=0.1)

    def test_absolute_area(self):
        """Creates a tf coil using the ToroidalFieldCoilCoatHanger parametric
        component and checks that the areas of the faces are correct."""

        assert self.test_shape.area == pytest.approx((((400 * 50 * 2) +
                                                       (50 * 50 * 0.5 * 2) + (((150 * 250) - (100 * 250 * 0.5) -
                                                                               (100 * 250 * 0.5)) * 2) + (500 * 50)) * 2) +
                                                     ((50 * 30) * 4) + ((400 * 30) * 4) + ((500 * 30) * 2) +
                                                     ((((50**2 + 50**2)**0.5) * 30) * 2) +
                                                     ((((100**2 + 250**2)**0.5) * 30) * 4) + ((50 * 1000) * 2) +
                                                     ((1000 * 30) * 2), rel=0.1)
        assert len(self.test_shape.areas) == 24

        assert self.test_shape.areas.count(pytest.approx(50 * 30)) == 4
        assert self.test_shape.areas.count(pytest.approx(400 * 30)) == 4
        assert self.test_shape.areas.count(pytest.approx(500 * 30)) == 2
        assert self.test_shape.areas.count(
            pytest.approx(((100**2 + 250**2)**0.5) * 30)) == 4
        assert self.test_shape.areas.count(pytest.approx(50 * 1000)) == 2
        assert self.test_shape.areas.count(pytest.approx(1000 * 30)) == 2

        self.test_shape.with_inner_leg = False
        assert self.test_shape.area == pytest.approx((((400 * 50 * 2) +
                                                       (50 * 50 * 0.5 * 2) + (((150 * 250) - (100 * 250 * 0.5) -
                                                                               (100 * 250 * 0.5)) * 2) + (500 * 50)) * 2) + ((50 * 30) * 2) +
                                                     ((400 * 30) * 4) + ((500 * 30) * 2) +
                                                     ((((50**2 + 50**2)**0.5) * 30) * 2) +
                                                     ((((100**2 + 250**2)**0.5) * 30) * 4), rel=0.1)

    def test_rotation_angle(self):
        """Creates a tf coil with a rotation_angle < 360 degrees and checks
        that the correct cut is performed and the volume is correct."""

        self.test_shape.number_of_coils = 8

        self.test_shape.rotation_angle = 360
        self.test_shape.workplane = "XZ"
        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert self.test_shape.volume == pytest.approx(
            test_volume * 0.5, rel=0.01)

        self.test_shape.rotation_angle = 360
        self.test_shape.workplane = "YZ"
        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert self.test_shape.volume == pytest.approx(
            test_volume * 0.5, rel=0.01)

        self.test_shape.rotation_angle = 360
        self.test_shape.workplane = "XY"
        self.test_shape.rotation_axis = "Y"
        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert self.test_shape.volume == pytest.approx(test_volume * 0.5)
