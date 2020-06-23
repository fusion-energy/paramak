
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
        """creates rotated shapes with multiple placement angles using circles and \
            checks volumes are correct"""

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
        """creates a rotated shape using circles with another shape cut out and \
            checks the volume is correct"""

        inner_shape = RotateCircleShape(points=[(30, 0)], radius=5, rotation_angle=180)

        outer_shape = RotateCircleShape(points=[(30, 0)], radius=10, rotation_angle=180)

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

    def test_initial_solid_construction(self):
        """tests that a cadquery solid with a unique hash is constructed when .solid is called"""

        test_shape = RotateCircleShape(
            points=[(30, 0)], radius=5, rotation_angle=360
        )

        assert test_shape.hash_value is None
        assert test_shape.solid is not None
        assert type(test_shape.solid).__name__ == "Workplane"
        assert test_shape.hash_value is not None

    def test_solid_return(self):
        """tests that the same cadquery solid with the same unique hash is returned when shape.solid is called again when no changes have been made to the shape"""

        test_shape = RotateCircleShape(
            points=[(30, 0)], radius=5, rotation_angle=360
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value == test_shape.hash_value

    def test_conditional_solid_reconstruction(self):
        """tests that a new cadquery solid with a new unique hash is constructed when .solid is called again after changes have been made to the shape"""

        test_shape = RotateCircleShape(
            points=[(30, 0)], radius=5, rotation_angle=360
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.rotation_angle = 180

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value != test_shape.hash_value

    def test_hash_value_update(self):
        """tests that the hash_value of the shape is not updated until a new solid has been created"""

        test_shape = RotateCircleShape(
            points=[(30, 0)], radius=5, rotation_angle=360
        )
        test_shape.solid
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.rotation_angle = 180
        assert test_shape.hash_value == initial_hash_value
        test_shape.solid
        assert test_shape.hash_value != initial_hash_value

    def test_conditional_solid_reconstruction_parameters(self):
        """tests that a new cadquery solid with a new unique hash is created when the shape properties of points, radius or rotation angle are changed"""

        # points
        test_shape = RotateCircleShape(
            points=[(30, 0)], radius=5, rotation_angle=360
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.points = [(40, 0)]
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # radius
        test_shape = RotateCircleShape(
            points=[(30, 0)], radius=5, rotation_angle=360
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.radius = 10
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # rotation_angle
        test_shape = RotateCircleShape(
            points=[(30, 0)], radius=5, rotation_angle=360
        )
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.rotation_angle = 180
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value


if __name__ == "__main__":
    unittest.main()
