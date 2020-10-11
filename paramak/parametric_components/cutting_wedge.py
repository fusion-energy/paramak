from paramak import RotateStraightShape


class CuttingWedge(RotateStraightShape):
    """Creates a wedge from height, radius and rotation angle agruements than
    can be useful for cutting sector models.

    Args:
        height (float): the vertical (z axis) height of the coil (cm).
        radius (float): the horizontal (x axis) width of the coil (cm).

    Keyword Args:
        name (str): the legend name used when exporting a html graph of the
            shape.
        color (sequences of 3 or 4 floats each in the range 0-1): the color to
            use when exporting as html graphs or png images.
        material_tag (str): The material name to use when exporting the
            neutronics description.
        stp_filename (str): The filename used when saving stp files as part of a
            reactor.
        azimuth_placement_angle (float or iterable of floats): The angle or
            angles to use when rotating the shape on the azimuthal axis.
        rotation_angle (float): The rotation angle to use when revolving the
            solid (degrees).
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
        with points determined by the find_points() method. A CadQuery solid of
        the shape can be called via shape.solid.
    """

    def __init__(
        self,
        height,
        radius,
        stp_filename="CuttingWedge.stp",
        stl_filename="CuttingWedge.stl",
        rotation_angle=180,
        material_tag="cutting_slice_mat",
        **kwargs
    ):

        super().__init__(
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            rotation_angle=rotation_angle,
            hash_value=None,
            **kwargs
        )

        self.height = height
        self.radius = radius

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    def find_points(self):

        points = [
            (0, self.height / 2),
            (self.radius, self.height / 2),
            (self.radius, -self.height / 2),
            (0, -self.height / 2)
        ]

        self.points = points
