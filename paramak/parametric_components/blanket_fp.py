import math

import numpy as np
import scipy
import sympy as sp

from paramak import RotateMixedShape, diff_between_angles


class BlanketFP(RotateMixedShape):
    """A blanket volume created from plasma parameters.

    Args:
        thickness (float, (float, float), callable): the thickness of the
            blanket (cm). If float, constant thickness. If tuple of floats,
            thickness will vary linearly between the two values. If callable,
            thickness will be a function of poloidal angle (in degrees).
        start_angle (float): the angle in degrees to start the blanket,
            measured anti clockwise from 3 o'clock
        stop_angle (float): the angle in degrees to stop the blanket, measured
            anti clockwise from 3 o'clock
        plasma (paramak.Plasma, optional): If not None, the parameters of the
            plasma Object will be used. Defaults to None.
        minor_radius (float, optional): the minor radius of the plasma (cm).
            Defaults to 150.
        major_radius (float, optional): the major radius of the plasma (cm).
            Defaults to 450.
        triangularity (float, optional): the triangularity of the plasma.
            Defaults to 0.55.
        elongation (float, optional): the elongation of the plasma.
            Defaults to 2.0.
        vertical_displacement (float, optional): the vertical_displacement of
            the plasma (cm). Defaults to 0.
        offset_from_plasma (float, optional): the distance bettwen the plasma
            and the blanket (cm). Defaults to 0.
        num_points (int, optional): number of points that will describe the
            shape. Defaults to 50.
        Others: see paramak.RotateMixedShape() arguments.

    Keyword Args:
        thickness (float, (float, float), callable): the thickness of the
            blanket (cm). If float, constant thickness. If tuple of floats,
            thickness will vary linearly between the two values. If callable,
            thickness will be a function of poloidal angle (in degrees).
        start_angle (float): the angle in degrees to start the blanket,
            measured anti clockwise from 3 o'clock
        stop_angle (float): the angle in degrees to stop the blanket, measured
            anti clockwise from 3 o'clock
        plasma (paramak.Plasma): If not None, the parameters of the
            plasma Object will be used.
        minor_radius (float): the minor radius of the plasma (cm).
        major_radius (float): the major radius of the plasma (cm).
        triangularity (float): the triangularity of the plasma.
        elongation (float): the elongation of the plasma.
            Defaults to 2.0.
        vertical_displacement (float): the vertical_displacement of
            the plasma (cm).
        offset_from_plasma (float): the distance bettwen the plasma
            and the blanket (cm).
        num_points (int): number of points that will describe the
            shape.
        Others: see paramak.RotateMixedShape() attributes.

    Returns:
        a paramak shape object: A shape object that has generic functionality with points determined by the find_points() method. A CadQuery solid of the shape can be called via shape.solid.
    """

    def __init__(
        self,
        thickness,
        start_angle,
        stop_angle,
        plasma=None,
        minor_radius=150.0,
        major_radius=450.0,
        triangularity=0.55,
        elongation=2.0,
        vertical_displacement=0,
        offset_from_plasma=0,
        num_points=50,
        stp_filename="BlanketFP.stp",
        stl_filename="BlanketFP.stl",
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
        # raise error if full coverage and full rotation angle are set
        if diff_between_angles(start_angle,
                               stop_angle) == 0 and rotation_angle == 360:
            raise ValueError("Full coverage and 360 rotation will result in a \
                standard construction error.")
        self.thickness = thickness
        self.start_angle = start_angle
        self.stop_angle = stop_angle
        self.plasma = plasma
        self.vertical_displacement = vertical_displacement
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
        # self.points = points
        self.physical_groups = None

    @property
    def physical_groups(self):
        self.create_physical_groups()
        return self._physical_groups

    @physical_groups.setter
    def physical_groups(self, physical_groups):
        self._physical_groups = physical_groups

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
        conversion_factor = 2 * np.pi / 360

        def R(theta, pkg=np):
            return self.major_radius + self.minor_radius * pkg.cos(
                theta + self.triangularity * pkg.sin(theta)
            )

        def Z(theta, pkg=np):
            return (
                self.elongation * self.minor_radius * pkg.sin(theta)
                + self.vertical_displacement
            )

        # create array of angles theta
        thetas = np.linspace(
            self.start_angle * conversion_factor,
            self.stop_angle * conversion_factor,
            num=self.num_points,
            endpoint=True,
        )

        # create inner points
        if self.plasma is None:
            # if no plasma object is given simply use the equation
            inner_points_R = R(thetas)
            inner_points_Z = Z(thetas)

            inner_points = [
                [inner_points_R[i], inner_points_Z[i], "spline"]
                for i in range(len(thetas))
            ]
        else:
            # if a plasma is given
            inner_points = self.create_offset_points(
                thetas, R, Z, self.offset_from_plasma
            )
        inner_points[-1][2] = "straight"

        # compute outer points
        def new_offset(theta):
            if callable(self.thickness):
                # use the function of angle
                return (
                    self.thickness(
                        theta /
                        conversion_factor) +
                    self.offset_from_plasma)
            elif isinstance(self.thickness, tuple):
                # increase thickness linearly
                start_thickness, stop_thickness = self.thickness
                a = (stop_thickness - start_thickness) / (
                    self.stop_angle * conversion_factor
                    - self.start_angle * conversion_factor
                )
                b = start_thickness - self.start_angle * a
                return a * theta + b + self.offset_from_plasma
            else:
                # use the constant value
                return self.thickness + self.offset_from_plasma

        outer_points = self.create_offset_points(
            np.flip(thetas), R, Z, new_offset)
        points = inner_points + outer_points
        points[-1][2] = "straight"
        points.append(inner_points[0])
        self.points = points

    def create_offset_points(self, thetas, R_fun, Z_fun, offset):
        """generates a list of points following parametric equations with an
        offset

        :param thetas: list of angles (radians)
        :type thetas: list
        :param R_fun: parametric function for R coordinate (cm)
        :type R_fun: callable
        :param Z_fun: parametric function for Z coordinate (cm)
        :type Z_fun: callable
        :param offset: offset value (cm). offset=0 will follow the parametric
         equations.
        :type offset: float, callable
        :return: list of points [[R1, Z1, connection1], [R2, Z2, connection2],
            ...]
        :rtype: list
        """
        # create sympy objects and derivatives
        theta_sp = sp.Symbol("theta")

        R_sp = R_fun(theta_sp, pkg=sp)
        Z_sp = Z_fun(theta_sp, pkg=sp)

        R_derivative = sp.diff(R_sp, theta_sp)
        Z_derivative = sp.diff(Z_sp, theta_sp)
        points = []

        def new_offset(theta):
            if callable(offset):
                return offset(theta)
            else:
                return offset

        for theta in thetas:
            # get local value of derivatives
            val_R_derivative = float(R_derivative.subs("theta", theta))
            val_Z_derivative = float(Z_derivative.subs("theta", theta))

            # get normal vector components
            nx = val_Z_derivative
            ny = -val_R_derivative

            # normalise normal vector
            normal_vector_norm = (nx ** 2 + ny ** 2) ** 0.5
            nx /= normal_vector_norm
            ny /= normal_vector_norm

            # calculate outer points
            val_R_outer = R_fun(theta) + new_offset(theta) * nx
            val_Z_outer = Z_fun(theta) + new_offset(theta) * ny

            points.append([float(val_R_outer), float(val_Z_outer), "spline"])
        return points

    def create_physical_groups(self):
        """Creates the physical groups for STP files

        Returns:
            list: list of dicts containing the physical groups
        """

        groups = []
        nb_volumes = 1  # only one volume
        nb_surfaces = 2  # inner and outer

        surface_names = ["inner", "outer"]
        volumes_names = ["inside"]

        # add two cut sections if they exist
        if self.rotation_angle != 360:
            nb_surfaces += 2
            surface_names += ["left_section", "right_section"]
            full_rot = False
        else:
            full_rot = True

        # add two surfaces between blanket and div if they exist
        if diff_between_angles(self.start_angle, self.stop_angle) != 0:
            nb_surfaces += 2
            surface_names += ["inner_section", "outer_section"]
            stop_equals_start = False
        else:
            stop_equals_start = True

        # rearrange order
        # TODO: fix issue #86 (full coverage)
        if full_rot:
            if stop_equals_start:
                print(
                    "Warning: If start_angle = stop_angle surfaces will not\
                     be handled correctly"
                )
                new_order = [0, 1, 2, 3]
            else:
                # from ["inner", "outer", "inner_section", "outer_section"]

                # to ["inner", "inner_section", "outer", "outer_section"]
                new_order = [0, 2, 1, 3]
        else:
            if stop_equals_start:
                print(
                    "Warning: If start_angle = stop_angle surfaces will not\
                     be handled correctly"
                )
                new_order = [0, 1, 2, 3]
            else:
                # from ['inner', 'outer', 'left_section', 'right_section',
                #           'inner_section', 'outer_section']

                # to ["inner", "inner_section", "outer", "outer_section",
                #         "left_section", "right_section"]
                new_order = [0, 4, 1, 5, 2, 3]
        surface_names = [surface_names[i] for i in new_order]

        for i in range(1, nb_volumes + 1):
            group = {"dim": 3, "id": i, "name": volumes_names[i - 1]}
            groups.append(group)
        for i in range(1, nb_surfaces + 1):
            group = {"dim": 2, "id": i, "name": surface_names[i - 1]}
            groups.append(group)
        self.physical_groups = groups
