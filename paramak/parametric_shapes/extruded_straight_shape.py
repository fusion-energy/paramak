
from collections import Iterable

import cadquery as cq

from paramak import Shape


class ExtrudeStraightShape(Shape):
    """Extrudes a 3d CadQuery solid from points connected with straight lines

    Args:
        distance (float): the extrusion distance to use (cm units if used for
            neutronics)
        extrude_both (bool, optional): if set to True, the extrusion will
            occur in both directions. Defaults to True.
        solid (cadquery.Workplane, optional): [description]. Defaults to None.
        stp_filename (str, optional): Defaults to "ExtrudeStraightShape.stp".
        stl_filename (str, optional): Defaults to "ExtrudeStraightShape.stl".
    """

    def __init__(
        self,
        distance,
        solid=None,
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
        self.solid = solid
        self.extrude_both = extrude_both

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value

    def create_solid(self):
        """Creates a 3d solid using points with straight connections
        edges, azimuth_placement_angle and rotation_angle.

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

        self.perform_boolean_operations(solid)

        return solid
