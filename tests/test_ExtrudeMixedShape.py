
import unittest

import pytest

from paramak import ExtrudeMixedShape


class test_object_properties(unittest.TestCase):
    def test_absolute_shape_volume(self):
        """creates an extruded shape with one placement angle using straight \
                and spline connections and checks the volume is correct"""

        test_shape = ExtrudeMixedShape(
            points=[
                (0, 0, "straight"),
                (0, 20, "straight"),
                (20, 20, "spline"),
                (20, 0, "spline")
            ],
            distance=30,
        )

        assert test_shape.solid is not None
        print(test_shape.volume)
        assert test_shape.volume >= 20 * 20 * 30

    def test_extruded_shape_relative_volume(self):
        """creates two extruded shapes with different placement angles using \
                straight and spline connections and checks their relative \
                volumes are correct"""

        test_shape_1 = ExtrudeMixedShape(
            points=[
                (5, 0, "straight"),
                (5, 20, "straight"),
                (10, 20, "spline"),
                (20, 10, "spline"),
                (10, 0, "straight")
            ],
            distance=10,
        )

        test_shape_1.azimuth_placement_angle = 0

        # test_shape_2 is test_shape_1 extruded 4 times

        test_shape_2 = ExtrudeMixedShape(
            points=[
                (5, 0, "straight"),
                (5, 20, "straight"),
                (10, 20, "spline"),
                (20, 10, "spline"),
                (10, 0, "straight")
            ],
            distance=10,
        )
        test_shape_2.azimuth_placement_angle = [0, 90, 180, 270]

        assert test_shape_1.volume * 4 == pytest.approx(test_shape_2.volume)

    def test_cut_volume(self):
        """creates an extruded shape with one placement angle using straight and \
                spline connections with another shape cut out and checks the \
                volume is correct"""

        inner_shape = ExtrudeMixedShape(
            points=[
                (5, 5, "straight"),
                (5, 10, "spline"),
                (10, 10, "spline"),
                (10, 5, "spline")
            ],
            distance=30,
        )

        outer_shape = ExtrudeMixedShape(
            points=[
                (3, 3, "straight"),
                (3, 12, "spline"),
                (12, 12, "spline"),
                (12, 3, "spline")
            ],
            distance=30,
        )

        outer_shape_with_cut = ExtrudeMixedShape(
            points=[
                (3, 3, "straight"),
                (3, 12, "spline"),
                (12, 12, "spline"),
                (12, 3, "spline")
            ],
            cut=inner_shape,
            distance=30,
        )

        assert inner_shape.volume == pytest.approx(1068, abs=2)
        assert outer_shape.volume == pytest.approx(3462, abs=2)
        assert outer_shape_with_cut.volume == pytest.approx(3462 - 1068, abs=2)

    def test_initial_solid_construction(self):
        """tests that a cadquery solid with a unique hash is constructed when .solid is called"""

        test_shape = ExtrudeMixedShape(
            points=[(0, 0, "straight"),
                    (0, 20, "spline"),
                    (20, 20, "spline"),
                    (20, 0, "straight"),
                    ],
            distance=20
        )

        assert test_shape.hash_value is None
        assert test_shape.solid is not None
        assert type(test_shape.solid).__name__ == "Workplane"
        assert test_shape.hash_value is not None

    def test_solid_return(self):
        """tests that the same cadquery solid with the same unique hash is returned when shape.solid is called again when no changes have been made to the shape"""

        test_shape = ExtrudeMixedShape(
            points=[(0, 0, "straight"),
                    (0, 20, "spline"),
                    (20, 20, "spline"),
                    (20, 0, "straight"),
                    ],
            distance=20
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value == test_shape.hash_value

    def test_conditional_solid_reconstruction(self):
        """tests that a new cadquery solid with a new unique hash is constructed when .solid is called again after changes have been made to the shape"""

        test_shape = ExtrudeMixedShape(
            points=[(0, 0, "straight"),
                    (0, 20, "spline"),
                    (20, 20, "spline"),
                    ],
            distance=20
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.distance = 30

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value != test_shape.hash_value

    def test_hash_value_update(self):
        """tests that the hash_value of the shape is not updated until a new solid has been created"""

        test_shape = ExtrudeMixedShape(
            points=[(0, 0, "straight"),
                    (0, 20, "spline"),
                    (20, 20, "spline"),
                    ],
            distance=20
        )
        test_shape.solid
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.distance = 30

        assert test_shape.hash_value == initial_hash_value
        test_shape.solid
        assert test_shape.hash_value != initial_hash_value

    def test_mixed_shape_with_straight_and_circle(self):
        """tests the construction of a shape with straight and circular edges"""
        test_shape = ExtrudeMixedShape(points=[(10, 20, 'straight'),
                                                (10, 10, 'straight'),
                                                (20, 10, 'circle'),
                                                (22, 15, 'circle'),
                                                (20, 20, 'straight'),
                                                ], distance = 10
                                        )
        assert test_shape.volume > 10 * 10 * 10

if __name__ == "__main__":
    unittest.main()
