import scipy
import math
import sympy as sp
import numpy as np

from paramak import RotateMixedShape


class BlanketConstantThicknessPlasma(RotateMixedShape):
    """
    :param thickness:  the thickness of the blanket (cm)
    :type thickness: float
    :param thickness:  the thickness of the blanket (cm)
    :type thickness: float
    :param name: The legend name used when exporting a html graph of the shape
    :type name: str
    :param color: the color to use when exporting as html graphs or png images
    :type color: Red, Green, Blue, [Alpha] values. RGB and RGBA are sequences
     of, 3 or 4 floats respectively each in the range 0-1
    :param material_tag: The material name to use when exporting the
     neutronics description
    :type material_tag: str
    :param stp_filename: the filename used when saving stp files as part of a
     reactor
    :type stp_filename: str
    :param azimuth_placement_angle: the angle or angles to use when rotating
     the shape on the azimuthal axis
    :type azimuth_placement_angle: float or iterable of floats
    :param rotation_angle: The rotation_angle to use when revoling the solid
     (degrees)
    :type rotation_angle: float
    :param cut: An optional cadquery object to perform a boolean cut with this
     object
    :type cut: cadquery object

    :return: a shape object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        thickness,
        start_angle,
        stop_angle,
        minor_radius,
        major_radius,
        triangularity,
        elongation,
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

        self.thickness = thickness
        self.start_angle = start_angle
        self.stop_angle = stop_angle
        self.minor_radius = minor_radius
        self.major_radius = major_radius
        self.triangularity = triangularity
        self.elongation = elongation
        self.points = points

    @property
    def points(self):
        self.find_points()
        return self._points

    @points.setter
    def points(self, points):
        self._points = points

    @property
    def minor_radius(self):
        return self._minor_radius

    @minor_radius.setter
    def minor_radius(self, minor_radius):
        self._minor_radius = minor_radius

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, thickness):
        self._thickness = thickness

    def find_points(self):
        conversion_factor = 2*np.pi/360
        precision = 0.1

        def R(theta, pkg=np):
            return self.major_radius + self.minor_radius*pkg.cos(
                theta + self.triangularity*pkg.sin(theta))

        def Z(theta, pkg=np):
            return self.elongation*self.minor_radius*pkg.sin(theta)
        theta_sp = sp.Symbol("theta")

        R_sp = R(theta_sp, pkg=sp)
        Z_sp = Z(theta_sp, pkg=sp)

        R_derivative = sp.diff(R_sp, theta_sp)
        Z_derivative = sp.diff(Z_sp, theta_sp)

        # create array of angles theta
        thetas = np.arange(
                    self.start_angle*conversion_factor,
                    self.stop_angle*conversion_factor,
                    precision)

        # create inner points
        inner_points_R = R(thetas)
        inner_points_Z = Z(thetas)

        points = [
            (inner_points_R[i], inner_points_Z[i], 'straight')
            for i in range(len(thetas))
            ]

        # compute outer points
        for i in range(len(thetas)):
            theta = thetas[-(i+1)]
            # get local value of derivatives
            val_R_derivative = float(R_derivative.subs(theta_sp, theta))
            val_Z_derivative = float(Z_derivative.subs(theta_sp, theta))

            # get normal vector components
            nx = val_Z_derivative
            ny = -val_R_derivative

            # normalise normal vector
            normal_vector_norm = (nx**2 + ny**2)**0.5
            nx /= normal_vector_norm
            ny /= normal_vector_norm

            # calculate outer points
            val_R_outer = R(theta) + self.thickness*nx
            val_Z_outer = Z(theta) + self.thickness*ny

            points.append((float(val_R_outer), float(val_Z_outer), 'straight'))
        self.points = points
