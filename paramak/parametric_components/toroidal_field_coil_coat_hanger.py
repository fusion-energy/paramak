from collections import Iterable

import cadquery as cq
import numpy as np
from paramak import ExtrudeStraightShape
from paramak.utils import calculate_wedge_cut


class ToroidalFieldCoilCoatHanger(ExtrudeStraightShape):
    """Creates a coat hanger shaped toroidal field coil.

    Args:
        horizontal_start_point (tuple of 2 floats): the (x,z) coordinates of
            the inner upper point (cm).
        horizontal_length (tuple of 2 floats): the radial length of the
            horizontal section of the TF coil (cm).
        vertical_start_point (tuple of 2 points): the (x,z) coordinates of the
            start point of the outboard vertical section (cm).
        vertical_length (tuple of 2 floats): the radial length of the outboard
            vertical section of the TF coil (cm).
        thickness (float): the thickness of the toroidal field coil.
        distance (float): the extrusion distance.
        number_of_coils (int): the number of TF coils. This changes with
            azimuth_placement_angle dividing up 360 degrees by the number of
            coils.
        with_inner_leg (bool, optional): Include the inner TF leg. Defaults to
            True.
        stp_filename (str, optional): defaults to
            "ToroidalFieldCoilCoatHangar.stp".
        stl_filename (str, optional): defaults to
            "ToroidalFieldCoilCoatHangar.stl".
        material_tag (str, optional): defaults to "outer_tf_coil_mat".
    """

    def __init__(
        self,
        horizontal_start_point,
        horizontal_length,
        vertical_start_point,
        vertical_length,
        thickness,
        distance,
        number_of_coils,
        with_inner_leg=True,
        stp_filename="ToroidalFieldCoilCoatHangar.stp",
        stl_filename="ToroidalFieldCoilCoatHangar.stl",
        material_tag="outer_tf_coil_mat",
        **kwargs
    ):

        super().__init__(
            distance=distance,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            material_tag=material_tag,
            **kwargs
        )

        self.horizontal_start_point = horizontal_start_point
        self.horizontal_length = horizontal_length
        self.vertical_start_point = vertical_start_point
        self.vertical_length = vertical_length
        self.thickness = thickness
        self.distance = distance
        self.number_of_coils = number_of_coils
        self.with_inner_leg = with_inner_leg

        self.find_points()
        self.find_azimuth_placement_angle()

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the 2D
        profile of the poloidal field coil shape."""

        points = [
            self.horizontal_start_point,  # upper right inner
            (
                self.horizontal_start_point[0] + self.horizontal_length,
                self.horizontal_start_point[1],
            ),
            (
                self.vertical_start_point[0],
                self.vertical_start_point[1] + 0.5 * self.vertical_length,
            ),  # upper inner horizontal section
            (
                self.vertical_start_point[0],
                self.vertical_start_point[1] - 0.5 * self.vertical_length,
            ),  # lower inner horizontal section
            (
                self.horizontal_start_point[0] + self.horizontal_length,
                -self.horizontal_start_point[1],
            ),  # lower left vertical section
            (
                self.horizontal_start_point[0],
                -self.horizontal_start_point[1],
            ),  # lower right vertical section
            (
                self.horizontal_start_point[0],
                -self.horizontal_start_point[1] - self.thickness,
            ),
            (
                self.horizontal_start_point[0] + self.horizontal_length,
                -self.horizontal_start_point[1] - self.thickness,
            ),
            (
                self.horizontal_start_point[0]
                + self.horizontal_length
                + self.thickness,
                -self.horizontal_start_point[1],
            ),  # lower left vertical section
            (
                self.vertical_start_point[0] + self.thickness,
                self.vertical_start_point[1] - 0.5 * self.vertical_length,
            ),  # lower inner horizontal section
            (
                self.vertical_start_point[0] + self.thickness,
                self.vertical_start_point[1] + 0.5 * self.vertical_length,
            ),  # upper inner horizontal section
            (
                self.horizontal_start_point[0]
                + self.horizontal_length
                + self.thickness,
                self.horizontal_start_point[1],
            ),
            (
                self.horizontal_start_point[0] + self.horizontal_length,
                self.horizontal_start_point[1] + self.thickness,
            ),
            (
                self.horizontal_start_point[0],
                self.horizontal_start_point[1] + self.thickness,
            )  # upper right inner
        ]

        self.inner_leg_connection_points = [
            points[0],
            (points[0][0] + self.thickness, points[0][1]),
            (points[5][0] + self.thickness, points[5][1]),
            # (points[4][0], points[4][1] - 2 * self.thickness),
            points[5],
        ]

        self.points = points

    def find_azimuth_placement_angle(self):
        """Calculates the azimuth placement angles based on the number of
        toroidal field coils"""

        angles = list(
            np.linspace(
                0,
                360,
                self.number_of_coils,
                endpoint=False))

        self.azimuth_placement_angle = angles

    def create_solid(self):
        """Creates a 3d solid using points with straight edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """

        # Creates a cadquery solid from points and revolves
        points_without_connections = [p[:2] for p in self.points]
        solid = (
            cq.Workplane(self.workplane)
            .polyline(points_without_connections)
            .close()
            .extrude(distance=-self.distance / 2.0, both=True)
        )

        if self.with_inner_leg is True:
            inner_leg_solid = cq.Workplane(self.workplane)
            inner_leg_solid = inner_leg_solid.polyline(
                self.inner_leg_connection_points)
            inner_leg_solid = inner_leg_solid.close().extrude(
                distance=-self.distance / 2.0, both=True)

        solid = cq.Compound.makeCompound(
            [a.val() for a in [inner_leg_solid, solid]]
        )

        # Checks if the azimuth_placement_angle is a list of angles
        if isinstance(self.azimuth_placement_angle, Iterable):
            rotated_solids = []
            # Perform seperate rotations for each angle
            for angle in self.azimuth_placement_angle:
                rotated_solids.append(
                    solid.rotate(
                        (0, 0, -1), (0, 0, 1), angle))
            solid = cq.Workplane(self.workplane)

            # Joins the seperate solids together
            for i in rotated_solids:
                solid = solid.union(i)
        else:
            # Peform rotations for a single azimuth_placement_angle angle
            solid = solid.rotate(
                (0, 0, 1), (0, 0, -1), self.azimuth_placement_angle)

        calculate_wedge_cut(self)
        self.perform_boolean_operations(solid)

        return solid
