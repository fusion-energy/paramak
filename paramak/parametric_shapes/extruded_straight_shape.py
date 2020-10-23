
from collections import Iterable

import cadquery as cq

from paramak import Shape
from paramak.utils import calculate_wedge_cut


class ExtrudeStraightShape(Shape):
    """Extrudes a 3d CadQuery solid from points connected with straight lines.

    Args:
        distance (float): the extrusion distance to use (cm units if used for
            neutronics).
        rotation_angle (float): rotation angle of solid created. a cut is performed
            from rotation_angle to 360 degrees. Defaults to 360.
        extrude_both (bool, optional): if set to True, the extrusion will
            occur in both directions. Defaults to True.
        stp_filename (str, optional): Defaults to "ExtrudeStraightShape.stp".
        stl_filename (str, optional): Defaults to "ExtrudeStraightShape.stl".
    """

    def __init__(
        self,
        distance,
        rotation_angle=360,
        extrude_both=True,
        stp_filename="ExtrudeStraightShape.stp",
        stl_filename="ExtrudeStraightShape.stl",
        **kwargs
    ):

        super().__init__(
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.distance = distance
        self.rotation_angle = rotation_angle
        self.extrude_both = extrude_both

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value

    @property
    def rotation_angle(self):
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        self._rotation_angle = value

    def create_solid(self):
        """Creates an extruded 3d solid using points connected with straight
        edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """

        # Creates a cadquery solid from points and revolves
        solid = (
            cq.Workplane(self.workplane)
            .polyline(self.points)
            .close()
            .extrude(distance=-self.distance / 2.0, both=self.extrude_both)
        )

        # Checks if the azimuth_placement_angle is a list of angles
        if isinstance(self.azimuth_placement_angle, Iterable):
            rotated_solids = []
            # Perform seperate rotations for each angle
            for angle in self.azimuth_placement_angle:
                rotated_solids.append(
                    solid.rotate(
                        (0, 0, -1), (0, 0, 1), angle))
            solid = cq.Workplane(self.workplane)

            # Joins the seperate solids together
            for i in rotated_solids:
                solid = solid.union(i)
        else:
            # Peform rotations for a single azimuth_placement_angle angle
            solid = solid.rotate(
                (0, 0, -1), (0, 0, 1), self.azimuth_placement_angle)

        calculate_wedge_cut(self)
        self.perform_boolean_operations(solid)

        return solid
