import scipy
import math

import numpy as np

from paramak import RotateMixedShape


class BlanketConstantThicknessArcH(RotateMixedShape):
    """An outboard blanket volume that follows the curvature of a circular
    arc and a constant blanket thickness. The upper and lower edges continue
    horizontally for the thickness of the blanket to back of the blanket.

    Arguments:
        inner_mid_point (tuple of 2 floats): the x,z coordinates of the mid point
            on the inner surface of the blanket.
        inner_upper_point (tuple of 2 floats): the x,z coordinates of the upper
            point on the inner surface of the blanket.
        inner_lower_point (tuple of 2 floats): the x,z coordinates of the lower point
            on the inner surface of the blanket.
        thickness (float): the radial thickness of the blanket in cm.

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
        inner_mid_point,
        inner_upper_point,
        inner_lower_point,
        thickness,
        stp_filename="BlanketConstantThicknessArcH.stp",
        stl_filename="BlanketConstantThicknessArcH.stl",
        rotation_angle=360,
        azimuth_placement_angle=0,
        color=None,
        name=None,
        material_tag="blanket_mat",
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
