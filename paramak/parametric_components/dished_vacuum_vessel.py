from typing import Tuple

from paramak import RotateMixedShape
from paramak import (
    find_center_point_of_circle,
    rotate,
    distance_between_two_points,
    angle_between_two_points_on_circle,
    find_radius_of_circle,
)


class DishedVacuumVessel(RotateMixedShape):
    """A cylindrical vessel volume with constant thickness with a simple dished
    head. This style of tank head has no knuckle radius or straight flange.

    Arguments:
        dish_height: the height of the dish section. This is also the chord
            heigh of the circle used to make the dish.
        cylinder_height: the height of the cylindrical section of the vacuum
            vessel.
        center_point: the x,z coordinates of the center of the vessel
        radius: the radius from which the centres of the vessel meets the outer
            circumference.
        thickness: the radial thickness of the vessel in cm.
    """

    def __init__(
        self,
        radius: float,
        center_point: Tuple[float, float],
        dish_height: float,
        cylinder_height: float,
        thickness: float,
        **kwargs,
    ):
        self.radius = radius
        self.thickness = thickness
        self.center_point = center_point
        self.dish_height = dish_height
        self.cylinder_height = cylinder_height

        super().__init__(**kwargs)

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if not isinstance(value, (float, int)):
            raise ValueError("VacuumVessel.radius must be a number. Not", value)
        if value <= 0:
            msg = "VacuumVessel.radius must be a positive number above 0. " f"Not {value}"
            raise ValueError(msg)
        self._radius = value

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        if not isinstance(value, (float, int)):
            msg = f"VacuumVessel.thickness must be a number. Not {value}"
            raise ValueError(msg)
        if value <= 0:
            msg = f"VacuumVessel.thickness must be a positive number above 0. Not {value}"
            raise ValueError(msg)
        self._thickness = value

    def find_points(self):
        """
        Finds the XZ points joined by straight and circle connections that
        describe the 2D profile of the vessel shape.
        """
        #               3
        #            -     -
        #         -           -
        #       2    -  8   -    -
        #     -    -    ^     -    -
        #   -    -      |       -    -
        # -    -       d,h         -    -
        # 1   7         |          9    4
        # |   |                    |    |
        # |   |                    |    |
        # |   |         c,p        |    |
        # |   |                    |    |
        # |   |                    |    |
        # 3   12                  10    1
        # -     -                  -   -
        #   -     -             -    -
        #     -     -    10_to_11    -
        #       -     -    -   1_to_2
        #         -     11    -
        #            -     -
        #               2

        point_1 = (self.center_point[0] + self.radius, self.center_point[1] - 0.5 * self.cylinder_height)
        # point_2 = (self.center_point[0]-self.radius, self.center_point[1] + 0.5* self.dish_height + self.thickness)
        point_2 = (self.center_point[0], self.center_point[1] - (0.5 * self.cylinder_height + self.dish_height))
        point_3 = (self.center_point[0] - self.radius, self.center_point[1] - 0.5 * self.cylinder_height)
        point_4 = (self.center_point[0] + self.radius, self.center_point[1] + 0.5 * self.cylinder_height)

        point_10 = (
            self.center_point[0] + self.radius - self.thickness,
            self.center_point[1] - 0.5 * self.cylinder_height,
        )
        point_11 = (
            self.center_point[0],
            self.center_point[1] - (0.5 * self.cylinder_height + self.dish_height - self.thickness),
        )
        point_12 = (
            self.center_point[0] - (self.radius - self.thickness),
            self.center_point[1] - 0.5 * self.cylinder_height,
        )

        print("point_10", point_10)
        print("point_11", point_11)
        print("point_12", point_12)

        center_point_lower_inner_circle = find_center_point_of_circle(point_10, point_11, point_12)
        print("center_point_lower_inner_circle", center_point_lower_inner_circle)

        center_point_lower_circle = find_center_point_of_circle(point_1, point_2, point_3)
        print("center_point_lower_circle", center_point_lower_circle)

        dish_radius = find_radius_of_circle(center_point=center_point_lower_circle, edge_point=point_1)

        angle_separation_1_to_2 = angle_between_two_points_on_circle(point_1, point_2, dish_radius)
        angle_separation_10_to_11 = angle_between_two_points_on_circle(point_10, point_11, dish_radius)

        print("angle_separation", angle_separation_1_to_2)
        print("angle_separation", angle_separation_10_to_11)

        point_1_to_2 = rotate(origin=center_point_lower_circle, point=point_1, angle=-angle_separation_1_to_2 / 2)
        point_10_to_11 = rotate(origin=center_point_lower_circle, point=point_10, angle=-angle_separation_10_to_11 / 2)

        # point_6 = (self.center_point[0]-self.radius-self.thickness, self.center_point[1] - 0.5* self.dish_height, 'straight')

        # point_4 = (point_4[0], point_4[1], 'straight')
        point_11 = (point_11[0], point_11[1], "circle")
        point_10_to_11 = (point_10_to_11[0], point_10_to_11[1], "circle")
        point_10 = (point_10[0], point_10[1], "straight")
        point_1 = (point_1[0], point_1[1], "circle")
        point_1_to_2 = (point_1_to_2[0], point_1_to_2[1], "circle")
        point_2 = (point_2[0], point_2[1], "straight")

        self.points = [point_11, point_10_to_11, point_10, point_1, point_1_to_2, point_2]
