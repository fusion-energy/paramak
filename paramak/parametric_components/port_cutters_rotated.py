
import math

from paramak import RotateStraightShape
from paramak.utils import coefficients_of_line_from_points, rotate


class PortCutterRotated(RotateStraightShape):
    """Creates wedges from a central point with angular extent in polar
    direction. To control the width the rotation_angle argument can be used.
    This is useful as a cutting volume for the creation of ports in blankets.

    Args:
        center_point (tuple of floats): the center point where the
            ports are aimed towards, typically the center of the plasma.
        polar_coverage_angle (float): the angular extent of port in the
            polar direction (degrees). Defaults to 10.0.
        polar_placement_angle (float): The angle used when rotating the shape
            on the polar axis. 0 degrees is the outboard equatorial point.
            Defaults to 0.0.
        max_distance_from_center (float): the maximum distance from the center
            point outwards (cm). Default 3000.0.
        fillet_radius (float, optional): If not None, radius (cm) of fillets
            added to all edges. Defaults to 0.0.
        rotation_angle (float, optional): defaults to 10.0.
        stp_filename (str, optional): defaults to "PortCutter.stp".
        stl_filename (str, optional): defaults to "PortCutter.stl".
        name (str, optional): defaults to "port_cutter".
        material_tag (str, optional): defaults to "port_cutter_mat".
    """

    def __init__(
        self,
        center_point,
        polar_coverage_angle=10.0,
        polar_placement_angle=0.0,
        max_distance_from_center=3000.0,
        fillet_radius=0.0,
        rotation_angle=10.0,
        stp_filename="PortCutter.stp",
        stl_filename="PortCutter.stl",
        name="port_cutter",
        material_tag="port_cutter_mat",
        **kwargs
    ):

        super().__init__(
            name=name,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            rotation_angle=rotation_angle,
            **kwargs
        )

        self.center_point = center_point
        self.polar_coverage_angle = polar_coverage_angle
        self.polar_placement_angle = polar_placement_angle
        self.max_distance_from_center = max_distance_from_center
        self.fillet_radius = fillet_radius

        self.add_fillet()

    @property
    def polar_coverage_angle(self):
        return self._polar_coverage_angle

    @polar_coverage_angle.setter
    def polar_coverage_angle(self, value):
        if value > 180:
            msg = "polar_coverage_angle must be greater than 180.0"
            raise ValueError(msg)
        self._polar_coverage_angle = value

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

        points.append(outer_point_1)
        points.append(outer_point_2)

        self.points = points

    def add_fillet(self):
        """adds fillets to all edges"""
        if self.fillet_radius != 0:
            self.solid = self.solid.edges().fillet(self.fillet_radius)
