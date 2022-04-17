import unittest

import pytest

import paramak


class TestExtrudeHollowRectangle(unittest.TestCase):
    def setUp(self):
        self.test_shape = paramak.ExtrudeHollowRectangle(height=10, width=15, casing_thickness=1, distance=2)

    def test_default_parameters(self):
        """Checks that the default parameters of a ExtrudeHollowRectangle are
        correct."""

        assert self.test_shape.center_point == (0, 0)

    def test_processed_points_calculation(self):
        """Checks that the processed_points used to construct the
        ExtrudeHollowRectangle are calculated correctly from the parameters given."""

        assert self.test_shape.processed_points == [
            (7.5, 5.0, "straight"),
            (7.5, -5.0, "straight"),
            (-7.5, -5.0, "straight"),
            (-7.5, 5.0, "straight"),
            (7.5, 5.0, "straight"),
            (8.5, 6.0, "straight"),
            (8.5, -6.0, "straight"),
            (-8.5, -6.0, "straight"),
            (-8.5, 6.0, "straight"),
            (8.5, 6.0, "straight"),
            (7.5, 5.0, "straight"),
        ]

    def test_points_calculation(self):
        """Checks that the points used to construct the ExtrudeHollowRectangle are
        calculated correctly from the parameters given."""

        assert self.test_shape.points == [
            (7.5, 5.0),
            (7.5, -5.0),
            (-7.5, -5.0),
            (-7.5, 5.0),
            (7.5, 5.0),
            (8.5, 6.0),
            (8.5, -6.0),
            (-8.5, -6.0),
            (-8.5, 6.0),
            (8.5, 6.0),
        ]

    def test_creation(self):
        """Creates a rectangular extrusion using the ExtrudeHollowRectangle
        parametric component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume() > 100

    def test_absolute_volume(self):
        """Creates a rectangular extrusion using the ExtrudeHollowRectangle
        parametric component and checks that the volume is correct"""

        assert self.test_shape.volume() == pytest.approx((17 * 12 * 2) - (15 * 10 * 2))

    def test_absolute_areas(self):
        """Creates a rectangular extrusion using the ExtrudeHollowRectangle
        parametric component and checks that the areas are correct"""

        assert len(self.test_shape.areas) == 10
        assert len(set([round(i) for i in self.test_shape.areas])) == 5
        assert self.test_shape.areas.count(pytest.approx(15 * 2)) == 2
        assert self.test_shape.areas.count(pytest.approx(10 * 2)) == 2

    def test_center_point_changes_bounding_box(self):

        default_shape_bb = ((-(15 + 2) / 2, -1.0, -(10 + 2) / 2), ((15 + 2) / 2, 1.0, (10 + 2) / 2))
        assert self.test_shape.bounding_box == default_shape_bb

        self.test_shape.center_point = (1, 1)

        assert self.test_shape.bounding_box == (
            (default_shape_bb[0][0] + 1, default_shape_bb[0][1], default_shape_bb[0][2] + 1),
            (default_shape_bb[1][0] + 1, default_shape_bb[1][1], default_shape_bb[1][2] + 1),
        )
