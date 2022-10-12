import numbers
from collections.abc import Iterable
from pathlib import Path
from typing import List, Optional, Tuple, Union

import matplotlib.pyplot as plt
from cadquery import Assembly, Color, Compound, Plane, Workplane, exporters, importers
from cadquery.occ_impl import shapes
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

import paramak
from paramak.utils import (
    _replace,
    cut_solid,
    facet_wire,
    get_hash,
    intersect_solid,
    union_solid,
    get_largest_dimension,
    get_bounding_box,
    export_solids_to_brep,
    export_solids_to_dagmc_h5m,
)


class Shape:
    """A shape object that represents a 3d volume and can have materials and
    neutronics tallies assigned. Shape objects are not intended to be used
    directly by the user but provide basic functionality for user-facing
    classes that inherit from Shape. Provides a .show attribute for rendering
    in Jupyter Lab

    Args:
        points (tuple of (float, float, float), optional): the x, y, z
            coordinates of points that make up the shape. Defaults to None.
        connection_type (str, optional): The type of connection between points.
            Possible values are "straight", "circle", "spline", "mixed".
            Defaults to "mixed".
        name (str, optional): the name of the shape, used in the graph legend
            by export_html. Defaults to None.
        color ((float, float, float [, float]), optional): The color to use
            when exporting as html graphs or png images. Can be in RGB or RGBA
            format with floats between 0 and 1. Defaults to (0.5, 0.5, 0.5).
        azimuth_placement_angle (iterable of floats or float, optional): the
            azimuth angle(s) used when positioning the shape. If a list of
            angles is provided, the shape is duplicated at all angles.
            Defaults to 0.0.
        workplane: the orientation of the Cadquery workplane. Options include
            strings "XY", "YZ", "XZ" or a Cadquery.Plane(). Defaults to "XZ".
        rotation_axis (str or list, optional): rotation axis around which the
            solid is rotated. If None, the rotation axis will depend on the
            workplane or path_workplane if applicable. Can be set to "X", "-Y",
            "Z", etc. A custom axis can be set by setting a list of two XYZ
            floats. Defaults to None.
        cut (paramak.shape or list, optional): If set, the current solid will
            be cut with the provided solid or iterable in cut. Defaults to
            None.
        intersect (paramak.shape or list, optional): If set, the current solid
            will be interested with the provided solid or iterable of solids.
            Defaults to None.
        union (paramak.shape or list, optional): If set, the current solid
            will be united with the provided solid or iterable of solids.
            Defaults to None.
        graveyard_size: The dimension of cube shaped the graveyard region used
            by DAGMC. This attribute is used preferentially over
            graveyard_offset.
        graveyard_offset: The distance between the graveyard and the largest
            shape. If graveyard_size is set the this is ignored.
    """

    def __init__(
        self,
        points: Union[tuple, list] = None,
        connection_type: Optional[str] = "mixed",
        name: Optional[str] = None,
        color: Tuple[float, float, float, Optional[float]] = (0.5, 0.5, 0.5),
        azimuth_placement_angle: Optional[Union[float, List[float]]] = 0.0,
        workplane: Optional[Union[str, Plane]] = "XZ",
        rotation_axis: Optional[str] = None,
        # TODO defining Shape types as paramak.Shape results in circular import
        cut=None,
        intersect=None,
        union=None,
        graveyard_size: Optional[float] = 20_000,
        graveyard_offset: Optional[float] = None,
    ):

        self.connection_type = connection_type
        self.points = points
        self.color = color
        self.name = name

        self.cut = cut
        self.intersect = intersect
        self.union = union

        self.azimuth_placement_angle = azimuth_placement_angle
        self.workplane = workplane
        self.rotation_axis = rotation_axis

        # initialise to something different than self.points
        # old_points is used in the processed_points getter
        self.old_points = 0

        # neutronics specific properties
        self.graveyard_offset = graveyard_offset
        self.graveyard_size = graveyard_size

        # properties calculated internally by the class
        self.solid = None
        self.wire = None
        self.render_mesh = None

        # set here but only used by Sweep shapes
        self.path_points = None
        self.force_cross_section = None

        # set here but only used by Extrude shapes
        self.extrusion_start_offset = None

        self.processed_points = None
        # self.volume = None
        self.hash_value = None
        self.points_hash_value = None
        self.x_min = None
        self.x_max = None
        self.z_min = None
        self.z_max = None
        self.graveyard_offset = None  # set by the make_graveyard method
        self.patch = None

    @property
    def graveyard_size(self):
        return self._graveyard_size

    @graveyard_size.setter
    def graveyard_size(self, value):
        if value is None:
            self._graveyard_size = None
        elif not isinstance(value, (float, int)):
            raise TypeError("graveyard_size must be a number")
        elif value < 0:
            raise ValueError("graveyard_size must be positive")
        self._graveyard_size = value

    @property
    def graveyard_offset(self):
        return self._graveyard_offset

    @graveyard_offset.setter
    def graveyard_offset(self, value):
        if value is None:
            self._graveyard_offset = None
        elif not isinstance(value, (float, int)):
            raise TypeError("graveyard_offset must be a number")
        elif value < 0:
            raise ValueError("graveyard_offset must be positive")
        self._graveyard_offset = value

    @property
    def solid(self):
        """The CadQuery solid of the 3d object. Returns a CadQuery workplane
        or CadQuery Compound"""

        ignored_keys = ["_solid", "_hash_value"]
        if get_hash(self, ignored_keys) != self.hash_value:
            self.create_solid()
            self.hash_value = get_hash(self, ignored_keys)

        return self._solid

    @solid.setter
    def solid(self, value):
        self._solid = value

    @property
    def wire(self):
        """The CadQuery wire of the 3d object. Returns a CadQuery workplane
        or CadQuery Compound"""

        ignored_keys = ["_wire", "_solid", "_hash_value"]
        if get_hash(self, ignored_keys) != self.hash_value:
            self.create_solid()
            self.hash_value = get_hash(self, ignored_keys)

        return self._wire

    @wire.setter
    def wire(self, value):
        self._wire = value

    @property
    def cut(self):
        return self._cut

    @cut.setter
    def cut(self, value):
        self._cut = value

    @property
    def intersect(self):
        return self._intersect

    @intersect.setter
    def intersect(self, value):
        self._intersect = value

    @property
    def union(self):
        return self._union

    @union.setter
    def union(self, value):
        self._union = value

    @property
    def largest_dimension(self) -> float:
        """Calculates a bounding box for the Reactor and returns the largest
        absolute value of the largest dimension of the bounding box"""

        return get_largest_dimension(self.solid)

    @largest_dimension.setter
    def largest_dimension(self, value):
        self._largest_dimension = value

    @property
    def bounding_box(self):
        """Calculates a bounding box for the Shape and returns the coordinates of
        the corners lower-left and upper-right. This function is useful when
        creating OpenMC mesh tallies as the bounding box is required in this form"""

        return get_bounding_box(self.solid)

    @bounding_box.setter
    def bounding_box(self, value):
        self._bounding_box = value

    @property
    def workplane(self):
        return self._workplane

    @workplane.setter
    def workplane(self, value):
        if isinstance(value, Plane):
            self._workplane = value
        elif isinstance(value, str):
            acceptable_values = ["XY", "YZ", "XZ", "YX", "ZY", "ZX"]
            if value in acceptable_values:
                self._workplane = value
            else:
                raise ValueError("Shape.workplane must be one of ", acceptable_values, " not ", value)
        else:
            raise TypeError("Shape.workplane must be a string or a ", "cadquery.Plane object")

    @property
    def rotation_axis(self):
        return self._rotation_axis

    @rotation_axis.setter
    def rotation_axis(self, value):
        if isinstance(value, str):
            acceptable_values = ["X", "Y", "Z", "-X", "-Y", "-Z", "+X", "+Y", "+Z"]
            if value not in acceptable_values:
                msg = "Shape.rotation_axis must be one of " + " ".join(acceptable_values) + " not " + value
                raise ValueError(msg)
        elif isinstance(value, Iterable):
            msg = "Shape.rotation_axis must be a tuple of three floats (X, Y, Z)"
            if len(value) != 2:
                raise ValueError(msg)
            for point in value:
                if not isinstance(point, Iterable):
                    msg = f"Shape.rotation_axis must be an iterable of iterables, not {type(point)}"
                    raise ValueError(msg)
                if len(point) != 3:
                    msg = f"Shape.rotation_axis must be an iterable of iterables with 3 entries, not {len(point)}"
                    raise ValueError(msg)
                for val in point:
                    if not isinstance(val, (int, float)):
                        msg = (
                            "Shape.rotation_axis should be an iterable of "
                            "iterables where the nested iterables are "
                            f"numerical, not {type(val)}"
                        )
                        raise ValueError(msg)

            if value[0] == value[1]:
                msg = "The two coordinates points for rotation_axis must be different"
                raise ValueError(msg)
        elif value is not None:
            msg = "Shape.rotation_axis must be an iterable or a string or None"
            raise ValueError(msg)
        self._rotation_axis = value

    @property
    def area(self):
        """Get the total surface area of the Shape. Returns a float"""
        if isinstance(self.solid, Compound):
            return self.solid.Area()

        return self.solid.val().Area()

    @property
    def areas(self):
        """Get the surface areas of the Shape. Compound shapes provide a
        separate area value for each entry. Returns a list of floats"""
        all_areas = []
        if isinstance(self.solid, Compound):
            for face in self.solid.Faces():
                all_areas.append(face.Area())
            return all_areas

        for face in self.solid.val().Faces():
            all_areas.append(face.Area())
        return all_areas

    @property
    def hash_value(self):
        return self._hash_value

    @hash_value.setter
    def hash_value(self, value):
        self._hash_value = value

    @property
    def points_hash_value(self):
        return self._points_hash_value

    @points_hash_value.setter
    def points_hash_value(self, value):
        self._points_hash_value = value

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if isinstance(value, (list, tuple)):
            if len(value) in [3, 4]:
                for i in value:
                    if not isinstance(i, (int, float)):
                        raise ValueError("Individual entries in the Shape.color must a " "number (float or int)")
                    if i > 1 or i < 0:
                        raise ValueError("Individual entries in the Shape.color must be " "between 0 and 1")
            else:
                raise ValueError("Shape.color must be a list or tuple of 3 or 4 floats")
        else:
            raise ValueError("Shape.color must be a list or tuple")

        self._color = value

    @property
    def name(self):
        """The name of the Shape, used to identify Shapes when exporting_html"""
        return self._name

    @name.setter
    def name(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Shape.name must be a string", value)
        self._name = value

    @property
    def processed_points(self):
        """Shape.processed_points attributes is set internally from the
        Shape.points"""

        if self.points is not None:
            # if .points have changed since last time this was run
            if self.old_points != self.points:
                # assign current .points value to .old_points
                self.old_points = self.points

                # compute .processed_points
                if self.connection_type == "mixed":
                    values = self.points
                else:
                    values = [(*p, self.connection_type) for p in self.points]

                if values[0][:2] != values[-1][:2]:
                    values.append(values[0])

                self._processed_points = values
            return self._processed_points
        return None

    @processed_points.setter
    def processed_points(self, value):
        self._processed_points = value

    @property
    def points(self):
        """Sets the Shape.point attributes.

        Args:
            points (a tuple of tuples): tuple of points that create the
                shape

        Raises:
            incorrect type: only list of lists or tuples are accepted
        """
        ignored_keys = ["_points", "_points_hash_value"]
        if self.find_points() and self.points_hash_value != get_hash(self, ignored_keys):
            self.find_points()
            self.points_hash_value = get_hash(self, ignored_keys)

        return self._points

    @points.setter
    def points(self, values_in):
        if values_in is None:
            values = values_in
        else:
            values = values_in[:]
        if values is not None:
            if not isinstance(values, (list, tuple)):
                raise ValueError("points must be a list or a tuple")

            for value in values:
                if not isinstance(value, (list, tuple)):
                    msg = f"individual points must be a tuple.{value} in of " f"type {type(value)}"
                    raise ValueError(msg)

            for counter, value in enumerate(values):
                if self.connection_type == "mixed":
                    if len(value) != 3:
                        if counter != len(values) - 1:  # last point doesn't need connections
                            msg = (
                                "individual points should contain 3 "
                                "entries when the Shape.connection_type is "
                                '"mixed". The entries should contain two '
                                f"coordinates and a connection type. {value} "
                                "has a length of {len(value)}"
                            )
                            print(values)
                            raise ValueError(msg)
                else:
                    if len(value) != 2:
                        msg = (
                            "individual points should contain 2 entries "
                            "when the Shape.connection_type is "
                            f"{self.connection_type}. The entries should "
                            f"just contain the coordinates {value} has a "
                            "length of {len(value)}"
                        )
                        raise ValueError(msg)

                # Checks that the XY points are numbers
                if not isinstance(value[0], numbers.Number):
                    msg = (
                        "The first value in the tuples that make up the "
                        "points represents the X value and must be a number "
                        f"{value}"
                    )
                    raise ValueError(msg)
                if not isinstance(value[1], numbers.Number):
                    msg = (
                        "The second value in the tuples that make up the "
                        "points represents the X value and must be a "
                        f"number {value}"
                    )
                    raise ValueError(msg)

                # Checks that only straight and spline are in the connections
                # part of points
                if len(value) == 3:
                    if value[2] not in ["straight", "spline", "circle"]:
                        msg = "individual connections must be either " '"straight", "circle" or "spline"'
                        raise ValueError(msg)

            if len(values) > 1:
                if values[0][:2] == values[-1][:2]:
                    msg = "The coordinates of the last and first points are " "the same."
                    raise ValueError(msg)

        self._points = values

    @property
    def azimuth_placement_angle(self):
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        error = False
        if isinstance(value, (int, float, Iterable)) and not isinstance(value, str):
            if isinstance(value, Iterable):
                for i in value:
                    if not isinstance(i, (int, float)):
                        error = True
        else:
            error = True

        if error:
            msg = "azimuth_placement_angle must be a float or list of floats"
            raise ValueError(msg)
        self._azimuth_placement_angle = value

    def from_stp_file(self, filename: str):
        """Loads the filename using CadQuery and populates the Shape.solid
        with the contents

        Args:
            filename: the file name of the stp / step file to be loaded
        """
        result = importers.importStep(filename)
        self.solid = result

    def show(self, **kwargs):
        """Shows / renders the CadQuery the 3d object in Jupyter Lab. Imports
        show from jupyter_cadquery and returns show(Shape.solid, kwargs)

        Args:
            kwargs: keyword arguments passed to jupyter-cadquery show()
                function. See https://github.com/bernhard-42/jupyter-cadquery#usage
                for more details on acceptable keywords

        Returns:
            jupyter_cadquery show object
        """

        try:
            from jupyter_cadquery import Part, PartGroup, show
        except ImportError:
            msg = (
                "To use Reactor.show() you must install jupyter_cadquery version "
                '3.0.0 or above. To install jupyter_cadquery type "pip install '
                'jupyter_cadquery" in the terminal'
            )
            raise ImportError(msg)

        parts = []
        if self.name is None:
            name = "Shape.name not set"
        else:
            name = self.name

        scaled_color = [int(i * 255) for i in self.color[0:3]]
        if isinstance(self.solid, (shapes.Shape, shapes.Compound)):
            for i, solid in enumerate(self.solid.Solids()):
                parts.append(Part(solid, name=f"{name}{i}", color=scaled_color, show_edges=True))
        else:
            parts.append(
                Part(
                    self.solid.val(),
                    name=f"{name}",
                    color=scaled_color,
                    show_edges=True,
                )
            )

        return show(PartGroup(parts), **kwargs)

    def create_solid(self) -> Workplane:
        solid = None
        if self.processed_points is not None:
            # obtains the first two values of the points list
            XZ_points = [(p[0], p[1]) for p in self.processed_points]

            # obtains the last values of the points list
            connections = [p[2] for p in self.processed_points[:-1]]

            current_linetype = connections[0]
            current_points_list = []
            instructions = []
            # groups together common connection types
            for i, connection in enumerate(connections):
                if connection == current_linetype:
                    current_points_list.append(XZ_points[i])
                else:
                    current_points_list.append(XZ_points[i])
                    instructions.append({current_linetype: current_points_list})
                    current_linetype = connection
                    current_points_list = [XZ_points[i]]
            instructions.append({current_linetype: current_points_list})

            if list(instructions[-1].values())[0][-1] != XZ_points[0]:
                keyname = list(instructions[-1].keys())[0]
                instructions[-1][keyname].append(XZ_points[0])

            if self.path_points:

                factor = 1
                if self.workplane in ["XZ", "YX", "ZY"]:
                    factor *= -1

                solid = Workplane(self.workplane).center(0, 0)

                if self.force_cross_section:
                    for point in self.path_points[:-1]:
                        solid = solid.workplane(offset=point[1] * factor).center(point[0], 0).workplane()
                        for entry in instructions:
                            connection_type = list(entry.keys())[0]
                            if connection_type == "spline":
                                solid = solid.spline(listOfXYTuple=list(entry.values())[0])
                            elif connection_type == "straight":
                                solid = solid.polyline(list(entry.values())[0])
                            elif connection_type == "circle":
                                p0, p1, p2 = list(entry.values())[0][:3]
                                solid = solid.moveTo(p0[0], p0[1]).threePointArc(p1, p2)
                        solid = solid.close()
                        solid = solid.center(-point[0], 0).workplane(offset=-point[1] * factor)

                elif self.force_cross_section is False:
                    solid = (
                        solid.workplane(offset=self.path_points[0][1] * factor)
                        .center(self.path_points[0][0], 0)
                        .workplane()
                    )
                    for entry in instructions:
                        connection_type = list(entry.keys())[0]
                        if connection_type == "spline":
                            solid = solid.spline(listOfXYTuple=list(entry.values())[0])
                        elif connection_type == "straight":
                            solid = solid.polyline(list(entry.values())[0])
                        elif connection_type == "circle":
                            p0 = list(entry.values())[0][0]
                            p1 = list(entry.values())[0][1]
                            p2 = list(entry.values())[0][2]
                            solid = solid.moveTo(p0[0], p0[1]).threePointArc(p1, p2)

                    solid = (
                        solid.close()
                        .center(0, 0)
                        .center(-self.path_points[0][0], 0)
                        .workplane(offset=-self.path_points[0][1] * factor)
                    )

                solid = (
                    solid.workplane(offset=self.path_points[-1][1] * factor)
                    .center(self.path_points[-1][0], 0)
                    .workplane()
                )

            else:
                # for rotate and extrude shapes
                solid = Workplane(self.workplane)
                # for extrude shapes
                if self.extrusion_start_offset:
                    extrusion_offset = -self.extrusion_start_offset
                    solid = solid.workplane(offset=extrusion_offset)

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

        return solid

    def rotate_solid(self, solid: Optional[Workplane]) -> Workplane:
        # Checks if the azimuth_placement_angle is a list of angles
        if isinstance(self.azimuth_placement_angle, Iterable):
            azimuth_placement_angles = self.azimuth_placement_angle
        else:
            azimuth_placement_angles = [self.azimuth_placement_angle]

        rotated_solids = []
        # Perform separate rotations for each angle
        for angle in azimuth_placement_angles:
            rotated_solids.append(solid.rotate(*self.get_rotation_axis()[0], angle))
        solid = Workplane(self.workplane)

        # Joins the seperate solids together
        for i in rotated_solids:
            solid = solid.union(i)
        return solid

    def get_rotation_axis(self):
        # TODO add return type hinting -> Tuple[List[Tuple[int, int, int],
        # Tuple[int, int, int]], str]
        """Returns the rotation axis for a given shape. If self.rotation_axis
        is None, the rotation axis will be computed from self.workplane (or
        from self.path_workplane if applicable). If self.rotation_axis is an
        acceptable string (eg. "X", "+Y", "-Z"...) then this axis will be used.
        If self.rotation_axis is a list of two points, then these two points
        will be used to form an axis.

        Returns:
            list, str: list of two XYZ points and the string of the axis (eg.
                "X", "Y"..)
        """
        rotation_axis = {
            "X": [(-1, 0, 0), (1, 0, 0)],
            "-X": [(1, 0, 0), (-1, 0, 0)],
            "Y": [(0, -1, 0), (0, 1, 0)],
            "-Y": [(0, 1, 0), (0, -1, 0)],
            "Z": [(0, 0, -1), (0, 0, 1)],
            "-Z": [(0, 0, 1), (0, 0, -1)],
        }
        if isinstance(self.rotation_axis, str):
            # X, Y or Z axis
            return (
                rotation_axis[self.rotation_axis.replace("+", "")],
                self.rotation_axis,
            )
        elif isinstance(self.rotation_axis, Iterable):
            # Custom axis
            return self.rotation_axis, "custom_axis"
        elif self.rotation_axis is None:
            # Axis from workplane or path_workplane
            if hasattr(self, "path_workplane"):
                # compute from path_workplane instead
                workplane = self.path_workplane
            else:
                workplane = self.workplane
            return rotation_axis[workplane[1]], workplane[1]

    def create_limits(self) -> Tuple[float, float, float, float]:
        """Finds the x,y,z limits (min and max) of the points that make up the
        face of the shape. Note the Shape may extend beyond this boundary if
        splines are used to connect points.

        Raises:
            ValueError: if no points are defined

        Returns:
            float, float, float, float, float, float: x_minimum, x_maximum,
            y_minimum, y_maximum, z_minimum, z_maximum
        """

        self.find_points()
        if self.points is None:
            raise ValueError("No points defined for", self)

        self.x_min = float(min([row[0] for row in self.points]))
        self.x_max = float(max([row[0] for row in self.points]))

        self.z_min = float(min([row[1] for row in self.points]))
        self.z_max = float(max([row[1] for row in self.points]))

        return self.x_min, self.x_max, self.z_min, self.z_max

    def find_points(self):
        """Calculates the shape points. Empty method which some components
        overright when inheritting."""
        return None

    def export_stl(
        self,
        filename: str,
        tolerance: float = 0.001,
        angular_tolerance: float = 0.1,
        verbose: bool = True,
    ) -> str:
        """Exports an stl file for the Shape.solid.

        Args:
            filename: the filename of exported the stl file. Defaults to None
                which will attempt to use the Shape.stl_filename. If both are
                None then a valueError will be raised.
            tolerance: the deflection tolerance of the faceting
            angular_tolerance: the angular tolerance, in radians
            verbose: Enables (True) or disables (False) the printing of the
                file produced.
        """

        path_filename = Path(filename)

        if path_filename.suffix != ".stl":
            msg = f"filename should end with .stl, not {path_filename.suffix}"
            raise ValueError(msg)

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        exporters.export(
            self.solid,
            str(path_filename),
            exportType="STL",
            tolerance=tolerance,
            angularTolerance=angular_tolerance,
        )

        if verbose:
            print("Saved file as ", path_filename)

        return str(path_filename)

    def export_brep(self, filename="shape.brep", include_graveyard=False) -> str:
        """Exports a brep file for the Shape. Optionally including a DAGMC
        graveyard.

        Args:
            filename: the filename of exported the brep file.
            include_graveyard: specify if the graveyard will be included or
                not. If True the the Shape.make_graveyard will be called
                using Shape.graveyard_size and Shape.graveyard_offset
                attribute values.

        Returns:
            filename of the brep created
        """

        geometry_to_save = [self.solid]

        if include_graveyard:
            self.make_graveyard()
            geometry_to_save.append(self.graveyard.solid)

        output_filename = export_solids_to_brep(
            solids=geometry_to_save,
            filename=filename,
        )

        return output_filename

    def export_dagmc_h5m(
        self,
        filename: str = "dagmc.h5m",
        min_mesh_size: float = 5,
        max_mesh_size: float = 20,
        verbose: bool = False,
        volume_atol: float = 0.000001,
        center_atol: float = 0.000001,
        bounding_box_atol: float = 0.000001,
        tags: Optional[List[str]] = None,
        include_graveyard: bool = False,
    ) -> str:
        """Export a DAGMC compatible h5m file for use in neutronics simulations.
        This method makes use of Gmsh to create a surface mesh of the geometry.
        MOAB is used to convert the meshed geometry into a h5m with parts tagged by
        using the reactor.shape_and_components.name properties. You will need
        Gmsh installed and MOAB installed to use this function. Acceptable
        tolerances may need increasing to match reactor parts with the parts
        in the intermediate Brep file produced during the process

        Args:
            filename: the filename of the DAGMC h5m file to write
            min_mesh_size: the minimum mesh element size to use in Gmsh. Passed
                into gmsh.option.setNumber("Mesh.MeshSizeMin", min_mesh_size)
            max_mesh_size: the maximum mesh element size to use in Gmsh. Passed
                into gmsh.option.setNumber("Mesh.MeshSizeMax", max_mesh_size)
            volume_atol: the absolute volume tolerance to allow when matching
                parts in the intermediate brep file with the cadquery parts
            center_atol: the absolute center coordinates tolerance to allow
                when matching parts in the intermediate brep file with the
                cadquery parts
            bounding_box_atol: the absolute volume tolerance to allow when
                matching parts in the intermediate brep file with the cadquery
                parts
            tags: the dagmc tag to use in when naming the shape in the h5m file.
                If left as None then the Shape.name will be used. This allows
                the DAGMC geometry created to be compatible with a wider range
                of neutronics codes that have specific DAGMC tag requirements.
            include_graveyard: specify if the graveyard will be included or
                not. If True the the Reactor.make_graveyard will be called
                using Reactor.graveyard_size and Reactor.graveyard_offset
                attribute values.
        """

        shapes_to_convert = [self.solid]

        if include_graveyard:
            self.make_graveyard()
            shapes_to_convert.append(self.graveyard.solid)

        if tags is None:
            tags = [self.name]
            if include_graveyard:
                tags.append(self.graveyard.name)

        output_filename = export_solids_to_dagmc_h5m(
            solids=shapes_to_convert,
            filename=filename,
            min_mesh_size=min_mesh_size,
            max_mesh_size=max_mesh_size,
            verbose=verbose,
            volume_atol=volume_atol,
            center_atol=center_atol,
            bounding_box_atol=bounding_box_atol,
            tags=tags,
        )

        return output_filename

    def export_stp(
        self,
        filename: str,
        units: Optional[str] = "mm",
        mode: Optional[str] = "solid",
        verbose: Optional[bool] = True,
    ) -> str:
        """Exports an stp file for the Shape.solid.

        Args:
            filename: the filename of exported the stp file.
            units: the units of the stp file, options are 'cm' or 'mm'.
                Default is mm.
            mode: the object to export can be either
                'solid' which exports 3D solid shapes or the 'wire' which
                exports the wire edges of the shape. Defaults to 'solid'.
            verbose: Enables (True) or disables (False) the printing of the
                file produced.
        """

        path_filename = Path(filename)

        if path_filename.suffix == ".stp" or path_filename.suffix == ".step":
            pass
        else:
            msg = f"filename should end with .stp or .step, not {path_filename.suffix}"
            raise ValueError(msg)

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        if mode == "solid":

            assembly = Assembly(name=self.name)

            if self.color is None:
                assembly.add(self.solid)
            else:
                assembly.add(self.solid, color=Color(*self.color))

            assembly.save(str(path_filename), exportType="STEP")

            # previous method does not support colours but puts the solid in the base file level
            # exporters.export(self.solid, str(path_filename), exportType='STEP')

        elif mode == "wire":
            exporters.export(self.wire, str(path_filename), exportType="STEP")
        else:
            raise ValueError(
                "The mode argument for export_stp \
                only accepts 'solid' or 'wire'",
                self,
            )

        if units == "cm":
            _replace(
                str(path_filename),
                "SI_UNIT(.MILLI.,.METRE.)",
                "SI_UNIT(.CENTI.,.METRE.)",
            )

        if verbose:
            print(f"Saved file as {path_filename}")

        return str(path_filename)

    def export_svg(
        self,
        filename: Optional[str] = "shape.svg",
        projectionDir: Tuple[float, float, float] = (-1.75, 1.1, 5),
        width: Optional[float] = 800,
        height: Optional[float] = 800,
        marginLeft: Optional[float] = 100,
        marginTop: Optional[float] = 100,
        strokeWidth: Optional[float] = None,
        strokeColor: Optional[Tuple[int, int, int]] = (0, 0, 0),
        hiddenColor: Optional[Tuple[int, int, int]] = (100, 100, 100),
        showHidden: Optional[bool] = True,
        showAxes: Optional[bool] = False,
    ) -> str:
        """Exports an svg file for the Reactor.solid. If the filename provided
        doesn't end with .svg it will be added.

        Args:
            filename: the filename of the svg file to be exported. Defaults to
                "reactor.svg".
            projectionDir: The direction vector to view the geometry from
                (x, y, z). Defaults to (-1.75, 1.1, 5)
            width: the width of the svg image produced in pixels. Defaults to
                1000
            height: the height of the svg image produced in pixels. Defaults to
                800
            marginLeft: the number of pixels between the left edge of the image
                and the start of the geometry.
            marginTop: the number of pixels between the top edge of the image
                and the start of the geometry.
            strokeWidth: the width of the lines used to draw the geometry.
                Defaults to None which automatically selects an suitable width.
            strokeColor: the color of the lines used to draw the geometry in
                RGB format with each value between 0 and 255. Defaults to
                (0, 0, 0) which is black.
            hiddenColor: the color of the lines used to draw the geometry in
                RGB format with each value between 0 and 255. Defaults to
                (100, 100, 100) which is light grey.
            showHidden: If the edges obscured by geometry should be included in
                the diagram. Defaults to True.
            showAxes: If the x, y, z axis should be included in the image.
                Defaults to False.

        Returns:
            str: the svg filename created
        """

        path_filename = Path(filename)

        if path_filename.suffix != ".svg":
            path_filename = path_filename.with_suffix(".svg")

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        opt = {
            "width": width,
            "height": height,
            "marginLeft": marginLeft,
            "marginTop": marginTop,
            "showAxes": showAxes,
            "projectionDir": projectionDir,
            "strokeColor": strokeColor,
            "hiddenColor": hiddenColor,
            "showHidden": showHidden,
        }

        if strokeWidth is not None:
            opt["strokeWidth"] = strokeWidth

        exporters.export(self.solid, str(path_filename), exportType="SVG", opt=opt)

        print("Saved file as ", path_filename)

        return str(path_filename)

    def export_html_3d(self, filename: Optional[str] = "shape_3d.html", **kwargs):
        """Saves an interactive 3d html view of the Shape to a html file.

        Args:
            filename: the filename used to save the html graph. Defaults to
                shape_3d.html
            kwargs: keyword arguments passed to jupyter-cadquery show()
                function. See https://github.com/bernhard-42/jupyter-cadquery#usage
                for more details on acceptable keywords

        Returns:
            str: filename of the created html file
        """

        view = self.show(**kwargs)

        view.export_html(filename)

        return filename

    def export_html(
        self,
        filename: str = "shape.html",
        facet_splines: bool = True,
        facet_circles: bool = True,
        tolerance: float = 1e-3,
        view_plane: Optional[str] = None,
    ):
        """Creates a html graph representation of the points and connections
        for the Shape object. Shapes are colored by their .color property.
        Shapes are also labelled by their .name. If filename provided doesn't
        end with .html then .html will be added.

        Args:
            filename: the filename used to save the html graph. Defaults to
                shape.html
            facet_splines: If True then spline edges will be faceted. Defaults
                to True.
            facet_circles: If True then circle edges will be faceted. Defaults
                to True.
            tolerance: faceting toleranceto use when faceting cirles and
                splines. Defaults to 1e-3.
            view_plane: The plane to project. Options are 'XZ', 'XY', 'YZ',
                'YX', 'ZY', 'ZX', 'RZ' and 'XYZ'. Defaults to 'RZ'. Defaults to
                the workplane of the paramak.Shape.

        Returns:
            plotly.Figure(): figure object
        """

        # if view plane is not set then use the shape workplane
        if view_plane is None:
            view_plane = self.workplane

        if self.solid is None:
            raise ValueError("No solid was found for ", self)

        if isinstance(self.solid, Workplane):
            edges = self.solid.val().Edges()
        else:
            edges = self.solid.Edges()

        fig = paramak.utils.export_wire_to_html(
            wires=edges,
            filename=None,
            view_plane=view_plane,
            facet_splines=facet_splines,
            facet_circles=facet_circles,
            tolerance=tolerance,
            title=f"coordinates of {self.__class__.__name__} shape, viewed from the {view_plane} plane",
        )

        if filename is not None:

            Path(filename).parents[0].mkdir(parents=True, exist_ok=True)

            path_filename = Path(filename)

            if path_filename.suffix != ".html":
                path_filename = path_filename.with_suffix(".html")

            fig.write_html(str(path_filename))

        return fig

    def export_2d_image(
        self,
        filename: Optional[str] = "shape.png",
        xmin: Optional[float] = 0.0,
        xmax: Optional[float] = 900.0,
        ymin: Optional[float] = -600.0,
        ymax: Optional[float] = 600.0,
    ):
        """Exports a 2d image (png) of the reactor. Components are colored by
        their Shape.color property. If filename provided doesn't end with .png
        then .png will be added.

        Args:
            filename: the filename of the saved png image.
            xmin: the minimum x value of the x axis.
                Defaults to 0..
            xmax: the maximum x value of the x axis.
                Defaults to 900..
            ymin: the minimum y value of the y axis.
                Defaults to -600..
            ymax: the maximum y value of the y axis.
                Defaults to 600..

        Returns:
            matplotlib.plt(): a plt object
        """

        fig, ax = plt.subplots()

        patch = self._create_patch()

        ax.add_collection(patch)

        ax.axis("equal")
        ax.set(xlim=(xmin, xmax), ylim=(ymin, ymax))
        ax.set_aspect("equal", "box")

        plt.savefig(filename, dpi=100)
        plt.close()
        print(
            f"\n saved 2d image to {filename}",
        )

        return plt

    def _create_patch(self):
        """Creates a matplotlib polygon patch from the Shape points. This is
        used when making 2d images of the Shape object.

        Raises:
            ValueError: No points defined for the Shape

        Returns:
            Matplotlib object patch: a plotable polygon shape
        """

        if self.processed_points is None:
            raise ValueError("No processed_points defined for", self)

        patches = []

        edges = facet_wire(wire=self.wire, facet_splines=True, facet_circles=True)

        fpoints = []
        for edge in edges:
            for vertice in edge.Vertices():
                fpoints.append((vertice.X, vertice.Z))

        polygon = Polygon(fpoints, closed=True)
        patches.append(polygon)

        patch = PatchCollection(patches)

        if self.color is not None:
            print("color is ", self.color)
            patch.set_facecolor(self.color[0:3])
            patch.set_color(self.color[0:3])
            patch.color = self.color[0:3]
            patch.edgecolor = self.color[0:3]
            # checks to see if an alpha value is provided in the color
            if len(self.color) == 4:
                patch.set_alpha = self.color[-1]
        self.patch = patch
        return patch

    def perform_boolean_operations(self, solid: Workplane, **kwargs):
        """Performs boolean cut, intersect and union operations if shapes are
        provided"""

        # If a cut solid is provided then perform a boolean cut
        if self.cut is not None:
            solid = cut_solid(solid, self.cut)

        # If a wedge cut is provided then perform a boolean cut
        # Performed independently to avoid use of self.cut
        # Prevents repetition of 'outdated' wedge cuts
        if "wedge_cut" in kwargs:
            if kwargs["wedge_cut"] is not None:
                solid = cut_solid(solid, kwargs["wedge_cut"])

        # If an intersect is provided then perform a boolean intersect
        if self.intersect is not None:
            solid = intersect_solid(solid, self.intersect)

        # If an intersect is provided then perform a boolean intersect
        if self.union is not None:
            solid = union_solid(solid, self.union)

        return solid

    def make_graveyard(
        self,
        graveyard_size: Optional[float] = None,
        graveyard_offset: Optional[float] = None,
    ):
        """Creates a graveyard volume (bounding box) that encapsulates all
        volumes. This is required by DAGMC when performing neutronics
        simulations. The graveyard size can be ascertained in two ways. Either
        the size can be set directly using the graveyard_size which is the
        quickest method. Alternativley the graveyard can be automatically sized
        to the geometry by setting a graveyard_offset value. If both options
        are set then the method will default to using the graveyard_size
        preferentially.

        Args:
            graveyard_size: directly sets the size of the graveyard. Defaults
                to None which then uses the Reactor.graveyard_size attribute.
            graveyard_offset: the offset between the largest edge of the
                geometry and inner bounding shell created. Defaults to None
                which then uses Reactor.graveyard_offset attribute.

        Returns:
            paramak.HollowCube: a shell volume that bounds the geometry,
                referred to as a graveyard in DAGMC.
        """

        if graveyard_size is not None:
            graveyard_size_to_use = graveyard_size

        elif self.graveyard_size is not None:
            graveyard_size_to_use = self.graveyard_size

        elif graveyard_offset is not None:
            self.solid
            graveyard_size_to_use = self.largest_dimension * 2 + graveyard_offset * 2

        elif self.graveyard_offset is not None:
            self.solid
            graveyard_size_to_use = self.largest_dimension * 2 + self.graveyard_offset * 2

        else:
            raise ValueError(
                "the graveyard_size, Shape.graveyard_size, "
                "graveyard_offset and Shape.graveyard_offset are all None. "
                "Please specify at least one of these attributes or arguments"
            )

        graveyard_shape = paramak.HollowCube(
            length=graveyard_size_to_use,
            name="graveyard",
        )

        self.graveyard = graveyard_shape

        return graveyard_shape

    def export_graveyard(
        self,
        filename: Optional[str] = "graveyard.stp",
        graveyard_offset: Optional[float] = 100,
    ) -> str:
        """Writes an stp file (CAD geometry) for the reactor graveyard. This
        is needed for DAGMC simulations. This method also calls
        Reactor.make_graveyard with the offset.

        Args:
            filename (str): the filename for saving the stp file
            graveyard_offset (float): the offset between the largest edge of
                the geometry and inner bounding shell created. Defaults to
                Reactor.graveyard_offset

        Returns:
            str: the stp filename created
        """

        self.make_graveyard(graveyard_offset=graveyard_offset)
        new_filename = self.graveyard.export_stp(str(Path(filename)))

        return new_filename

    def convert_all_circle_connections_to_splines(
        self, tolerance: Optional[float] = 0.1
    ) -> List[Tuple[float, float, str]]:
        """Replaces circle edges in Shape.processed_points points with spline
        edges. The spline control coordinates are obtained by faceting the
        circle edge with the provided tolerance. The Shape.processed_points
        will be updated to exclude the circle points and include the new spline
        points. This method works best when the connection before and after the
        circle is a straight connection type. This method is useful when
        converting the stp file into other formats due to errors in the
        conversion of circle edges.

        Args:
            tolerance: the precision of the faceting.

        Returns:
            The new points with spline connections
        """

        new_points = []
        counter = 0
        while counter < len(self.processed_points):

            if self.processed_points[counter][2] == "circle":
                p_0 = self.processed_points[counter][:2]
                p_1 = self.processed_points[counter + 1][:2]
                p_2 = self.processed_points[counter + 2][:2]

                points = paramak.utils.convert_circle_to_spline(p_0, p_1, p_2, tolerance=tolerance)

                # the last point needs to have the connection type of p2
                for point in points[:-1]:
                    new_points.append((point[0], point[1], "spline"))

                new_points.append(self.processed_points[counter + 2])
                counter = counter + 3
            else:
                new_points.append(self.processed_points[counter])
                counter = counter + 1

        # @jon I'm not 100% if this change is correct or not
        self.processed_points = new_points
        return new_points

    def volume(self, split_compounds: bool = False) -> Union[float, List[float]]:
        """Get the total volume of the Shape.

        Args:
            split_compounds: If the Shape is a compound of Shapes and therefore
                contains multiple volumes. This option allows access to the
                separate volumes of each component within a Shape (True) or the
                volumes of compounds can be summed (False).

        Returns:
            The the volume(s) of the Shape
        """

        if not isinstance(split_compounds, bool):
            msg = f"split_compounds must be True or False. Not {split_compounds}"
            raise ValueError(msg)

        # returns a list of floats
        if split_compounds:
            all_volumes = []
            if isinstance(self.solid, Compound):
                for solid in self.solid.Solids():
                    all_volumes.append(solid.Volume())
                return all_volumes

            return [self.solid.val().Volume()]

        # returns a float

        if isinstance(self.solid, Compound):
            return self.solid.Volume()

        return self.solid.val().Volume()
