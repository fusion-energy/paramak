import math
from paramak import RotateMixedShape, RotateStraightShape, Shape, CuttingWedge
import cadquery as cq


class ConstantThicknessDome(RotateMixedShape):
    """A cylindrical vessel volume with constant thickness with a simple dished
    head. This style of tank head has no knuckle radius or straight flange. The
    dished shape is made from a chord of a circle.

    Arguments:
        thickness: the radial thickness of the dome.
        chord_center_height: the vertical position of the chord center
        chord_width: the width of the chord base
        chord_height: the height of the chord which is also distance between
            the chord_center_height and the inner surface of the dome
        upper_or_lower: Curves the dish with a positive or negative direction
            to allow the upper section or lower section of vacuum vessel
            domes to be made.
        name:
        rotation_angle
    """

    def __init__(
        self,
        thickness: float = 10,
        chord_center_height: float = 50,
        chord_width: float = 100,
        chord_height: float = 20,
        upper_or_lower: str = "upper",
        name="constant_thickness_dome",
        **kwargs,
    ):

        self.thickness = thickness
        self.chord_center_height = chord_center_height
        self.chord_width = chord_width
        self.chord_height = chord_height
        self.upper_or_lower = upper_or_lower
        self.name = name

        super().__init__(name=name, **kwargs)

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
        #
        #
        #
        #         cc           1 -- 2
        #                    -      |
        #                  -        3
        #                -       -
        #          7  -       -
        #          |       -
        #          6   -
        #       far side

        if self.chord_height * 2 >= self.chord_width:
            msg = "ConstantThicknessDome requires that the self.chord_width is at least 2 times as large as the chord height"
            raise ValueError(msg)

        radius_of_sphere = ((math.pow(self.chord_width, 2)) + (4.0 * math.pow(self.chord_height, 2))) / (
            8 * self.chord_height
        )
        
        # TODO set to 0 for now, add ability to shift the center of the chord left and right
        self.chord_center = (0, self.chord_center_height)

        point_1 = (self.chord_center[0] + (self.chord_width / 2), self.chord_center[1], "straight")

        if self.upper_or_lower == "upper":
            center_point = (self.chord_center[0], self.chord_center[1] + self.chord_height - radius_of_sphere)
            inner_tri_angle = math.atan((center_point[1] - self.chord_center[1]) / (self.chord_width / 2))
            outer_tri_adj = math.cos(inner_tri_angle) * self.thickness
            # original ending type
            # point_2 = (point_1[0] + outer_tri_adj, point_1[1], "straight")
            point_2 = (point_1[0] + self.thickness, point_1[1], "straight")
            outer_tri_opp = math.sqrt(math.pow(self.thickness, 2) - math.pow(outer_tri_adj, 2))
            point_7 = (self.chord_center[0], self.chord_center[1] + radius_of_sphere, "straight")
            point_6 = (self.chord_center[0], self.chord_center[1] + radius_of_sphere + self.thickness, "straight")
            self.far_side = (center_point[0], center_point[1] - (radius_of_sphere + self.thickness))
            point_3 = (point_2[0], point_2[1] + outer_tri_opp, "straight")
        elif self.upper_or_lower == "lower":
            center_point = (self.chord_center[0], self.chord_center[1] - self.chord_height + radius_of_sphere)
            inner_tri_angle = math.atan((center_point[1] - self.chord_center[1]) / (self.chord_width / 2))
            outer_tri_adj = math.cos(inner_tri_angle) * self.thickness
            # original ending type
            # point_2 = (point_1[0] + outer_tri_adj, point_1[1], "straight")
            point_2 = (point_1[0] + self.thickness, point_1[1], "straight")
            outer_tri_opp = math.sqrt(math.pow(self.thickness, 2) - math.pow(outer_tri_adj, 2))
            point_7 = (self.chord_center[0], self.chord_center[1] - radius_of_sphere, "straight")
            point_6 = (self.chord_center[0], self.chord_center[1] - (radius_of_sphere + self.thickness), "straight")
            self.far_side = (center_point[0], center_point[1] + radius_of_sphere + self.thickness)
            point_3 = (point_2[0], point_2[1] - outer_tri_opp, "straight")
        else:
            msg = f'upper_or_lower should be either "upper"  or "lower". Not {self.upper_or_lower}'
            raise ValueError(msg)

        self.points = [point_1, point_2, point_3, point_6, point_7]

    def create_solid(self):
        """Creates a rotated 3d solid using points with circular edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """
    
        radius_of_sphere = ((math.pow(self.chord_width, 2)) + (4.0 * math.pow(self.chord_height, 2))) / (
            8 * self.chord_height
        )
        
        # TODO set to 0 for now, add ability to shift the center of the chord left and right
        self.chord_center = (0, self.chord_center_height)

        if self.upper_or_lower == "upper":
            center_point = (self.chord_center[0], self.chord_center[1] + self.chord_height - radius_of_sphere)
            self.far_side = (center_point[0], center_point[1] - (radius_of_sphere + self.thickness))
        elif self.upper_or_lower == "lower":
            center_point = (self.chord_center[0], self.chord_center[1] - self.chord_height + radius_of_sphere)
            self.far_side = (center_point[0], center_point[1] + radius_of_sphere + self.thickness)
        else:
            raise ValueError("self.upper_or_lower")

        big_sphere = (
            cq.Workplane(self.workplane)
            .moveTo(center_point[0], center_point[1])
            .sphere(radius_of_sphere + self.thickness)
        )
        small_sphere = cq.Workplane(self.workplane).moveTo(center_point[0], center_point[1]).sphere(radius_of_sphere)

        outer_cylinder_cutter = RotateStraightShape(
            workplane=self.workplane,
            points=(
                (self.chord_center[0], self.chord_center[1]),  # cc
                (self.points[1][0], self.points[1][1]),  # point 2
                (self.points[2][0], self.points[2][1]),  # point 3
                (self.points[2][0] + radius_of_sphere, self.points[2][1]),  # point 3 wider
                (self.points[2][0] + radius_of_sphere, self.far_side[1]),
                self.far_side,
            ),
            rotation_angle=360,
        )

        cap = Shape()
        cap.solid = big_sphere.cut(small_sphere)

        height = 2 * (radius_of_sphere + abs(center_point[1]) + self.thickness)
        radius = 2 * (radius_of_sphere + abs(center_point[0]) + self.thickness)
        cutter = CuttingWedge(height=height, radius=radius, rotation_angle=self.rotation_angle)

        cap.solid = cap.solid.intersect(cutter.solid)
        cap.solid = cap.solid.cut(outer_cylinder_cutter.solid)

        self.solid = cap.solid
