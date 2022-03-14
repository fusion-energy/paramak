from typing import Optional, Tuple

import numpy as np
from scipy import integrate
from scipy.optimize import minimize

from .toroidal_field_coil import ToroidalFieldCoil
from paramak.utils import add_thickness


class ToroidalFieldCoilPrincetonD(ToroidalFieldCoil):
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
        azimuth_start_angle: The azimuth angle to for the first TF coil which
            offsets the placement of coils around the azimuthal angle
        rotation_angle: rotation angle of solid created. A cut is performed
            from rotation_angle to 360 degrees. Defaults to 360.0.
    """

    def __init__(
        self,
        name: str = "toroidal_field_coil",
        R1: float = 100,
        R2: float = 300,
        thickness: float = 30,
        distance: float = 20,
        number_of_coils: int = 12,
        vertical_displacement: float = 0.0,
        with_inner_leg: bool = True,
        azimuth_start_angle: float = 0,
        rotation_angle: float = 360.0,
        color: Tuple[float, float, float, Optional[float]] = (0.0, 0.0, 1.0),
        **kwargs
    ) -> None:

        super().__init__(
            name=name,
            thickness=thickness,
            number_of_coils=number_of_coils,
            vertical_displacement=vertical_displacement,
            with_inner_leg=with_inner_leg,
            azimuth_start_angle=azimuth_start_angle,
            rotation_angle=rotation_angle,
            distance=distance,
            color=color,
            **kwargs
        )

        self.R1 = R1
        self.R2 = R2
        self.inner_leg_connection_points = None

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
            return [Y[1], -1 / (k * R) * (1 + Y[1] ** 2) ** (3 / 2)]

        R0 = (R1 * R2) ** 0.5
        k = 0.5 * np.log(R2 / R1)

        # computing of z_0
        # z_0 is computed by ensuring outer segment end is zero
        z_0 = 10  # initial guess for z_0
        res = minimize(error, z_0, args=(R0, R2))
        z_0 = res.x

        # compute inner and outer segments
        segment1 = get_segment(R0, R1, z_0)
        segment2 = get_segment(R0, R2, z_0)

        r_values = np.concatenate(
            [
                np.flip(segment1[0]),
                segment2[0][1:],
                np.flip(segment2[0])[1:],
                segment1[0][1:],
            ]
        )
        z_values = np.concatenate(
            [
                np.flip(segment1[1]),
                segment2[1][1:],
                -np.flip(segment2[1])[1:],
                -segment1[1][1:],
            ]
        )
        return r_values, z_values

    def find_points(self):
        """Finds the XZ points joined by connections that describe the 2D
        profile of the toroidal field coil shape."""
        # compute inner points
        r_inner, z_inner = self._compute_inner_points(self.R1 + self.thickness, self.R2)

        # compute outer points
        dz_dr = np.diff(z_inner) / np.diff(r_inner)
        dz_dr[0] = float("-inf")
        dz_dr = np.append(dz_dr, float("inf"))
        r_outer, z_outer = add_thickness(r_inner, z_inner, self.thickness, dy_dx=dz_dr)
        r_outer, z_outer = np.flip(r_outer), np.flip(z_outer)

        # add vertical displacement
        z_outer += self.vertical_displacement
        z_inner += self.vertical_displacement

        # extract helping points for inner leg
        self.inner_leg_connection_points = [
            (r_inner[0], z_inner[0]),
            (r_inner[-1], z_inner[-1]),
            (r_outer[0], z_outer[0]),
            (r_outer[-1], z_outer[-1]),
        ]

        # add connections
        inner_points = [[r, z, "spline"] for r, z in zip(r_inner, z_inner)]
        outer_points = [[r, z, "spline"] for r, z in zip(r_outer, z_outer)]

        inner_points[-1][2] = "straight"
        outer_points[-1][2] = "straight"

        points = inner_points + outer_points
        self.outer_points = np.vstack((r_outer, z_outer)).T
        self.inner_points = np.vstack((r_inner, z_inner)).T

        self.points = points
