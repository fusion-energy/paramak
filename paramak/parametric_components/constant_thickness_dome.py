from typing import Tuple

from paramak import RotateMixedShape, RotateStraightShape
from paramak import (
    find_center_point_of_circle,
    rotate,
    distance_between_two_points,
    angle_between_two_points_on_circle,
    find_radius_of_circle,
    extend,
)
import cadquery as cq


class ConstantThicknessDome(RotateMixedShape):
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
        thickness: float,
        chord_center: Tuple[float, float],
        chord_width: float,
        chord_height: float,
        **kwargs,
    ):

        self.thickness = thickness
        self.chord_center = chord_center
        self.chord_width = chord_width
        self.chord_height = chord_height

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
        #
        #          6   -
        #          |       -
        #          7  -       4
        #                8       -
        #                  -       3
        #                    -     |
        #         cc          1 -- 2
        #     chord center
        #
        #
        #          cp
        #     center point
        #

        # print('radius_of_sphere',radius_of_sphere)

        # point_6 = (self.chord_center[0], self.chord_center[1] + radius_of_sphere, 'straight')
        # point_7 = (self.chord_center[0], self.chord_center[1] + radius_of_sphere + self.thickness, 'circle')
        # print('point_6',point_6)
        # print('point_7',point_7)

        # point_1 = (self.chord_center[0] + self.chord_width / 2 , self.chord_center[1], 'straight')
        # print('point_1',point_1)

        self.points = None

        # point_3 = extend(point_1, center_point, -self.thickness)
        # point_3 = (point_3[0], point_3[1], 'circle')
        # print('point_3',point_3)

        # # def rotate(origin: Tuple[float, float], point: Tuple[float, float], angle: float):
        # # angle_between_two_points_on_circle(point_1, point_2, radius_of_circle):

        # rotaion_angle_upper = angle_between_two_points_on_circle(point_3, point_6, radius_of_sphere)
        # point_4 = rotate(center_point, point_6, -rotaion_angle_upper)
        # point_4 = (point_4[0], point_4[1], 'circle')

        # rotaion_angle_lower = angle_between_two_points_on_circle(point_1, point_7, radius_of_sphere)
        # point_8 = rotate(center_point, point_7, -rotaion_angle_lower)
        # point_8 = (point_8[0], point_8[1], 'circle')

        # point_2 = (point_3[0], point_1[1], 'straight')
        # # for p in [point_1, point_2, point_3, point_4, point_6, point_7, point_8]:
        # #     print(p)

        # self.points = [point_1, point_2, point_3, point_4, point_6, point_7, point_8]

    def create_solid(self):

        radius_of_sphere = ((self.chord_width * self.chord_width) / (8.0 * self.chord_height)) + (
            self.chord_height / 2.0
        )
        center_point = (self.chord_center[0], self.chord_center[1] + self.chord_height - radius_of_sphere)
        big_sphere = cq.Workplane("XZ").sphere(radius_of_sphere + self.thickness).translate(center_point)
        small_sphere = cq.Workplane("XZ").sphere(radius_of_sphere).translate(center_point)

        max_z = max(
            center_point[1] + radius_of_sphere + self.thickness, center_point[1] - (radius_of_sphere + self.thickness)
        )
        # min_z =

        cylinder_cutter = RotateStraightShape(
            points=(
                (10, -max_z),
                (10, max_z),
                (10 + 100, max_z),
                (10 + 100, -max_z),
            ),
            translate=center_point,
        )

        solid = big_sphere.cut(cylinder_cutter.solid)

        self.solid = solid.cut(small_sphere)
