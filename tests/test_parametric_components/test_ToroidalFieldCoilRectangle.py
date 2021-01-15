
import unittest

import paramak
import pytest


class TestToroidalFieldCoilRectangle(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.ToroidalFieldCoilRectangle(
            horizontal_start_point=(100, 700),
            vertical_mid_point=(800, 0),
            thickness=50,
            distance=30,
            number_of_coils=1,
            with_inner_leg=True
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a ToroidalFieldCoilRectangle are correct."""

        assert self.test_shape.rotation_angle == 360
        assert self.test_shape.with_inner_leg
        assert self.test_shape.stp_filename == "ToroidalFieldCoilRectangle.stp"
        assert self.test_shape.stl_filename == "ToroidalFieldCoilRectangle.stl"
        assert self.test_shape.material_tag == "outer_tf_coil_mat"

    def test_points_calculation(self):
        """Checks that the points used to construct the ToroidalFieldCoilRectangle are
        calculated correctly from the parameters given."""

        assert self.test_shape.points == [
            (100, 700, 'straight'), (150, 700, 'straight'), (800, 700, 'straight'),
            (800, -700, 'straight'), (150, -700, 'straight'), (100, -700, 'straight'),
            (100, -750, 'straight'), (850, -750, 'straight'), (850, 750, 'straight'),
            (100, 750, 'straight'), (100, 700, 'straight')
        ]

    def test_creation_with_inner_leg(self):
        """Creates a tf coil with inner leg using the ToroidalFieldCoilRectangle
        parametric component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000
        assert self.test_shape.inner_leg_connection_points is not None

        test_inner_leg = paramak.ExtrudeStraightShape(
            points=self.test_shape.inner_leg_connection_points, distance=30
        )
        assert test_inner_leg.solid is not None

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
        """Creates a tf coil using the ToroidalFieldCoilRectangle parametric
        component and checks that the volume is correct."""

        self.test_shape.thickness = 150
        self.test_shape.distance = 50

        assert self.test_shape.volume == pytest.approx(
            (850 * 150 * 50 * 2) + (1400 * 150 * 50 * 2))

        self.test_shape.with_inner_leg = False
        assert self.test_shape.volume == pytest.approx(
            (850 * 150 * 50 * 2) + (1400 * 150 * 50))

        self.test_shape.with_inner_leg = True
        self.test_shape.number_of_coils = 8
        assert self.test_shape.volume == pytest.approx(
            ((850 * 150 * 50 * 2) + (1400 * 150 * 50 * 2)) * 8
        )

        self.test_shape.with_inner_leg = False
        assert self.test_shape.volume == pytest.approx(
            ((850 * 150 * 50 * 2) + (1400 * 150 * 50)) * 8
        )

    def test_absolute_areas(self):
        """Creates tf coils using the ToroidalFieldCoilRectangle parametric
        component and checks that the areas of the faces are correct."""

        self.test_shape.thickness = 150
        self.test_shape.distance = 50

        assert self.test_shape.area == pytest.approx((((850 * 150 * 2) + (1400 * 150)) * 2) + (
            1400 * 150 * 2) + (850 * 50 * 2) + (1700 * 50) + (1400 * 50 * 3) + (700 * 50 * 2) + (150 * 50 * 4))
        assert len(self.test_shape.areas) == 16
        assert self.test_shape.areas.count(pytest.approx(
            (850 * 150 * 2) + (1400 * 150))) == 2
        assert self.test_shape.areas.count(pytest.approx((1400 * 150))) == 2
        assert self.test_shape.areas.count(pytest.approx(850 * 50)) == 2
        assert self.test_shape.areas.count(pytest.approx(1700 * 50)) == 1
        assert self.test_shape.areas.count(pytest.approx(1400 * 50)) == 3
        assert self.test_shape.areas.count(pytest.approx(700 * 50)) == 2
        assert self.test_shape.areas.count(pytest.approx(150 * 50)) == 4

        self.test_shape.with_inner_leg = False
        assert self.test_shape.area == pytest.approx((((850 * 150 * 2) + (1400 * 150)) * 2) + (
            850 * 50 * 2) + (1700 * 50) + (1400 * 50) + (700 * 50 * 2) + (150 * 50 * 2))

    def test_rotation_angle(self):
        """Creates tf coils with rotation_angles < 360 degrees in different
        workplanes and checks that the correct cuts are performed and their
        volumes are correct."""

        self.test_shape.number_of_coils = 8

        self.test_shape.rotation_angle = 360
        self.test_shape.workplane = "XZ"
        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert self.test_shape.volume == pytest.approx(test_volume * 0.5)

        self.test_shape.rotation_angle = 360
        self.test_shape.workplane = "YZ"
        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert self.test_shape.volume == pytest.approx(test_volume * 0.5)

        self.test_shape.rotation_angle = 360
        self.test_shape.workplane = "XY"
        self.test_shape.rotation_axis = "Y"
        test_volume = self.test_shape.volume
        self.test_shape.rotation_angle = 180
        assert self.test_shape.volume == pytest.approx(test_volume * 0.5)

    def test_ToroidalFieldCoilRectangle_incorrect_horizonal_start_point(self):
        """Checks that an error is raised when a ToroidalFieldCoilRectangle is made
        with an incorrect horizontal_start_point."""

        def make_ToroidalFieldCoilRectangle_incorrect_horizontal_start_point():
            self.test_shape.vertical_mid_point = (800, 0)
            self.test_shape.horizontal_start_point = (801, 700)
            self.test_shape.solid

        self.assertRaises(
            ValueError,
            make_ToroidalFieldCoilRectangle_incorrect_horizontal_start_point
        )

    def test_ToroidalFieldCoilRectangle_incorrect_vertical_mid_point(self):
        """Checks that an error is raised when a ToroidalFieldCoilRectangle is made
        with an incorrect vertical_mid_point."""

        def make_ToroidalFieldCoilRectangle_incorrect_vertical_mid_point():
            self.test_shape.horizontal_start_point = (100, 700)
            self.test_shape.vertical_mid_point = (800, 701)
            self.test_shape.solid

        self.assertRaises(
            ValueError,
            make_ToroidalFieldCoilRectangle_incorrect_vertical_mid_point
        )
