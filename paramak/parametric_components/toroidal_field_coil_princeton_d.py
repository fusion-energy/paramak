
from typing import Optional, Tuple

import numpy as np
from paramak import ExtrudeMixedShape
from paramak.utils import add_thickness
from scipy import integrate
from scipy.optimize import minimize


class ToroidalFieldCoilPrincetonD(ExtrudeMixedShape):
    """Toroidal field coil based on Princeton-D curve

    Args:
        R1: smallest radius (cm)
        R2: largest radius (cm)
        thickness: magnet thickness (cm)
        distance: extrusion distance (cm)
        number_of_coils: the number of tf coils. This changes by the
            azimuth_placement_angle dividing up 360 degrees by the number of
            coils.
        vertical_displacement: vertical displacement (cm). Defaults to 0.0.
        with_inner_leg: Include the inner tf leg. Defaults to True.
        stp_filename: Defaults to "ToroidalFieldCoilPrincetonD.stp".
        stl_filename: Defaults to "ToroidalFieldCoilPrincetonD.stl".
        material_tag: Defaults to "outer_tf_coil_mat".
    """

    def __init__(
        self,
        R1: float,
        R2: float,
        thickness: float,
        distance: float,
        number_of_coils: int,
        vertical_displacement: Optional[float] = 0.0,
        with_inner_leg: Optional[bool] = True,
        stp_filename: Optional[str] = "ToroidalFieldCoilPrincetonD.stp",
        stl_filename: Optional[str] = "ToroidalFieldCoilPrincetonD.stl",
        material_tag: Optional[str] = "outer_tf_coil_mat",
        color: Optional[Tuple[float, float, float, Optional[float]]] = (0., 0., 1.),
        **kwargs
    ) -> None:

        super().__init__(
            distance=distance,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            material_tag=material_tag,
            color=color,
            **kwargs
        )

        self.R1 = R1
        self.R2 = R2
        self.thickness = thickness
        self.distance = distance
        self.number_of_coils = number_of_coils
        self.vertical_displacement = vertical_displacement
        self.with_inner_leg = with_inner_leg

    @property
    def inner_points(self):
        self.points
        return self._inner_points

    @inner_points.setter
    def inner_points(self, value):
        self._inner_points = value

    @property
    def outer_points(self):
        self.points
        return self._outer_points

    @outer_points.setter
    def outer_points(self, value):
        self._outer_points = value

    @property
    def azimuth_placement_angle(self):
        self.find_azimuth_placement_angle()
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        self._azimuth_placement_angle = value

    def _compute_inner_points(self, R1, R2):
        """Computes the inner curve points

        Args:
            R1 (float): smallest radius (cm)
            R2 (float): largest radius (cm)

        Returns:
            (list, list, list): R, Z and derivative lists for outer curve
            points
        """
        def error(z_0, R0, R2):
            segment = get_segment(R0, R2, z_0)
            return abs(segment[1][-1])

        def get_segment(a, b, z_0):
            a_R = np.linspace(a, b, num=70, endpoint=True)
            asol = integrate.odeint(solvr, [z_0, 0], a_R)
            return a_R, asol[:, 0], asol[:, 1]

        def solvr(Y, R):
            return [Y[1], -1 / (k * R) * (1 + Y[1]**2)**(3 / 2)]

        R0 = (R1 * R2)**0.5
        k = 0.5 * np.log(R2 / R1)

        # computing of z_0
        # z_0 is computed by ensuring outer segment end is zero
        z_0 = 10  # initial guess for z_0
        res = minimize(error, z_0, args=(R0, R2))
        z_0 = res.x

        # compute inner and outer segments
        segment1 = get_segment(R0, R1, z_0)
        segment2 = get_segment(R0, R2, z_0)

        R = np.concatenate([np.flip(segment1[0]), segment2[0]
                            [1:], np.flip(segment2[0])[1:], segment1[0][1:]])
        Z = np.concatenate([np.flip(segment1[1]), segment2[1]
                            [1:], -np.flip(segment2[1])[1:], -segment1[1][1:]])
        return R, Z

    def find_points(self):
        """Finds the XZ points joined by connections that describe the 2D
        profile of the toroidal field coil shape."""
        # compute inner points
        R_inner, Z_inner = self._compute_inner_points(
            self.R1 + self.thickness, self.R2)

        # compute outer points
        dz_dr = np.diff(Z_inner) / np.diff(R_inner)
        dz_dr[0] = float("-inf")
        dz_dr = np.append(dz_dr, float("inf"))
        R_outer, Z_outer = add_thickness(
            R_inner, Z_inner, self.thickness, dy_dx=dz_dr
        )
        R_outer, Z_outer = np.flip(R_outer), np.flip(Z_outer)

        # add vertical displacement
        Z_outer += self.vertical_displacement
        Z_inner += self.vertical_displacement

        # extract helping points for inner leg
        inner_leg_connection_points = [
            (R_inner[0], Z_inner[0]),
            (R_inner[-1], Z_inner[-1]),
            (R_outer[0], Z_outer[0]),
            (R_outer[-1], Z_outer[-1])
        ]
        self.inner_leg_connection_points = inner_leg_connection_points

        # add the leg to the points
        if self.with_inner_leg:
            R_inner = np.append(R_inner, R_inner[0])
            Z_inner = np.append(Z_inner, Z_inner[0])

            R_outer = np.append(R_outer, R_outer[0])
            Z_outer = np.append(Z_outer, Z_outer[0])
        # add connections
        inner_points = [[r, z, 'spline'] for r, z in zip(R_inner, Z_inner)]
        outer_points = [[r, z, 'spline'] for r, z in zip(R_outer, Z_outer)]
        if self.with_inner_leg:
            outer_points[-2][2] = 'straight'
            inner_points[-2][2] = 'straight'

        inner_points[-1][2] = 'straight'
        outer_points[-1][2] = 'straight'

        points = inner_points + outer_points
        self.outer_points = np.vstack((R_outer, Z_outer)).T
        self.inner_points = np.vstack((R_inner, Z_inner)).T
        self.points = points

    def find_azimuth_placement_angle(self):
        """Calculates the azimuth placement angles based on the number of tf
        coils"""

        angles = list(
            np.linspace(
                0,
                360,
                self.number_of_coils,
                endpoint=False))

        self.azimuth_placement_angle = angles
