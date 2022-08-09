import unittest

import plotly.graph_objects as go
import pytest

import paramak
from paramak.utils import (
    EdgeLengthSelector,
    FaceAreaSelector,
    extract_points_from_edges,
    facet_wire,
    find_center_point_of_circle,
    plotly_trace,
    find_radius_of_circle,
    get_bounding_box,
    get_largest_dimension,
    get_largest_distance_from_origin,
)
import cadquery as cq


class TestUtilityFunctions(unittest.TestCase):
    """ "tests the utility functions"""

    def test_bounding_box_with_single_shape_at_origin(self):
        """checks the type and values of the bounding box returned"""

        test_sphere = cq.Workplane("XY").moveTo(0, 0).sphere(10)

        bounding_box = get_bounding_box(test_sphere)

        assert len(bounding_box) == 2
        assert len(bounding_box[0]) == 3
        assert len(bounding_box[1]) == 3
        assert bounding_box[0][0] == -10
        assert bounding_box[0][1] == -10
        assert bounding_box[0][2] == -10
        assert bounding_box[1][0] == 10
        assert bounding_box[1][1] == 10
        assert bounding_box[1][2] == 10

    def test_bounding_box_with_single_shape(self):
        """checks the type and values of the bounding box returned"""

        test_sphere = cq.Workplane("XY").moveTo(100, 50).sphere(10)

        bounding_box = get_bounding_box(test_sphere)

        assert len(bounding_box) == 2
        assert len(bounding_box[0]) == 3
        assert len(bounding_box[1]) == 3
        assert bounding_box[0][0] == 90
        assert bounding_box[0][1] == 40
        assert bounding_box[0][2] == -10
        assert bounding_box[1][0] == 110
        assert bounding_box[1][1] == 60
        assert bounding_box[1][2] == 10

    def test_bounding_box_with_compound(self):
        """checks the type and values of the bounding box returned"""

        test_sphere_1 = cq.Workplane("XY").moveTo(100, 50).sphere(10)
        test_sphere_2 = cq.Workplane("XY").moveTo(-100, -50).sphere(10)

        both_shapes = cq.Compound.makeCompound([test_sphere_1.val(), test_sphere_2.val()])

        bounding_box = get_bounding_box(both_shapes)

        assert len(bounding_box) == 2
        assert len(bounding_box[0]) == 3
        assert len(bounding_box[1]) == 3
        assert bounding_box[0][0] == -110
        assert bounding_box[0][1] == -60
        assert bounding_box[0][2] == -10
        assert bounding_box[1][0] == 110
        assert bounding_box[1][1] == 60
        assert bounding_box[1][2] == 10

    def test_largest_dimension_with_single_solid_at_origin(self):

        test_sphere = cq.Workplane("XY").moveTo(0, 0).sphere(10)

        largest_dimension = get_largest_dimension(test_sphere)

        assert largest_dimension == 20

    def test_largest_dimension__from_origin_with_single_solid_at_origin(self):

        test_sphere = cq.Workplane("XY").moveTo(0, 0).sphere(10)

        largest_dimension = get_largest_distance_from_origin(test_sphere)

        assert largest_dimension == 10

    def test_largest_dimension_with_single_solid(self):

        test_sphere = cq.Workplane("XY").moveTo(100, 0).sphere(10)

        largest_dimension = get_largest_distance_from_origin(test_sphere)

        assert largest_dimension == 110

    def test_largest_dimension_with_compound(self):

        test_sphere_1 = cq.Workplane("XY").moveTo(100, 50).sphere(10)
        test_sphere_2 = cq.Workplane("XY").moveTo(-200, -50).sphere(10)

        both_shapes = cq.Compound.makeCompound([test_sphere_1.val(), test_sphere_2.val()])

        largest_dimension = get_largest_distance_from_origin(both_shapes)

        assert largest_dimension == 210

    def test_convert_circle_to_spline(self):
        """Tests the conversion of 3 points on a circle into points on a spline
        curve."""

        new_points = paramak.utils.convert_circle_to_spline(
            p_0=(200.0, 0.0), p_1=(250.0, 50.0), p_2=(200.0, 100.0), tolerance=0.2
        )

        # these points can change from 200. to values like 200.00000000000009
        assert pytest.approx(new_points[0][0], abs=0.0000000000001) == 200
        assert pytest.approx(new_points[0][1], abs=0.0000000000001) == 0
        assert pytest.approx(new_points[-1][0], abs=0.0000000000001) == 200
        assert pytest.approx(new_points[-1][1], abs=0.0000000000001) == 100

        new_points_more_details = paramak.utils.convert_circle_to_spline(
            p_0=(200, 0), p_1=(250, 50), p_2=(200, 100), tolerance=0.1
        )

        assert len(new_points_more_details) > len(new_points)

    def test_extract_points_from_edges(self):
        """Extracts points from edges and checks the list returned is the
        correct len and contains the correct types"""

        test_points = [(1, 1), (3, 1), (4, 2)]
        test_shape = paramak.ExtrudeStraightShape(points=test_points, distance=6, workplane="YZ")

        edges = facet_wire(wire=test_shape.wire)

        points = extract_points_from_edges(edges=edges, view_plane="YZ")

        assert len(points) == 6

        for point in points:
            assert len(point) == 2
            assert isinstance(point[0], float)
            assert isinstance(point[1], float)

        points_single_edge = extract_points_from_edges(edges=edges[0], view_plane="YZ")

        assert len(points) > len(points_single_edge)
        for point in points_single_edge:
            assert len(point) == 2
            assert isinstance(point[0], float)
            assert isinstance(point[1], float)

        points_single_edge = extract_points_from_edges(edges=edges[0], view_plane="XYZ")

        assert len(points) > len(points_single_edge)
        for point in points_single_edge:
            assert len(point) == 3
            assert isinstance(point[0], float)
            assert isinstance(point[1], float)
            assert isinstance(point[2], float)

    def test_trace_creation(self):
        """Creates a plotly trace and checks the type returned"""
        trace = plotly_trace(
            points=[(0, 20), (20, 0), (0, -20)],
            mode="markers+lines",
            color=(10, 10, 10, 0.5),
        )

        assert isinstance(trace, go.Scatter)

    def test_trace_creation_3d(self):
        """Creates a 3d plotly trace and checks the type returned"""
        trace = plotly_trace(
            points=[(0, 20, 0), (20, 0, 10), (0, -20, -10)],
            mode="markers+lines",
            color=(10, 10, 10),
        )

        assert isinstance(trace, go.Scatter3d)

    def test_find_center_point_of_circle(self):
        """passes three points on a circle to the function and checks that the
        radius and center of the circle is calculated correctly"""

        point_a = (0, 20)
        point_b = (20, 0)
        point_3 = (0, -20)

        assert find_center_point_of_circle(point_a, point_b, point_3) == (0, 0)

    def test_find_radius_circle(self):
        """passes and edge point and the center point of a circle in to the
        function and checks the radius is calculated correctly"""

        edge_point = (0, 20)
        center_point = (0, 0)

        assert find_radius_of_circle(center_point, edge_point) == 20

    def test_EdgeLengthSelector_with_fillet_areas(self):
        """tests the filleting of a RotateStraightShape results in an extra
        surface area"""

        test_shape = paramak.RotateStraightShape(points=[(1, 1), (2, 1), (2, 2)])

        assert len(test_shape.areas) == 3

        test_shape.solid = test_shape.solid.edges(EdgeLengthSelector(6.28)).fillet(0.1)

        assert len(test_shape.areas) == 4

    def test_FaceAreaSelector_with_fillet_areas(self):
        """tests the filleting of a ExtrudeStraightShape"""

        test_shape = paramak.ExtrudeStraightShape(distance=5, points=[(1, 1), (2, 1), (2, 2)])

        assert len(test_shape.areas) == 5

        test_shape.solid = test_shape.solid.faces(FaceAreaSelector(0.5)).fillet(0.1)

        assert len(test_shape.areas) == 11

    def test_find_center_point_of_circle_zero_det(self):
        """Checks that None is given if det is zero"""
        point_a = (0, 0)
        point_b = (0, 0)
        point_3 = (0, 0)

        assert find_center_point_of_circle(point_a, point_b, point_3) is None
