
from typing import Optional

import cadquery as cq
from paramak import RotateStraightShape


class VacuumVesselInnerLeg(RotateStraightShape):
    """A cylindrical vessel volume with constant thickness.

    Arguments:
        inner_height: height of the vessel.
        inner_radius: the inner radius of the vessel.
        inner_leg_radius: the inner radius of the inner leg.
        thickness: thickness of the vessel
        stp_filename: defaults to "CenterColumnShieldCylinder.stp".
        stl_filename: defaults to "CenterColumnShieldCylinder.stl".
        material_tag: defaults to "center_column_shield_mat".
    """

    def __init__(
        self,
        inner_height: float,
        inner_radius: float,
        inner_leg_radius: float,
        thickness: float,
        stp_filename: Optional[float] = "CenterColumnShieldCylinder.stp",
        stl_filename: Optional[float] = "CenterColumnShieldCylinder.stl",
        material_tag: Optional[float] = "center_column_shield_mat",
        **kwargs
    ):
        self.inner_height = inner_height
        self.inner_radius = inner_radius
        self.inner_leg_radius = inner_leg_radius
        self.thickness = thickness
        super().__init__(
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

    @property
    def inner_height(self):
        return self._inner_height

    @inner_height.setter
    def inner_height(self, value):
        if not isinstance(value, (float, int)):
            raise ValueError(
                'VacuumVesselInnerLeg.inner_height must be a number. Not', value)
        if value <= 0:
            raise ValueError(
                'VacuumVesselInnerLeg.inner_height must be a positive number above 0. Not',
                value)
        self._inner_height = value

    @property
    def inner_radius(self):
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, value):
        if not isinstance(value, (float, int)):
            raise ValueError(
                'VacuumVesselInnerLeg.inner_radius must be a number. Not', value)
        if value <= 0:
            raise ValueError(
                'VacuumVesselInnerLeg.inner_radius must be a positive number above 0. Not',
                value)
        self._inner_radius = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe the
            2D profile of the vessel shape."""
        thickness = self.thickness
        inner_radius = self.inner_radius
        inner_height = self.inner_height
        inner_leg_radius = self.inner_leg_radius

        point_1 = (inner_leg_radius + 2 * thickness +
                   inner_radius, thickness + (inner_height / 2.))
        point_2 = (0, thickness + (inner_height / 2.))
        point_3 = (0, -(thickness + (inner_height / 2.)))
        point_4 = (inner_leg_radius + 2 * thickness +
                   inner_radius, -(thickness + (inner_height / 2)))

        point_5 = (
            inner_leg_radius +
            thickness +
            inner_radius,
            inner_height /
            2)
        point_6 = (inner_leg_radius + thickness, inner_height / 2)
        point_7 = (inner_leg_radius + thickness, -inner_height / 2)
        point_8 = (inner_leg_radius + thickness +
                   inner_radius, -inner_height / 2)

        points_9 = (inner_leg_radius, thickness + inner_height / 2)
        points_10 = (inner_leg_radius, -(thickness + inner_height / 2))

        self.points = [
            point_1, point_2, point_3, point_4, point_5, point_6, point_7,
            point_8, points_9, points_10
        ]

    def create_solid(self):
        """Creates a 3d solid using points with straight edges. Individual
        solids in the compound can be accessed using .Solids()[i] where i is an
        int

           Returns:
              A CadQuery solid: A 3D solid volume
        """

        local_points = []
        for point in self.points:
            local_points.append((point[0], point[1]))

        big_wire = (
            cq.Workplane(self.workplane)
            .polyline(local_points[:4])
        ).close()

        small_wire = (
            cq.Workplane(self.workplane)
            .polyline(local_points[4:8])  # list of points has 10 entries
        ).close()

        inner_wire = (
            cq.Workplane(self.workplane)
            .polyline(
                [
                    local_points[1],
                    local_points[2],
                    local_points[9],
                    local_points[8]
                ]
            )
        ).close()

        inner_solid = inner_wire.revolve(self.rotation_angle)
        big_solid = big_wire.revolve(self.rotation_angle)
        small_solid = small_wire.revolve(self.rotation_angle)

        solid = big_solid.cut(small_solid).cut(inner_solid)

        self.wire = [big_wire, small_wire]

        self.solid = solid

        return solid
