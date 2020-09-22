
import cadquery as cq
from paramak import RotateStraightShape


class PoloidalFieldCoilSet(RotateStraightShape):
    """Creates a series of rectangular poloidal field coils.

    Args:
        heights (float): the vertical (z axis) heights of the coil (cm).
        widths (float): the horizontal (x axis) widths of the coil (cm).
        center_points (tuple of floats): the center of the coil (x,z) values (cm).

    Keyword Args:
        name (str): the legend name used when exporting a html graph of the shape.
        color (sequences of 3 or 4 floats each in the range 0-1): the color to use when
            exportin as html graphs or png images.
        material_tag (str): The material name to use when exporting the neutronics description.
        stp_filename (str): The filename used when saving stp files as part of a reactor.
        azimuth_placement_angle (float or iterable of floats): The angle or angles to use when
            rotating the shape on the azimuthal axis.
        rotation_angle (float): The rotation angle to use when revolving the solid (degrees).
        workplane (str): The orientation of the CadQuery workplane. Options are XY, YZ or XZ.
        intersect (CadQuery object): An optional CadQuery object to perform a boolean intersect with
            this object.
        cut (CadQuery object): An optional CadQuery object to perform a boolean cut with this object.
        union (CadQuery object): An optional CadQuery object to perform a boolean union with this object.
        tet_mesh (str): Insert description.
        physical_groups (type): Insert description.

    Returns:
        a paramak shape object: A shape object that has generic functionality with points determined by the find_points() method. A CadQuery solid of the shape can be called via shape.solid.
    """

    def __init__(
        self,
        heights,
        widths,
        center_points,
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

        self.center_points = center_points
        self.heights = heights
        self.widths = widths

        if len(
            self.widths) != len(
            self.heights) or len(
            self.heights) != len(
                self.center_points):
            raise ValueError("The length of widthts, height and center_points \
                must be the same when making a PoloidalFieldCoilSet")

        self.find_points()

    @property
    def solid(self):
        """Returns a CadQuery compound object consisting of 1 or more 3d volumes"""
        if self.get_hash() != self.hash_value:
            self.create_solid()
        return self._solid

    @solid.setter
    def solid(self, value):
        self._solid = value

    @property
    def center_points(self):
        return self._center_points

    @center_points.setter
    def center_points(self, value):
        if not isinstance(value, list):
            raise ValueError(
                "PoloidalFieldCoilSet center_points must be a list")
        self._center_points = value

    @property
    def heights(self):
        return self._heights

    @heights.setter
    def heights(self, value):
        if not isinstance(value, list):
            raise ValueError("PoloidalFieldCoilSet heights must be a list")
        self._heights = value

    @property
    def widths(self):
        return self._widths

    @widths.setter
    def widths(self, value):
        if not isinstance(value, list):
            raise ValueError("PoloidalFieldCoilSet widths must be a list")
        self._widths = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the 2D
        profile of the poloidal field coil shape."""

        all_points = []

        for height, width, center_point in zip(
                self.heights, self.widths, self.center_points):

            all_points = all_points + [
                (
                    center_point[0] + width / 2.0,
                    center_point[1] + height / 2.0,
                ),  # upper right
                (
                    center_point[0] + width / 2.0,
                    center_point[1] - height / 2.0,
                ),  # lower right
                (
                    center_point[0] - width / 2.0,
                    center_point[1] - height / 2.0,
                ),  # lower left
                (
                    center_point[0] - width / 2.0,
                    center_point[1] + height / 2.0,
                ),  # upper left
            ]

        self.points = all_points

    def create_solid(self):
        """Creates a 3d solid using points with straight connections
           edges, azimuth_placement_angle and rotation angle.
           individual solids in the compound can be accessed using .Solids()[i] where i is an int
           Returns:
              A CadQuery solid: A 3D solid volume
        """

        iter_points = iter(self.points)
        pf_coils_set = []
        for p1, p2, p3, p4 in zip(
                iter_points, iter_points, iter_points, iter_points):

            solid = (
                cq.Workplane(self.workplane)
                .polyline([p1, p2, p3, p4])
                .close()
                .revolve(self.rotation_angle)
            )
            pf_coils_set.append(solid)

        compound = cq.Compound.makeCompound(
            [a.val() for a in pf_coils_set]
        )

        self.solid = compound

        # Calculate hash value for current solid
        self.hash_value = self.get_hash()

        return compound
