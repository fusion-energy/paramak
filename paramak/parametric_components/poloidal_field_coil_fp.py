from paramak import PoloidalFieldCoil


class PoloidalFieldCoilFP(PoloidalFieldCoil):
    """Creates a rectangular poloidal field coil.

    Args:
        corner_points (list of float tuples): the coordinates of the oppersite
            corners of the rectangular shaped coil e.g [(x1, y1), (x2, y2)]

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
        corner_points,
        rotation_angle=360,
        stp_filename="PoloidalFieldCoil.stp",
        stl_filename="PoloidalFieldCoil.stl",
        color=(0.5, 0.5, 0.5),
        azimuth_placement_angle=0,
        name="pf_coil",
        material_tag="pf_coil_mat",
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

        height = abs(corner_points[0][1]-corner_points[1][1])
        width = abs(corner_points[0][0]-corner_points[1][0])

        center_width = (corner_points[0][1]+corner_points[1][1])/2.
        center_height = (corner_points[0][1]+corner_points[1][1])/2.
        center_point = (center_width, center_height)

        super().__init__(
            height=height,
            width=width,
            center_point=center_point,
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

        self.corner_points = corner_points


    @property
    def corner_points(self):
        return self._corner_points

    @corner_points.setter
    def corner_points(self, value):
        # ToDo check the corner points are a list with two entries
        # and each entry is a tuple with two floats
        self._corner_points = value
