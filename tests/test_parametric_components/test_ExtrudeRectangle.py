
import unittest

import paramak
import pytest


class TestExtrudeRectangle(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.ExtrudeRectangle(
            height=50, width=60, center_point=(1000, 500), distance=333
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a ExtrudeRectangle are
        correct."""

        assert self.test_shape.distance == 333
        assert self.test_shape.stp_filename == "ExtrudeRectangle.stp"
        assert self.test_shape.stl_filename == "ExtrudeRectangle.stl"
        assert self.test_shape.material_tag == "extrude_rectangle_mat"

    def test_processed_points_calculation(self):
        """Checks that the processed_points used to construct the
        ExtrudeRectangle are calculated correctly from the parameters given."""

        assert self.test_shape.processed_points == [
            (1030.0, 525.0, 'straight'),
            (1030.0, 475.0, 'straight'),
            (970.0, 475.0, 'straight'),
            (970.0, 525.0, 'straight'),
            (1030.0, 525.0, 'straight')
        ]

    def test_points_calculation(self):
        """Checks that the points used to construct the ExtrudeRectangle are
        calculated correctly from the parameters given."""

        assert self.test_shape.points == [
            (1030.0, 525.0),
            (1030.0, 475.0),
            (970.0, 475.0),
            (970.0, 525.0)
        ]

    def test_creation(self):
        """Creates a rectangular extrusion using the ExtrudeRectangle
        parametric component and checks that a cadquery solid is created."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_absolute_volume(self):
        """Creates a rectangular extrusion using the ExtrudeRectangle
        parametric component and checks that the volume is correct"""

        assert self.test_shape.volume == pytest.approx(50 * 60 * 333)

    def test_absolute_areas(self):
        """Creates a rectangular extrusion using the ExtrudeRectangle
        parametric component and checks that the areas are correct"""

        assert len(self.test_shape.areas) == 6
        assert len(set([round(i) for i in self.test_shape.areas])) == 3
        assert self.test_shape.areas.count(
            pytest.approx(60 * 50)) == 2
        assert self.test_shape.areas.count(
            pytest.approx(50 * 333)) == 2
        assert self.test_shape.areas.count(
            pytest.approx(60 * 333)) == 2
