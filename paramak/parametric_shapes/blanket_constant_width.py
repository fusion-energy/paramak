
import scipy
import math

import numpy as np

from paramak import RotateMixedShape

class ConstantThicknessArcV(RotateMixedShape):
    """An outboard blanket volume that follows the curvature of a circular
    arc and a constant blanket thickness. The upper and lower edges continue
    verticall for the thickness of the blanket to back of the blanket.

    :param inner_mid_point: the x,z coordinates of the mid point on
     the inner surface of the blanket.
    :type inner_mid_point: tuple of 2 floats
    :param inner_upper_point: the x,z coordinates of the upper point on
     the inner surface of the blanket.
    :type inner_upper_point: tuple of 2 floats
    :param inner_lower_point: the x,z coordinates of the lower point on
     the inner surface of the blanket.
    :type inner_lower_point: tuple of 2 floats
    :param thickness: the radial thickness of the blanket in cm
    :type thickness: float
    :param name: The legend name used when exporting a html graph of the shape
    :type name: str
    :param color: the color to use when exporting as html graphs or png images
    :type color: Red, Green, Blue, [Alpha] values. RGB and RGBA are sequences of,
     3 or 4 floats respectively each in the range 0-1
    :param material_tag: The material name to use when exporting the neutronics description
    :type material_tag: str
    :param stp_filename: the filename used when saving stp files as part of a reactor
    :type stp_filename: str
    :param azimuth_placement_angle: the angle or angles to use when rotating the 
     shape on the azimuthal axis
    :type azimuth_placement_angle: float or iterable of floats
    :param rotation_angle: The rotation_angle to use when revoling the solid (degrees)
    :type rotation_angle: float
    :param cut: An optional cadquery object to perform a boolean cut with this object
    :type cut: cadquery object

    :return: a shape object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        inner_mid_point,
        inner_upper_point,
        inner_lower_point,
        thickness,
        workplane="XZ",
        points=None,
        stp_filename=None,
        rotation_angle=360,
        azimuth_placement_angle=0,
        solid=None,
        color=None,
        name=None,
        material_tag=None,
        cut=None,
    ):

        super().__init__(
            points,
            workplane,
            name,
            color,
            material_tag,
            stp_filename,
            azimuth_placement_angle,
            solid,
            rotation_angle,
            cut,
        )

        self.inner_upper_point = inner_upper_point
        self.inner_lower_point = inner_lower_point
        self.inner_mid_point = inner_mid_point
        self.thickness = thickness

    @property
    def points(self):
        self.find_points()
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    def find_points(self):

        self.points = [
            (self.inner_upper_point[0], self.inner_upper_point[1], 'circle'),
            (self.inner_mid_point[0], self.inner_mid_point[1], 'circle'),
            (self.inner_lower_point[0], self.inner_lower_point[1], 'straight'),
            (self.inner_lower_point[0], self.inner_lower_point[1]-abs(self.thickness), 'circle'),
            (self.inner_mid_point[0]+self.thickness, self.inner_mid_point[1], 'circle'),
            (self.inner_upper_point[0], self.inner_upper_point[1]+abs(self.thickness), 'straight'),
            (self.inner_upper_point[0], self.inner_upper_point[1]),
        ]


class BlanketConstantThickness(RotateMixedShape):
    """An outboard blanket volume that follows the curvature of the plasma
    with a fixed offset from the plasma and a constant blanket thickness.
    The blanket volume has start and stop angles that allow the blanket 
    coverage to be increased or decreased.

    :param major_radius: the major radius of the plasma (cm)
    :type major_radius: float
    :param minor_radius: the minor radius of the plasma (cm)
    :type minor_radius: float
    :param triangularity: the triangularity of the plasma
    :type triangularity: float
    :param elongation: the elongation of the plasma
    :type elongation: float
    :param thickness:  the thickness of the blanket (cm)
    :type thickness: float
    :param stop_angle: the angle in degrees to stop the blanket, measured anti clockwise from 3 o'clock
    :type stop_angle: float
    :param start_angle: the angle in degrees to start the blanket, measured anti clockwise from 3 o'clock
    :type start_angle: float
    :param offset_from_plasma: the distance bettwen the plasma and the blanket (cm)
    :type offset_from_plasma: float


    :return: a shape object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        major_radius,
        minor_radius,
        triangularity,
        elongation,
        thickness,
        stop_angle,
        start_angle,
        offset_from_plasma,
        workplane="XZ",
        points=None,
        stp_filename=None,
        rotation_angle=360,
        azimuth_placement_angle=0,
        solid=None,
        color=None,
        name=None,
        material_tag=None,
        cut=None,
    ):

        super().__init__(
            points,
            workplane,
            name,
            color,
            material_tag,
            stp_filename,
            azimuth_placement_angle,
            solid,
            rotation_angle,
            cut,
        )

        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.triangularity = triangularity
        self.elongation = elongation
        self.thickness = thickness
        self.stop_angle = stop_angle
        self.start_angle = start_angle
        self.offset_from_plasma = offset_from_plasma
        self.points = points

    @property
    def points(self):
        self.find_points()
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    @property
    def major_radius(self):
        return self._major_radius

    @major_radius.setter
    def major_radius(self, major_radius):
        self._major_radius = major_radius

    @property
    def minor_radius(self):
        return self._minor_radius

    @minor_radius.setter
    def minor_radius(self, minor_radius):
        self._minor_radius = minor_radius

    @property
    def triangularity(self):
        return self._triangularity

    @triangularity.setter
    def triangularity(self, triangularity):
        self._triangularity = triangularity

    @property
    def elongation(self):
        return self._elongation

    @elongation.setter
    def elongation(self, elongation):
        self._elongation = elongation

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, thickness):
        self._thickness = thickness

    @property
    def stop_angle(self):
        return self._stop_angle

    @stop_angle.setter
    def stop_angle(self, stop_angle):
        self._stop_angle = stop_angle

    @property
    def start_angle(self):
        return self._start_angle

    @start_angle.setter
    def start_angle(self, start_angle):
        self._start_angle = start_angle

    @property
    def offset_from_plasma(self):
        return self._offset_from_plasma

    @offset_from_plasma.setter
    def offset_from_plasma(self, offset_from_plasma):
        self._offset_from_plasma = offset_from_plasma

    @property
    def inner_limit(self):
        return self._inner_limit

    @inner_limit.setter
    def inner_limit(self, inner_limit):
        self._inner_limit = inner_limit

    def find_points(self):
        """Finds the XZ points and connection types (straight and spline) that
        describe the 2D profile of the blanket shape."""

        # This section finds the points on the front face of the divertor
        radius_of_front_curve = (
            0.5
            * scipy.sqrt(
                (
                    self.minor_radius ** 2
                    * ((self.triangularity + 1) ** 2 + self.elongation ** 2) ** 2
                )
                / ((self.triangularity + 1) ** 2)
            )
            + self.offset_from_plasma
        )

        x_position_for_outside_arc = (
            2 * self.major_radius * (1 + self.triangularity)
            - self.minor_radius * (self.triangularity ** 2 + self.elongation ** 2 - 1)
        ) / (2 * (1 + self.triangularity))

        angles = np.linspace(
            math.radians(self.start_angle), math.radians(self.stop_angle), 100
        )

        xs = -(radius_of_front_curve * scipy.cos(angles) - x_position_for_outside_arc)
        zs = radius_of_front_curve * scipy.sin(angles)

        points = []
        for x, z, in zip(xs, zs):
            points.append([x, z, "spline"])

        points[-1][2] = "straight"

        # This section finds the points on the rear face of the divertor
        radius_of_back_curve = radius_of_front_curve + self.thickness

        # stop angle is converted from degrees to radians
        angles = np.linspace(
            math.radians(self.stop_angle), math.radians(self.start_angle), 100
        )

        xs = -(radius_of_back_curve * scipy.cos(angles) - x_position_for_outside_arc)
        zs = radius_of_back_curve * scipy.sin(angles)

        for x, z, in zip(xs, zs):
            points.append([x, z, "spline"])

        # changes the last point to a straght conenctor
        points[-1][2] = "straight"

        self.points = points
