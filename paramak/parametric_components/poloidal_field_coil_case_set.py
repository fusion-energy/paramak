
from typing import Optional, Tuple

import cadquery as cq
from paramak import RotateStraightShape, PoloidalFieldCoilCase


class PoloidalFieldCoilCaseSet(RotateStraightShape):
    """Creates a series of rectangular poloidal field coils.

    Args:
        heights (list of floats): the vertical (z axis) heights of the coil
            (cm).
        widths (list of floats): the horizontal (x axis) widths of the coil
            (cm).
        casing_thicknesses (float or list of floats): the thicknesses of the
            coil casing (cm). If float then the same thickness is applied to
            all coils. If list of floats then each entry is applied to a
            seperate pf_coil, one entry for each pf_coil.
        center_points (tuple of floats): the center of the coil (x,z) values
            (cm).
        stp_filename (str, optional): defaults to "PoloidalFieldCoilCaseSet.stp".
        stl_filename (str, optional): defaults to "PoloidalFieldCoilCaseSet.stl".
        name (str, optional): defaults to "pf_coil_case_set".
        material_tag (str, optional): defaults to "pf_coil_case_mat".
    """

    def __init__(
        self,
        heights,
        widths,
        casing_thicknesses,
        center_points,
        split=False,
        stp_filename="PoloidalFieldCoilCaseSet.stp",
        stl_filename="PoloidalFieldCoilCaseSet.stl",
        name="pf_coil_case_set",
        material_tag="pf_coil_case_mat",
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

        self.center_points = center_points
        self.heights = heights
        self.widths = widths
        self.casing_thicknesses = casing_thicknesses
        self.split = split

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

    def create_solid(self):

        if isinstance(self.casing_thicknesses, list):
            casing_thicknesses_list = self.casing_thicknesses
        else:
            casing_thicknesses_list = [
                self.casing_thicknesses] * len(self.widths)

        if not len(
            self.heights) == len(
            self.widths) == len(
                self.center_points) == len(casing_thicknesses_list):
            raise ValueError(
                "The number of heights, widths, center_points and "
                "casing_thicknesses must be equal")

        cases = []
        wires = []

        for height, width, center_point, casing_thickness in zip(
            self.heights, self.widths, 
            self.center_points, casing_thicknesses_list):

            case = PoloidalFieldCoilCase(
                coil_height = height,
                coil_width = width,
                center_point = center_point,
                casing_thickness = casing_thickness,
                split = self.split,
                rotation_angle = self.rotation_angle
            )
            cases.append(case.solid)
            wires.append(case.wire)

        if self.split == True:
            compound = cq.Compound.makeCompound(
                [a for a in cases]
            )
        elif self.split == False:
            compound = cq.Compound.makeCompound(
                [a.val() for a in cases]
            )

        self.solid = compound
        self.wire = wires

        return compound
