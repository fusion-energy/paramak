
import math

import cadquery as cq
from paramak import RotateStraightShape
from paramak.utils import (coefficients_of_line_from_points, intersect_solid,
                           rotate)


class PoloidalSegments(RotateStraightShape):
    """Creates a ring of wedges from a central point. When provided with a
    shape_to_segment the shape will be segmented by the wedges. This is useful
    for segmenting geometry into equal poloidal angles. Intended to segment the
    firstwall geometry for using in neutron wall loading simulations.

    Args:
        center_point (tuple of floats): the center of the segmentation wedges
            (x,z) values (cm).
        shape_to_segment (paramak.Shape, optional): the Shape to segment, if
            None then the segmenting solids will be returned. Defaults to None.
        number_of_segments (int, optional): the number of equal angles
            segments in 360 degrees. Defaults to 10.
        max_distance_from_center (float): the maximum distance from the center
            point outwards (cm). Defaults to 1000.0.
        stp_filename (str, optional): defaults to "PoloidalSegmenter.stp".
        stl_filename (str, optional): defaults to "PoloidalSegmenter.stl".
        name (str, optional): defaults to "poloidal_segmenter".
        material_tag (str, optional): defaults to "poloidal_segmenter_mat".
    """

    def __init__(
        self,
        center_point,
        shape_to_segment=None,
        number_of_segments=10,
        max_distance_from_center=1000.0,
        stp_filename="PoloidalSegmenter.stp",
        stl_filename="PoloidalSegmenter.stl",
        name="poloidal_segmenter",
        material_tag="poloidal_segmenter_mat",
        **kwargs
    ):

        super().__init__(
            name=name,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.center_point = center_point
        self.shape_to_segment = shape_to_segment
        self.number_of_segments = number_of_segments
        self.max_distance_from_center = max_distance_from_center

    @property
    def number_of_segments(self):
        return self._number_of_segments

    @number_of_segments.setter
    def number_of_segments(self, value):
        if isinstance(value, int) is False:
            raise TypeError(
                "PoloidalSegmenter.number_of_segments must be an int.")
        if value < 1:
            raise ValueError(
                "PoloidalSegmenter.number_of_segments must be a minimum of 1.")
        self._number_of_segments = value

    @property
    def shape_to_segment(self):
        return self._shape_to_segment

    @shape_to_segment.setter
    def shape_to_segment(self, value):
        self._shape_to_segment = value

    @property
    def center_point(self):
        return self._center_point

    @center_point.setter
    def center_point(self, center_point):
        self._center_point = center_point

    @property
    def max_distance_from_center(self):
        return self._max_distance_from_center

    @max_distance_from_center.setter
    def max_distance_from_center(self, value):
        self._max_distance_from_center = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe
        the 2D profile of the poloidal segmentation shape."""

        angle_per_segment = 360. / self.number_of_segments

        points = []

        current_angle = 0

        outer_point = (
            self.center_point[0] +
            self.max_distance_from_center,
            self.center_point[1])
        for i in range(self.number_of_segments):

            points.append(self.center_point)

            outer_point_1 = rotate(
                self.center_point,
                outer_point,
                math.radians(current_angle)
            )

            outer_point_2 = rotate(
                self.center_point,
                outer_point,
                math.radians(current_angle + angle_per_segment)
            )

            # if the point goes beyond the zero line then set to zero
            for new_point in [outer_point_1, outer_point_2]:
                if new_point[0] < 0:
                    m, c = coefficients_of_line_from_points(
                        new_point, self.center_point)
                    points.append((0, c))
                else:
                    points.append(new_point)

            current_angle = current_angle + angle_per_segment

        self.points = points

    def create_solid(self):
        """Creates a 3d solid using points with straight edges. Individual
        solids in the compound can be accessed using .Solids()[i] where i is an
        int.

           Returns:
              A CadQuery solid: A 3D solid volume
        """

        iter_points = iter(self.points)
        triangle_wedges = []
        wires = []
        for p1, p2, p3 in zip(iter_points, iter_points, iter_points):

            solid = (
                cq.Workplane(self.workplane)
                .polyline([p1[:2], p2[:2], p3[:2]])
            )

            wire = solid.close()

            wires.append(wire)

            solid = wire.revolve(self.rotation_angle)

            triangle_wedges.append(solid)

        self.wire = wires

        if self.shape_to_segment is None:

            compound = cq.Compound.makeCompound(
                [a.val() for a in triangle_wedges]
            )

        else:

            intersected_solids = []
            for segment in triangle_wedges:
                overlap = intersect_solid(segment, self.shape_to_segment)
                intersected_solids.append(overlap)

            compound = cq.Compound.makeCompound(
                [a.val() for a in intersected_solids]
            )

        self.solid = compound

        return compound
