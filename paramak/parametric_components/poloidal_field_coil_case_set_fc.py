
from typing import Optional, Tuple

import cadquery as cq
from paramak import PoloidalFieldCoilSet, RotateStraightShape


class PoloidalFieldCoilCaseSetFC(RotateStraightShape):
    """Creates a series of rectangular poloidal field coils.

    Args:
        pf_coils (paramak.PoloidalFieldCoil): a list of pf coil objects or a
            CadQuery compound object
        casing_thicknesses (float or list of floats): the thicknesses of the
            coil casing (cm). If float then the same thickness is applied to
            all coils. If list of floats then each entry is applied to a
            seperate pf_coil, one entry for each pf_coil.
        stp_filename (str, optional): defaults to "PoloidalFieldCoilCaseSetFC.stp".
        stl_filename (str, optional): defaults to "PoloidalFieldCoilCaseSetFC.stl".
        name (str, optional): defaults to "pf_coil_case_set_fc".
        material_tag (str, optional): defaults to "pf_coil_mat".
    """

    def __init__(
        self,
        pf_coils,
        casing_thicknesses,
        stp_filename="PoloidalFieldCoilCaseSetFC.stp",
        stl_filename="PoloidalFieldCoilCaseSetFC.stl",
        name="pf_coil_case_set_fc",
        material_tag="pf_coil_mat",
        color: Optional[Tuple[int, int, int]] = (1., 1., 0.498),
        **kwargs
    ):

        super().__init__(
            name=name,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            color=color,
            **kwargs
        )

        self.casing_thicknesses = casing_thicknesses
        self.pf_coils = pf_coils

        # calculated internally by the class
        self.heights = None
        self.widths = None
        self.center_points = None

    @property
    def casing_thicknesses(self):
        return self._casing_thicknesses

    @casing_thicknesses.setter
    def casing_thicknesses(self, value):
        if isinstance(value, list):
            if not all(isinstance(x, (int, float)) for x in value):
                raise ValueError(
                    "Every entry in Casing_thicknesses must be a float or int")
        else:
            if not isinstance(value, (float, int)):
                raise ValueError(
                    "Casing_thicknesses must be a list of numbers or a number")
        self._casing_thicknesses = value

    @property
    def pf_coils(self):
        return self._pf_coils

    @pf_coils.setter
    def pf_coils(self, value):
        if not isinstance(value, (list, PoloidalFieldCoilSet)):
            raise ValueError(
                "PoloidalFieldCoilCaseSetFC.pf_coils must be either a list \
                paramak.PoloidalFieldCoil or a \
                paramak.PoloidalFieldCoilSet object")
        self._pf_coils = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe
        the 2D profile of the poloidal field coil shape."""

        if isinstance(self.pf_coils, list):
            self.heights = [entry.height for entry in self.pf_coils]
            self.widths = [entry.width for entry in self.pf_coils]
            self.center_points = [
                entry.center_point for entry in self.pf_coils]

            num_of_coils = len(self.pf_coils)

        elif isinstance(self.pf_coils, PoloidalFieldCoilSet):
            self.heights = self.pf_coils.heights
            self.widths = self.pf_coils.widths
            self.center_points = self.pf_coils.center_points
            num_of_coils = len(self.pf_coils.solid.Solids())

        if isinstance(self.casing_thicknesses, list):
            if len(self.casing_thicknesses) != num_of_coils:
                raise ValueError(
                    "The number pf_coils is not equal to the "
                    "number of thichnesses provided. "
                    "casing_thicknesses=",
                    self.casing_thicknesses,
                    "num_of_coils=",
                    num_of_coils)
            casing_thicknesses_list = self.casing_thicknesses
        else:
            casing_thicknesses_list = [self.casing_thicknesses] * num_of_coils

        all_points = []

        for height, width, center_point, casing_thickness in zip(
                self.heights, self.widths,
                self.center_points, casing_thicknesses_list):

            if casing_thickness != 0:

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
        wires = []
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
            )

            wire = solid.close()

            wires.append(wire)

            solid = wire.revolve(self.rotation_angle)

            pf_coils_set.append(solid)

        compound = cq.Compound.makeCompound(
            [a.val() for a in pf_coils_set]
        )

        self.wire = wires

        self.solid = compound

        return compound
