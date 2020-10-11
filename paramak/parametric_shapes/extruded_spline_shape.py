from collections import Iterable

import cadquery as cq

from paramak import Shape


class ExtrudeSplineShape(Shape):
    """Extrudes a 3d CadQuery solid from points connected with spline connections

    Args:
        distance (float): the extrusion distance to use (cm units if used for neutronics)
        extrude_both (bool): if set to True, the extrusion will occur in both
            directions. Defaults to True.
        Others: see paramak.Shape() arguments.

    Returns:
        a paramak shape object: a Shape object that has generic functionality
    """

    def __init__(
        self,
        distance,
        stp_filename="ExtrudeSplineShape.stp",
        stl_filename="ExtrudeSplineShape.stl",
        solid=None,
        **kwargs
    ):

        super().__init__(
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.distance = distance
        self.solid = solid

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value

    def create_solid(self):
        """Creates a 3d solid using points with spline
           edges, azimuth_placement_angle and distance.

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

        self.perform_boolean_operations(solid)

        return solid
