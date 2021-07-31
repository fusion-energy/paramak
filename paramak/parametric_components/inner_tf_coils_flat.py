
import math
from typing import Optional
import numpy as np
from paramak import ExtrudeStraightShape


class InnerTfCoilsFlat(ExtrudeStraightShape):
    """A tf coil volume with straight inner and outer profiles and
    constant gaps between each coil. Note: the inner / outer surface is not
    equal distance to the center point everywhere as the corners are further
    than the straight sections.

    Args:
        height: height of tf coils.
        inner_radius: Distance between center point and the inner surface of
            the tf coils.
        outer_radius: Distance between center point and the outer surface of
            the tf coils.
        number_of_coils: number of tf coils.
        gap_size: gap between adjacent tf coils.
        radius_type: Controls the part of the inner surface used when
            defining the inner_radius and outer_radius. Can be set to either
            'corner' or 'straight'.
        azimuth_start_angle: defaults to 0.0.
        stp_filename: defaults to "InnerTfCoilsFlat.stp".
        stl_filename: defaults to "InnerTfCoilsFlat.stl".
        material_tag: defaults to "inner_tf_coil_mat".
        workplane:defaults to "XY".
        rotation_axis: Defaults to "Z".
    """

    def __init__(
        self,
        height: float,
        inner_radius: float,
        outer_radius: float,
        number_of_coils: int,
        gap_size: float,
        radius_type: Optional[str] = 'corner',
        azimuth_start_angle: Optional[float] = 0.0,
        stp_filename: Optional[str] = "InnerTfCoilsFlat.stp",
        stl_filename: Optional[str] = "InnerTfCoilsFlat.stl",
        material_tag: Optional[str] = "inner_tf_coil_mat",
        workplane: Optional[str] = "XY",
        rotation_axis: Optional[str] = "Z",
        **kwargs
    ) -> None:

        super().__init__(
            distance=height,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            material_tag=material_tag,
            workplane=workplane,
            rotation_axis=rotation_axis,
            **kwargs
        )

        self.azimuth_start_angle = azimuth_start_angle
        self.height = height
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.radius_type = radius_type
        self.number_of_coils = number_of_coils
        self.gap_size = gap_size
        self.distance = height

    @property
    def azimuth_start_angle(self):
        return self._azimuth_start_angle

    @azimuth_start_angle.setter
    def azimuth_start_angle(self, value):
        self._azimuth_start_angle = value

    @property
    def radius_type(self):
        return self._radius_type

    @radius_type.setter
    def radius_type(self, value):
        if value not in ['corner', 'straight']:
            msg = (
                f'radius_type must be either "corner" or "straight". Not {value}')
            raise ValueError(msg)
        self._radius_type = value

    @property
    def azimuth_placement_angle(self):
        self.find_azimuth_placement_angle()
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        self._azimuth_placement_angle = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def distance(self):
        return self.height

    @distance.setter
    def distance(self, value):
        self._distance = value

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, inner_radius):
        self._inner_radius = inner_radius

    @property
    def outer_radius(self):
        return self._outer_radius

    @outer_radius.setter
    def outer_radius(self, outer_radius):
        self._outer_radius = outer_radius

    @property
    def number_of_coils(self):
        return self._number_of_coils

    @number_of_coils.setter
    def number_of_coils(self, number_of_coils):
        self._number_of_coils = number_of_coils

    @property
    def gap_size(self):
        return self._gap_size

    @gap_size.setter
    def gap_size(self, gap_size):
        self._gap_size = gap_size

    def find_points(self):
        """Finds the points that describe the 2D profile of the tf coil shape"""

        #       /   p4
        #      /    /¦
        #     /    / ¦
        #    /    /  ¦
        #   /    /   ¦
        #     p1/    ¦
        #      ¦     ¦
        # x    ¦     ¦
        #      ¦     ¦
        #     p2\    ¦
        #   \    \   ¦
        #    \    \  ¦
        #     \    \ ¦
        #      \    p3

        if self.radius_type == 'corner':
            distance_to_inner_corner = self.inner_radius
            distance_to_rear_corner = self.outer_radius
        # this section calculates a new distance to the corners now that we
        # know the user provided the distance to the straight
        if self.radius_type == 'straight':
            angle = 360 / (self.number_of_coils * 2)
            distance_to_inner_corner = self.inner_radius / \
                math.cos(math.radians(angle))
            distance_to_rear_corner = self.outer_radius / \
                math.cos(math.radians(angle))

        if self.gap_size * self.number_of_coils > 2 * math.pi * distance_to_inner_corner:
            msg = (
                'Gap_size is too large. The gap_size * number of coils must '
                'be less than the circumference of the circle made by '
                'the inner_radius')
            raise ValueError(msg)

        if distance_to_inner_corner != 0.:
            theta_inner = (
                (2 * math.pi * distance_to_inner_corner) - (self.gap_size * self.number_of_coils)
            ) / (distance_to_inner_corner * self.number_of_coils)
            omega_inner = math.asin(
                self.gap_size / (2 * distance_to_inner_corner))

            # inner points
            point_1 = (
                (distance_to_inner_corner * math.cos(-omega_inner)),
                (-distance_to_inner_corner * math.sin(-omega_inner)),
            )
            point_2 = (
                (
                    distance_to_inner_corner * math.cos(theta_inner) * math.cos(-omega_inner)
                    + distance_to_inner_corner * math.sin(theta_inner) * math.sin(-omega_inner)
                ),
                (
                    -distance_to_inner_corner * math.cos(theta_inner) * math.sin(-omega_inner)
                    + distance_to_inner_corner * math.sin(theta_inner) * math.cos(-omega_inner)
                ),
            )
            points = [
                (point_1[0], point_1[1]),
                (point_2[0], point_2[1])
            ]

        else:

            points = [(0, 0)]

        # print(point_1)
        # print(point_2)

        theta_outer = (
            (2 * math.pi * distance_to_rear_corner) - (self.gap_size * self.number_of_coils)
        ) / (distance_to_rear_corner * self.number_of_coils)
        omega_outer = math.asin(self.gap_size / (2 * distance_to_rear_corner))

        # outer points
        point_4 = (
            (distance_to_rear_corner * math.cos(-omega_outer)),
            (-distance_to_rear_corner * math.sin(-omega_outer)),
        )
        point_6 = (
            (
                distance_to_rear_corner * math.cos(theta_outer) * math.cos(-omega_outer)
                + distance_to_rear_corner * math.sin(theta_outer) * math.sin(-omega_outer)
            ),
            (
                -distance_to_rear_corner * math.cos(theta_outer) * math.sin(-omega_outer)
                + distance_to_rear_corner * math.sin(theta_outer) * math.cos(-omega_outer)
            ),
        )
        points.append((point_6[0], point_6[1]))
        points.append((point_4[0], point_4[1]))

        self.points = points

    def find_azimuth_placement_angle(self):
        """Calculates the azimuth placement angles based on the number of tf
        coils"""

        angles = list(
            np.linspace(
                0 + self.azimuth_start_angle,
                360 + self.azimuth_start_angle,
                self.number_of_coils,
                endpoint=False))

        self.azimuth_placement_angle = angles
