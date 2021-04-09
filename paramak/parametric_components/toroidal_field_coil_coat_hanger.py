
import math

from typing import Optional, Tuple
import cadquery as cq
import numpy as np
from paramak import ExtrudeStraightShape
from paramak.utils import calculate_wedge_cut, rotate


class ToroidalFieldCoilCoatHanger(ExtrudeStraightShape):
    """Creates a coat hanger shaped toroidal field coil.

    Args:
        horizontal_start_point: the (x,z) coordinates of the inner upper
            point (cm).
        horizontal_length: the radial length of the horizontal section of
            the TF coil (cm).
        vertical_mid_point: the (x,z) coordinates of the mid point of the
            outboard vertical section (cm).
        vertical_length: the radial length of the outboard vertical section
            of the TF coil (cm).
        thickness: the thickness of the toroidal field coil.
        distance: the extrusion distance.
        number_of_coils: the number of TF coils. This changes with
            azimuth_placement_angle dividing up 360 degrees by the number of
            coils.
        with_inner_leg: Include the inner TF leg. Defaults to True.
        stp_filename: Defaults to "ToroidalFieldCoilCoatHanger.stp".
        stl_filename: Defaults to "ToroidalFieldCoilCoatHanger.stl".
        material_tag: Defaults to "outer_tf_coil_mat".
    """

    def __init__(
        self,
        horizontal_start_point: Tuple[float, float],
        horizontal_length: float,
        vertical_mid_point: Tuple[float, float],
        vertical_length: float,
        thickness: float,
        distance: float,
        number_of_coils: int,
        with_inner_leg: Optional[bool] = True,
        stp_filename: Optional[str] = "ToroidalFieldCoilCoatHanger.stp",
        stl_filename: Optional[str] = "ToroidalFieldCoilCoatHanger.stl",
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

        self.horizontal_start_point = horizontal_start_point
        self.horizontal_length = horizontal_length
        self.vertical_mid_point = vertical_mid_point
        self.vertical_length = vertical_length
        self.thickness = thickness
        self.distance = distance
        self.number_of_coils = number_of_coils
        self.with_inner_leg = with_inner_leg

    @property
    def azimuth_placement_angle(self):
        self.find_azimuth_placement_angle()
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        self._azimuth_placement_angle = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the 2D
        profile of the poloidal field coil shape."""

        # 16---15
        # -     -
        # -       14
        # -        -
        # 1---2     -
        #       -    -
        #        -    13
        #         -    -
        #          3    12
        #          -    -
        #          -    -
        #          -    -
        #          4    11
        #         -    -
        #        -    10
        #       -    -
        # 6---5     -
        # -       -
        # -      9
        # -    -
        # 7---8

        adjacent_length = self.vertical_mid_point[0] - (
            self.horizontal_start_point[0] + self.horizontal_length)
        oppersite_length = self.horizontal_start_point[1] - (
            self.vertical_mid_point[1] + 0.5 * self.vertical_length)

        point_rotation = math.atan(oppersite_length / adjacent_length)
        point_rotation_mid = math.radians(90) - point_rotation

        points = [
            self.horizontal_start_point,  # point 1
            (
                self.horizontal_start_point[0] + self.horizontal_length,
                self.horizontal_start_point[1],
            ),  # point 2
            (
                self.vertical_mid_point[0],
                self.vertical_mid_point[1] + 0.5 * self.vertical_length,
            ),  # point 3
            (
                self.vertical_mid_point[0],
                self.vertical_mid_point[1] - 0.5 * self.vertical_length,
            ),  # point 4
            (
                self.horizontal_start_point[0] + self.horizontal_length,
                -self.horizontal_start_point[1],
            ),  # point 5
            (
                self.horizontal_start_point[0],
                -self.horizontal_start_point[1],
            ),  # point 6
            (
                self.horizontal_start_point[0],
                -self.horizontal_start_point[1] - self.thickness,
            ),  # point 7
            (
                self.horizontal_start_point[0] + self.horizontal_length,
                -self.horizontal_start_point[1] - self.thickness,
            ),  # point 8
            rotate(
                (
                    self.horizontal_start_point[0] + self.horizontal_length,
                    -self.horizontal_start_point[1],
                ),  # same as point 5
                (
                    self.horizontal_start_point[0] + self.horizontal_length,
                    -self.horizontal_start_point[1] - self.thickness,
                ),  # same as point 8
                point_rotation
            ),  # point 9
            rotate(
                (
                    self.vertical_mid_point[0],
                    self.vertical_mid_point[1] - 0.5 * self.vertical_length,
                ),  # same as point 4
                (
                    self.vertical_mid_point[0] + self.thickness,
                    self.vertical_mid_point[1] - 0.5 * self.vertical_length,
                ),  # same as point 11
                -point_rotation_mid
            ),  # point 10
            (
                self.vertical_mid_point[0] + self.thickness,
                self.vertical_mid_point[1] - 0.5 * self.vertical_length,
            ),  # point 11
            (
                self.vertical_mid_point[0] + self.thickness,
                self.vertical_mid_point[1] + 0.5 * self.vertical_length,
            ),  # point 12
            rotate(
                (
                    self.vertical_mid_point[0],
                    self.vertical_mid_point[1] + 0.5 * self.vertical_length,
                ),  # same as point 3
                (
                    self.vertical_mid_point[0] + self.thickness,
                    self.vertical_mid_point[1] + 0.5 * self.vertical_length,
                ),  # same as point 12
                point_rotation_mid
            ),  # point 13
            rotate(
                (
                    self.horizontal_start_point[0] + self.horizontal_length,
                    self.horizontal_start_point[1],
                ),  # same as point 2
                (
                    self.horizontal_start_point[0] + self.horizontal_length,
                    self.horizontal_start_point[1] + self.thickness,
                ),  # same as point 15
                -point_rotation
            ),  # point 14
            (
                self.horizontal_start_point[0] + self.horizontal_length,
                self.horizontal_start_point[1] + self.thickness,
            ),  # point 15
            (
                self.horizontal_start_point[0],
                self.horizontal_start_point[1] + self.thickness,
            )   # point 16
        ]

        self.inner_leg_connection_points = [
            points[0],
            (points[0][0] + self.thickness, points[0][1]),
            (points[5][0] + self.thickness, points[5][1]),
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
        )

        wire = solid.close()

        self.wire = wire

        solid = wire.extrude(distance=-self.distance / 2.0, both=True)

        solid = self.rotate_solid(solid)

        cutting_wedge = calculate_wedge_cut(self)
        solid = self.perform_boolean_operations(solid, wedge_cut=cutting_wedge)

        if self.with_inner_leg is True:
            inner_leg_solid = cq.Workplane(self.workplane)
            inner_leg_solid = inner_leg_solid.polyline(
                self.inner_leg_connection_points)
            inner_leg_solid = inner_leg_solid.close().extrude(
                distance=-self.distance / 2.0, both=True)

            inner_leg_solid = self.rotate_solid(inner_leg_solid)
            inner_leg_solid = self.perform_boolean_operations(
                inner_leg_solid, wedge_cut=cutting_wedge)

            solid = cq.Compound.makeCompound(
                [a.val() for a in [inner_leg_solid, solid]]
            )

        self.solid = solid   # not necessarily required as set in boolean_operations

        return solid
