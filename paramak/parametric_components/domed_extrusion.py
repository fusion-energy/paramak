import math
from paramak import Shape, ExtrudeCircleShape
import cadquery as cq


class DomedExtrusion(Shape):
    """

    Arguments:

        name: the name of the shape, used in the graph legend and as a
            filename prefix when exporting.
    """

    def __init__(
        self,
        extrusion_distance: float,
        dome_height: float,
        radius: float,
        extrusion_start_offset: float = 0.0,
        name: str = "domed_extrusion",
        **kwargs,
    ):

        super().__init__(name=name, **kwargs)

        self.extrusion_distance = extrusion_distance
        self.dome_height = dome_height
        self.radius = radius
        self.extrusion_start_offset = extrusion_start_offset
        self.name = name
 
    def find_points(self):
        """
        Finds the XZ points joined by straight and circle connections that
        describe the 2D profile of the vessel shape.
        """

        # Note these points are not used in the normal way when constructing
        # the solid
        #
        #          
        #          
        #          p3  -
        #                -
        #                  -
        #                    -
        #         cc          p2 
        #     chord center    |
        #                     |
        #         sc          |
        #     sphere center   |
        #                     |
        #        p0 ----------p1
        #

        radius_of_sphere = ((math.pow(self.radius, 2)) + (4.0 * math.pow(self.chord_height, 2))) / (
            8 * self.chord_height
        )

        # TODO set to 0 for now, add ability to shift the center of the chord left and right
        chord_center = (0, self.chord_center_height)

        point_1 = (chord_center[0] + (self.chord_width / 2), chord_center[1], "straight")

        point_0 = [(self.ring_radius, 0)]

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
        chord_center = (0, self.chord_center_height)

        if self.upper_or_lower == "upper":
            center_point = (chord_center[0], chord_center[1] + self.chord_height - radius_of_sphere)
            far_side = (center_point[0], center_point[1] - (radius_of_sphere + self.thickness))
        elif self.upper_or_lower == "lower":
            center_point = (chord_center[0], chord_center[1] - self.chord_height + radius_of_sphere)
            far_side = (center_point[0], center_point[1] + radius_of_sphere + self.thickness)
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
                (chord_center[0], chord_center[1]),  # cc
                (self.points[1][0], self.points[1][1]),  # point 2
                (self.points[2][0], self.points[2][1]),  # point 3
                (self.points[2][0] + radius_of_sphere, self.points[2][1]),  # point 3 wider
                (self.points[2][0] + radius_of_sphere, far_side[1]),
                far_side,
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
