import warnings
from typing import Optional, Union, Iterable

import mpmath
import numpy as np
import sympy as sp
from scipy.interpolate import interp1d

import paramak
from paramak import RotateMixedShape


class BlanketFP(RotateMixedShape):
    """A blanket volume created from plasma parameters. In might be nessecary
    to increase the num_points when making long but thin geometry with this
    component.

    Args:
        thickness (float or [float] or callable or [(float), (float)]):
            the thickness of the blanket (cm). If the thickness is a float then
            this produces a blanket of constant thickness. If the thickness is
            a tuple of floats, blanket thickness will vary linearly between the
            two values. If thickness is callable, then the blanket thickness
            will be a function of poloidal angle (in degrees). If thickness is
            a list of two lists (thicknesses and angles) then these will be
            used together with linear interpolation.
        start_angle: the angle in degrees to start the blanket, measured anti
            clockwise from 3 o'clock.
        stop_angle: the angle in degrees to stop the blanket, measured anti
            clockwise from 3 o'clock.
        plasma: If not None, the parameters of the plasma Object will be used.
        minor_radius: the minor radius of the plasma (cm).
        major_radius: the major radius of the plasma (cm).
        triangularity: the triangularity of the plasma.
        elongation: the elongation of the plasma.
        vertical_displacement: the vertical_displacement of the plasma (cm).
        offset_from_plasma: the distance between the plasma and the blanket
            (cm). If float, constant offset. If list of floats, offset will
            vary linearly between the values. If callable, offset will be a
            function of poloidal angle (in degrees). If a list of two lists
            (angles and offsets) then these will be used together with linear
            interpolation.
        num_points: number of points that will describe the shape.
    """

    def __init__(
        self,
        thickness,
        start_angle: float,
        stop_angle: float,
        plasma: Optional[Union[paramak.Plasma, paramak.PlasmaBoundaries, paramak.PlasmaFromPoints]] = None,
        minor_radius: float = 150.0,
        major_radius: float = 450.0,
        triangularity: float = 0.55,
        elongation: float = 2.0,
        vertical_displacement: float = 0.0,
        offset_from_plasma: Union[float, Iterable[float]] = 0.0,
        num_points: int = 50,
        allow_overlapping_shape=False,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.thickness = thickness
        self.start_angle, self.stop_angle = None, None
        self.start_angle = start_angle
        self.stop_angle = stop_angle
        self.plasma = plasma
        self.vertical_displacement = vertical_displacement
        self.allow_overlapping_shape = allow_overlapping_shape
        if plasma is None:
            self.minor_radius = minor_radius
            self.major_radius = major_radius
            self.triangularity = triangularity
            self.elongation = elongation
        else:  # if plasma object is given, use its parameters
            self.minor_radius = plasma.minor_radius
            self.major_radius = plasma.major_radius
            self.triangularity = plasma.triangularity
            self.elongation = plasma.elongation
        self.offset_from_plasma = offset_from_plasma
        self.num_points = num_points

    @property
    def start_angle(self):
        return self._start_angle

    @start_angle.setter
    def start_angle(self, value):
        self._start_angle = value

    @property
    def stop_angle(self):
        return self._stop_angle

    @stop_angle.setter
    def stop_angle(self, value):
        self._stop_angle = value

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

    @property
    def inner_points(self):
        self.find_points()
        return self._inner_points

    @inner_points.setter
    def inner_points(self, value):
        self._inner_points = value

    @property
    def outer_points(self):
        self.find_points()
        return self._outer_points

    @outer_points.setter
    def outer_points(self, value):
        self._outer_points = value

    def make_callable(self, attribute):
        """This function transforms an attribute (thickness or offset) into a
        callable function of theta
        """
        # if the attribute is a list, create a interpolated object of the
        # values
        if isinstance(attribute, (tuple, list)):
            if (
                isinstance(attribute[0], (tuple, list))
                and isinstance(attribute[1], (tuple, list))
                and len(attribute) == 2
            ):
                # attribute is a list of 2 lists
                if len(attribute[0]) != len(attribute[1]):
                    raise ValueError(
                        "The length of angles list must equal \
                     the length of values list"
                    )
                list_of_angles = np.array(attribute[0])
                offset_values = attribute[1]
            else:
                # no list of angles is given
                offset_values = attribute
                list_of_angles = np.linspace(self.start_angle, self.stop_angle, len(offset_values), endpoint=True)
            interpolated_values = interp1d(list_of_angles, offset_values)

        def fun(theta):
            if callable(attribute):
                return attribute(theta)
            elif isinstance(attribute, (tuple, list)):
                return interpolated_values(theta)
            else:
                return attribute

        return fun

    def find_points(self, angles=None):
        self._overlapping_shape = False
        # create array of angles theta
        if angles is None:
            thetas = np.linspace(
                self.start_angle,
                self.stop_angle,
                num=self.num_points,
                endpoint=True,
            )
        else:
            thetas = angles

        # create inner points
        inner_offset = self.make_callable(self.offset_from_plasma)
        inner_points = self.create_offset_points(thetas, inner_offset)
        inner_points[-1][2] = "straight"
        self.inner_points = inner_points

        # create outer points
        thickness = self.make_callable(self.thickness)

        def outer_offset(theta):
            return inner_offset(theta) + thickness(theta)

        outer_points = self.create_offset_points(np.flip(thetas), outer_offset)
        outer_points[-1][2] = "straight"
        self.outer_points = outer_points

        # assemble
        points = inner_points + outer_points
        if self._overlapping_shape and self.allow_overlapping_shape is False:
            msg = "BlanketFP: Some points with negative R coordinate have " "been ignored."
            warnings.warn(msg)

        self.points = points
        return points

    def create_offset_points(self, thetas, offset):
        """generates a list of points following parametric equations with an
        offset

        Args:
            thetas (np.array): the angles in degrees.
            offset (callable): offset value (cm). offset=0 will follow the
                parametric equations.

        Returns:
            list: list of points [[R1, Z1, connection1], [R2, Z2, connection2],
            ...]
        """
        # create sympy objects and derivatives
        theta_sp = sp.Symbol("theta")

        R_sp, Z_sp = self.distribution(theta_sp, pkg=sp)
        R_derivative = sp.diff(R_sp, theta_sp)
        Z_derivative = sp.diff(Z_sp, theta_sp)
        points = []

        for theta in thetas:
            # get local value of derivatives
            val_R_derivative = float(R_derivative.subs("theta", theta))
            val_Z_derivative = float(Z_derivative.subs("theta", theta))

            # get normal vector components
            nx = val_Z_derivative
            ny = -val_R_derivative

            # normalise normal vector
            normal_vector_norm = (nx**2 + ny**2) ** 0.5
            nx /= normal_vector_norm
            ny /= normal_vector_norm

            # calculate outer points
            val_R_outer = self.distribution(theta)[0] + offset(theta) * nx
            val_Z_outer = self.distribution(theta)[1] + offset(theta) * ny
            if float(val_R_outer) > 0:
                points.append([float(val_R_outer), float(val_Z_outer), "spline"])
            else:
                self._overlapping_shape = True
        return points

    def distribution(self, theta, pkg=np):
        """Plasma distribution theta in degrees

        Args:
            theta (float or np.array or sp.Symbol): the angle(s) in degrees.
            pkg (module, optional): Module to use in the funciton. If sp, as
                sympy object will be returned. If np, a np.array or a float
                will be returned. Defaults to np.

        Returns:
            (float, float) or (sympy.Add, sympy.Mul) or
                (numpy.array, numpy.array): The R and Z coordinates of the
                point with angle theta
        """
        if pkg == np:
            theta = np.radians(theta)
        else:
            theta = mpmath.radians(theta)
        R = self.major_radius + self.minor_radius * pkg.cos(theta + self.triangularity * pkg.sin(theta))
        Z = self.elongation * self.minor_radius * pkg.sin(theta) + self.vertical_displacement
        return R, Z
