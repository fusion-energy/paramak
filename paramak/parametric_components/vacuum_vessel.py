from paramak import \
    RotateStraightShape, ExtrudeCircleShape, ExtrudeStraightShape


class VacuumVessel(RotateStraightShape):
    """A cylindrical vessel volume with constant thickness.

    Arguments:
        height (float): height of the vessel.
        inner_radius (float): the inner radius of the vessel.
        thickness (float): thickness of the vessel

    Keyword Args:
        workplane (str): The orientation of the CadQuery workplane. Options are
            XY, YZ or XZ.
        intersect (CadQuery object): An optional CadQuery object to perform a
            boolean intersect with this object.
        cut (CadQuery object): An optional CadQuery object to perform a boolean
            cut with this object.
        union (CadQuery object): An optional CadQuery object to perform a
            boolean union with this object.
        tet_mesh (str): Insert description.
        physical_groups (type): Insert description.

    Returns:
        a paramak shape object: A shape object that has generic functionality
        with points determined by the find_points() method. A CadQuery solid
        of the shape can be called via shape.solid.
    """

    def __init__(
        self,
        height,
        inner_radius,
        thickness,
        circular_ports=[],
        rectangular_ports=[],
        name=None,
        color=(0.5, 0.5, 0.5),
        stp_filename="CenterColumnShieldCylinder.stp",
        stl_filename="CenterColumnShieldCylinder.stl",
        rotation_angle=360,
        material_tag="center_column_shield_mat",
        azimuth_placement_angle=0,
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
            name=name,
            color=color,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            azimuth_placement_angle=azimuth_placement_angle,
            rotation_angle=rotation_angle,
            hash_value=None,
            **default_dict
        )

        self.height = height
        self.inner_radius = inner_radius
        self.thickness = thickness
        self.circular_ports = circular_ports
        self.rectangular_ports = rectangular_ports
        self.add_ports()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, inner_radius):
        self._inner_radius = inner_radius

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the
            2D profile of the vessel shape."""

        inner_points = [
            (0, self.height / 2),
            (self.inner_radius, self.height / 2),
            (self.inner_radius, -self.height / 2),
            (0, -self.height / 2),
        ]

        outer_points = [
            (0, self.height / 2 + self.thickness),
            (self.inner_radius + self.thickness, self.height / 2 + self.thickness),
            (self.inner_radius + self.thickness, -(self.height / 2 + self.thickness)),
            (0, -(self.height / 2 + self.thickness)),
        ]
        self.points = inner_points + outer_points[::-1]

    def add_ports(self):
        cutter_shapes = []
        safety_factor = 2
        # circular ports
        for port in self.circular_ports:
            port_z_pos, placement_angle, radius = port
            shape = ExtrudeCircleShape(
                points=[(0, port_z_pos)],
                distance=2*(self.inner_radius+self.thickness*safety_factor),
                radius=radius,
                azimuth_placement_angle=placement_angle - 90,
                extrude_both=False)
            cutter_shapes.append(shape)

        # rectangular ports
        for port in self.rectangular_ports:
            port_z_pos, placement_angle, port_width, port_height = port[:4]
            points = [
                (-port_width/2, -port_height/2),
                (port_width/2, -port_height/2),
                (port_width/2, port_height/2),
                (-port_width/2, port_height/2),
            ]
            points = [(e[0], e[1] + port_z_pos) for e in points]
            shape = ExtrudeStraightShape(
                points=points,
                distance=2*(self.inner_radius+self.thickness*safety_factor),
                azimuth_placement_angle=placement_angle - 90,
                extrude_both=False
                )

            # add fillet
            if len(port) == 5:
                shape.solid = shape.solid.edges('#Z').fillet(port[4])
            shape.export_stp("cutter.stp")
            cutter_shapes.append(shape)

        self.cut = cutter_shapes
