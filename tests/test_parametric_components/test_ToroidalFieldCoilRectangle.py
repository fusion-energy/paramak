
import paramak
import pytest
import unittest


class test_ToroidalFieldCoilRectangle(unittest.TestCase):
    def test_ToroidalFieldCoilRectangle_creation_with_inner_leg(self):
        """creates a tf coil with inner leg using the ToroidalFieldCoilRectangle
        parametric component and checks that a cadquery solid is created"""

        test_shape = paramak.ToroidalFieldCoilRectangle(
            horizontal_start_point=(100, 700),
            vertical_mid_point=(800, 0),
            thickness=150,
            distance=50,
            number_of_coils=1,
            with_inner_leg=True
        )
        assert test_shape.solid is not None
        assert test_shape.volume > 1000
        assert test_shape.inner_leg_connection_points is not None

        test_inner_leg = paramak.ExtrudeStraightShape(
            points=test_shape.inner_leg_connection_points, distance=50
        )
        assert test_inner_leg.solid is not None

    def test_ToroidalFieldCoilRectangle_creation_no_inner_leg(self):
        """creates a tf coil with no inner leg using the ToroidalFieldCoilRectangle
        parametric component and checks that a cadquery solid is created"""

        test_shape_1 = paramak.ToroidalFieldCoilRectangle(
            horizontal_start_point=(100, 700), vertical_mid_point=(800, 0),
            thickness=150, distance=50, number_of_coils=1,
            with_inner_leg=True
        )
        test_volume_1 = test_shape_1.volume

        test_inner_leg = paramak.ExtrudeStraightShape(
            points=test_shape_1.inner_leg_connection_points, distance=50
        )
        inner_leg_volume = test_inner_leg.volume

        test_shape_2 = paramak.ToroidalFieldCoilRectangle(
            horizontal_start_point=(100, 700), vertical_mid_point=(800, 0),
            thickness=150, distance=50, number_of_coils=1,
            with_inner_leg=False
        )
        assert test_shape_2.solid is not None
        assert test_shape_2.volume == pytest.approx(
            test_volume_1 - inner_leg_volume)

    def test_ToroidalFieldCoilRectangle_absolute_volume(self):
        """creates a tf coil using the ToroidalFieldCoilRectangle parametric
        component and checks that the volume is correct"""

        test_shape = paramak.ToroidalFieldCoilRectangle(
            horizontal_start_point=(100, 700),
            vertical_mid_point=(800, 0),
            thickness=150,
            distance=50,
            number_of_coils=1
        )

        assert test_shape.volume == pytest.approx(
            (850 * 150 * 50 * 2) + (1400 * 150 * 50 * 2))

        test_shape.with_inner_leg = False
        assert test_shape.volume == pytest.approx(
            (850 * 150 * 50 * 2) + (1400 * 150 * 50))

        test_shape.with_inner_leg = True
        test_shape.number_of_coils = 8
        assert test_shape.volume == pytest.approx(
            ((850 * 150 * 50 * 2) + (1400 * 150 * 50 * 2)) * 8
        )

        test_shape.with_inner_leg = False
        assert test_shape.volume == pytest.approx(
            ((850 * 150 * 50 * 2) + (1400 * 150 * 50)) * 8
        )

    def test_ToroidalFieldCoilRectangle_absolute_areas(self):
        """creates tf coils using the ToroidalFieldCoilRectangle parametric
        component and checks that the areas of the faces are correct"""

        test_shape = paramak.ToroidalFieldCoilRectangle(
            horizontal_start_point=(100, 700),
            vertical_mid_point=(800, 0),
            thickness=150,
            distance=50,
            number_of_coils=1
        )

        assert test_shape.area == pytest.approx((((850 * 150 * 2) + (1400 * 150)) * 2) + (
            1400 * 150 * 2) + (850 * 50 * 2) + (1700 * 50) + (1400 * 50 * 3) + (700 * 50 * 2) + (150 * 50 * 4))
        assert len(test_shape.areas) == 16
        assert test_shape.areas.count(pytest.approx(
            (850 * 150 * 2) + (1400 * 150))) == 2
        assert test_shape.areas.count(pytest.approx((1400 * 150))) == 2
        assert test_shape.areas.count(pytest.approx(850 * 50)) == 2
        assert test_shape.areas.count(pytest.approx(1700 * 50)) == 1
        assert test_shape.areas.count(pytest.approx(1400 * 50)) == 3
        assert test_shape.areas.count(pytest.approx(700 * 50)) == 2
        assert test_shape.areas.count(pytest.approx(150 * 50)) == 4

        test_shape.with_inner_leg = False
        assert test_shape.area == pytest.approx((((850 * 150 * 2) + (1400 * 150)) * 2) + (
            850 * 50 * 2) + (1700 * 50) + (1400 * 50) + (700 * 50 * 2) + (150 * 50 * 2))

    def test_ToroidalFieldCoilRectangle_rotation_angle(self):
        """Creates tf coils with rotation_angles < 360 degrees in different
        workplanes and checks that the correct cuts are performed and their
        volumes are correct."""

        test_shape = paramak.ToroidalFieldCoilRectangle(
            horizontal_start_point=(100, 700),
            vertical_mid_point=(800, 0),
            with_inner_leg=False,
            thickness=50,
            distance=50,
            number_of_coils=8,
        )

        test_shape.rotation_angle = 360
        test_shape.workplane = "XZ"
        test_volume = test_shape.volume
        test_shape.rotation_angle = 180
        assert test_shape.volume == pytest.approx(test_volume * 0.5)

        test_shape.rotation_angle = 360
        test_shape.workplane = "YZ"
        test_volume = test_shape.volume
        test_shape.rotation_angle = 180
        assert test_shape.volume == pytest.approx(test_volume * 0.5)

        # this test will remain commented until workplane issue #308 is
        # resolved currently causes terminal to crash due to large number of
        # unions
        # test_shape.rotation_angle = 360
        # test_shape.workplane = "XY"
        # test_volume = test_shape.volume
        # test_shape.rotation_angle = 180
        # assert test_shape.volume == pytest.approx(test_volume * 0.5)

    def test_ToroidalFieldCoilRectangle_error(self):
        """Checks errors are raised with invalid arguments."""

        test_shape = paramak.ToroidalFieldCoilRectangle(
            horizontal_start_point=(100, 700),
            vertical_mid_point=(800, 0),
            with_inner_leg=False,
            thickness=50,
            distance=50,
            number_of_coils=8,
        )

        def incorrect_horizontal_start_point():
            test_shape.vertical_mid_point = (800, 0)
            test_shape.horizontal_start_point = (801, 700)
            test_shape.solid

        self.assertRaises(ValueError, incorrect_horizontal_start_point)

        def incorrect_vertical_mid_point():
            test_shape.horizontal_start_point = (100, 700)
            test_shape.vertical_mid_point = (800, 701)
            test_shape.solid

        self.assertRaises(ValueError, incorrect_vertical_mid_point)
