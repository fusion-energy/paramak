
import unittest
from cadquery.cq import Workplane

import numpy as np
import paramak
from paramak.utils import (EdgeLengthSelector, FaceAreaSelector,
                           find_center_point_of_circle, plotly_trace,
                           extract_points_from_edges, facet_wire)
import plotly.graph_objects as go


class TestUtilityFunctions(unittest.TestCase):

    def test_extract_points_from_edges(self):
        """Extracts points from edges and checks the list returned is the
        correct len and contains the correct types"""

        test_points = [(1, 1), (3, 1), (4, 2)]
        test_shape = paramak.ExtrudeStraightShape(
            points=test_points,
            distance=6,
            workplane='YZ')

        edges = facet_wire(wire=test_shape.wire)

        points = extract_points_from_edges(edges=edges, view_plane='YZ')

        assert len(points) == 6

        for point in points:
            assert len(point) == 2
            assert isinstance(point[0], float)
            assert isinstance(point[1], float)

        points_single_edge = extract_points_from_edges(edges=edges[0], view_plane='YZ')

        assert len(points) > len(points_single_edge)
        for point in points_single_edge:
            assert len(point) == 2
            assert isinstance(point[0], float)
            assert isinstance(point[1], float)

        points_single_edge = extract_points_from_edges(edges=edges[0], view_plane='XYZ')

        assert len(points) > len(points_single_edge)
        for point in points_single_edge:
            assert len(point) == 3
            assert isinstance(point[0], float)
            assert isinstance(point[1], float)
            assert isinstance(point[2], float)

    def test_trace_creation(self):
        """Creates a plotly trace and checks the type returned"""
        trace = plotly_trace(
            points=[
                (0, 20),
                (20, 0),
                (0, -20)
            ],
            mode='markers+lines',
            color=(10, 10, 10, 0.5)
        )

        assert isinstance(trace, go.Scatter)

    def test_trace_creation_3d(self):
        """Creates a 3d plotly trace and checks the type returned"""
        trace = plotly_trace(
            points=[
                (0, 20, 0),
                (20, 0, 10),
                (0, -20, -10)
            ],
            mode='markers+lines',
            color=(10, 10, 10)
        )

        assert isinstance(trace, go.Scatter3d)

    def test_find_center_point_of_circle(self):
        """passes three points on a circle to the function and checks that the
        radius and center of the circle is calculated correctly"""

        point_1 = (0, 20)
        point_2 = (20, 0)
        point_3 = (0, -20)

        assert find_center_point_of_circle(
            point_1, point_2, point_3) == (
            (0, 0), 20)

    def test_EdgeLengthSelector_with_fillet_areas(self):
        """tests the filleting of a RotateStraightShape results in an extra
        surface area"""

        test_shape = paramak.RotateStraightShape(
            points=[(1, 1), (2, 1), (2, 2)])

        assert len(test_shape.areas) == 3

        test_shape.solid = test_shape.solid.edges(
            EdgeLengthSelector(6.28)).fillet(0.1)

        assert len(test_shape.areas) == 4

    def test_FaceAreaSelector_with_fillet_areas(self):
        """tests the filleting of a ExtrudeStraightShape"""

        test_shape = paramak.ExtrudeStraightShape(
            distance=5, points=[(1, 1), (2, 1), (2, 2)])

        assert len(test_shape.areas) == 5

        test_shape.solid = test_shape.solid.faces(
            FaceAreaSelector(0.5)).fillet(0.1)

        assert len(test_shape.areas) == 11

    def test_find_center_point_of_circle_zero_det(self):
        """Checks that None is given if det is zero
        """
        point_1 = (0, 0)
        point_2 = (0, 0)
        point_3 = (0, 0)

        assert find_center_point_of_circle(
            point_1, point_2, point_3) == (
            None, np.inf)
