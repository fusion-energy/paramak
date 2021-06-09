
import json
import numbers
import warnings
from collections.abc import Iterable
from pathlib import Path
from typing import List, Optional, Tuple, Union

from cadquery import exporters, Workplane, Compound, Assembly, Color
from cadquery.occ_impl import shapes

from cadquery import importers

import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

import paramak

from paramak.utils import (_replace, cut_solid, facet_wire, get_hash,
                           intersect_solid, plotly_trace, union_solid,
                           add_stl_to_moab_core, define_moab_core_and_tags,
                           export_vtk)


class Shape:
    """A shape object that represents a 3d volume and can have materials and
    neutronics tallies assigned. Shape objects are not intended to be used
    directly by the user but provide basic functionality for user-facing
    classes that inherit from Shape. Provides a .show attribute for rendering
    in Jupyter Lab

    Args:
        points (list of (float, float, float), optional): the x, y, z
            coordinates of points that make up the shape. Defaults to None.
        connection_type (str, optional): The type of connection between points.
            Possible values are "straight", "circle", "spline", "mixed".
            Defaults to "mixed".
        name (str, optional): the name of the shape, used in the graph legend
            by export_html. Defaults to None.
        color ((float, float, float [, float]), optional): The color to use
            when exporting as html graphs or png images. Can be in RGB or RGBA
            format with floats between 0 and 1. Defaults to (0.5, 0.5, 0.5).
        material_tag (str, optional): the material name to use when exporting
            the neutronics description. Defaults to None.
        stp_filename (str, optional): the filename used when saving stp files.
            Defaults to None.
        stl_filename (str, optional): the filename used when saving stl files.
            Defaults to None.
        azimuth_placement_angle (iterable of floats or float, optional): the
            azimuth angle(s) used when positioning the shape. If a list of
            angles is provided, the shape is duplicated at all angles.
            Defaults to 0.0.
        workplane (str, optional): the orientation of the Cadquery workplane.
            (XY, YZ or XZ). Defaults to "XZ".
        rotation_axis (str or list, optional): rotation axis around which the
            solid is rotated. If None, the rotation axis will depend on the
            workplane or path_workplane if applicable. Can be set to "X", "-Y",
            "Z", etc. A custom axis can be set by setting a list of two XYZ
            floats. Defaults to None.
        tet_mesh (str, optional): If not None, a tet mesh flag will be added to
            the neutronics description output. Defaults to None.
        scale (float, optional): If not None, a scale flag will be added to
            the neutronics description output. Defaults to None.
        surface_reflectivity (Boolean, optional): If True, a
            surface_reflectivity flag will be added to the neutronics
            description output. Defaults to None.
        physical_groups (dict, optional): contains information on physical
            groups (volumes and surfaces). Defaults to None.
        cut (paramak.shape or list, optional): If set, the current solid will
            be cut with the provided solid or iterable in cut. Defaults to
            None.
        intersect (paramak.shape or list, optional): If set, the current solid
            will be interested with the provided solid or iterable of solids.
            Defaults to None.
        union (paramak.shape or list, optional): If set, the current solid
            will be united with the provided solid or iterable of solids.
            Defaults to None.
        method: The method to use when making the h5m geometry. Options are
            "trelis" or "pymoab".
        graveyard_size: The dimention of cube shaped the graveyard region used
            by DAGMC. This attribtute is used preferentially over
            graveyard_offset.
        graveyard_offset: The distance between the graveyard and the largest
            shape. If graveyard_size is set the this is ignored.
    """

    def __init__(
        self,
        points: list = None,
        connection_type: Optional[str] = "mixed",
        name: Optional[str] = None,
        color: Optional[Tuple[float, float, float,
                              Optional[float]]] = (0.5, 0.5, 0.5),
        material_tag: Optional[str] = None,
        stp_filename: Optional[str] = None,
        stl_filename: Optional[str] = None,
        azimuth_placement_angle: Optional[Union[float, List[float]]] = 0.0,
        workplane: Optional[str] = "XZ",
        rotation_axis: Optional[str] = None,
        tet_mesh: Optional[str] = None,
        scale: Optional[float] = None,
        surface_reflectivity: Optional[bool] = False,
        physical_groups=None,
        method: str = 'pymoab',
        faceting_tolerance: Optional[float] = 1e-1,
        merge_tolerance: Optional[float] = 1e-4,
        # TODO defining Shape types as paramak.Shape results in circular import
        cut=None,
        intersect=None,
        union=None,
        graveyard_size: Optional[float] = 20_000,
        graveyard_offset: Optional[float] = None,
    ):

        self.connection_type = connection_type
        self.points = points
        self.stp_filename = stp_filename
        self.stl_filename = stl_filename
        self.color = color
        self.name = name

        self.cut = cut
        self.intersect = intersect
        self.union = union

        self.azimuth_placement_angle = azimuth_placement_angle
        self.workplane = workplane
        self.rotation_axis = rotation_axis

        # neutronics specific properties
        self.method = method
        self.material_tag = material_tag
        self.tet_mesh = tet_mesh
        self.scale = scale
        self.surface_reflectivity = surface_reflectivity
        self.faceting_tolerance = faceting_tolerance
        self.merge_tolerance = merge_tolerance
        self.graveyard_offset = graveyard_offset
        self.graveyard_size = graveyard_size

        self.physical_groups = physical_groups

        # properties calculated internally by the class
        self.solid = None
        self.wire = None
        self.render_mesh = None
        self.h5m_filename = None
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
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        if value not in ['trelis', 'pymoab']:
            raise ValueError("the method using in should be either trelis, \
                pymoab. {} is not an option".format(value))
        self._method = value

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
    def largest_dimension(self):
        """Calculates a bounding box for the Shape and returns the largest
        absolute value of the largest dimension of the bounding box"""
        largest_dimension = 0
        if isinstance(self.solid, (Compound, shapes.Solid)):
            for solid in self.solid.Solids():
                bound_box = solid.BoundingBox()
                largest_dimension = max(
                    abs(bound_box.xmax),
                    abs(bound_box.xmin),
                    abs(bound_box.ymax),
                    abs(bound_box.ymin),
                    abs(bound_box.zmax),
                    abs(bound_box.zmin),
                    largest_dimension
                )
        else:
            bound_box = self.solid.val().BoundingBox()
            largest_dimension = max(
                abs(bound_box.xmax),
                abs(bound_box.xmin),
                abs(bound_box.ymax),
                abs(bound_box.ymin),
                abs(bound_box.zmax),
                abs(bound_box.zmin),
            )
        self.largest_dimension = largest_dimension
        return largest_dimension

    @largest_dimension.setter
    def largest_dimension(self, value):
        self._largest_dimension = value

    @property
    def workplane(self):
        return self._workplane

    @workplane.setter
    def workplane(self, value):
        acceptable_values = ["XY", "YZ", "XZ", "YX", "ZY", "ZX"]
        if value in acceptable_values:
            self._workplane = value
        else:
            raise ValueError(
                "Shape.workplane must be one of ",
                acceptable_values,
                " not ",
                value)

    @property
    def rotation_axis(self):
        return self._rotation_axis

    @rotation_axis.setter
    def rotation_axis(self, value):
        if isinstance(value, str):
            acceptable_values = \
                ["X", "Y", "Z", "-X", "-Y", "-Z", "+X", "+Y", "+Z"]
            if value not in acceptable_values:
                msg = "Shape.rotation_axis must be one of " + \
                    " ".join(acceptable_values) + \
                    " not " + value
                raise ValueError(msg)
        elif isinstance(value, Iterable):
            msg = "Shape.rotation_axis must be a tuple of three floats (X, Y, Z)"
            if len(value) != 2:
                raise ValueError(msg)
            for point in value:
                if not isinstance(point, tuple):
                    raise ValueError(msg)
                if len(point) != 3:
                    raise ValueError(msg)
                for val in point:
                    if not isinstance(val, (int, float)):
                        raise ValueError(msg)

            if value[0] == value[1]:
                msg = "The two points must be different"
                raise ValueError(msg)
        elif value is not None:
            msg = "Shape.rotation_axis must be a list or a string or None"
            raise ValueError(msg)
        self._rotation_axis = value

    @property
    def volume(self):
        """Get the total volume of the Shape. Returns a float"""
        if isinstance(self.solid, Compound):
            return self.solid.Volume()

        return self.solid.val().Volume()

    @property
    def volumes(self):
        """Get the volumes of the Shape. Compound shapes provide a seperate
        volume value for each entry. Returns a list of floats"""
        all_volumes = []
        if isinstance(self.solid, Compound):
            for solid in self.solid.Solids():
                all_volumes.append(solid.Volume())
            return all_volumes

        return [self.solid.val().Volume()]

    @property
    def area(self):
        """Get the total surface area of the Shape. Returns a float"""
        if isinstance(self.solid, Compound):
            return self.solid.Area()

        return self.solid.val().Area()

    @property
    def areas(self):
        """Get the surface areas of the Shape. Compound shapes provide a
        seperate area value for each entry. Returns a list of floats"""
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
                        raise ValueError(
                            "Individual entries in the Shape.color must a "
                            "number (float or int)")
                    if i > 1 or i < 0:
                        raise ValueError(
                            "Individual entries in the Shape.color must be "
                            "between 0 and 1"
                        )
            else:
                raise ValueError(
                    "Shape.color must be a list or tuple of 3 or 4 floats")
        else:
            raise ValueError(
                "Shape.color must be a list or tuple")

        self._color = value

    @property
    def material_tag(self):
        """The material_tag assigned to the Shape. Used when taging materials
        for use in neutronics descriptions"""

        return self._material_tag

    @material_tag.setter
    def material_tag(self, value):
        if value is None:
            self._material_tag = value
        elif isinstance(value, str):
            if len(value) > 27:
                msg = "Shape.material_tag > 28 characters." + \
                      "Use with DAGMC will be affected." + str(value)
                warnings.warn(msg)
            self._material_tag = value
        else:
            raise ValueError("Shape.material_tag must be a string", value)

    @property
    def tet_mesh(self):
        return self._tet_mesh

    @tet_mesh.setter
    def tet_mesh(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Shape.tet_mesh must be a string", value)
        self._tet_mesh = value

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        if value is not None and not isinstance(value, float):
            raise ValueError("Shape.scale must be a float", value)
        self._scale = value

    @property
    def name(self):
        """The name of the Shape, used to identify Shapes when exporting_html
        """
        return self._name

    @name.setter
    def name(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Shape.name must be a string", value)
        self._name = value

    @property
    def points(self):
        """Sets the Shape.point attributes.

        Args:
            points (a list of lists or tuples): list of points that create the
                shape

        Raises:
            incorrect type: only list of lists or tuples are accepted
        """
        ignored_keys = ["_points", "_points_hash_value"]
        if hasattr(self, 'find_points') and \
                self.points_hash_value != get_hash(self, ignored_keys):
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
            if not isinstance(values, list):
                raise ValueError("points must be a list")

            if self.connection_type != "mixed":
                values = [(*p, self.connection_type) for p in values]

            for value in values:
                if type(value) not in [list, tuple]:
                    msg = "individual points must be a list or a tuple." + \
                        "{} in of type {}".format(value, type(value))
                    raise ValueError(msg)

            for value in values:
                # Checks that the length of each tuple in points is 2 or 3
                if len(value) not in [2, 3]:
                    msg = "individual points contain 2 or 3 entries {} has a \
                        length of {}".format(value, len(values[0]))
                    raise ValueError(msg)

                # Checks that the XY points are numbers
                if not isinstance(value[0], numbers.Number):
                    msg = "The first value in the tuples that make \
                                        up the points represents the X value \
                                        and must be a number {}".format(value)
                    raise ValueError(msg)
                if not isinstance(value[1], numbers.Number):
                    msg = "The second value in the tuples that make \
                                      up the points represents the X value \
                                      and must be a number {}".format(value)
                    raise ValueError(msg)

                # Checks that only straight and spline are in the connections
                # part of points
                if len(value) == 3:
                    if value[2] not in ["straight", "spline", "circle"]:
                        msg = 'individual connections must be either \
                            "straight", "circle" or "spline"'
                        raise ValueError(msg)

            # checks that the entries in the points are either all 2 long or
            # all 3 long, not a mixture
            if not all(len(entry) == 2 for entry in values):
                if not all(len(entry) == 3 for entry in values):
                    msg = "The points list should contain entries of length 2 \
                            or 3 but not a mixture of 2 and 3"
                    raise ValueError(msg)

            if len(values) > 1:
                if values[0][:2] == values[-1][:2]:
                    msg = "The coordinates of the last and first points are \
                        the same."
                    raise ValueError(msg)

                values.append(values[0])

        self._points = values

    @property
    def stp_filename(self):
        """Sets the Shape.stp_filename attribute which is used as the filename
        when exporting the geometry to stp format. Note, .stp will be added to
        filenames not ending with .step or .stp.

        Args:
            value (str): the value to use as the stp_filename

        Raises:
            incorrect type: only str values are accepted
        """

        return self._stp_filename

    @stp_filename.setter
    def stp_filename(self, value):
        if value is not None:
            if isinstance(value, str):
                if Path(value).suffix not in [".stp", ".step"]:
                    msg = "Incorrect filename ending, filename must end with \
                            .stp or .step"
                    raise ValueError(msg)
            else:
                msg = "stp_filename must be a \
                    string {} {}".format(value, type(value))
                raise ValueError(msg)
        self._stp_filename = value

    @property
    def stl_filename(self):
        """Sets the Shape.stl_filename attribute which is used as the filename
        when exporting the geometry to stl format. Note .stl will be added to
        filenames not ending with .stl

        Args:
            value (str): the value to use as the stl_filename

        Raises:
            incorrect type: only str values are accepted
        """
        return self._stl_filename

    @stl_filename.setter
    def stl_filename(self, value):
        if value is not None:
            if isinstance(value, str):
                if Path(value).suffix != ".stl":
                    msg = "Incorrect filename ending, filename must end with \
                            .stl"
                    raise ValueError(msg)
            else:
                msg = "stl_filename must be a string \
                    {} {}".format(value, type(value))
                raise ValueError(msg)
        self._stl_filename = value

    @property
    def azimuth_placement_angle(self):
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        error = False
        if isinstance(value, (int, float, Iterable)) and \
                not isinstance(value, str):
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

    def show(self):
        """Shows / renders the CadQuery the 3d object in Jupyter Lab. Imports
        show from jupyter_cadquery.cadquery and returns show(Shape.solid)"""

        from jupyter_cadquery.cadquery import Part, PartGroup

        parts = []
        if self.name is None:
            name = 'Shape.name not set'
        else:
            name = self.name

        scaled_color = [int(i * 255) for i in self.color[0:3]]
        if isinstance(
                self.solid,
                (shapes.Shape, shapes.Compound)):
            for i, solid in enumerate(self.solid.Solids()):
                parts.append(
                    Part(
                        solid,
                        name=f"{name}{i}",
                        color=scaled_color))
        else:
            parts.append(
                Part(
                    self.solid.val(),
                    name=f"{name}",
                    color=scaled_color))

        return PartGroup(parts)

    def create_solid(self) -> Workplane:
        solid = None
        if self.points is not None:
            # obtains the first two values of the points list
            XZ_points = [(p[0], p[1]) for p in self.points]

            for point in self.points:
                if len(point) != 3:
                    msg = "The points list should contain two coordinates and \
                        a connetion type"
                    raise ValueError(msg)

            # obtains the last values of the points list
            connections = [p[2] for p in self.points[:-1]]

            current_linetype = connections[0]
            current_points_list = []
            instructions = []
            # groups together common connection types
            for i, connection in enumerate(connections):
                if connection == current_linetype:
                    current_points_list.append(XZ_points[i])
                else:
                    current_points_list.append(XZ_points[i])
                    instructions.append(
                        {current_linetype: current_points_list})
                    current_linetype = connection
                    current_points_list = [XZ_points[i]]
            instructions.append({current_linetype: current_points_list})

            if list(instructions[-1].values())[0][-1] != XZ_points[0]:
                keyname = list(instructions[-1].keys())[0]
                instructions[-1][keyname].append(XZ_points[0])

            if hasattr(self, "path_points"):

                factor = 1
                if self.workplane in ["XZ", "YX", "ZY"]:
                    factor *= -1

                solid = Workplane(self.workplane).center(0, 0)

                if self.force_cross_section:
                    for point in self.path_points[:-1]:
                        solid = solid.workplane(offset=point[1] * factor).\
                            center(point[0], 0).workplane()
                        for entry in instructions:
                            connection_type = list(entry.keys())[0]
                            if connection_type == "spline":
                                solid = solid.spline(
                                    listOfXYTuple=list(entry.values())[0])
                            elif connection_type == "straight":
                                solid = solid.polyline(list(entry.values())[0])
                            elif connection_type == "circle":
                                p0, p1, p2 = list(entry.values())[0][:3]
                                solid = solid.moveTo(p0[0], p0[1]).\
                                    threePointArc(p1, p2)
                        solid = solid.close()
                        solid = solid.center(-point[0], 0).\
                            workplane(offset=-point[1] * factor)

                elif self.force_cross_section is False:
                    solid = solid.workplane(
                        offset=self.path_points[0][1] *
                        factor).center(
                        self.path_points[0][0],
                        0).workplane()
                    for entry in instructions:
                        connection_type = list(entry.keys())[0]
                        if connection_type == "spline":
                            solid = solid.spline(
                                listOfXYTuple=list(entry.values())[0])
                        elif connection_type == "straight":
                            solid = solid.polyline(list(entry.values())[0])
                        elif connection_type == "circle":
                            p0 = list(entry.values())[0][0]
                            p1 = list(entry.values())[0][1]
                            p2 = list(entry.values())[0][2]
                            solid = solid.moveTo(
                                p0[0], p0[1]).threePointArc(
                                p1, p2)

                    solid = solid.close().center(0, 0).\
                        center(-self.path_points[0][0], 0).\
                        workplane(offset=-self.path_points[0][1] * factor)

                solid = solid.workplane(offset=self.path_points[-1][1] * factor).\
                    center(self.path_points[-1][0], 0).workplane()

            else:
                # for rotate and extrude shapes
                solid = Workplane(self.workplane)
                # for extrude shapes
                if hasattr(self, "extrusion_start_offset"):
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

    def rotate_solid(
            self,
            solid: Optional[Workplane]) -> Workplane:
        # Checks if the azimuth_placement_angle is a list of angles
        if isinstance(self.azimuth_placement_angle, Iterable):
            azimuth_placement_angles = self.azimuth_placement_angle
        else:
            azimuth_placement_angles = [self.azimuth_placement_angle]

        rotated_solids = []
        # Perform seperate rotations for each angle
        for angle in azimuth_placement_angles:
            rotated_solids.append(
                solid.rotate(
                    *self.get_rotation_axis()[0], angle))
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
                self.rotation_axis
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

        if hasattr(self, "find_points"):
            self.find_points()
        if self.points is None:
            raise ValueError("No points defined for", self)

        self.x_min = float(min([row[0] for row in self.points]))
        self.x_max = float(max([row[0] for row in self.points]))

        self.z_min = float(min([row[1] for row in self.points]))
        self.z_max = float(max([row[1] for row in self.points]))

        return self.x_min, self.x_max, self.z_min, self.z_max

    def export_stl(
            self,
            filename: Optional[str] = None,
            tolerance: Optional[float] = 0.001,
            angular_tolerance: Optional[float] = 0.1,
            verbose: Optional[bool] = True) -> str:
        """Exports an stl file for the Shape.solid. If the provided filename
        doesn't end with .stl it will be added.

        Args:
            filename: the filename of exported the stl file. Defaults to None
                which will attempt to use the Shape.stl_filename. If both are
                None then a valueError will be raised.
            tolerance: the deflection tolerance of the faceting
            angular_tolerance: the angular tolerance, in radians
            verbose: Enables (True) or disables (False) the printing of the
                file produced.
        """

        if filename is not None:
            path_filename = Path(filename)
        elif self.stl_filename is not None:
            path_filename = Path(self.stl_filename)
        else:
            raise ValueError("The filename must be specified either the \
                filename argument or the Shape.stl_filename must be set")

        if path_filename.suffix != ".stl":
            path_filename = path_filename.with_suffix(".stl")

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        exporters.export(self.solid, str(path_filename), exportType='STL',
                         tolerance=tolerance,
                         angularTolerance=angular_tolerance)

        if verbose:
            print("Saved file as ", path_filename)

        return str(path_filename)

    def export_stp(
            self,
            filename: Optional[str] = None,
            units: Optional[str] = 'mm',
            mode: Optional[str] = 'solid',
            verbose: Optional[bool] = True) -> str:
        """Exports an stp file for the Shape.solid. If the filename provided
        doesn't end with .stp or .step then .stp will be added.

        Args:
            filename: the filename of exported the stp file. Defaults to None
                which will attempt to use the Shape.stp_filename. If both are
                None then a valueError will be raised.
            units: the units of the stp file, options are 'cm' or 'mm'.
                Default is mm.
            mode: the object to export can be either
                'solid' which exports 3D solid shapes or the 'wire' which
                exports the wire edges of the shape. Defaults to 'solid'.
            verbose: Enables (True) or disables (False) the printing of the
                file produced.
        """

        if filename is not None:
            path_filename = Path(filename)
        elif self.stp_filename is not None:
            path_filename = Path(self.stp_filename)
        else:
            raise ValueError("The filename must be specified either the \
                filename argument or the Shape.stp_filename must be set")

        if path_filename.suffix == ".stp" or path_filename.suffix == ".step":
            pass
        else:
            path_filename = path_filename.with_suffix(".stp")

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        if mode == 'solid':

            assembly = Assembly(name=self.name)

            if self.color is None:
                assembly.add(self.solid)
            else:
                assembly.add(self.solid, color=Color(*self.color))

            assembly.save(str(path_filename), exportType='STEP')

            # previous method does not support colours but puts the solid in the base file level
            # exporters.export(self.solid, str(path_filename), exportType='STEP')

        elif mode == 'wire':
            exporters.export(self.wire, str(path_filename), exportType='STEP')
        else:
            raise ValueError("The mode argument for export_stp \
                only accepts 'solid' or 'wire'", self)

        if units == 'cm':
            _replace(
                path_filename,
                'SI_UNIT(.MILLI.,.METRE.)',
                'SI_UNIT(.CENTI.,.METRE.)')

        if verbose:
            print("Saved file as ", path_filename)

        return str(path_filename)

    def export_physical_groups(self, filename: str) -> str:
        """Exports a JSON file containing a look up table which is useful for
        identifying faces and volumes. If filename provided doesn't end with
        .json then .json will be added.

        Args:
            filename (str): the filename used to save the json file
        """

        path_filename = Path(filename)

        if path_filename.suffix != ".json":
            path_filename = path_filename.with_suffix(".json")

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)
        if self.physical_groups is not None:
            with open(filename, "w") as outfile:
                json.dump(self.physical_groups, outfile, indent=4)

            print("Saved physical_groups description to ", path_filename)
        else:
            print(
                "Warning: physical_groups attribute is None \
                for {}".format(
                    self.name
                )
            )

        return str(path_filename)

    def export_svg(
            self,
            filename: Optional[str] = 'shape.svg',
            projectionDir: Tuple[float, float, float] = (-1.75, 1.1, 5),
            width: Optional[float] = 800,
            height: Optional[float] = 800,
            marginLeft: Optional[float] = 100,
            marginTop: Optional[float] = 100,
            strokeWidth: Optional[float] = None,
            strokeColor: Optional[Tuple[int, int, int]] = (0, 0, 0),
            hiddenColor: Optional[Tuple[int, int, int]] = (100, 100, 100),
            showHidden: Optional[bool] = True,
            showAxes: Optional[bool] = False) -> str:
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
            "showHidden": showHidden
        }

        if strokeWidth is not None:
            opt["strokeWidth"] = strokeWidth

        exporters.export(self.solid, str(path_filename), exportType='SVG',
                         opt=opt)

        print("Saved file as ", path_filename)

        return str(path_filename)

    def export_html_3d(
            self,
            filename: Optional[str] = "shape_3d.html",
    ):
        """Saves an interactive 3d html view of the Shape to a html file.

        Args:
            filename: the filename used to save the html graph. Defaults to
                shape_3d.html

        Returns:
            str: filename of the created html file
        """

        from ipywidgets.embed import embed_minimal_html

        embed_minimal_html(
            filename,
            views=[self.show().show().cq_view.renderer],
            title='Renderer'
        )

        return filename

    def export_html(
            self,
            filename: Optional[str] = "shape.html",
            facet_splines: Optional[bool] = True,
            facet_circles: Optional[bool] = True,
            tolerance: Optional[float] = 1e-3,
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
            title="coordinates of " + self.__class__.__name__ +
            " shape, viewed from the " + view_plane + " plane",
        )

        if self.points is not None:
            fig.add_trace(
                plotly_trace(
                    points=self.points,
                    mode="markers",
                    name='Shape.points'
                )
            )

        # sweep shapes have .path_points but not .points attribute
        if hasattr(self, 'path_points'):
            fig.add_trace(
                plotly_trace(
                    points=self.path_points,
                    mode="markers",
                    name='Shape.path_points'
                )
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
            filename: Optional[str] = 'shape.png',
            xmin: Optional[float] = 0.,
            xmax: Optional[float] = 900.,
            ymin: Optional[float] = -600.,
            ymax: Optional[float] = 600.):
        """Exports a 2d image (png) of the reactor. Components are colored by
        their Shape.color property. If filename provided doesn't end with .png
        then .png will be added.

        Args:
            filename (str): the filename of the saved png image.
            xmin (float, optional): the minimum x value of the x axis.
                Defaults to 0..
            xmax (float, optional): the maximum x value of the x axis.
                Defaults to 900..
            ymin (float, optional): the minimum y value of the y axis.
                Defaults to -600..
            ymax (float, optional): the maximum y value of the y axis.
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
        print("\n saved 2d image to ", filename)

        return plt

    def _create_patch(self):
        """Creates a matplotlib polygon patch from the Shape points. This is
        used when making 2d images of the Shape object.

        Raises:
            ValueError: No points defined for the Shape

        Returns:
            Matplotlib object patch: a plotable polygon shape
        """

        if self.points is None:
            raise ValueError("No points defined for", self)

        patches = []

        edges = facet_wire(
            wire=self.wire,
            facet_splines=True,
            facet_circles=True)

        fpoints = []
        for edge in edges:
            for vertice in edge.Vertices():
                fpoints.append((vertice.X, vertice.Z))

        polygon = Polygon(fpoints, closed=True)
        patches.append(polygon)

        patch = PatchCollection(patches)

        if self.color is not None:
            print('color is ', self.color)
            patch.set_facecolor(self.color[0:3])
            patch.set_color(self.color[0:3])
            patch.color = self.color[0:3]
            patch.edgecolor = self.color[0:3]
            # checks to see if an alpha value is provided in the color
            if len(self.color) == 4:
                patch.set_alpha = self.color[-1]
        self.patch = patch
        return patch

    def neutronics_description(self) -> dict:
        """Returns a neutronics description of the Shape object. This is needed
        for the use with automated neutronics model methods which require
        linkage between the stp files and materials. If tet meshing of the
        volume is required then Trelis meshing commands can be optionally
        specified as the tet_mesh argument.

        Returns:
            dictionary: a dictionary of the step filename and material name
        """

        neutronics_description = {"material_tag": self.material_tag}

        if self.stp_filename is not None:
            neutronics_description["stp_filename"] = self.stp_filename

        if self.tet_mesh is not None:
            neutronics_description["tet_mesh"] = self.tet_mesh

        if self.scale is not None:
            neutronics_description["scale"] = self.scale

        if self.surface_reflectivity is True:
            neutronics_description["surface_reflectivity"] = self.surface_reflectivity

        if self.stl_filename is not None:
            neutronics_description["stl_filename"] = self.stl_filename

        return neutronics_description

    def export_neutronics_description(
            self,
            filename: Optional[str] = "manifest.json") -> str:
        """
        Saves Shape.neutronics_description to a json file. The resulting json
        file contains a list of dictionaries. Each dictionary entry comprises
        of a material and a filename and optionally a tet_mesh instruction. The
        json file can then be used with the neutronics workflows to create a
        neutronics model. Creating of the neutronics model requires linkage
        between volumes, materials and identification of which volumes to
        tet_mesh. If the filename does not end with .json then .json will be
        added. The plasma geometry is not included by default as it is
        typically not included in neutronics simulations. The reason for this
        is that the low number density results in minimal interactions with
        neutrons. However, the plasma can be added if the include_plasma
        argument is set to True.

        Args:
            filename (str, optional): the filename used to save the neutronics
                description
            include_plasma (Boolean, optional): should the plasma be included.
                Defaults to False as the plasma volume and material has very
                little impact on the neutronics results due to the low density.
                Including the plasma does however slow down the simulation.
            include_graveyard (Boolean, optional): should the graveyard be
                included. Defaults to True as this is needed for DAGMC models.
        """

        path_filename = Path(filename)

        if path_filename.suffix != ".json":
            path_filename = path_filename.with_suffix(".json")

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        with open(path_filename, "w") as outfile:
            json.dump(
                [self.neutronics_description()],
                outfile,
                indent=4,
            )

        print("saved geometry description to ", path_filename)

        return str(path_filename)

    def perform_boolean_operations(self, solid: Workplane, **kwargs):
        """Performs boolean cut, intersect and union operations if shapes are
        provided"""

        # If a cut solid is provided then perform a boolean cut
        if self.cut is not None:
            solid = cut_solid(solid, self.cut)

        # If a wedge cut is provided then perform a boolean cut
        # Performed independantly to avoid use of self.cut
        # Prevents repetition of 'outdated' wedge cuts
        if 'wedge_cut' in kwargs:
            if kwargs['wedge_cut'] is not None:
                solid = cut_solid(solid, kwargs['wedge_cut'])

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
                "Please specify at least one of these attributes or agruments")

        graveyard_shape = paramak.HollowCube(
            length=graveyard_size_to_use,
            name="graveyard",
            material_tag="graveyard",
            stp_filename="graveyard.stp",
            stl_filename="graveyard.stl",
        )

        self.graveyard = graveyard_shape

        return graveyard_shape

    def export_vtk(
        self,
        filename: Optional[str] = 'dagmc.vtk',
        h5m_filename: Optional[str] = None,
        include_graveyard: Optional[bool] = False
    ):
        """Produces a vtk geometry compatable from the dagmc h5m file. This is
        useful for checking the geometry that is used for transport.

        Arguments:
            filename: filename of vtk outputfile. If the filename does not end
                with .vtk then .vtk will be added.
            h5m_filename: filename of h5m outputfile. If the filename does not
                end with .h5m then .h5m will be added. Defaults to None which
                uses the Reactor.h5m_filename.
            include_graveyard: optionally include the graveyard in the vtk file

        Returns:
            filename of the vtk file produced
        """

        if h5m_filename is None:
            if self.h5m_filename is None:
                raise ValueError(
                    'h5m_filename not provided and Reactor.h5m_filename is '
                    'not set, Unable to use mbconvert to convert to vtk '
                    'without input h5m filename. Try running '
                    'Reactor.export_h5m() first.')

            h5m_filename = self.h5m_filename

        vtk_filename = paramak.utils.export_vtk(
            filename=filename,
            h5m_filename=h5m_filename,
            include_graveyard=include_graveyard
        )

        return vtk_filename

    def export_h5m(
            self,
            filename: str = 'dagmc.h5m',
            method: Optional[str] = None,
            merge_tolerance: Optional[float] = None,
            faceting_tolerance: Optional[float] = None,
    ) -> str:
        """Produces a dagmc.h5m neutronics file compatable with DAGMC
        simulations. Tags the volumes with their material_tag attributes. Sets
        the Shape.h5m_filename to the filename of the h5m file produced.

        Arguments:
            method: The method to use when making the imprinted and
                merged geometry. Options are "trelis" and "pymoab" Defaults to
                None which uses the Shape.method attribute.
            merge_tolerance: the allowable distance between edges and surfaces
                before merging these CAD objects into a single CAD object. See
                https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html
                for more details. Defaults to None which uses the
                Shape.merge_tolerance attribute.
            faceting_tolerance: the allowable distance between facetets
                before merging these CAD objects into a single CAD object See
                https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html
                for more details. Defaults to None which uses the
                Shape.faceting_tolerance attribute.

        Returns:
            The filename of the DAGMC file created
        """

        if merge_tolerance is None:
            merge_tolerance = self.merge_tolerance

        if faceting_tolerance is None:
            faceting_tolerance = self.faceting_tolerance

        if method is None:
            method = self.method

        if method == 'trelis':
            output_filename = self.export_h5m_with_trelis(
                merge_tolerance=merge_tolerance,
                faceting_tolerance=faceting_tolerance,
            )

        elif method == 'pymoab':
            output_filename = self.export_h5m_with_pymoab(
                filename=filename,
                faceting_tolerance=faceting_tolerance,
            )

        else:
            raise ValueError("the method using in should be either trelis, \
                pymoab. {} is not an option".format(method))

        return output_filename

    def export_h5m_with_trelis(
            self,
            merge_tolerance: Optional[float] = None,
            faceting_tolerance: Optional[float] = None,
    ):
        """Produces a dagmc.h5m neutronics file compatable with DAGMC
        simulations using Coreform Trelis.

        Arguments:
            merge_tolerance: the allowable distance between edges and surfaces
                before merging these CAD objects into a single CAD object. See
                https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html
                for more details. Defaults to None which uses the
                Shape.merge_tolerance attribute.
            faceting_tolerance: the allowable distance between facetets
                before merging these CAD objects into a single CAD object See
                https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html
                for more details. Defaults to None which uses the
                Shape.faceting_tolerance attribute.

        Returns:
            str: filename of the DAGMC file produced
        """

        if merge_tolerance is None:
            merge_tolerance = self.merge_tolerance
        if faceting_tolerance is None:
            faceting_tolerance = self.faceting_tolerance

        self.export_stp()
        self.export_neutronics_description()

        not_watertight_file = paramak.utils.trelis_command_to_create_dagmc_h5m(
            faceting_tolerance=faceting_tolerance, merge_tolerance=merge_tolerance)

        water_tight_h5m = paramak.utils.make_watertight(
            input_filename=not_watertight_file,
            output_filename="dagmc.h5m"
        )

        self.h5m_filename = water_tight_h5m

        return water_tight_h5m

    def export_h5m_with_pymoab(
            self,
            filename: Optional[str] = 'dagmc.h5m',
            include_graveyard: Optional[bool] = True,
            faceting_tolerance: Optional[float] = 0.001,
    ) -> str:
        """Converts stl files into DAGMC compatible h5m file using PyMOAB. The
        DAGMC file produced has not been imprinted and merged unlike the other
        supported method which uses Trelis to produce an imprinted and merged
        DAGMC geometry. If the provided filename doesn't end with .h5m it will
        be added

        Args:
            filename: filename of h5m outputfile.
            include_graveyard: specifiy if the graveyard will be included or
                not. If True the the Reactor.make_graveyard will be called
                using Reactor.graveyard_size and Reactor.graveyard_offset
                attribute values.
            faceting_tolerance: the precision of the faceting.

        Returns:
            The filename of the DAGMC file created
        """

        path_filename = Path(filename)

        if path_filename.suffix != ".h5m":
            path_filename = path_filename.with_suffix(".h5m")

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        self.export_stl(self.stl_filename, tolerance=faceting_tolerance)

        moab_core, moab_tags = define_moab_core_and_tags()

        moab_core = add_stl_to_moab_core(
            moab_core=moab_core,
            surface_id=1,
            volume_id=1,
            material_name=self.material_tag,
            tags=moab_tags,
            stl_filename=self.stl_filename
        )

        if include_graveyard:
            self.make_graveyard()
            self.graveyard.export_stl(self.graveyard.stl_filename)
            volume_id = 2
            surface_id = 2
            moab_core = add_stl_to_moab_core(
                moab_core=moab_core,
                surface_id=surface_id,
                volume_id=volume_id,
                material_name=self.graveyard.material_tag,
                tags=moab_tags,
                stl_filename=self.graveyard.stl_filename
            )

        all_sets = moab_core.get_entities_by_handle(0)

        file_set = moab_core.create_meshset()

        moab_core.add_entities(file_set, all_sets)

        moab_core.write_file(str(path_filename))

        self.h5m_filename = str(path_filename)

        return str(path_filename)

    def export_graveyard(
            self,
            filename: Optional[str] = "graveyard.stp",
            graveyard_offset: Optional[float] = 100) -> str:
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
        new_filename = self.graveyard.export_stp(Path(filename))

        return new_filename

    def convert_all_circle_connections_to_splines(
            self,
            tolerance: Optional[float] = 0.1
    ) -> List[Tuple[float, float, str]]:
        """Replaces circle edges in Shape.points with spline edges. The spline
        control coordinates are obtained by faceting the circle edge with the
        provided tolerance. The Shape.points will be updated to exclude the
        circle points and include the new spline points. This method works best
        when the connection before and after the circle is s straight
        connection type. This method is useful when converting the stp file
        into other formats due to errors in the conversion of circle edges.

        Args:
            tolerance: the precision of the faceting.

        Returns:
            The new points with spline connections
        """

        new_points = []
        counter = 0
        while counter < len(self.points):

            if self.points[counter][2] == 'circle':
                p_0 = self.points[counter][:2]
                p_1 = self.points[counter + 1][:2]
                p_2 = self.points[counter + 2][:2]

                points = paramak.utils.convert_circle_to_spline(
                    p_0, p_1, p_2, tolerance=tolerance
                )

                # the last point needs to have the connection type of p2
                for point in points[:-1]:
                    new_points.append((point[0], point[1], 'spline'))

                new_points.append(self.points[counter + 2])
                counter = counter + 3
            else:
                new_points.append(self.points[counter])
                counter = counter + 1
        self.points = new_points[:-1]
        return new_points[:-1]
