import math
import numpy as np
import cadquery as cq

from paramak import RotateStraightShape
from paramak.utils import rotate, intersect_solid, coefficients_of_line_from_points


class PoloidalSegments(RotateStraightShape):
    """Creates a ring of wedges from a central point. When provided with a shape_to_segment the shape
    will be segmented by the wedges. This is useful for segmenting geometry into equal poloidal angles.
    Intended to segment the firstwall geometry for using in neutron wall loading simulations.

    Args:
        shape_to_segment (paramak.Shape): the Shape to segment, if None then the segmenting solids will be returned
        max_distance_from_center (float): the maximum distance from the center_point outwards (cm).
        center_point (tuple of floats): the center of the segmentation wedges (x,z) values (cm).
        number_of_segments (int): the number of equal angles segments in 360 degrees.

    Keyword Args:
        name (str): the legend name used when exporting a html graph of the shape.
        color (sequences of 3 or 4 floats each in the range 0-1): the color to use when
            exportin as html graphs or png images.
        material_tag (str): The material name to use when exporting the neutronics description.
        stp_filename (str): The filename used when saving stp files as part of a reactor.
        azimuth_placement_angle (float or iterable of floats): The angle or angles to use when
            rotating the shape on the azimuthal axis.
        rotation_angle (float): The rotation angle to use when revolving the solid (degrees).
        workplane (str): The orientation of the CadQuery workplane. Options are XY, YZ or XZ.
        intersect (CadQuery object): An optional CadQuery object to perform a boolean intersect with
            this object.
        cut (CadQuery object): An optional CadQuery object to perform a boolean cut with this object.
        union (CadQuery object): An optional CadQuery object to perform a boolean union with this object.
        tet_mesh (str): Insert description.
        physical_groups (type): Insert description.

    Returns:
        a paramak shape object: A shape object that has generic functionality with points determined by the find_points() method. A CadQuery solid of the shape can be called via shape.solid.
    """

    def __init__(
        self,
        center_point,
        shape_to_segment=None,
        number_of_segments=10,
        max_distance_from_center=1000,
        rotation_angle=360,
        stp_filename="PoloidalSegmenter.stp",
        stl_filename="PoloidalSegmenter.stl",
        color=(0.5, 0.5, 0.5),
        azimuth_placement_angle=0,
        name="poloidal_segmenter",
        material_tag="poloidal_segmenter_mat",
        **kwargs
    ):

        default_dict = {
            "points": None,
            "workplane": "XZ",
            "solid": None,
            "intersect": None,
            "cut": None,
            "union": None,
            "tet_mesh": None,
            "physical_groups": None,
        }

        for arg in kwargs:
            if arg in default_dict:
                default_dict[arg] = kwargs[arg]

        super().__init__(
            name=name,
            color=color,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            azimuth_placement_angle=azimuth_placement_angle,
            rotation_angle=rotation_angle,
            hash_value=None,
            **default_dict
        )

        self.center_point = center_point
        self.shape_to_segment = shape_to_segment
        self.number_of_segments = number_of_segments
        self.max_distance_from_center = max_distance_from_center

        self.find_points()

    @property
    def number_of_segments(self):
        return self._number_of_segments

    @number_of_segments.setter
    def number_of_segments(self, value):
        if isinstance(value, int) is False:
            raise ValueError(
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

    @property
    def solid(self):
        # TODO
        # if self.get_hash() != self.hash_value:
        self.create_solid()
        return self._solid

    @solid.setter
    def solid(self, value):
        self._solid = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the 2D
        profile of the poloidal segmentation shape."""

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
                math.radians(current_angle))
            outer_point_2 = rotate(
                self.center_point, outer_point, math.radians(
                    current_angle + angle_per_segment))

            if outer_point_1[0] < 0:
                m, c = coefficients_of_line_from_points(
                    outer_point_1, self.center_point)
                points.append((0, c))
            else:
                points.append(outer_point_1)

            if outer_point_2[0] < 0:
                m, c = coefficients_of_line_from_points(
                    outer_point_2, self.center_point)
                points.append((0, c))
            else:
                points.append(outer_point_2)

            current_angle = current_angle + angle_per_segment

        self.points = points

    def create_solid(self):
        """Creates a 3d solid using points with straight connections
           edges, azimuth_placement_angle and rotation angle.

           individual solids in the compound can be accessed using .Solids()[i] where i is an int

           Returns:
              A CadQuery solid: A 3D solid volume
        """

        iter_points = iter(self.points)
        triangle_wedges = []
        for p1, p2, p3 in zip(iter_points, iter_points, iter_points):

            solid = (
                cq.Workplane(self.workplane)
                .polyline([p1, p2, p3])
                .close()
                .revolve(self.rotation_angle)
            )
            triangle_wedges.append(solid)

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

        # TODO
        # # Calculate hash value for current solid
        # self.hash_value = self.get_hash()

        return compound
