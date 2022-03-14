from typing import Optional, Tuple

import numpy as np

from paramak import ExtrudeMixedShape, ExtrudeStraightShape


class ToroidalFieldCoil(ExtrudeMixedShape):
    """Toroidal field coil based on Princeton-D curve

    Args:
        thickness: magnet thickness (cm)
        distance: extrusion distance (cm)
        number_of_coils: the number of tf coils. This changes by the
            azimuth_placement_angle dividing up 360 degrees by the number of
            coils.
        vertical_displacement: vertical displacement (cm). Defaults to 0.0.
        with_inner_leg: Include the inner tf leg. Defaults to True.
        azimuth_start_angle: The azimuth angle to for the first TF coil which
            offsets the placement of coils around the azimuthal angle
        rotation_angle: rotation angle of solid created. A cut is performed
            from rotation_angle to 360 degrees. Defaults to 360.0.
    """

    def __init__(
        self,
        thickness: float,
        distance: float,
        number_of_coils: int,
        vertical_displacement: float = 0.0,
        with_inner_leg: bool = True,
        azimuth_start_angle: float = 0,
        rotation_angle: float = 360.0,
        color: Tuple[float, float, float, Optional[float]] = (0.0, 0.0, 1.0),
        **kwargs
    ) -> None:

        super().__init__(distance=distance, color=color, **kwargs)

        self.thickness = thickness
        self.distance = distance
        self.number_of_coils = number_of_coils
        self.vertical_displacement = vertical_displacement
        self.with_inner_leg = with_inner_leg
        self.azimuth_start_angle = azimuth_start_angle
        self.rotation_angle = rotation_angle
        self.inner_leg_connection_points = None

    @property
    def azimuth_placement_angle(self):
        self.find_azimuth_placement_angle()
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        self._azimuth_placement_angle = value

    def find_azimuth_placement_angle(self):
        """Calculates the azimuth placement angles based on the number of tf
        coils"""

        angles = list(
            np.linspace(
                self.azimuth_start_angle,
                360 + self.azimuth_start_angle,
                self.number_of_coils,
                endpoint=False,
            )
        )

        self.azimuth_placement_angle = angles

    def create_solid(self):
        """Creates a 3d solid using points with straight edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """

        if self.with_inner_leg:
            outer_leg = ExtrudeMixedShape(
                name=self.name,
                points=self.points,
                distance=self.distance,
                azimuth_placement_angle=self.azimuth_placement_angle,
                color=self.color,
                rotation_angle=self.rotation_angle,
            )
            inner_leg = ExtrudeStraightShape(
                name=self.name,
                points=self.inner_leg_connection_points,
                distance=self.distance,
                azimuth_placement_angle=self.azimuth_placement_angle,
                color=self.color,
                rotation_angle=self.rotation_angle,
                union=[outer_leg],
            )
            solids = inner_leg.solid
        else:
            outer_leg = ExtrudeMixedShape(
                name=self.name,
                points=self.points,
                distance=self.distance,
                azimuth_placement_angle=self.azimuth_placement_angle,
                color=self.color,
                rotation_angle=self.rotation_angle,
            )
            solids = outer_leg.solid

        # TODO check the wires are made correctly
        # self.wire = wires

        self.solid = solids
        return solids
