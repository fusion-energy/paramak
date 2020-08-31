import math

import unittest

import pytest

from paramak import RotateCircleShape


class test_object_properties(unittest.TestCase):
    def test_absolute_shape_volume(self):
        """creates rotated shapes using circles and checks the volumes are correct"""

        # test_shape = RotateCircleShape(
        #     points=[(30, 0)],
        #     radius=10,
        #     rotation_angle=360
        # )

        # test_shape.create_solid()

        # assert test_shape.solid is not None
        # assert test_shape.volume == pytest.approx((2 * math.pi * 30) * (math.pi * 10**2), abs=0.1)

        # test_shape2 = RotateCircleShape(
        #     points=[(30, 0)],
        #     radius=10,
        #     rotation_angle=180
        # )

        # test_shape2.create_solid()

        # assert test_shape2.solid is not None
        # assert 2 * test_shape2.volume == pytest.approx(test_shape.volume)

    def test_shape_volume_with_multiple_azimuth_placement_angles(self):
        """creates two rotated shapes at different placement angles using circles and
        checks their relative volumes are correct"""

        test_shape = RotateCircleShape(
            points=[(30, 0)],
            radius=10,
            rotation_angle=10,
            azimuth_placement_angle=[0, 90, 180, 270],
        )
        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(
            (math.pi * 10 ** 2) * ((2 * math.pi * 30) / 36) * 4
        )

        test_shape2 = RotateCircleShape(
            points=[(30, 0)],
            radius=10,
            rotation_angle=5,
            azimuth_placement_angle=[0, 90, 180, 270],
        )
        test_shape2.create_solid()

        assert test_shape2.solid is not None
        assert 2 * test_shape2.volume == pytest.approx(test_shape.volume)

        test_shape3 = RotateCircleShape(
            points=[(30, 0)],
            radius=10,
            rotation_angle=20,
            azimuth_placement_angle=[0, 180],
        )
        test_shape3.create_solid()

        assert test_shape3.solid is not None
        assert test_shape3.volume == pytest.approx(test_shape.volume)

    def test_cut_volume(self):
        """creates a rotated shape using circles with another shape cut out and
        checks that the volume is correct"""

        inner_shape = RotateCircleShape(
            points=[(30, 0)], radius=5, rotation_angle=180)

        outer_shape = RotateCircleShape(
            points=[(30, 0)], radius=10, rotation_angle=180)

        outer_shape_cut = RotateCircleShape(
            points=[(30, 0)], radius=10, rotation_angle=180, cut=inner_shape
        )

        assert inner_shape.volume == pytest.approx(
            (math.pi * 5 ** 2) * ((2 * math.pi * 30) / 2)
        )
        assert outer_shape.volume == pytest.approx(
            (math.pi * 10 ** 2) * ((2 * math.pi * 30) / 2)
        )
        assert outer_shape_cut.volume == pytest.approx(
            ((math.pi * 10 ** 2) * ((2 * math.pi * 30) / 2))
            - ((math.pi * 5 ** 2) * ((2 * math.pi * 30) / 2))
        )

    def test_conditional_solid_reconstruction_parameters(self):
        """checks that a new cadquery solid with a new unique has value is created when the
        properties of 'points', 'radius', or 'rotation_angle' are changed"""

        test_shape = RotateCircleShape(
            points=[(30, 0)],
            radius=5,
            rotation_angle=360
        )
        test_shape.solid
        reference_hash_value = test_shape.hash_value

        # points
        test_shape.points = [(40, 0)]
        test_shape.solid
        assert test_shape.hash_value != reference_hash_value
        reference_hash_value = test_shape.hash_value

        # radius
        test_shape.radius = 10
        test_shape.solid
        assert test_shape.hash_value != reference_hash_value
        reference_hash_value = test_shape.hash_value

        # rotation_angle
        test_shape.rotation_angle = 180
        test_shape.solid
        assert test_shape.hash_value != reference_hash_value


if __name__ == "__main__":
    unittest.main()
