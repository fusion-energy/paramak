from typing import Iterable, Optional, Tuple, Union

import cadquery as cq
from paramak import RotateStraightShape


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
            separate pf_coil, one entry for each pf_coil.
        center_points (tuple of floats): the center of the coil (x,z) values
            (cm).
        name (str, optional): defaults to "pf_coil_case_set".
    """

    def __init__(
        self,
        heights: Iterable[float],
        widths: Iterable[float],
        casing_thicknesses: Iterable[float],
        center_points: Iterable[float],
        name: str = "pf_coil_case_set",
        color: Tuple[float, float, float, Optional[float]] = (1.0, 1.0, 0.498),
        **kwargs
    ):

        super().__init__(name=name, color=color, **kwargs)

        self.center_points = center_points
        self.heights = heights
        self.widths = widths
        self.casing_thicknesses = casing_thicknesses

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
    def casing_thicknesses(self, value: Union[Iterable[float], float]):
        if isinstance(value, list):
            if not all(isinstance(x, (int, float)) for x in value):
                raise ValueError("Every entry in Casing_thicknesses must be a float or int")
        else:
            if not isinstance(value, (float, int)):
                raise ValueError("Casing_thicknesses must be a list of numbers or a number")
        self._casing_thicknesses = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe
        the 2D profile of the poloidal field coil shape."""

        all_points = []

        if isinstance(self.casing_thicknesses, list):
            casing_thicknesses_list = self.casing_thicknesses
        else:
            casing_thicknesses_list = [self.casing_thicknesses] * len(self.widths)

        if not len(self.heights) == len(self.widths) == len(self.center_points) == len(casing_thicknesses_list):
            raise ValueError("The number of heights, widths, center_points and " "casing_thicknesses must be equal")

        for height, width, center_point, casing_thickness in zip(
            self.heights, self.widths, self.center_points, casing_thicknesses_list
        ):

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
                    ),
                ]

        self.points = all_points

    def create_solid(self):
        """Creates a 3d solid using points with straight edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """

        iter_points = iter(self.points)
        pf_coils_set = []
        wires = []
        for p1, p2, p3, p4, p5, p6, p7, p8, p9, p10 in zip(
            iter_points,
            iter_points,
            iter_points,
            iter_points,
            iter_points,
            iter_points,
            iter_points,
            iter_points,
            iter_points,
            iter_points,
        ):

            # creates a small box that surrounds the geometry
            inner_box = RotateStraightShape(
                points=[p1, p2, p3, p4],
                rotation_axis=self.rotation_axis,
                rotation_angle=360,  # full rotated
                azimuth_placement_angle=self.azimuth_placement_angle,
                workplane=self.workplane,
                cut=self.cut,
                intersect=self.intersect,
                union=self.union,
            )

            outer_box = RotateStraightShape(
                points=[p7, p8, p9, p10],
                rotation_axis=self.rotation_axis,
                rotation_angle=self.rotation_angle,
                azimuth_placement_angle=self.azimuth_placement_angle,
                workplane=self.workplane,
                cut=self.cut,
                intersect=self.intersect,
                union=self.union,
            )

            # subtracts the two boxes to leave a hollow box
            new_shape = outer_box.solid.cut(inner_box.solid)

            # makes wires for the inside and outside loops
            wire = (
                cq.Workplane(self.workplane)
                .polyline(
                    [
                        p1[:2],
                        p2[:2],
                        p3[:2],
                        p4[:2],
                        p5[:2],
                    ]
                )
                .close()
            )

            wires.append(wire)

            wire = (
                cq.Workplane(self.workplane)
                .polyline(
                    [
                        p6[:2],
                        p7[:2],
                        p8[:2],
                        p9[:2],
                        p10[:2],
                    ]
                )
                .close()
            )

            wires.append(wire)

            pf_coils_set.append(new_shape)

        compound = cq.Compound.makeCompound([a.val() for a in pf_coils_set])

        self.wire = wires

        self.solid = compound

        return compound
