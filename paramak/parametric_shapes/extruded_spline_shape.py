from collections import Iterable

import cadquery as cq

from paramak import Shape
from paramak.utils import calculate_wedge_cut


class ExtrudeSplineShape(Shape):
    """Extrudes a 3d CadQuery solid from points connected with spline
    connections.

    Args:
        distance (float): the extrusion distance to use (cm units if used for
            neutronics).
        rotation_angle (float): rotation angle of solid created. a cut is performed
            from rotation_angle to 360 degrees. Defaults to 360.
        stp_filename (str, optional): Defaults to "ExtrudeSplineShape.stp".
        stl_filename (str, optional): Defaults to "ExtrudeSplineShape.stl".
    """

    def __init__(
        self,
        distance,
        rotation_angle=360,
        stp_filename="ExtrudeSplineShape.stp",
        stl_filename="ExtrudeSplineShape.stl",
        **kwargs
    ):

        super().__init__(
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.distance = distance
        self.rotation_angle = rotation_angle

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
        """Creates an extruded 3d solid using points connected with spline
        edges.

        :return: a 3d solid volume
        :rtype: a cadquery solid
        """

        # Creates a cadquery solid from points and extrudes
        solid = (
            cq.Workplane(self.workplane)
            .spline(self.points)
            .close()
            .extrude(distance=-1 * self.distance / 2.0, both=True)
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
