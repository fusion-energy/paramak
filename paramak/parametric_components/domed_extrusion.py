import math
from paramak import Shape, CuttingWedge

from paramak.utils import get_largest_dimension
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
        print("radius_of_sphere", radius_of_sphere)

        if self.upper_or_lower == "upper" and self.extrusion_distance > 0:
            center_of_sphere_offset = self.extrusion_start_offset - self.dome_height + radius_of_sphere
        elif self.upper_or_lower == "upper" and self.extrusion_distance < 0:
            center_of_sphere_offset = self.extrusion_start_offset + self.dome_height - radius_of_sphere
        elif self.upper_or_lower == "lower" and self.extrusion_distance > 0:
            # not sure why this one is not working
            print(self.extrusion_start_offset, self.extrusion_distance, self.dome_height, radius_of_sphere)
            center_of_sphere_offset = self.extrusion_start_offset - self.dome_height + radius_of_sphere
        elif self.upper_or_lower == "lower" and self.extrusion_distance < 0:
            center_of_sphere_offset = self.extrusion_start_offset + self.dome_height - radius_of_sphere
        else:
            raise ValueError(f"upper_or_lower should be set to 'upper' or 'lower' not {self.upper_or_lower}")

        sphere = (
            cq.Workplane(self.workplane)
            .workplane(offset=center_of_sphere_offset)
            .sphere(radius_of_sphere)
            # .cut(cutting_cylinder)
        )

        wire_cutter = (
            cq.Workplane(self.workplane).workplane(offset=self.extrusion_start_offset).circle(radius_of_sphere)
        )

        # negative or not
        solid_cutter = wire_cutter.extrude(until=self.extrusion_distance * radius_of_sphere * 3, both=False)

        wire = cq.Workplane(self.workplane).workplane(offset=self.extrusion_start_offset).circle(self.radius)

        solid = wire.extrude(until=self.extrusion_distance, both=False)

        solid = self.rotate_solid(solid)

        solid = sphere.cut(solid_cutter).union(solid)

        # solid = sphere.cut(solid)

        # largest_dim = get_largest_dimension(solid)
        # cutting_wedge = CuttingWedge(height=largest_dim*2, radius=largest_dim*2, rotation_angle=360.-self.rotation_angle)

        # solid2 = self.perform_boolean_operations(solid, wedge_cut=cutting_wedge)

        self.solid = solid  # cutting_cylinder.union(sphere)

        return solid


# pool0 = paramak.DomedExtrusion(
#     extrusion_distance = 100,
#     dome_height = 50,
#     extrusion_start_offset = -20,
#     radius=200,
#     name='lower_20',
#     upper_or_lower='lower',
#     rotation_angle=180
# )
# pool0.export_html_3d(f'{pool0.name}.html')

# pool1 = paramak.DomedExtrusion(
#     extrusion_distance = 100,
#     dome_height = 50,
#     extrusion_start_offset = -20,
#     radius=200,
#     name='upper_20',
#     upper_or_lower='upper',
#     rotation_angle=180
# )
# pool1.export_html_3d(f'{pool1.name}.html')

# pool2 = paramak.DomedExtrusion(
#     extrusion_distance = -100,
#     dome_height = 50,
#     extrusion_start_offset = -20,
#     radius=200,
#     name='upper_-20',
#     upper_or_lower='upper',
#     rotation_angle=180
# )
# pool2.export_html_3d(f'{pool2.name}.html')

# pool3 = paramak.DomedExtrusion(
#     extrusion_distance = -100,
#     dome_height = 50,
#     extrusion_start_offset = -20,
#     radius=200,
#     name='lower_-20',
#     upper_or_lower='lower',
#     rotation_angle=180
# )
