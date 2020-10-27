import json
import numbers
import warnings
from collections import Iterable
from hashlib import blake2b
from os import fdopen, remove
from pathlib import Path
from shutil import copymode, move
from tempfile import mkstemp

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import cadquery as cq
from cadquery import exporters
import cadquery as cq
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

from paramak.utils import cut_solid, intersect_solid, union_solid


class Shape:
    """A shape object that represents a 3d volume and can have materials and
    neutronics tallies assigned. Shape objects are not intended to be used
    directly bly the user but provide basic functionality for user-facing
    classes that inherit from Shape.

    Args:
        points (list of (float, float, float), optional): the x, y, z
            coordinates of points that make up the shape. Defaults to None.
        name (str, optional): the name of the shape, used in the graph legend
            by export_html. Defaults to None.
        color (RGB or RGBA, sequences of 3 or 4 floats, respectively, each in
            the range 0-1, optional): the color to use when exporting as html
            graphs or png images. Defaults to (0.5, 0.5, 0.5).
        material_tag (str, optional): the material name to use when exporting
            the neutronics description. Defaults to None.
        stp_filename (str, optional): the filename used when saving stp files.
            Defaults to None.
        stl_filename (str, optional): the filename used when saving stl files.
            Defaults to None.
        azimuth_placement_angle (iterable of floats or float, optional): the azimuth angle(s) used
            when positioning the shape. If a list of angles is provided, the
            shape is duplicated at all angles. Defaults to 0.0.
        workplane (str, optional): the orientation of the Cadquery workplane.
            (XY, YZ or XZ). Defaults to "XZ".
        tet_mesh (str, optional): If not None, a tet mesh flag will be added to
            the neutronics description output. Defaults to None.
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
        points=None,
        connection_type="mixed",
        name=None,
        color=(0.5, 0.5, 0.5),
        material_tag=None,
        stp_filename=None,
        stl_filename=None,
        azimuth_placement_angle=0.0,
        workplane="XZ",
        tet_mesh=None,
        physical_groups=None,
        cut=None,
        intersect=None,
        union=None
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

        # neutronics specific properties
        self.material_tag = material_tag
        self.tet_mesh = tet_mesh

        self.physical_groups = physical_groups

        # properties calculated internally by the class
        self.solid = None
        self.render_mesh = None
        # self.volume = None
        self.hash_value = None

    @property
    def solid(self):
        if self.get_hash() != self.hash_value:
            self.create_solid()
        return self._solid

    @solid.setter
    def solid(self, value):
        self._solid = value

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
    def workplane(self):
        return self._workplane

    @workplane.setter
    def workplane(self, value):
        acceptable_values = ["XY", "YZ", "XZ"]
        if value in acceptable_values:
            self._workplane = value
        else:
            raise ValueError(
                "Shape.workplane must be one of ",
                acceptable_values,
                " not ",
                value)

    @property
    def volume(self):
        if isinstance(self.solid, cq.Compound):
            return self.solid.Volume()
        else:
            return self.solid.val().Volume()

    @property
    def hash_value(self):
        return self._hash_value

    @hash_value.setter
    def hash_value(self, value):
        self._hash_value = value

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
        if hasattr(self, 'find_points'):
            self.find_points()

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
                else:
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
        if isinstance(value, (int, float, Iterable)):
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
        """Dummy create_solid method
        """
        return

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
                    (0, 0, -1), (0, 0, 1), angle))
        solid = cq.Workplane(self.workplane)

        # Joins the seperate solids together
        for i in rotated_solids:
            solid = solid.union(i)
        return solid

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
            ValueError("No points defined for", self)

        self.x_min = float(min([row[0] for row in self.points]))
        self.x_max = float(max([row[0] for row in self.points]))

        self.z_min = float(min([row[1] for row in self.points]))
        self.z_max = float(max([row[1] for row in self.points]))

        return self.x_min, self.x_max, self.z_min, self.z_max

    def export_stl(self, filename, tolerance=0.001):
        """Exports an stl file for the Shape.solid. If the provided filename
            doesn't end with .stl it will be added

        Args:
            filename (str): the filename of the stl file to be exported
            tolerance (float): the precision of the faceting
        """

        Pfilename = Path(filename)

        if Pfilename.suffix != ".stl":
            Pfilename = Pfilename.with_suffix(".stl")

        Pfilename.parents[0].mkdir(parents=True, exist_ok=True)

        with open(Pfilename, "w") as f:
            exporters.exportShape(self.solid, "STL", f, tolerance)
        print("Saved file as ", Pfilename)

        return str(Pfilename)

    def export_stp(self, filename=None):
        """Exports an stp file for the Shape.solid. If the filename provided
            doesn't end with .stp or .step then .stp will be added. If a
            filename is not provided and the shape's stp_filename property is
            not None the stp_filename will be used as the export filename.

        Args:
            filename (str): the filename of the stp
        """

        if filename is not None:
            Pfilename = Path(filename)

            if Pfilename.suffix == ".stp" or Pfilename.suffix == ".step":
                pass
            else:
                Pfilename = Pfilename.with_suffix(".stp")

            Pfilename.parents[0].mkdir(parents=True, exist_ok=True)
        elif self.stp_filename is not None:
            Pfilename = Path(self.stp_filename)

        with open(Pfilename, "w") as f:
            exporters.exportShape(self.solid, "STEP", f)

        self._replace(
            Pfilename,
            'SI_UNIT(.MILLI.,.METRE.)',
            'SI_UNIT(.CENTI.,.METRE.)')

        print("Saved file as ", Pfilename)

        return str(Pfilename)

    def export_physical_groups(self, filename):
        """Exports a JSON file containing a look up table which is useful for
        identifying faces and volumes. If filename provided doesn't end with
        .json then .json will be added.

        Args:
            filename (str): the filename used to save the json file
        """

        Pfilename = Path(filename)

        if Pfilename.suffix != ".json":
            Pfilename = Pfilename.with_suffix(".json")

        Pfilename.parents[0].mkdir(parents=True, exist_ok=True)
        if self.physical_groups is not None:
            with open(filename, "w") as outfile:
                json.dump(self.physical_groups, outfile, indent=4)

            print("Saved physical_groups description to ", Pfilename)
        else:
            print(
                "Warning: physical_groups attribute is None \
                for {}".format(
                    self.name
                )
            )

        return filename

    def export_svg(self, filename):
        """Exports an svg file for the Shape.solid. If the provided filename
        doesn't end with .svg it will be added.

        Args:
            filename (str): the filename of the svg file to be exported
        """

        Pfilename = Path(filename)

        if Pfilename.suffix != ".svg":
            Pfilename = Pfilename.with_suffix(".svg")

        Pfilename.parents[0].mkdir(parents=True, exist_ok=True)

        with open(Pfilename, "w") as f:
            exporters.exportShape(self.solid, "SVG", f)
        print("Saved file as ", Pfilename)

        return str(Pfilename)

    def export_html(self, filename):
        """Creates a html graph representation of the points and connections
        for the Shape object. Shapes are colored by their .color property.
        Shapes are also labelled by their .name. If filename provided doesn't
        end with .html then .html will be added.

        Args:
            filename (str): the filename used to save the html graph

        Returns:
            plotly.Figure(): figure object
        """

        if self.points is None:
            ValueError("No points defined for", self)

        Path(filename).parents[0].mkdir(parents=True, exist_ok=True)

        Pfilename = Path(filename)

        if Pfilename.suffix != ".html":
            Pfilename = Pfilename.with_suffix(".html")

        fig = go.Figure()
        fig.update_layout(
            {"title": "coordinates of components", "hovermode": "closest"}
        )

        fig.add_trace(self._trace())

        fig.write_html(str(Pfilename))

        print("Exported html graph to ", Pfilename)

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

        for i, p in enumerate(self.points[:-1]):
            if len(p) == 3:
                text_values.append(
                    "point number="
                    + str(i)
                    + "<br>"
                    + "connection to next point="
                    + str(p[2])
                    + "<br>"
                    + "x="
                    + str(p[0])
                    + "<br>"
                    + "z="
                    + str(p[1])
                    + "<br>"
                )
            else:
                text_values.append(
                    "point number="
                    + str(i)
                    + "<br>"
                    + "x="
                    + str(p[0])
                    + "<br>"
                    + "z="
                    + str(p[1])
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
            self, filename, xmin=0., xmax=900., ymin=-600., ymax=600.):
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

        p = self._create_patch()

        ax.add_collection(p)

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
            ValueError("No points defined for", self)

        patches = []
        xylist = []

        for point in self.points:
            xylist.append([point[0], point[1]])

        polygon = Polygon(xylist, closed=True)
        patches.append(polygon)

        p = PatchCollection(patches)

        if self.color is not None:
            p.set_facecolor(self.color)
            p.set_color(self.color)
            p.color = self.color
            p.edgecolor = self.color
            # checks to see if an alpha value is provided in the color
            if len(self.color) == 4:
                p.set_alpha = self.color[-1]
        self.patch = p
        return p

    def neutronics_description(self):
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

        if self.stl_filename is not None:
            neutronics_description["stl_filename"] = self.stl_filename

        return neutronics_description

    def get_hash(self):
        hash_object = blake2b()
        shape_dict = dict(self.__dict__)
        # set _solid and _hash_value to None to prevent unnecessary
        # reconstruction
        shape_dict["_solid"] = None
        shape_dict["_hash_value"] = None

        hash_object.update(str(list(shape_dict.values())).encode("utf-8"))
        value = hash_object.hexdigest()
        return value

    def perform_boolean_operations(self, solid):
        """Performs boolean cut, intersect and union operations if shapes are
        provided"""

        # If a cut solid is provided then perform a boolean cut
        if self.cut is not None:
            solid = cut_solid(solid, self.cut)

        # If an intersect is provided then perform a boolean intersect
        if self.intersect is not None:
            solid = intersect_solid(solid, self.intersect)

        # If an intersect is provided then perform a boolean intersect
        if self.union is not None:
            solid = union_solid(solid, self.union)

        self.hash_value = self.get_hash()

        return solid

    def _replace(self, filename, pattern, subst):
        """Opens a file and replaces occurances of a particular string
            (pattern)with a new string (subst) and overwrites the file.
            Used internally within the paramak to ensure .STP files are
            in units of cm not the default mm.
        Args:
            filename (str): the filename of the file to edit
            pattern (str): the string that should be removed
            subst (str): the string that should be used in the place of the
                pattern string
        """
        # Create temp file
        fh, abs_path = mkstemp()
        with fdopen(fh, 'w') as new_file:
            with open(filename) as old_file:
                for line in old_file:
                    new_file.write(line.replace(pattern, subst))

        # Copy the file permissions from the old file to the new file
        copymode(filename, abs_path)

        # Remove original file
        remove(filename)

        # Move new file
        move(abs_path, filename)
