import math
import cadquery as cq

from paramak import Shape


class DomedExtrusion(Shape):
    """A circular extrustion with a domed surface at one end.

    Arguments:
        extrusion_distance: the length of the circular extrustion. Not
            including the dome.
        dome_height: the height of the dome section starting from the end of
            the circular extrusion
        radius: the radius of the circular extrusion.
        extrusion_start_offset: the starting offset of the extrusion
        upper_or_lower: controls if the dome should be added at the upper or
            lower end of the circular extrusion
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

    #
    #          -  -
    #                -
    #                  -
    #                    -
    #         cc          -
    #     chord center    |
    #                     |
    #         sc          |
    #     sphere center   |
    #                     |
    #        ------------- workplane offset
    #
    #
    #     workplane 0

    def create_solid(self):
        """Creates a rotated 3d solid using points with circular edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """

        self.points = [(0, self.extrusion_start_offset)]

        radius_of_sphere = ((math.pow(self.radius * 2, 2)) + (4.0 * math.pow(self.dome_height, 2))) / (
            8 * self.dome_height
        )

        if self.upper_or_lower == "upper" and self.extrusion_distance > 0:
            center_of_sphere_offset = self.extrusion_start_offset - self.dome_height + radius_of_sphere
        elif self.upper_or_lower == "upper" and self.extrusion_distance < 0:
            center_of_sphere_offset = self.extrusion_start_offset + self.dome_height - radius_of_sphere
        elif self.upper_or_lower == "lower" and self.extrusion_distance > 0:
            center_of_sphere_offset = self.extrusion_start_offset - self.dome_height + radius_of_sphere
        elif self.upper_or_lower == "lower" and self.extrusion_distance < 0:
            center_of_sphere_offset = self.extrusion_start_offset + self.dome_height - radius_of_sphere
        else:
            raise ValueError(f"upper_or_lower should be set to 'upper' or 'lower' not {self.upper_or_lower}")

        sphere = cq.Workplane(self.workplane).workplane(offset=center_of_sphere_offset).sphere(radius_of_sphere)

        wire_cutter = (
            cq.Workplane(self.workplane).workplane(offset=self.extrusion_start_offset).circle(radius_of_sphere)
        )

        solid_cutter = wire_cutter.extrude(until=self.extrusion_distance * radius_of_sphere * 3, both=False)

        wire = cq.Workplane(self.workplane).workplane(offset=self.extrusion_start_offset).circle(self.radius)

        solid = wire.extrude(until=self.extrusion_distance, both=False)

        solid = self.rotate_solid(solid)

        solid = sphere.cut(solid_cutter).union(solid)

        self.solid = solid

        return solid
