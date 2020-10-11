from paramak import \
    RotateStraightShape, ExtrudeCircleShape, \
    ExtrudeStraightShape, PortCutterRotated


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
        stp_filename="CenterColumnShieldCylinder.stp",
        stl_filename="CenterColumnShieldCylinder.stl",
        material_tag="center_column_shield_mat",
        **kwargs
    ):

        super().__init__(
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.height = height
        self.inner_radius = inner_radius
        self.thickness = thickness

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
        thickness = self.thickness
        inner_radius = self.inner_radius
        height = self.height

        inner_points = [
            (0, height / 2),
            (inner_radius, height / 2),
            (inner_radius, -height / 2),
            (0, -height / 2),
        ]

        outer_points = [
            (0, height / 2 + thickness),
            (inner_radius + thickness, height / 2 + thickness),
            (inner_radius + thickness, -(height / 2 + thickness)),
            (0, -(height / 2 + thickness)),
        ]
        self.points = inner_points + outer_points[::-1]
