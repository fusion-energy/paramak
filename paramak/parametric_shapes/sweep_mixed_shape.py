from collections import Iterable

import cadquery as cq

from paramak import Shape


class SweepMixedShape(Shape):
    """Sweeps a 2D shape created from points connected with straight, spline or circle
    connections along a defined spline path to create a 3D CadQuery solid.

    Args:
        points (list of tuples each containing X (float), Z (float), connection): A list
            of XY, YZ or XZ coordinates connected by straight connections which define
            the 2D shape to be swept. The coordinates are defined with respect to origins
            at the first and last points of the spline path.
        path_points (list of tuples each containing X (float), Z (float)): A list of XY,
            YZ or XZ coordinates connected by spline connections which define the path
            along which the 2D shape is swept.
        workplane (str): Workplane in which the 2D shape to be swept is defined. Defaults
            to "XY".
        path_workplane (str): Workplane in which the spline path is defined. Defaults to
            "XZ".
        stp_filename (str, optional): Defaults to "SweepMixedShape.stp".
        stl_filename (str, optional): Defaults to "SweepMixedShape.stl".
    """

    def __init__(
        self,
        path_points,
        workplane="XY",
        path_workplane="XZ",
        stp_filename="SweepMixedShape.stp",
        stl_filename="SweepMixedShape.stl",
        **kwargs
    ):

        super().__init__(
            workplane=workplane,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.path_points = path_points
        self.path_workplane = path_workplane

    @property
    def path_points(self):
        return self._path_points

    @path_points.setter
    def path_points(self, value):
        self._path_points = value

    @property
    def path_workplane(self):
        return self._path_workplane

    @path_workplane.setter
    def path_workplane(self, value):
        if value[0] != self.workplane[0]:
            raise ValueError(
                "workplane and path_workplane must start with the same letter"
            )
        elif value == self.workplane:
            raise ValueError(
                "workplane and path_workplane must be different"
            )
        else:
            self._path_workplane = value

    def create_solid(self):
        """Creates a swept 3D solid from a 2D shape with mixed connections.

        Returns:
            A CadQuery solid: A 3D solid volume
        """

        path = cq.Workplane(self.path_workplane).spline(self.path_points)
        distance = float(self.path_points[-1][1] - self.path_points[0][1])

        if self.workplane in ["XZ", "YX", "ZY"]:
            distance *= -1

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

        solid = cq.Workplane(
            self.workplane).workplane(
            offset=self.path_points[0][1]).moveTo(
            self.path_points[0][0],
            0).workplane()

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

        solid = solid.close().moveTo(-self.path_points[0][0], 0).workplane(
            offset=distance).moveTo(self.path_points[-1][0], 0).workplane()

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

        solid = solid.close().sweep(path, multisection=True)

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
                (0, 0, 1), (0, 0, -1), self.azimuth_placement_angle)

        self.perform_boolean_operations(solid)

        return solid
