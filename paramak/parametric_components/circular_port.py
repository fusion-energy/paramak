from typing import Optional, Tuple
from paramak import Shape
from cadquery import Workplane
from paramak.utils import calculate_wedge_cut


class CircularPort(Shape):
    """Creates an extruded pipe with a flange end and optional.

    Args:
        inner_radius: inner_radius (cm) of tubular section.
        distance: extruded distance (cm) of the tubular section.
        wall_thickness: the radial thickness of the  tubular section wall.
        flange_overhang: the distance of the flange overhang or lip.
        flange_thickness: the thickness of the flange, should be a positive
            number. Set to None if no blank flange is required.
        blank_flange_thickness: the thickness of the blank flange
        center_point: center point of the port cutter. Defaults to (0, 0).
        workplane: workplane in which the port cutters are created. Defaults
            to "ZY".
        rotation_axis: axis around which the port cutters are rotated and
            placed. Defaults to "Z".
        extrusion_start_offset: the distance between 0 and the start of the
            extrusion. Defaults to 1..
        name: defaults to "circular_port_cutter".
    """

    def __init__(
        self,
        inner_radius: float = 30,
        distance: float = 20,
        wall_thickness: float = 2,
        flange_overhang: float = 10,
        flange_thickness: float = 5,
        flange_gap: float = 0,
        blank_flange_thickness: float = 5,
        workplane: str = "ZY",
        rotation_axis: str = "Z",
        extrusion_start_offset: float = 100,
        center_point: tuple = (0, 0),
        name: str = "circular_port_cutter",
        color: Tuple[float, float, float, Optional[float]] = (
            0.984,
            0.603,
            0.6,
        ),
        rotation_angle: float = 360,
        **kwargs,
    ):
        super().__init__(color=color, name=name, **kwargs)

        self.inner_radius = inner_radius
        self.distance = distance
        self.wall_thickness = wall_thickness
        self.flange_overhang = flange_overhang
        self.flange_thickness = flange_thickness
        self.flange_gap = flange_gap
        self.blank_flange_thickness = blank_flange_thickness
        self.workplane = workplane
        self.rotation_axis = rotation_axis
        self.extrusion_start_offset = extrusion_start_offset
        self.center_point = center_point
        self.rotation_angle = rotation_angle

    def find_points(self):
        self.points = [self.center_point]

    def create_solid(self):
        """Creates a extruded 3d solid using points with circular edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """

        extrusion_offset = -self.extrusion_start_offset
        flange_gap = -self.flange_gap
        extrusion_distance = -self.distance
        flange_thickness = self.flange_thickness

        inner_wire = (
            Workplane(self.workplane)
            .workplane(offset=extrusion_offset)
            .moveTo(self.points[0][0], self.points[0][1])
            .circle(self.inner_radius)
        )
        inner_solid = inner_wire.extrude(until=extrusion_distance - flange_thickness, both=False)

        outer_wire = (
            Workplane(self.workplane)
            .workplane(offset=extrusion_offset)
            .moveTo(self.points[0][0], self.points[0][1])
            .circle(self.inner_radius + self.wall_thickness)
        )
        outer_solid = outer_wire.extrude(until=extrusion_distance, both=False)

        flange_wire = (
            Workplane(self.workplane)
            .workplane(offset=extrusion_offset + extrusion_distance)
            .moveTo(self.points[0][0], self.points[0][1])
            .circle(self.inner_radius + self.wall_thickness + self.flange_overhang)
        )
        flange_solid = flange_wire.extrude(until=flange_thickness, both=False)

        solid = outer_solid.cut(inner_solid)
        flange_solid = flange_solid.cut(inner_solid)
        solid = solid.union(flange_solid)

        blank_flange_thickness = self.blank_flange_thickness

        if blank_flange_thickness > 0:
            blank_flange_wire = (
                Workplane(self.workplane)
                .workplane(offset=extrusion_offset + extrusion_distance + flange_gap - self.blank_flange_thickness)
                .moveTo(self.points[0][0], self.points[0][1])
                .circle(self.inner_radius + self.wall_thickness + self.flange_overhang)
            )
            blank_flange_solid = blank_flange_wire.extrude(until=blank_flange_thickness, both=False)
            solid = solid.union(blank_flange_solid)
        elif blank_flange_thickness < 0:
            msg = f"blank_flange_thickness should be larger than 0 or None. Not {blank_flange_thickness}"
            raise ValueError(msg)

        # TODO combine all wires into one
        # self.wire = solid.Wires()

        solid = self.rotate_solid(solid)

        # calculates the size of the component as these attributes are used
        # when making the cutting wedge
        self.radius = self.extrusion_start_offset + self.distance + self.flange_thickness + blank_flange_thickness
        self.height = self.center_point[0] + self.inner_radius + self.wall_thickness

        cutting_wedge = calculate_wedge_cut(self)
        solid = self.perform_boolean_operations(solid, wedge_cut=cutting_wedge)
        self.solid = solid

        return solid
