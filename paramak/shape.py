import json
import math
import numbers
from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from PIL import Image
from hashlib import blake2b

from cadquery import exporters


class Shape:
    """A shape object that represents a 3d volume and can have materials and
    neutronics tallies assigned. Shape objects are not intended to be used
    directly bly the user but provide basic functionality for user-facing
    classes that inherit from Shape.

    Args:
        points (list of (x,y,z) tuples where x, y, z are floats): the x, y, z
            coordinates of points that make up the shape
        name (str): the name of the shape, used in the graph legend by export_html
        color (RGB or RGBA, sequences of 3 or 4 floats, respectively, each in the
            range 0-1): the color to use when exporting as html graphs or png images
        material_tag (str): the material name to use when exporting the neutronics
            description
        stp_filename (str): the filename used when saving stp files
        azimuth_placement_angle: the azimuth angle(s) used when positioning the shape.
            If a list of angles is provided, the shape is duplicated at all angles
        workplane (str): the orientation of the Cadquery workplane. (XY, YZ or XZ)

    Returns:
        a paramak shape object: a Shape object that has generic functionality
    """

    def __init__(
        self,
        points=None,
        name=None,
        color=None,
        material_tag=None,
        stp_filename=None,
        stl_filename=None,
        azimuth_placement_angle=0,
        workplane="XZ",
        tet_mesh=None,
        physical_groups=None,
        hash_value=None,
    ):

        self.points = points
        self.stp_filename = stp_filename
        self.stl_filename = stl_filename
        self.color = color
        self.name = name

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
                warnings.warn(
                    "Shape.material_tag > 28 characters. Use with DAGMC will be affected." +
                    str(value),
                    UserWarning)
            self._material_tag = value
        else:
            raise ValueError("Shape.material_tag must be a string", value)

    @property
    def tet_mesh(self):
        return self._tet_mesh

    @tet_mesh.setter
    def tet_mesh(self, value):
        if value is None:
            self._tet_mesh = value
        elif isinstance(value, str):
            self._tet_mesh = value
        else:
            raise ValueError("Shape.tet_mesh must be a string", value)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value is None:
            self._name = value
        elif isinstance(value, str):
            self._name = value
        else:
            raise ValueError("Shape.name must be a string", value)

    @property
    def points(self):
        """Sets the Shape.point attributes.

        Args:
            points (a list of lists or tuples): list of points that create the shape

        Raises:
            incorrect type: only list of lists or tuples are accepted
        """

        return self._points

    @points.setter
    def points(self, values):

        if values is None:
            self._points = values
        else:
            if not isinstance(values, list):
                raise ValueError("points must be a list")

            for value in values:
                if type(value) not in [list, tuple]:
                    raise ValueError(
                        "individual points must be a list or a tuple.",
                        value,
                        " in of type ",
                        type(value),
                    )

            for value in values:
                # Checks that the length of each tuple in points is 2 or 3
                if len(value) not in [2, 3]:
                    raise ValueError(
                        "individual points contain 2 or 3 entries",
                        value,
                        " has a length of ",
                        len(values[0]),
                    )

                # Checks that the XY points are numbers
                if not isinstance(value[0], numbers.Number):
                    raise ValueError(
                        "The first value in the tuples that make \
                                        up the points represents the X value and \
                                        must be a number",
                        value,
                    )
                if not isinstance(value[1], numbers.Number):
                    raise ValueError(
                        "The second value in the tuples that make \
                                      up the points represents the X value and \
                                      must be a number",
                        value,
                    )

                # Checks that only straight and spline are in the connections
                # part of points
                if len(value) == 3:
                    if value[2] not in ["straight", "spline", "circle"]:
                        raise ValueError(
                            'individual connections must be either "straight" or "spline"'
                        )

            # checks that the entries in the points are either all 2 long or
            # all 3 long, not a mixture
            if not all(len(entry) == 2 for entry in values):
                if not all(len(entry) == 3 for entry in values):
                    raise ValueError(
                        "The points list should contain entries of length 2 or 3 but not a mixture of 2 and 3"
                    )

            if len(values) > 1:
                if values[-1][0] == values[0][0] and values[-1][1] == values[0][1]:
                    raise ValueError(
                        "The coordinates of the last and first points are the same."
                    )
                else:
                    values.append(values[0])

            self._points = values

    @property
    def stp_filename(self):
        """Sets the Shape.stp_filename attribute which is used as the filename when
        exporting the geometry to stp format. Note, .stp will be added to filenames
        not ending with .step or .stp.

        Args:
            value (str): the value to use as the stp_filename

        Raises:
            incorrect type: only str values are accepted
        """

        return self._stp_filename

    @stp_filename.setter
    def stp_filename(self, value):
        if value is None:
            # print("stp_filename will need setting to use this shape in a Reactor")
            self._stp_filename = value
        elif isinstance(value, str):
            if Path(value).suffix == ".stp" or Path(value).suffix == ".step":
                self._stp_filename = value
            else:
                raise ValueError(
                    "Incorrect filename ending, filename must end with .stp or .step"
                )
        else:
            raise ValueError(
                "stp_filename must be a string",
                value,
                type(value))

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
        if value is None:
            # print("stl_filename will need setting to use this shape in a Reactor")
            self._stl_filename = value
        elif isinstance(value, str):
            if Path(value).suffix == ".stl":
                self._stl_filename = value
            else:
                raise ValueError(
                    "Incorrect filename ending, filename must end with .stl"
                )
        else:
            raise ValueError(
                "stl_filename must be a string",
                value,
                type(value))

    def create_limits(self):
        """Finds the x,y,z limits (min and max) of the points that make up the face of the shape.
        Note the Shape may extend beyond this boundary if splines are used to connect points.

        Raises:
            ValueError: if no points are defined

        Returns:
            float, float, float, float, float, float: x_minimum, x_maximum, y_minimum, y_maximum,
            z_minimum, z_maximum
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
        """Exports an stl file for the Shape.solid. If the provided filename doesn't end with .stl
        it will be added

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
        """Exports an stp file for the Shape.solid. If the filename provided doesn't end with
        .stp or .step then .stp will be added. If a filename is not provided and the shape's
        stp_filename property is not None the stp_filename will be used as the export filename.

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
        """Creates a html graph representation of the points and connections for
        the Shape object. Shapes are colored by their .color property. Shapes are
        also labelled by their .name. If filename provided doesn't end with .html
        then .html will be added.

        Args:
            filename (str): the filename used to save the html graph

        Returns:
            plotly figure: figure object
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
        """Creates a plotly trace representation of the points of the Shape object.
        This method is intended for internal use by Shape.export_html.

        Returns:
            plotly trace: trace object
        """

        # provides a default color if color is not set
        if self.color is None:
            color = "grey"
        else:
            color = self.color

        if self.name is None:
            name = "Shape not named"
        else:
            name = self.name

        text_values = []
        # for mixed shapes there are also connections added to the plot
        if hasattr(self, "connections"):
            if len(self.points[0]) == 3:
                for i, (p, c) in enumerate(zip(self.points[:-1])):
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
        # connections are not avaialbe for some shapes
        else:
            for i, p in enumerate(self.points):
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
                "marker": {"size": 4, "color": color},
                "name": name,
            }
        )

        return trace

    def export_2d_image(self, filename, xmin=0, xmax=900, ymin=-600, ymax=600):
        """Exports a 2d image (png) of the reactor. Components are colored by their
        Shape.color property. If filename provided doesn't end with .png then .png
        will be added.

        Args:
            filename (str): the filename of the saved png image
            xmin (float): the minimum x value of the x axis
            xmax (float): the maximum x value of the x axis
            ymin (float): the minimum y value of the y axis
            ymax (float); the maximum y value of the y axis

        Returns:
            matplotlib plot: a plt object
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

        for x1, z1 in zip(
            [row[0] for row in self.points], [row[1] for row in self.points]
        ):
            xylist.append([x1, z1])

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
        for the use with automated neutronics model methods which require linkage
        between the stp files and materials. If tet meshing of the volume is required
        then Trelis meshing commands can be optionally specified as the tet_mesh
        argument.

        Returns:
            dictionary: a dictionary of the step filename and material name
        """

        neutronics_description = {"material": self.material_tag}

        if self.stp_filename is not None:
            neutronics_description["stp_filename"] = self.stp_filename

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
