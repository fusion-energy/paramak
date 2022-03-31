import math
from paramak import Shape, CuttingWedge

# from paramak.utils import calculate_wedge_cut
import cadquery as cq


class DomedExtrusion(Shape):
    """

    Arguments:

        name: the name of the shape, used in the graph legend and as a
            filename prefix when exporting.
    """

    def __init__(
        self,
        extrusion_distance: float = 100,
        dome_height: float = 5,
        radius: float = 20,
        extrusion_start_offset: float = 50.0,
        name: str = "domed_extrusion",
        upper_or_lower: str = "upper",
        workplane="XY",
        # rotation_axis="Z",
        rotation_angle=360,
        **kwargs,
    ):

        super().__init__(name=name, **kwargs)

        self.extrusion_distance = extrusion_distance
        self.dome_height = dome_height
        self.radius = radius
        self.extrusion_start_offset = extrusion_start_offset
        self.name = name
        self.upper_or_lower = upper_or_lower
        self.workplane = workplane
        self.rotation_angle = rotation_angle
        # self.rotation_axis = rotation_axis

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

    def create_solid(self):
        """Creates a rotated 3d solid using points with circular edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """

        # so a positive offset moves extrusion further from axis of azimuthal
        # placement rotation

        self.points = [(0, self.extrusion_start_offset)]

        radius_of_sphere = ((math.pow(self.radius * 2, 2)) + (4.0 * math.pow(self.dome_height, 2))) / (
            8 * self.dome_height
        )

        cutting_cylinder_wire = (
            cq.Workplane(self.workplane).workplane(offset=-self.extrusion_start_offset).circle(radius_of_sphere)
        )
        cutting_cylinder = cutting_cylinder_wire.extrude(until=-self.extrusion_distance, both=False)

        if self.upper_or_lower == "upper":
            center_of_sphere_offset = -(
                self.extrusion_distance - self.extrusion_start_offset + radius_of_sphere - self.dome_height
            )
        elif self.upper_or_lower == "lower":
            center_of_sphere_offset = (
                -self.extrusion_distance - self.extrusion_start_offset + radius_of_sphere - self.dome_height
            )
        else:
            raise ValueError("self.upper_or_lower")

        sphere = (
            cq.Workplane(self.workplane)
            .workplane(offset=center_of_sphere_offset)
            .sphere(radius_of_sphere)
            .cut(cutting_cylinder)
        )

        wire = cq.Workplane(self.workplane).workplane(offset=-self.extrusion_start_offset).circle(self.radius)

        solid = wire.extrude(until=-self.extrusion_distance, both=False)

        solid = self.rotate_solid(solid)

        print(solid.val().BoundingBox())
        # cutting_wedge = calculate_wedge_cut(self)
        cutting_wedge = CuttingWedge(height=1000, radius=1000)
        solid = self.perform_boolean_operations(solid, wedge_cut=cutting_wedge)

        # if self.translate:
        #     solid = solid.translate(self.translate)

        self.solid = solid.union(sphere)
        # self.solid = solid.cut(sphereorg)
        # self.solid = solid

        return solid
