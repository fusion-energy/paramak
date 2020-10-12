
from paramak import ExtrudeStraightShape


class PortCutterRectangular(ExtrudeStraightShape):
    """Creates a extruded shape with a rectangular section that is used to cut
    other components (eg. blanket, vessel,..) in order to create ports.

    Args:
        z_pos (float): Z position (cm) of the port
        height (float): height (cm) of the port
        width (float): width (cm) of the port
        distance (float): extruded distance (cm) of the cutter
        fillet_radius (float, optional): If not None, radius (cm) of fillets
            added to edges orthogonal to the Z direction. Defaults to None.
        azimuth_placement_angle (float or iterable of floats): The angle or
            angles to use when rotating the shape on the azimuthal axis.
            Defaults to 0.0.
        stp_filename (str, optional): The filename used when saving stp files
            as part of a reactor. Defaults to "PortCutterRectangular.stp".
        stl_filename (str, optional): The filename used when saving stl files
            as part of a reactor. Defaults to "PortCutterRectangular.stl".
        color (tuple, optional): (sequences of 3 or 4 floats each in the range
            0-1): the color to  use when exporting as html graphs or png
            images. Defaults to (0.5, 0.5, 0.5).
        azimuth_placement_angle (int, optional): [description]. Defaults to 0.
        name (str, optional): the legend name used when exporting a html graph
            of the shape. Defaults to "rectangular_port_cutter".
        material_tag (str, optional): The material name to use when exporting
            the neutronics description. Defaults to
            "rectangular_port_cutter_mat".

    """
    def __init__(
        self,
        z_pos,
        height,
        width,
        distance,
        fillet_radius=None,
        stp_filename="PortCutterRectangular.stp",
        stl_filename="PortCutterRectangular.stl",
        color=(0.5, 0.5, 0.5),
        azimuth_placement_angle=0.0,
        name="rectangular_port_cutter",
        material_tag="rectangular_port_cutter_mat",
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
            extrude_both=False,
            name=name,
            color=color,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            azimuth_placement_angle=azimuth_placement_angle-90,
            distance=distance,
            hash_value=None,
            **default_dict
        )

        self.z_pos = z_pos
        self.height = height
        self.width = width
        self.fillet_radius = fillet_radius
        self.add_fillet()

    def find_points(self):
        points = [
            (-self.width/2, -self.height/2),
            (self.width/2, -self.height/2),
            (self.width/2, self.height/2),
            (-self.width/2, self.height/2),
        ]
        points = [(e[0], e[1] + self.z_pos) for e in points]
        self.points = points

    def add_fillet(self):
        if self.fillet_radius is not None and self.fillet_radius != 0:
            self.solid = self.solid.edges('#Z').fillet(self.fillet_radius)
