
from paramak import ExtrudeCircleShape


class PortCutterCircular(ExtrudeCircleShape):
    """Creates a extruded shape with a circular section that is used to cut
    other components (eg. blanket, vessel,..) in order to create ports.

    Args:
        z_pos (float): Z position (cm) of the port
        height (float): height (cm) of the port
        width (float): width (cm) of the port
        distance (float): extruded distance (cm) of the cutter
        stp_filename (str, optional): The filename used when saving stp files
            as part of a reactor. Defaults to "PortCutterCircular.stp".
        stl_filename (str, optional): The filename used when saving stl files
            as part of a reactor. Defaults to "PortCutterCircular.stl".
        color (tuple, optional): (sequences of 3 or 4 floats each in the range
            0-1): the color to  use when exporting as html graphs or png
            images. Defaults to (0.5, 0.5, 0.5).
        azimuth_placement_angle (float or iterable of floats, optional): The
            angle or angles to use when rotating the shape on the azimuthal
            axis. Defaults to 0.0.
        name (str, optional): the legend name used when exporting a html graph
            of the shape. Defaults to "circular_port_cutter".
        material_tag (str, optional): The material name to use when exporting
            the neutronics description. Defaults to "circular_port_cutter_mat".
    """
    def __init__(
        self,
        z_pos,
        radius,
        distance,
        stp_filename="PortCutterCircular.stp",
        stl_filename="PortCutterCircular.stl",
        color=(0.5, 0.5, 0.5),
        azimuth_placement_angle=0.0,
        name="circular_port_cutter",
        material_tag="circular_port_cutter_mat",
        **kwargs
    ):

        default_dict = {
            "points": None,
            "workplane": "XZ",
            "solid": None,
            "intersect": None,
            "cut": None,
            "union": None,
            "tet_mesh": None,
            "physical_groups": None,
        }

        for arg in kwargs:
            if arg in default_dict:
                default_dict[arg] = kwargs[arg]

        super().__init__(
            radius=radius,
            extrude_both=False,
            name=name,
            color=color,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            azimuth_placement_angle=azimuth_placement_angle - 90,
            distance=distance,
            hash_value=None,
            **default_dict
        )

        self.z_pos = z_pos
        self.radius = radius

    def find_points(self):
        self.points = [(0, self.z_pos)]
