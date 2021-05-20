
from typing import Optional

from paramak import ExtrudeCircleShape


class PortCutterCircular(ExtrudeCircleShape):
    """Creates an extruded shape with a circular section that is used to cut
    other components (eg. blanket, vessel,..) in order to create ports.

    Args:
        radius: radius (cm) of port cutter.
        distance: extruded distance (cm) of the port cutter.
        center_point: center point of the port cutter. Defaults to (0, 0).
        workplane: workplane in which the port cutters are created. Defaults
            to "ZY".
        rotation_axis: axis around which the port cutters are rotated and
            placed. Defaults to "Z".
        extrusion_start_offset: the distance between 0 and the start of the
            extrusion. Defaults to 1..
        stp_filename: defaults to "PortCutterCircular.stp".
        stl_filename: defaults to "PortCutterCircular.stl".
        name: defaults to "circular_port_cutter".
        material_tag: defaults to "circular_port_cutter_mat".
    """

    def __init__(
        self,
        radius: float,
        distance: float,
        center_point: Optional[tuple] = (0, 0),
        workplane: Optional[str] = "ZY",
        rotation_axis: Optional[str] = "Z",
        extrusion_start_offset: Optional[float] = 1.,
        stp_filename: Optional[str] = "PortCutterCircular.stp",
        stl_filename: Optional[str] = "PortCutterCircular.stl",
        name: Optional[str] = "circular_port_cutter",
        material_tag: Optional[str] = "circular_port_cutter_mat",
        **kwargs
    ):
        super().__init__(
            workplane=workplane,
            rotation_axis=rotation_axis,
            extrusion_start_offset=extrusion_start_offset,
            radius=radius,
            extrude_both=False,
            name=name,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            distance=distance,
            **kwargs
        )

        self.radius = radius
        self.center_point = center_point

    def find_points(self):
        self.points = [self.center_point]
