from collections import Iterable

import cadquery as cq

from paramak import Shape
from paramak.utils import calculate_wedge_cut


class ExtrudeMixedShape(Shape):
    """Extrudes a 3d CadQuery solid from points connected with a mixture of
    straight and spline connections.

    Args:
        distance (float): the extrusion distance to use (cm units if used for
            neutronics)
        extrude_both (bool, optional): If set to True, the extrusion will
            occur in both directions. Defaults to True.
        rotation_angle (float, optional): rotation angle of solid created. A
            cut is performed from rotation_angle to 360 degrees. Defaults to
            360.0.
        stp_filename (str, optional): Defaults to "ExtrudeMixedShape.stp".
        stl_filename (str, optional): Defaults to "ExtrudeMixedShape.stl".

    """

    def __init__(
        self,
        distance,
        extrude_both=True,
        rotation_angle=360.0,
        stp_filename="ExtrudeMixedShape.stp",
        stl_filename="ExtrudeMixedShape.stl",
        **kwargs
    ):

        super().__init__(
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )
        self.distance = distance
        self.extrude_both = extrude_both
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
        """Creates an extruded 3d solid using points connected with straight
        and spline edges.

        :return: a 3d solid volume
        :rtype: a cadquery solid
        """

        # obtains the first two values of the points list
        XZ_points = [(p[0], p[1]) for p in self.points]

        # obtains the last values of the points list
        connections = [p[2] for p in self.points[:-1]]

        current_linetype = connections[0]
        current_points_list = []
        instructions = []
        # groups together common connection types
        for i, c in enumerate(connections):
            if c == current_linetype:
                current_points_list.append(XZ_points[i])
            else:
                current_points_list.append(XZ_points[i])
                instructions.append({current_linetype: current_points_list})
                current_linetype = c
                current_points_list = [XZ_points[i]]
        instructions.append({current_linetype: current_points_list})

        if list(instructions[-1].values())[0][-1] != XZ_points[0]:
            keyname = list(instructions[-1].keys())[0]
            instructions[-1][keyname].append(XZ_points[0])

        solid = cq.Workplane(self.workplane)
        solid.moveTo(XZ_points[0][0], XZ_points[0][1])

        for entry in instructions:
            if list(entry.keys())[0] == "spline":
                solid = solid.spline(listOfXYTuple=list(entry.values())[0])
            if list(entry.keys())[0] == "straight":
                solid = solid.polyline(list(entry.values())[0])
            if list(entry.keys())[0] == "circle":
                p0 = list(entry.values())[0][0]
                p1 = list(entry.values())[0][1]
                p2 = list(entry.values())[0][2]
                solid = solid.moveTo(p0[0], p0[1]).threePointArc(p1, p2)

        # performs extrude in both directions, hence distance / 2
        solid = solid.close().extrude(
            distance=-self.distance / 2.0,
            both=self.extrude_both)

        solid = self.rotate_solid(solid)
        calculate_wedge_cut(self)
        self.perform_boolean_operations(solid)

        return solid
