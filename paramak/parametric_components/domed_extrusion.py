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
        extrusion_distance: float=100,
        dome_height: float=10,
        radius: float=20,
        extrusion_start_offset: float = 0.0,
        name: str = "domed_extrusion",
        upper_or_lower: str = 'upper',
        **kwargs,
    ):

        super().__init__(name=name, **kwargs)

        self.extrusion_distance = extrusion_distance
        self.dome_height = dome_height
        self.radius = radius
        self.extrusion_start_offset = extrusion_start_offset
        self.name = name
        self.upper_or_lower = upper_or_lower
    # def find_points(self):
    #     """
    #     Finds the XZ points joined by straight and circle connections that
    #     describe the 2D profile of the vessel shape.
    #     """

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



        # TODO set to 0 for now, add ability to shift the center of the chord left and right
        # chord_center = (0, self.chord_center_height)

        # point_1 = (chord_center[0] + (self.chord_width / 2), chord_center[1], "straight")

        # point_0 = [(self.ring_radius, 0)]

        # self.points = [point_1, point_2, point_3, point_6, point_7]

    # def find_points(self):
    
    #     points = [(0, 0)]

    #     self.points = points

    def create_solid(self):
        """Creates a rotated 3d solid using points with circular edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """

        radius_of_sphere = ((math.pow(self.radius, 2)) + (4.0 * math.pow(self.dome_height, 2))) / (
            8 * self.dome_height
        )

        chord_center = (0, self.dome_height)
        
        if self.upper_or_lower == "upper":
            center_point = (chord_center[0], chord_center[1] + self.dome_height - radius_of_sphere)
        elif self.upper_or_lower == "lower":
            center_point = (chord_center[0], chord_center[1] - self.dome_height + radius_of_sphere)
        else:
            raise ValueError("self.upper_or_lower")
        
        big_sphere = (
            cq.Workplane(self.workplane)
            .moveTo(center_point[0], center_point[1])
            .sphere(radius_of_sphere)
        )

        solid = ExtrudeCircleShape(
            distance=self.extrusion_distance,
            radius=self.radius,
            extrusion_start_offset=self.extrusion_start_offset,
            extrude_both = False,
            color=self.color,
            name="domed_extrusion",
            # translate=self.translate
        )
        
        solid.points = [(0, 0)]


        self.solid = solid.solid.union(big_sphere)
