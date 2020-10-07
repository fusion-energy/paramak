import math
import cadquery as cq

from paramak import RotateStraightShape
from paramak.utils import rotate, coefficients_of_line_from_points


class PortCutterRotated(RotateStraightShape):
    """Creates wedges from a central point with angular extent in polar
    direction. To control the width the rotation_angle argument can be used.
    This is useful as a cutting volume for the creation of ports in blankets.

    Args:
        polar_coverage_angle (float): the angluar extent of port in the
            polar direction (degrees).
        center_point (tuple of floats): the center point where the
            ports are aimed towards, typically the center of the plasma.
        polar_placement_angle (float): The angle used when rotating the shape
            on the polar axis. 0 degrees is the outboard equatorial point.
        max_distance_from_center (float): the maximum distance from the center
            point outwards (cm). Default 3000

    Keyword Args:
        name (str): the legend name used when exporting a html graph of the
            shape.
        color (sequences of 3 or 4 floats each in the range 0-1): the color to
            use when exporting as html graphs or png images.
        material_tag (str): The material name to use when exporting the
            neutronics description.
        stp_filename (str): The filename used when saving stp files as part of
            a reactor.
        azimuth_placement_angle (float or iterable of floats): The angle or
            angles to use when rotating the shape on the azimuthal axis.
        rotation_angle (float): The rotation angle to use when revolving the
            solid (degrees).
        workplane (str): The orientation of the CadQuery workplane. Options are
            XY, YZ or XZ.
        intersect (CadQuery object): An optional CadQuery object to perform a
            boolean intersect with this object.
        cut (CadQuery object): An optional CadQuery object to perform a boolean
            cut with this object.
        union (CadQuery object): An optional CadQuery object to perform a
            boolean union with this object.
        tet_mesh (str): Insert description.
        physical_groups (type): Insert description.

    Returns:
        a paramak shape object: A shape object that has generic functionality
        with points determined by the find_points() method. A CadQuery solid of
        the shape can be called via shape.solid.
    """

    def __init__(
        self,
        center_point,
        polar_coverage_angle=10,
        polar_placement_angle=0,
        max_distance_from_center=3000,
        rotation_angle=0,
        stp_filename="PortCutter.stp",
        stl_filename="PortCutter.stl",
        color=(0.5, 0.5, 0.5),
        azimuth_placement_angle=0,
        name="port_cutter",
        material_tag="port_cutter_mat",
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
        self.polar_coverage_angle = polar_coverage_angle
        self.polar_placement_angle = polar_placement_angle
        self.max_distance_from_center = max_distance_from_center

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
        if self.get_hash() != self.hash_value:
            self.create_solid()
        return self._solid

    @solid.setter
    def solid(self, value):
        self._solid = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the
        2D profile of the port cutter."""

        points = [self.center_point]

        outer_point = (self.center_point[0] + self.max_distance_from_center,
                       self.center_point[1])

        outer_point_rotated = rotate(
            self.center_point,
            outer_point,
            math.radians(self.polar_placement_angle))

        outer_point_1 = rotate(
            self.center_point,
            outer_point_rotated,
            math.radians(0.5 * self.polar_coverage_angle))

        outer_point_2 = rotate(
            self.center_point,
            outer_point_rotated,
            math.radians(-0.5 * self.polar_coverage_angle))

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

        self.points = points
