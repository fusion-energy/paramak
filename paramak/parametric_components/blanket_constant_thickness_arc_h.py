import scipy
import math

import numpy as np

from paramak import RotateMixedShape


class BlanketConstantThicknessArcH(RotateMixedShape):
    """An outboard blanket volume that follows the curvature of a circular
    arc and a constant blanket thickness. The upper and lower edges continue
    horizontally for the thickness of the blanket to back of the blanket.

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
            (self.inner_upper_point[0], self.inner_upper_point[1], "circle"),
            (self.inner_mid_point[0], self.inner_mid_point[1], "circle"),
            (self.inner_lower_point[0], self.inner_lower_point[1], "straight"),
            (
                self.inner_lower_point[0] + abs(self.thickness),
                self.inner_lower_point[1],
                "circle",
            ),
            (
                self.inner_mid_point[0] + abs(self.thickness),
                self.inner_mid_point[1],
                "circle",
            ),
            (
                self.inner_upper_point[0] + abs(self.thickness),
                self.inner_upper_point[1],
                "straight",
            ),
            (self.inner_upper_point[0], self.inner_upper_point[1]),
        ]
