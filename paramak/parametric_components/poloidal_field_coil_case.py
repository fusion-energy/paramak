
from typing import Optional, Tuple

import cadquery as cq
from paramak import RotateStraightShape


class PoloidalFieldCoilCase(RotateStraightShape):
    """Creates a casing for a rectangular coil from inputs that
    describe the existing coil and the thickness of the casing required.

    Args:
        coil_height: the vertical (z axis) height of the coil (cm).
        coil_width: the horizontal (x axis) width of the coil (cm).
        center_point: the center of the coil (x,z) values (cm).
        casing_thickness: the thickness of the coil casing (cm).
        split: controls whether the pf coil casing is split horizontally into
            two sections. Defaults to False.
        stp_filename: defaults to "PoloidalFieldCoilCase.stp".
        stl_filename: defaults to "PoloidalFieldCoilCase.stl".
        material_tag: defaults to "pf_coil_case_mat".
    """

    def __init__(
        self,
        casing_thickness: Tuple[float, float],
        coil_height: float,
        coil_width: float,
        center_point: Tuple[float, float],
        split: Optional[bool] = False,
        stp_filename: Optional[str] = "PoloidalFieldCoilCase.stp",
        stl_filename: Optional[str] = "PoloidalFieldCoilCase.stl",
        material_tag: Optional[str] = "pf_coil_case_mat",
        color: Optional[Tuple[int, int, int]] = (1., 1., 0.498),
        **kwargs
    ) -> None:

        super().__init__(
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            color=color,
            **kwargs
        )

        self.center_point = center_point
        self.height = coil_height
        self.width = coil_width
        self.casing_thickness = casing_thickness
        self.split = split

    @property
    def center_point(self):
        return self._center_point

    @center_point.setter
    def center_point(self, value):
        self._center_point = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        self._width = width

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe
        the 2D profile of the poloidal field coil case shape."""

        inner_top_right = (  
            self.center_point[0] + self.width / 2.0,
            self.center_point[1] + self.height / 2.0
        )
        inner_mid_right = (
            self.center_point[0] + self.width / 2.0,
            self.center_point[1]
        )
        inner_bottom_right = (  
            self.center_point[0] + self.width / 2.0,
            self.center_point[1] - self.height / 2.0
        )
        inner_bottom_left = (
            self.center_point[0] - self.width / 2.0,
            self.center_point[1] - self.height / 2.0
        )
        inner_mid_left = (
            self.center_point[0] - self.width / 2.0,
            self.center_point[1]
        )
        inner_top_left = (
            self.center_point[0] - self.width / 2.0,
            self.center_point[1] + self.height / 2.0
        )        
        outer_top_right = (
            self.center_point[0] + self.width / 2.0 + self.casing_thickness,
            self.center_point[1] + self.height / 2.0 + self.casing_thickness
        )
        outer_mid_right = (
            self.center_point[0] + self.width / 2.0 + self.casing_thickness, 
            self.center_point[1]
        )
        outer_bottom_right = (
            self.center_point[0] + self.width / 2.0 + self.casing_thickness,
            self.center_point[1] - self.height / 2.0 - self.casing_thickness
        )
        outer_bottom_left = (
            self.center_point[0] - self.width / 2.0 - self.casing_thickness,
            self.center_point[1] - self.height / 2.0 - self.casing_thickness
        )
        outer_mid_left = (
            self.center_point[0] - self.width / 2.0 - self.casing_thickness,
            self.center_point[1]
        )
        outer_top_left = (
            self.center_point[0] - self.width / 2.0 - self.casing_thickness,
            self.center_point[1] + self.height / 2.0 + self.casing_thickness
        )

        top_points = [
            inner_top_right, inner_mid_right, outer_mid_right, outer_top_right,
            outer_top_left, outer_mid_left, inner_mid_left, inner_top_left
        ]

        bottom_points = [
            inner_bottom_right, inner_mid_right, outer_mid_right, 
            outer_bottom_right, outer_bottom_left, outer_mid_left,
            inner_mid_left, inner_bottom_left
        ]

        unsplit_points = [
            inner_top_right, inner_bottom_right, inner_bottom_left,
            inner_top_left, inner_top_right, outer_top_right,
            outer_bottom_right, outer_bottom_left, outer_top_left,
            outer_top_right
        ]

        if self.split == False:
            self.points = unsplit_points
        
        else:
            self.points = top_points + bottom_points
            self._bottom_points = bottom_points
            self._top_points = top_points
    
    def create_solid(self):
        """Creates a 3d solid using points with straight edges.

           Returns:
              A CadQuery solid: A 3D solid volume
        """

        all_points = self.points

        if self.split == True:
            wires = []
            casings = []
            for points in (self._top_points, self._bottom_points):
                solid = (
                    cq.Workplane(self.workplane)
                    .polyline([i[:2] for i in points])
                )
                wire = solid.close()
                wires.append(wire)
                solid = wire.revolve(self.rotation_angle)
                casings.append(solid)
            compound = cq.Compound.makeCompound(
                [a.val() for a in casings]
            )

        elif self.split == False:
            solid = (
                cq.Workplane(self.workplane)
                .polyline([i[:2] for i in all_points])
            )
            wires = solid.close()
            compound = wires.revolve(self.rotation_angle)

        self.wire = wires
        self.solid = compound

        return compound
