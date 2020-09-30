from paramak import RotateStraightShape


class CuttingWedgeFS(RotateStraightShape):
    """Creates a wedge from a Shape than can be useful for cutting sector models.

    Args:
        shape (float): a paramak.Shape object that is used to find the
            height and radius of the wedge

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
        union (CadQuery object): An optional CadQuery object to perform a boolean
            union with this object.
        tet_mesh (str): Insert description.
        physical_groups (type): Insert description.

    Returns:
        a paramak shape object: A shape object that has generic functionality
        with points determined by the find_points() method. A CadQuery solid of
        the shape can be called via shape.solid.
    """

    def __init__(
        self,
        shape,
        name=None,
        color=(0.5, 0.5, 0.5),
        stp_filename="CuttingWedgeFS.stp",
        stl_filename="CuttingWedgeFS.stl",
        rotation_angle=180,
        material_tag="cutting_slice_mat",
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

        self.shape = shape

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, value):
        self._shape = value

    def find_points(self):

        if self.shape.rotation_angle == 360:
            raise ValueError(
                'rotation angle = 360, cutting slice cannot be defined')

        else:
            max_dimension = self.shape.solid.largestDimension()

            points = [
                (0, max_dimension),
                (max_dimension, max_dimension),
                (max_dimension, -max_dimension),
                (0, -max_dimension)
            ]

            rotation_angle = 360 - self.shape.rotation_angle
            azimuth_placement_angle = 360 - self.shape.rotation_angle

        self.points = points
        self.rotation_angle = rotation_angle
        self.azimuth_placement_angle = azimuth_placement_angle
