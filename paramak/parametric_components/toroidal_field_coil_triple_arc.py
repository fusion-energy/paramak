
from typing import Optional, Tuple
import numpy as np
from paramak import ExtrudeMixedShape


class ToroidalFieldCoilTripleArc(ExtrudeMixedShape):
    """Toroidal field coil made of three arcs

    Args:
        R1: smallest radius (cm).
        h: height of the straight section (cm).
        radii: radii of the small and medium arcs (cm).
        coverages: coverages of the small and medium arcs (deg).
        thickness: magnet thickness (cm).
        distance: extrusion distance (cm).
        number_of_coils: the number of TF coils. This changes by the
            azimuth_placement_angle dividing up 360 degrees by the number of
            coils.
        vertical_displacement: vertical displacement (cm). Defaults to 0.0.
        with_inner_leg: Include the inner tf leg. Defaults to True.
        stp_filename: Defaults to "ToroidalFieldCoilTripleArc.stp".
        stl_filename: Defaults to "ToroidalFieldCoilTripleArc.stl".
        material_tag: Defaults to "outer_tf_coil_mat".
    """

    def __init__(
        self,
        R1: float,
        h: float,
        radii: Tuple[float, float],
        coverages: Tuple[float, float],
        thickness: float,
        distance: float,
        number_of_coils: int,
        vertical_displacement: Optional[float] = 0.0,
        with_inner_leg: Optional[bool] = True,
        stp_filename: Optional[str] = "ToroidalFieldCoilTripleArc.stp",
        stl_filename: Optional[str] = "ToroidalFieldCoilTripleArc.stl",
        material_tag: Optional[str] = "outer_tf_coil_mat",
        **kwargs
    ) -> None:

        super().__init__(
            distance=distance,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            material_tag=material_tag,
            **kwargs
        )
        self.R1 = R1
        self.h = h
        self.small_radius, self.mid_radius = radii

        self.small_coverage, self.mid_coverage = coverages
        self.thickness = thickness
        self.distance = distance
        self.number_of_coils = number_of_coils
        self.vertical_displacement = vertical_displacement
        self.with_inner_leg = with_inner_leg

    @property
    def azimuth_placement_angle(self):
        self.find_azimuth_placement_angle()
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        self._azimuth_placement_angle = value

    def _compute_curve(self, R1, h, radii, coverages):
        npoints = 500

        small_radius, mid_radius = radii
        small_coverage, mid_coverage = coverages
        asum = small_coverage + mid_coverage

        # small arc
        theta = np.linspace(
            0, small_coverage, round(0.5 * npoints * small_coverage / np.pi))
        small_arc_R = R1 + small_radius * (1 - np.cos(theta))
        small_arc_Z = h + small_radius * np.sin(theta)

        # mid arc
        theta = np.linspace(
            theta[-1], asum, round(0.5 * npoints * mid_coverage / np.pi))
        mid_arc_R = small_arc_R[-1] + mid_radius * \
            (np.cos(small_coverage) - np.cos(theta))
        mid_arc_Z = small_arc_Z[-1] + mid_radius * \
            (np.sin(theta) - np.sin(small_coverage))

        # large arc
        large_radius = (mid_arc_Z[-1]) / np.sin(np.pi - asum)
        theta = np.linspace(theta[-1], np.pi, 60)
        large_arc_R = mid_arc_R[-1] + large_radius * \
            (np.cos(np.pi - theta) - np.cos(np.pi - asum))
        large_arc_Z = mid_arc_Z[-1] - large_radius * \
            (np.sin(asum) - np.sin(np.pi - theta))

        R = np.concatenate((small_arc_R, mid_arc_R[1:], large_arc_R[1:]))
        R = np.append(R, np.flip(R)[1:])
        Z = np.concatenate((small_arc_Z, mid_arc_Z[1:], large_arc_Z[1:]))
        Z = np.append(Z, -np.flip(Z)[1:])
        return R, Z

    def find_points(self):
        """Finds the XZ points joined by connections that describe the 2D
        profile of the toroidal field coil shape."""

        thickness = self.thickness
        small_radius, mid_radius = self.small_radius, self.mid_radius
        small_coverage, mid_coverage = self.small_coverage, self.mid_coverage
        small_coverage *= np.pi / 180  # convert to radians
        mid_coverage *= np.pi / 180

        # create inner coordinates
        R_inner, Z_inner = self._compute_curve(
            self.R1, self.h * 0.5, radii=(small_radius, mid_radius),
            coverages=(small_coverage, mid_coverage))

        # create outer coordinates
        R_outer, Z_outer = self._compute_curve(
            self.R1 - thickness, self.h * 0.5,
            radii=(small_radius + thickness, mid_radius + thickness),
            coverages=(small_coverage, mid_coverage))
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
