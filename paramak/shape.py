
import json
import numbers
import warnings
from collections import Iterable
from pathlib import Path

import cadquery as cq
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from cadquery import exporters
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

import paramak
from paramak.neutronics_utils import (add_stl_to_moab_core,
                                      define_moab_core_and_tags)
from paramak.utils import (cut_solid, get_hash, intersect_solid, union_solid,
                           _replace)


class Shape:
    """A shape object that represents a 3d volume and can have materials and
    neutronics tallies assigned. Shape objects are not intended to be used
    directly bly the user but provide basic functionality for user-facing
    classes that inherit from Shape.

    Args:
        points (list of (float, float, float), optional): the x, y, z
            coordinates of points that make up the shape. Defaults to None.
        connection_type (str, optional): The type of connection between points.
            Possible values are "straight", "circle", "spline", "mixed".
            Defaults to "mixed".
        name (str, optional): the name of the shape, used in the graph legend
            by export_html. Defaults to None.
        color ((float, float, float [, float]), optional): The color to use when exporting as html
            graphs or png images. Can be in RGB or RGBA format with floats
            between 0 and 1. Defaults to (0.5, 0.5, 0.5).
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
    """

    def __init__(
        self,
        points: list = None,
        connection_type="mixed",
        name=None,
        color=(0.5, 0.5, 0.5),
        material_tag: str = None,
        stp_filename: str = None,
        stl_filename: str = None,
        azimuth_placement_angle=0.0,
        workplane: str = "XZ",
        rotation_axis=None,
        tet_mesh: str = None,
        surface_reflectivity: bool = False,
        physical_groups=None,
        cut=None,
        intersect=None,
        union=None,
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
        self.material_tag = material_tag
        self.tet_mesh = tet_mesh
        self.surface_reflectivity = surface_reflectivity

        self.physical_groups = physical_groups

        # properties calculated internally by the class
        self.solid = None
        self.wire = None
        self.render_mesh = None
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
        if isinstance(self.solid, (cq.Compound, cq.occ_impl.shapes.Solid)):
            for solid in self.solid.Solids():
                largest_dimension = max(
                    abs(self.solid.BoundingBox().xmax),
                    abs(self.solid.BoundingBox().xmin),
                    abs(self.solid.BoundingBox().ymax),
                    abs(self.solid.BoundingBox().ymin),
                    abs(self.solid.BoundingBox().zmax),
                    abs(self.solid.BoundingBox().zmin),
                    largest_dimension
                )
        else:
            largest_dimension = max(
                abs(self.solid.val().BoundingBox().xmax),
                abs(self.solid.val().BoundingBox().xmin),
                abs(self.solid.val().BoundingBox().ymax),
                abs(self.solid.val().BoundingBox().ymin),
                abs(self.solid.val().BoundingBox().zmax),
                abs(self.solid.val().BoundingBox().zmin),
                largest_dimension
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
            msg = "Shape.rotation_axis must be a list of two (X, Y, Z) floats"
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
        if isinstance(self.solid, cq.Compound):
            return self.solid.Volume()

        return self.solid.val().Volume()

    @property
    def volumes(self):
        """Get the volumes of the Shape. Compound shapes provide a seperate
        volume value for each entry. Returns a list of floats"""
        all_volumes = []
        if isinstance(self.solid, cq.Compound):
            for solid in self.solid.Solids():
                all_volumes.append(solid.Volume())
            return all_volumes

        return [self.solid.val().Volume()]

    @property
    def area(self):
        """Get the total surface area of the Shape. Returns a float"""
        if isinstance(self.solid, cq.Compound):
            return self.solid.Area()

        return self.solid.val().Area()

    @property
    def areas(self):
        """Get the surface areas of the Shape. Compound shapes provide a
        seperate area value for each entry. Returns a list of floats"""
        all_areas = []
        if isinstance(self.solid, cq.Compound):
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
        error = False
        if isinstance(value, (list, tuple)):
            if len(value) in [3, 4]:
                for i in value:
                    if not isinstance(i, (int, float)):
                        error = True
            else:
                error = True
        else:
            error = True
        # raise error
        if error:
            raise ValueError(
                "Shape.color must be a list or tuple of 3 or 4 floats")
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
                warnings.warn(msg, UserWarning)
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
    def points(self, values):

        if values is not None:
            if not isinstance(values, list):
                raise ValueError("points must be a list")

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
            if self.connection_type != "mixed":
                values = [(*p, self.connection_type) for p in values]

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

    def create_solid(self):
        solid = None
        if self.points is not None:
            # obtains the first two values of the points list
            XZ_points = [(p[0], p[1]) for p in self.points]

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

                solid = cq.Workplane(self.workplane).center(0, 0)

                if self.force_cross_section:
                    for point in self.path_points[:-1]:
                        solid = solid.workplane(offset=point[1] * factor).\
                            center(point[0], 0).workplane()
                        for entry in instructions:
                            if list(entry.keys())[0] == "spline":
                                solid = solid.spline(
                                    listOfXYTuple=list(entry.values())[0])
                            if list(entry.keys())[0] == "straight":
                                solid = solid.polyline(list(entry.values())[0])
                            if list(entry.keys())[0] == "circle":
                                p0, p1, p2 = list(entry.values())[0][:3]
                                solid = solid.moveTo(p0[0], p0[1]).\
                                    threePointArc(p1, p2)
                        solid = solid.close()
                        solid = solid.center(-point[0], 0).\
                            workplane(offset=-point[1] * factor)

                elif self.force_cross_section == False:
                    solid = solid.workplane(
                        offset=self.path_points[0][1] *
                        factor).center(
                        self.path_points[0][0],
                        0).workplane()
                    for entry in instructions:
                        if list(entry.keys())[0] == "spline":
                            solid = solid.spline(
                                listOfXYTuple=list(entry.values())[0])
                        if list(entry.keys())[0] == "straight":
                            solid = solid.polyline(list(entry.values())[0])
                        if list(entry.keys())[0] == "circle":
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
                solid = cq.Workplane(self.workplane)
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

    def rotate_solid(self, solid):
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
        solid = cq.Workplane(self.workplane)

        # Joins the seperate solids together
        for i in rotated_solids:
            solid = solid.union(i)
        return solid

    def get_rotation_axis(self):
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

    def create_limits(self):
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

    def export_stl(self, filename: str, tolerance: float = 0.001) -> str:
        """Exports an stl file for the Shape.solid. If the provided filename
            doesn't end with .stl it will be added

        Args:
            filename (str): the filename of the stl file to be exported
            tolerance (float): the precision of the faceting
        """

        path_filename = Path(filename)

        if path_filename.suffix != ".stl":
            path_filename = path_filename.with_suffix(".stl")

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        with open(path_filename, "w") as out_file:
            exporters.exportShape(self.solid, "STL", out_file, tolerance)
        print("Saved file as ", path_filename)

        return str(path_filename)

    def export_stp(
            self,
            filename=None,
            units='mm',
            mode: str = 'solid') -> str:
        """Exports an stp file for the Shape.solid. If the filename provided
            doesn't end with .stp or .step then .stp will be added. If a
            filename is not provided and the shape's stp_filename property is
            not None the stp_filename will be used as the export filename.

        Args:
            filename (str): the filename of the stp
            units (str): the units of the stp file, options are 'cm' or 'mm'.
                Default is mm.
            mode (str, optional): the object to export can be either
                'solid' which exports 3D solid shapes or the 'wire' which
                exports the wire edges of the shape. Defaults to 'solid'.
        """

        if filename is not None:
            path_filename = Path(filename)

            if path_filename.suffix == ".stp" or path_filename.suffix == ".step":
                pass
            else:
                path_filename = path_filename.with_suffix(".stp")

            path_filename.parents[0].mkdir(parents=True, exist_ok=True)
        elif self.stp_filename is not None:
            path_filename = Path(self.stp_filename)

        with open(path_filename, "w") as out_file:
            if mode == 'solid':
                exporters.exportShape(self.solid, "STEP", out_file)
            elif mode == 'wire':
                exporters.exportShape(self.wire, "STEP", out_file)
            else:
                raise ValueError("The mode argument for export_stp \
                    only accepts 'solid' or 'wire'", self)

        if units == 'cm':
            _replace(
                path_filename,
                'SI_UNIT(.MILLI.,.METRE.)',
                'SI_UNIT(.CENTI.,.METRE.)')

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

    def export_svg(self, filename: str) -> str:
        """Exports an svg file for the Shape.solid. If the provided filename
        doesn't end with .svg it will be added.

        Args:
            filename (str): the filename of the svg file to be exported
        """

        path_filename = Path(filename)

        if path_filename.suffix != ".svg":
            path_filename = path_filename.with_suffix(".svg")

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        with open(path_filename, "w") as out_file:
            exporters.exportShape(self.solid, "SVG", out_file)
        print("Saved file as ", path_filename)

        return str(path_filename)

    def export_html(self, filename: str):
        """Creates a html graph representation of the points and connections
        for the Shape object. Shapes are colored by their .color property.
        Shapes are also labelled by their .name. If filename provided doesn't
        end with .html then .html will be added.

        Args:
            filename (str): the filename used to save the html graph

        Returns:
            plotly.Figure(): figure object
        """

        if self.__class__.__name__ == "SweepCircleShape":
            msg = 'WARNING: export_html will plot path_points for ' + \
                'the SweepCircleShape class'
            print(msg)

        if self.points is None:
            raise ValueError("No points defined for", self)

        Path(filename).parents[0].mkdir(parents=True, exist_ok=True)

        path_filename = Path(filename)

        if path_filename.suffix != ".html":
            path_filename = path_filename.with_suffix(".html")

        fig = go.Figure()
        fig.update_layout(
            {"title": "coordinates of components", "hovermode": "closest"}
        )

        fig.add_trace(self._trace())

        fig.write_html(str(path_filename))

        print("Exported html graph to ", path_filename)

        return fig

    def _trace(self):
        """Creates a plotly trace representation of the points of the Shape
        object. This method is intended for internal use by Shape.export_html.

        Returns:
            plotly trace: trace object
        """

        color_list = [i * 255 for i in self.color]

        if len(color_list) == 3:
            color = "rgb(" + str(color_list).strip("[]") + ")"
        elif len(color_list) == 4:
            color = "rgba(" + str(color_list).strip("[]") + ")"

        if self.name is None:
            name = "Shape not named"
        else:
            name = self.name

        text_values = []

        for i, point in enumerate(self.points[:-1]):
            if len(point) == 3:
                text_values.append(
                    "point number="
                    + str(i)
                    + "<br>"
                    + "connection to next point="
                    + str(point[2])
                    + "<br>"
                    + "x="
                    + str(point[0])
                    + "<br>"
                    + "z="
                    + str(point[1])
                    + "<br>"
                )
            else:
                text_values.append(
                    "point number="
                    + str(i)
                    + "<br>"
                    + "x="
                    + str(point[0])
                    + "<br>"
                    + "z="
                    + str(point[1])
                    + "<br>"
                )

        trace = go.Scatter(
            {
                "x": [row[0] for row in self.points],
                "y": [row[1] for row in self.points],
                "hoverinfo": "text",
                "text": text_values,
                "mode": "markers+lines",
                "marker": {"size": 5, "color": color},
                "name": name,
            }
        )

        return trace

    def export_2d_image(
            self, filename: str, xmin: float = 0., xmax: float = 900.,
            ymin: float = -600., ymax: float = 600.):
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
        xylist = []

        for point in self.points:
            xylist.append([point[0], point[1]])

        polygon = Polygon(xylist, closed=True)
        patches.append(polygon)

        patch = PatchCollection(patches)

        if self.color is not None:
            patch.set_facecolor(self.color)
            patch.set_color(self.color)
            patch.color = self.color
            patch.edgecolor = self.color
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

        neutronics_description = {"material": self.material_tag}

        if self.stp_filename is not None:
            neutronics_description["stp_filename"] = self.stp_filename
            # this is needed as ppp looks for the filename key
            neutronics_description["filename"] = self.stp_filename

        if self.tet_mesh is not None:
            neutronics_description["tet_mesh"] = self.tet_mesh

        if self.surface_reflectivity is True:
            neutronics_description["surface_reflectivity"] = self.surface_reflectivity

        if self.stl_filename is not None:
            neutronics_description["stl_filename"] = self.stl_filename

        return neutronics_description

    def perform_boolean_operations(self, solid, **kwargs):
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

    def make_graveyard(self, graveyard_offset: int = 100):
        """Creates a graveyard volume (bounding box) that encapsulates all
        volumes. This is required by DAGMC when performing neutronics
        simulations.

        Args:
            graveyard_offset (float): the offset between the largest edge of
                the geometry and inner bounding shell created. Defaults to
                100

        Returns:
            CadQuery solid: a shell volume that bounds the geometry, referred
            to as a graveyard in DAGMC
        """

        self.graveyard_offset = graveyard_offset

        if self.solid is None:
            self.create_solid()

        graveyard_shape = paramak.HollowCube(
            length=self.largest_dimension * 2 + graveyard_offset * 2,
            name="Graveyard",
            material_tag="Graveyard",
            stp_filename="Graveyard.stp",
            stl_filename="Graveyard.stl",
        )

        self.graveyard = graveyard_shape

        return graveyard_shape

    def export_h5m(
            self,
            filename: str = 'dagmc.h5m',
            skip_graveyard: bool = False,
            tolerance: float = 0.001,
            graveyard_offset: float = 100) -> str:
        """Converts stl files into DAGMC compatible h5m file using PyMOAB. The
        DAGMC file produced has not been imprinted and merged unlike the other
        supported method which uses Trelis to produce an imprinted and merged
        DAGMC geometry. If the provided filename doesn't end with .h5m it will
        be added

        Args:
            filename (str, optional): filename of h5m outputfile
                Defaults to "dagmc.h5m".
            skip_graveyard (boolean, optional): filename of h5m outputfile
                Defaults to False.
            tolerance (float, optional): the precision of the faceting
                Defaults to 0.001.
            graveyard_offset (float, optional): the offset between the largest
                edge of the geometry and inner bounding shell created. Defualts
                to 100.
        Returns:
            filename: output h5m filename
        """

        path_filename = Path(filename)

        if path_filename.suffix != ".h5m":
            path_filename = path_filename.with_suffix(".h5m")

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        self.export_stl(self.stl_filename, tolerance=tolerance)

        moab_core, moab_tags = define_moab_core_and_tags()

        moab_core = add_stl_to_moab_core(
            moab_core=moab_core,
            surface_id=1,
            volume_id=1,
            material_name=self.material_tag,
            tags=moab_tags,
            stl_filename=self.stl_filename
        )

        if skip_graveyard is False:
            self.make_graveyard(graveyard_offset=graveyard_offset)
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

        return str(path_filename)

    def export_graveyard(
            self,
            graveyard_offset: float = 100,
            filename: str = "Graveyard.stp") -> str:
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
