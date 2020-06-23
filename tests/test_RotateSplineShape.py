
import unittest

import pytest

from paramak import RotateSplineShape


class test_object_properties(unittest.TestCase):
    def test_absolute_shape_volume(self):
        """creates a rotated shape using spline connections and checks \
                the volume is correct"""

        test_shape = RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)]
        )

        test_shape.rotation_angle = 360
        test_shape.create_solid()

        assert test_shape.solid is not None
        assert test_shape.volume > 100

    def test_cut_volume(self):
        """creates a rotated shape using spline connections with another shape \
                cut out and checks the volume is correct"""

        inner_shape = RotateSplineShape(
            points=[(5, 5), (5, 10), (10, 10), (10, 5)], rotation_angle=180
        )

        outer_shape = RotateSplineShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)], rotation_angle=180
        )

        outer_shape_with_cut = RotateSplineShape(
            points=[(3, 3), (3, 12), (12, 12), (12, 3)],
            cut=inner_shape,
            rotation_angle=180,
        )

        assert inner_shape.volume == pytest.approx(900.88, abs=0.1)
        assert outer_shape.volume == pytest.approx(2881.76, abs=0.1)
        assert outer_shape_with_cut.volume == pytest.approx(
            2881.76 - 900.88, abs=0.2
        )

    def test_initial_solid_construction(self):
        """tests that a cadquery solid with a unique hash is constructed when .solid is called"""

        test_shape = RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)],
            rotation_angle=360
        )

        assert test_shape.hash_value is None
        assert test_shape.solid is not None
        assert type(test_shape.solid).__name__ == "Workplane"
        assert test_shape.hash_value is not None

    def test_solid_return(self):
        """tests that the same cadquery solid with the same unique hash is returned when shape.solid is called again when no changes have been made to the shape"""

        test_shape = RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)],
            rotation_angle=360
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value == test_shape.hash_value

    def test_conditional_solid_reconstruction(self):
        """tests that a new cadquery solid with a new unique hash is constructed when .solid is called again after changes have been made to the shape"""

        test_shape = RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20)],
            rotation_angle=360
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

        test_shape = RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20)],
            rotation_angle=360
        )
        test_shape.solid
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.rotation_angle = 180
        assert test_shape.hash_value == initial_hash_value
        test_shape.solid
        assert test_shape.hash_value != initial_hash_value


if __name__ == "__main__":
    unittest.main()
