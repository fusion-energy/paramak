from typing import Tuple
import math
from paramak import RotateMixedShape, RotateStraightShape
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

        # Note these points are not used in the normal way when constructing
        # the solid
        #
        #          6   -
        #          |       -
        #          7  -       -
        #                -       -
        #                  -       3
        #                    -     |
        #         cc          1 -- 2
        #     chord center
        #
        #
        #          cp
        #     center point
        #

        radius_of_sphere = ((math.pow(self.chord_width, 2)) + (4.0 * math.pow(self.chord_height, 2))) / (
            8 * self.chord_height
        )

        center_point = (self.chord_center[0], self.chord_center[1] + self.chord_height - radius_of_sphere)

        point_7 = (self.chord_center[0], self.chord_center[1] + radius_of_sphere, "straight")

        point_6 = (self.chord_center[0], self.chord_center[1] + radius_of_sphere + self.thickness, "straight")

        point_1 = (self.chord_center[0] + (self.chord_width / 2), self.chord_center[1], "straight")

        inner_tri_angle = math.atan((center_point[1] - self.chord_center[1]) / (self.chord_width / 2))

        outer_tri_adj = math.cos(inner_tri_angle) * self.thickness

        point_2 = (point_1[0] + outer_tri_adj, point_1[1], "straight")

        outer_tri_opp = math.sqrt(math.pow(self.thickness, 2) - math.pow(outer_tri_adj, 2))

        point_3 = (point_2[0], point_2[1] + outer_tri_opp, "straight")

        self.points = [point_1, point_2, point_3, point_6, point_7]

    def create_solid(self):

        radius_of_sphere = ((math.pow(self.chord_width, 2)) + (4.0 * math.pow(self.chord_height, 2))) / (
            8 * self.chord_height
        )

        center_point = (self.chord_center[0], self.chord_center[1] + self.chord_height - radius_of_sphere)

        big_sphere = cq.Workplane("XZ").sphere(radius_of_sphere + self.thickness).translate(center_point)
        small_sphere = cq.Workplane("XZ").sphere(radius_of_sphere).translate(center_point)

        max_z = 1000
        min_radius = self.points[1][0]
        max_radius = 1000
        # min_z =

        outer_cylinder_cutter = RotateStraightShape(
            points=(
                (min_radius, -max_z),
                (min_radius, max_z),
                (max_radius, max_z),
                (max_radius, -max_z),
            ),
            translate=center_point,
        )

        inner_cylinder_cutter = RotateStraightShape(
            points=(
                (0, -max_z),
                (0, max_z),
                (self.points[1][0], max_z),
                (self.points[1][0], -max_z),
            ),
            translate=center_point,
        )

        solid = big_sphere.cut(outer_cylinder_cutter.solid)

        solid = solid.cut(inner_cylinder_cutter.solid)

        self.solid = solid.cut(small_sphere)
