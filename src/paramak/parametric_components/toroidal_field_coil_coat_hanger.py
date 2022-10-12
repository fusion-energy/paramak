import math
from typing import Optional, Tuple

from .toroidal_field_coil import ToroidalFieldCoil
from paramak.utils import rotate, patch_workplane

patch_workplane()


class ToroidalFieldCoilCoatHanger(ToroidalFieldCoil):
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
        azimuth_start_angle: The azimuth angle to for the first TF coil which
            offsets the placement of coils around the azimuthal angle
    """

    def __init__(
        self,
        name: str = "toroidal_field_coil",
        horizontal_start_point: Tuple[float, float] = (40, 200),
        horizontal_length: float = 200,
        vertical_mid_point: Tuple[float, float] = (400, 0),
        vertical_length: float = 250,
        thickness: float = 30,
        distance: float = 20,
        number_of_coils: int = 12,
        with_inner_leg: bool = True,
        azimuth_start_angle: float = 0,
        vertical_displacement: float = 0.0,
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

        self.horizontal_start_point = horizontal_start_point
        self.horizontal_length = horizontal_length
        self.vertical_mid_point = vertical_mid_point
        self.vertical_length = vertical_length

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the
        2D profile of the poloidal field coil shape."""

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

        adjacent_length = self.vertical_mid_point[0] - (self.horizontal_start_point[0] + self.horizontal_length)
        oppersite_length = self.horizontal_start_point[1] - (self.vertical_mid_point[1] + 0.5 * self.vertical_length)

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
                point_rotation,
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
                -point_rotation_mid,
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
                point_rotation_mid,
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
                -point_rotation,
            ),  # point 14
            (
                self.horizontal_start_point[0] + self.horizontal_length,
                self.horizontal_start_point[1] + self.thickness,
            ),  # point 15
            (
                self.horizontal_start_point[0],
                self.horizontal_start_point[1] + self.thickness,
            ),  # point 16
        ]

        self.inner_leg_connection_points = [
            points[0],
            (points[0][0] + self.thickness, points[0][1]),
            (points[5][0] + self.thickness, points[5][1]),
            points[5],
        ]

        # adds any vertical displacement and the connection type to the points
        points = [(point[0], point[1] + self.vertical_displacement, "straight") for point in points]

        self.points = points
