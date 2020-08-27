import math
import unittest

import pytest

import paramak


class test_object_properties(unittest.TestCase):
    def test_absolute_shape_volume(self):
        """creates extruded shapes using circles and checks the volumes are correct"""

        test_shape = paramak.ExtrudeCircleShape(
            points=[(30, 0)], radius=10, distance=20
        )

        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume == pytest.approx(math.pi * 10 ** 2 * 20)

        test_shape2 = paramak.ExtrudeCircleShape(
            points=[(30, 0)], radius=10, distance=10
        )

        test_shape2.create_solid()

        assert test_shape2.solid is not None
        assert 2 * test_shape2.volume == pytest.approx(test_shape.volume)

    def test_extruded_shape_relative_volume(self):
        """creates two extruded shapes at different placement angles using
        circles and checks their relative volumes are correct"""

        test_shape1 = paramak.ExtrudeCircleShape(
            points=[(30, 0)], radius=10, distance=20, azimuth_placement_angle=0
        )

        test_shape2 = paramak.ExtrudeCircleShape(
            points=[(30, 0)],
            radius=10,
            distance=20,
            azimuth_placement_angle=[0, 90, 180, 270],
        )

        assert test_shape1.volume * 4 == pytest.approx(test_shape2.volume)

    def test_cut_volume(self):
        """creates an extruded shape using circles with another shape cut out and
        checks that the volume is correct"""

        inner_shape = paramak.ExtrudeCircleShape(
            points=[(30, 0)], radius=5, distance=20
        )

        outer_shape = paramak.ExtrudeCircleShape(
            points=[(30, 0)], radius=10, distance=20
        )

        outer_shape_with_cut = paramak.ExtrudeCircleShape(
            points=[(30, 0)], radius=10, distance=20, cut=inner_shape
        )

        assert inner_shape.volume == pytest.approx(math.pi * 5 ** 2 * 20)
        assert outer_shape.volume == pytest.approx(math.pi * 10 ** 2 * 20)
        assert outer_shape_with_cut.volume == pytest.approx(
            (math.pi * 10 ** 2 * 20) - (math.pi * 5 ** 2 * 20)
        )

    def test_initial_solid_construction(self):
        """creates an extruded shape using circles and checks that a cadquery solid with a unique
        hash value is created when .solid is called"""

        test_shape = paramak.ExtrudeCircleShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], radius=10, distance=20
        )

        assert test_shape.hash_value is None
        assert test_shape.solid is not None
        assert type(test_shape.solid).__name__ == "Workplane"
        assert test_shape.hash_value is not None

    def test_solid_return(self):
        """checks that the same cadquery solid with the same unique hash value is returned when
        shape.solid is called again after no changes have been made to the ExtrudeCircleShape"""

        test_shape = paramak.ExtrudeCircleShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], radius=10, distance=20
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value == test_shape.hash_value

    def test_conditional_solid_reconstruction(self):
        """checks that a new cadquery solid with a new unique hash value is constructed when .solid
        is called after changes to the ExtrudeCircleShape have been made"""

        test_shape = paramak.ExtrudeCircleShape(
            points=[(0, 0), (0, 20), (20, 20)], radius=10, distance=20
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.distance = 30

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value != test_shape.hash_value

    def test_hash_value_update(self):
        """checks that the hash value of an ExtrudeCircleShape is not updated until a new solid
        has been created"""

        test_shape = paramak.ExtrudeCircleShape(
            points=[(0, 0), (0, 20), (20, 20)], radius=10, distance=20
        )
        test_shape.solid
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.distance = 30

        assert test_shape.hash_value == initial_hash_value
        test_shape.solid
        assert test_shape.hash_value != initial_hash_value

    def test_conditional_solid_reconstruction_parameters(self):
        """checks that a new cadquery solid with a new unique hash value is created when the shape
        properties of 'points', 'radius' or 'distance' are changed"""

        # points
        test_shape = paramak.ExtrudeCircleShape(
            points=[(30, 0)], radius=5, distance=20)
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.points = [(40, 0)]
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # radius
        test_shape = paramak.ExtrudeCircleShape(
            points=[(30, 0)], radius=5, distance=20)
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.radius = 10
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value

        # distance
        test_shape = paramak.ExtrudeCircleShape(
            points=[(30, 0)], radius=5, distance=20)
        test_shape.solid
        initial_hash_value = test_shape.hash_value
        test_shape.distance = 30
        test_shape.solid
        assert test_shape.solid is not None
        assert test_shape.hash_value != initial_hash_value


if __name__ == "__main__":
    unittest.main()
