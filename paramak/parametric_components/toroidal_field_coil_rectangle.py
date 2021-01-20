
from typing import Optional, Tuple
import cadquery as cq
import numpy as np
from paramak import ExtrudeStraightShape
from paramak.utils import calculate_wedge_cut


class ToroidalFieldCoilRectangle(ExtrudeStraightShape):
    """Creates a rectangular shaped toroidal field coil.

    Args:
        horizontal_start_point: the (x,z) coordinates of the inner upper
            point (cm).
        vertical_mid_point: the (x,z) coordinates of the mid point of the
            vertical section (cm).
        thickness: the thickness of the toroidal field coil.
        distance: the extrusion distance.
        number_of_coils: the number of tf coils. This changes by the
            azimuth_placement_angle dividing up 360 degrees by the number of
            coils.
        with_inner_leg: include the inner tf leg. Defaults to True.
        stp_filename: Defaults to "ToroidalFieldCoilRectangle.stp".
        stl_filename: Defaults to "ToroidalFieldCoilRectangle.stl".
        material_tag: Defaults to "outer_tf_coil_mat".
    """

    def __init__(
        self,
        horizontal_start_point: Tuple[float, float],
        vertical_mid_point: Tuple[float, float],
        thickness: float,
        distance: float,
        number_of_coils: int,
        with_inner_leg: Optional[bool] = True,
        stp_filename: Optional[str] = "ToroidalFieldCoilRectangle.stp",
        stl_filename: Optional[str] = "ToroidalFieldCoilRectangle.stl",
        material_tag: Optional[str] = "outer_tf_coil_mat",
        **kwargs
    ) -> None:

        super().__init__(
            distance=distance,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            material_tag=material_tag,
            **kwargs
        )

        self.horizontal_start_point = horizontal_start_point
        self.vertical_mid_point = vertical_mid_point
        self.thickness = thickness
        self.distance = distance
        self.number_of_coils = number_of_coils
        self.with_inner_leg = with_inner_leg

    @property
    def azimuth_placement_angle(self):
        self.find_azimuth_placement_angle()
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        self._azimuth_placement_angle = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe
        the 2D profile of the poloidal field coil shape."""

        if self.horizontal_start_point[0] >= self.vertical_mid_point[0]:
            raise ValueError(
                'horizontal_start_point x should be smaller than the \
                    vertical_mid_point x value')
        if self.vertical_mid_point[1] >= self.horizontal_start_point[1]:
            raise ValueError(
                'vertical_mid_point y value should be smaller than the \
                    horizontal_start_point y value')

        points = [
            self.horizontal_start_point,  # connection point
            # connection point
            (self.horizontal_start_point[0] +
             self.thickness, self.horizontal_start_point[1]),
            (self.vertical_mid_point[0], self.horizontal_start_point[1]),
            (self.vertical_mid_point[0], -self.horizontal_start_point[1]),
            # connection point
            (self.horizontal_start_point[0] +
             self.thickness, -
             self.horizontal_start_point[1]),
            # connection point
            (self.horizontal_start_point[0], -self.horizontal_start_point[1]),
            (self.horizontal_start_point[0], -
             (self.horizontal_start_point[1] +
                self.thickness)),
            (self.vertical_mid_point[0] +
             self.thickness, -
             (self.horizontal_start_point[1] +
                self.thickness)),
            (self.vertical_mid_point[0] + self.thickness,
             self.horizontal_start_point[1] + self.thickness),
            (self.horizontal_start_point[0],
             self.horizontal_start_point[1] + self.thickness),
        ]

        self.inner_leg_connection_points = [
            points[0], points[1], points[4], points[5]]

        self.points = points

    def find_azimuth_placement_angle(self):
        """Calculates the azimuth placement angles based on the number of tf
        coils"""

        angles = list(
            np.linspace(
                0,
                360,
                self.number_of_coils,
                endpoint=False))

        self.azimuth_placement_angle = angles

    def create_solid(self):
        """Creates a 3d solid using points with straight edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """

        # Creates a cadquery solid from points and revolves
        points_without_connections = [p[:2] for p in self.points]
        solid = (
            cq.Workplane(self.workplane)
            .polyline(points_without_connections)
            .close()
            .extrude(distance=-self.distance / 2.0, both=True)
        )

        if self.with_inner_leg is True:
            inner_leg_solid = cq.Workplane(self.workplane)
            inner_leg_solid = inner_leg_solid.polyline(
                self.inner_leg_connection_points)
            inner_leg_solid = inner_leg_solid.close().extrude(
                distance=-self.distance / 2.0, both=True)

            solid = cq.Compound.makeCompound(
                [a.val() for a in [inner_leg_solid, solid]]
            )

        solid = self.rotate_solid(solid)
        cutting_wedge = calculate_wedge_cut(self)
        solid = self.perform_boolean_operations(solid, wedge_cut=cutting_wedge)
        self.solid = solid   # not necessarily required as set in boolean_operations

        return solid
