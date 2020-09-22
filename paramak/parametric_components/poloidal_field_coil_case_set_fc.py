
import cadquery as cq
from paramak import RotateStraightShape, PoloidalFieldCoilSet


class PoloidalFieldCoilCaseSetFC(RotateStraightShape):
    """Creates a series of rectangular poloidal field coils.

    Args:
        pf_coils (PoloidalFieldCoil object): a list of pf coil objects or a CadQuery compound object
        casing_thicknesses (list of floats): the thicknesses of the coil casing (cm).

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
        pf_coils,
        casing_thicknesses,
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

        self.pf_coils = pf_coils
        self.casing_thicknesses = casing_thicknesses

        self.find_points()

    @property
    def solid(self):
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
    def center_points(self, center_points):
        self._center_points = center_points

    @property
    def heights(self):
        return self._heights

    @heights.setter
    def heights(self, heights):
        self._heights = heights

    @property
    def widths(self):
        return self._widths

    @widths.setter
    def widths(self, widths):
        self._widths = widths

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the 2D
        profile of the poloidal field coil shape."""

        all_points = []

        if isinstance(self.pf_coils, list):
            self.heights = [entry.height for entry in self.pf_coils]
            self.widths = [entry.width for entry in self.pf_coils]
            self.center_points = [
                entry.center_point for entry in self.pf_coils]
            if len(self.pf_coils) != len(self.casing_thicknesses):
                raise ValueError(
                    "The number of pf_coils should be the same as the number of casing_thickness")
        elif isinstance(self.pf_coils, PoloidalFieldCoilSet):
            self.heights = self.pf_coils.heights
            self.widths = self.pf_coils.widths
            self.center_points = self.pf_coils.center_points
            if len(
                    self.pf_coils.solid.Solids()) != len(
                    self.casing_thicknesses):
                raise ValueError(
                    "The number of pf_coils should be the same as the number of casing_thickness")
        else:
            raise ValueError(
                "PoloidalFieldCoilCaseSetFC.pf_coils must be either a list paramak.PoloidalFieldCoil \
                        or a paramak.PoloidalFieldCoilSet object")

        for height, width, center_point, casing_thickness in zip(
                self.heights, self.widths, self.center_points, self.casing_thicknesses):

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
                (
                    center_point[0] + width / 2.0,
                    center_point[1] + height / 2.0,
                ),  # upper right
                (
                    center_point[0] + (casing_thickness + width / 2.0),
                    center_point[1] + (casing_thickness + height / 2.0),
                ),
                (
                    center_point[0] + (casing_thickness + width / 2.0),
                    center_point[1] - (casing_thickness + height / 2.0),
                ),
                (
                    center_point[0] - (casing_thickness + width / 2.0),
                    center_point[1] - (casing_thickness + height / 2.0),
                ),
                (
                    center_point[0] - (casing_thickness + width / 2.0),
                    center_point[1] + (casing_thickness + height / 2.0),
                ),
                (
                    center_point[0] + (casing_thickness + width / 2.0),
                    center_point[1] + (casing_thickness + height / 2.0),
                )
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
        for p1, p2, p3, p4, p5, p6, p7, p8, p9, p10 in zip(
                iter_points, iter_points, iter_points, iter_points,
                iter_points, iter_points, iter_points, iter_points,
                iter_points, iter_points,
        ):

            solid = (
                cq.Workplane(self.workplane)
                .polyline([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10])
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
