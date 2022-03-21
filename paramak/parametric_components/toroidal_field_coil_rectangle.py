from typing import Optional, Tuple

from .toroidal_field_coil import ToroidalFieldCoil
from paramak.utils import patch_workplane

patch_workplane()


class ToroidalFieldCoilRectangle(ToroidalFieldCoil):
    """Creates a rectangular shaped toroidal field coil.

    Args:
        horizontal_start_point: the (x,z) coordinates of the inner upper
            point (cm).
        vertical_mid_point: the (x,z) coordinates of the mid point of the
            vertical section (cm).
        thickness: the thickness of the toroidal field coil.
        distance: the extrusion distance.
        number_of_coils: the number of tf coils. This changes by the
            azimuth_placement_angle dividing up 360 degrees by the number of
            coils.
        with_inner_leg: include the inner tf leg. Defaults to True.
        azimuth_start_angle: The azimuth angle to for the first TF coil which
            offsets the placement of coils around the azimuthal angle
    """

    def __init__(
        self,
        name: str = "toroidal_field_coil",
        horizontal_start_point: Tuple[float, float] = (20, 200),
        vertical_mid_point: Tuple[float, float] = (350, 0),
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
        self.vertical_mid_point = vertical_mid_point
        self.inner_leg_connection_points = None

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe
        the 2D profile of the poloidal field coil shape."""

        if self.horizontal_start_point[0] >= self.vertical_mid_point[0]:
            raise ValueError(
                "horizontal_start_point x should be smaller than the \
                    vertical_mid_point x value"
            )
        if self.vertical_mid_point[1] >= self.horizontal_start_point[1]:
            raise ValueError(
                "vertical_mid_point y value should be smaller than the \
                    horizontal_start_point y value"
            )

        points = [
            self.horizontal_start_point,  # connection point
            # connection point
            (
                self.horizontal_start_point[0] + self.thickness,
                self.horizontal_start_point[1],
            ),
            (self.vertical_mid_point[0], self.horizontal_start_point[1]),
            (self.vertical_mid_point[0], -self.horizontal_start_point[1]),
            # connection point
            (
                self.horizontal_start_point[0] + self.thickness,
                -self.horizontal_start_point[1],
            ),
            # connection point
            (self.horizontal_start_point[0], -self.horizontal_start_point[1]),
            (
                self.horizontal_start_point[0],
                -(self.horizontal_start_point[1] + self.thickness),
            ),
            (
                self.vertical_mid_point[0] + self.thickness,
                -(self.horizontal_start_point[1] + self.thickness),
            ),
            (
                self.vertical_mid_point[0] + self.thickness,
                self.horizontal_start_point[1] + self.thickness,
            ),
            (
                self.horizontal_start_point[0],
                self.horizontal_start_point[1] + self.thickness,
            ),
        ]

        # adds any vertical displacement and the connection type to the points
        points = [(point[0], point[1] + self.vertical_displacement, "straight") for point in points]

        self.inner_leg_connection_points = [
            (points[0][0], points[0][1]),
            (points[1][0], points[1][1]),
            (points[4][0], points[4][1]),
            (points[5][0], points[5][1]),
        ]

        self.points = points
