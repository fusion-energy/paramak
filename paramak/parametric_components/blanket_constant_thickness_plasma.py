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
        minor_radius=None,
        major_radius=None,
        triangularity=None,
        elongation=None,
        plasma=None,
        offset_from_plasma=0,
        num_points=50,
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
        self.plasma = plasma
        if plasma is None:
            self.minor_radius = minor_radius
            self.major_radius = major_radius
            self.triangularity = triangularity
            self.elongation = elongation
            self.offset_from_plasma = 0
        else:  # if plasma object is given, use its parameters
            self.minor_radius = plasma.minor_radius
            self.major_radius = plasma.major_radius
            self.triangularity = plasma.triangularity
            self.elongation = plasma.elongation
            self.offset_from_plasma = offset_from_plasma
        self.num_points = num_points
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

        def R(theta, pkg=np):
            return self.major_radius + self.minor_radius*pkg.cos(
                theta + self.triangularity*pkg.sin(theta))

        def Z(theta, pkg=np):
            return self.elongation*self.minor_radius*pkg.sin(theta)
        # create array of angles theta
        thetas = np.linspace(
                    self.start_angle*conversion_factor,
                    self.stop_angle*conversion_factor,
                    num=self.num_points,
                    endpoint=True)

        # create sympy objects and derivatives
        theta_sp = sp.Symbol("theta")

        R_sp = R(theta_sp, pkg=sp)
        Z_sp = Z(theta_sp, pkg=sp)

        R_derivative = sp.diff(R_sp, theta_sp)
        Z_derivative = sp.diff(Z_sp, theta_sp)
        # create inner points
        if self.plasma is None:
            # if no plasma object is given simply use the equation
            inner_points_R = R(thetas)
            inner_points_Z = Z(thetas)

            points = [
                [inner_points_R[i], inner_points_Z[i], 'spline']
                for i in range(len(thetas))
                ]
        else:
            # if a plasma is given
            points = self.create_offset_points(
                thetas, R, Z,
                R_derivative, Z_derivative,
                self.offset_from_plasma)
        points[-1][2] = 'straight'

        # compute outer points
        outer_points = self.create_offset_points(
            thetas, R, Z,
            R_derivative, Z_derivative,
            self.thickness + self.offset_from_plasma, flip=True)
        points = points + outer_points
        points[-2][2] = 'straight'
        self.points = points

    def create_offset_points(
            self, thetas, R_fun, Z_fun, R_derivative, Z_derivative, offset,
            flip=False):
        """generates a list of points following parametric equations with an
            offset.

        Args:
            thetas (list): list of angles (radiants)
            R_fun (callable): parametric function for R coordinate (cm)
            Z_fun ([type]): parametric function for Z coordinate (cm)
            R_derivative (sympy.Mul): derivative of R over theta (cm/rad)
            Z_derivative (sympy.Mul): derivative of Z over theta (cm/rad)
            offset (float): offset value (cm). offset=0 will follow the
                parametric equations.
            flip (bool, optional): If True thetas will be iterated from the
                end. Defaults to False.

        Returns:
            list: list of points
                [[R1, Z1, connection1], [R2, Z2, connection2], ...]
        """

        points = []
        list_of_thetas = thetas
        if flip:
            list_of_thetas = np.flip(thetas)

        for theta in list_of_thetas:
            # get local value of derivatives
            val_R_derivative = float(R_derivative.subs('theta', theta))
            val_Z_derivative = float(Z_derivative.subs('theta', theta))

            # get normal vector components
            nx = val_Z_derivative
            ny = -val_R_derivative

            # normalise normal vector
            normal_vector_norm = (nx**2 + ny**2)**0.5
            nx /= normal_vector_norm
            ny /= normal_vector_norm

            # calculate outer points
            val_R_outer = R_fun(theta) + offset*nx
            val_Z_outer = Z_fun(theta) + offset*ny

            points.append([float(val_R_outer), float(val_Z_outer), 'spline'])
        return points
