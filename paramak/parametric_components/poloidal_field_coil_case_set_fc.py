
import cadquery as cq
from paramak import RotateStraightShape, PoloidalFieldCoilSet

from paramak.utils import get_hash


class PoloidalFieldCoilCaseSetFC(RotateStraightShape):
    """Creates a series of rectangular poloidal field coils.

    Args:
        pf_coils (paramak.PoloidalFieldCoil): a list of pf coil objects or a
            CadQuery compound object
        casing_thicknesses (list of floats): the thicknesses of the coil
            casing (cm).
        stp_filename (str, optional): defaults to "PoloidalFieldCoil.stp".
        stl_filename (str, optional): defaults to "PoloidalFieldCoil.stl".
        name (str, optional): defaults to "pf_coil".
        material_tag (str, optional): defaults to "pf_coil_mat".
    """

    def __init__(
        self,
        pf_coils,
        casing_thicknesses,
        stp_filename="PoloidalFieldCoil.stp",
        stl_filename="PoloidalFieldCoil.stl",
        name="pf_coil",
        material_tag="pf_coil_mat",
        **kwargs
    ):

        super().__init__(
            name=name,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.pf_coils = pf_coils
        self.casing_thicknesses = casing_thicknesses

    @property
    def solid(self):
        if get_hash(self) != self.hash_value:
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
        """Finds the XZ points joined by straight connections that describe
        the 2D profile of the poloidal field coil shape."""

        all_points = []

        if isinstance(self.pf_coils, list):
            self.heights = [entry.height for entry in self.pf_coils]
            self.widths = [entry.width for entry in self.pf_coils]
            self.center_points = [
                entry.center_point for entry in self.pf_coils]
            if len(self.pf_coils) != len(self.casing_thicknesses):
                raise ValueError(
                    "The number of pf_coils should be the same as the number \
                    of casing_thickness")
        elif isinstance(self.pf_coils, PoloidalFieldCoilSet):
            self.heights = self.pf_coils.heights
            self.widths = self.pf_coils.widths
            self.center_points = self.pf_coils.center_points
            if len(
                    self.pf_coils.solid.Solids()) != len(
                    self.casing_thicknesses):
                raise ValueError(
                    "The number of pf_coils should be the same as the number \
                    of casing_thickness")
        else:
            raise ValueError(
                "PoloidalFieldCoilCaseSetFC.pf_coils must be either a list \
                paramak.PoloidalFieldCoil or a \
                paramak.PoloidalFieldCoilSet object")

        for height, width, center_point, casing_thickness in zip(
                self.heights, self.widths,
                self.center_points, self.casing_thicknesses):

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
        """Creates a 3d solid using points with straight edges. Individual
        solids in the compound can be accessed using .Solids()[i] where i is an
        int

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
                .polyline(
                    [p1[:2], p2[:2], p3[:2], p4[:2], p5[:2], p6[:2],
                     p7[:2], p8[:2], p9[:2], p10[:2]])
                .close()
                .revolve(self.rotation_angle)
            )
            pf_coils_set.append(solid)

        compound = cq.Compound.makeCompound(
            [a.val() for a in pf_coils_set]
        )

        self.solid = compound

        # Calculate hash value for current solid
        self.hash_value = get_hash(self)

        return compound
