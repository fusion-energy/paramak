from collections import Iterable

import cadquery as cq

from paramak import Shape


class RotateMixedShape(Shape):
    """Rotates a 3d CadQuery solid from points connected with a mixture of
    straight lines and splines.

    Args:
        rotation_angle (float, optional): The rotation_angle to use when
            revolving the solid (degrees). Defaults to 360.0.
        stp_filename (str, optional):  Defaults to "RotateMixedShape.stp".
        stl_filename (str, optional):  Defaults to "RotateMixedShape.stl".
    """

    def __init__(
        self,
        rotation_angle=360.0,
        stp_filename="RotateMixedShape.stp",
        stl_filename="RotateMixedShape.stl",
        **kwargs
    ):

        super().__init__(
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )
        self.rotation_angle = rotation_angle

    @property
    def rotation_angle(self):
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        self._rotation_angle = value

    def create_solid(self):
        """Creates a rotated 3d solid using points with straight and spline edges.

           Returns:
              A CadQuery solid: A 3D solid volume
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

        solid = solid.close().revolve(self.rotation_angle)

        solid = self.rotate_solid(solid)
        solid = self.perform_boolean_operations(solid)

        return solid
