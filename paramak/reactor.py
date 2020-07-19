import json
import math
from collections import Iterable
from pathlib import Path

import cadquery as cq
import matplotlib.pyplot as plt
import numpy as np
from cadquery import exporters
from PIL import Image

import paramak
import plotly.graph_objects as go
import pyrender
from paramak.shape import Shape


class Reactor():

    """The Reactor object allows Shapes to be added and then collective 
    opperations to be performed on all the Shapes within the Reactor.
    Combining all the shapes is required for creating images of the whole reactor and 
    creating a Graveyard (bounding box) that is needed for neutronics simulations.
    """

    def __init__(self):

        self.graveyard = None
        self.shapes_and_components = []
        self.material_tags = []
        self.stp_filenames = []
        self.solid = None

    @property
    def solid(self):
        return cq.Compound.makeCompound([a.solid.val() for a in self.shapes_and_components])

    @solid.setter
    def solid(self, value):
        self._solid = value

    def add_shape_or_component(self, shapes):
        """Adds a parametric shape(s) or a parametric component(s) to the Reactor 
        object. An individual shape/component or a list of shapes/ components are
        added to the Reactor object so that collective operations can be performed
        on all the shapes in the reactor. When adding a shape or componet the 
        stp_filename for the shape or compnent should not already be used in the 
        reactor.
        """
        if isinstance(shapes, Iterable):
            for shape in shapes:
                if shape.material_tag != None:
                    self.material_tags.append(shape.material_tag)
                if shape.stp_filename != None:
                    if shape.stp_filename in self.stp_filenames:
                        raise ValueError(
                            "Set Reactor already contains a shape or component \
                                 with this stp_filename", shapes.stp_filename
                        )
                    else:
                        self.stp_filenames.append(shape.stp_filename)
                self.shapes_and_components.append(shape)
        else:
            if shapes.material_tag != None:
                self.material_tags.append(shapes.material_tag)
            if shapes.stp_filename != None:
                if shapes.stp_filename in self.stp_filenames:
                    raise ValueError(
                        "Set Reactor already contains a shape or component \
                                with this stp_filename", shapes.stp_filename
                    )
                else:
                    self.stp_filenames.append(shapes.stp_filename)
            self.shapes_and_components.append(shapes)

    def neutronics_description(self, include_plasma=False):
        """A description of the reactor containing materials tags,
        stp filenames, tet mesh instructions. This is can be used
        for neutronics simulations which require linkage between
        volumes, materials and identification of which volumes to
        tet mesh. The plasma geometry is not included by default
        as it is typically not included in neutronics simulations.
        The reason for this is that the low number density results
        in minimal interaction with neutrons. However it can be added
        if the include_plasma argument is set to True

        :return: a dictionary of materials and filenames for the reactor
        :rtype: dictionary
        """

        neutronics_description = []

        for entry in self.shapes_and_components:

            if include_plasma==False and isinstance(entry,paramak.Plasma) == True:
                continue

            if entry.stp_filename is None:
                raise ValueError(
                    "Set Shape.stp_filename for all the \
                                  Reactor entries before using this method"
                )

            if entry.material_tag is None:
                raise ValueError(
                    "set Shape.material_tag for all the \
                                  Reactor entries before using this method"
                )

            if entry.tet_mesh == None:
                Shape_neutronics_description = entry.neutronics_description(
                    stp_filename=entry.stp_filename,
                    material_tag=entry.material_tag 
                )
            else:
                Shape_neutronics_description = entry.neutronics_description(
                    stp_filename=entry.stp_filename,
                    material_tag=entry.material_tag,
                    tet_mesh=entry.tet_mesh 
                )

            neutronics_description.append(Shape_neutronics_description)

        # This add the neutronics descirption for the graveyard which is unique as
        # it is automatically calculated instead of being added by the user.
        # Also the graveyard must have 'Graveyard' as the material name
        if self.graveyard is None:
            self.make_graveyard()
        neutronics_description.append(
            self.graveyard.neutronics_description(
                stp_filename="Graveyard.stp", material_tag="Graveyard"
            )
        )

        return neutronics_description

    def export_neutronics_description(self, filename="manifest.json", include_plasma=False):
        """Saves Reactor.neutronics_description to a json file.
        The resulting json file contains a list of dictionaries.
        Each dictionary entry comprising of a material and a
        filename and optionally a tet_mesh instruction. The json
        file can then be used with the neutronics workflows to
        create a neutronics model. Creation of the netronics
        model requires linkage between volumes, materials and
        identifcation of which volumes to tet_mesh. If the 
        filename does not end with .json then .json will be added.
        The plasma geometry is not included by default as it is
        typically not included in neutronics simulations. The 
        reason for this is that the low number density results
        in minimal interaction with neutrons. However the plasma
        can be added if the include_plasma argument is set to True

        :param filename: the filename used to save the neutronics description
        :type filename: str
        """

        Pfilename = Path(filename)

        if Pfilename.suffix != ".json":
            Pfilename = Pfilename.with_suffix(".json")

        Pfilename.parents[0].mkdir(parents=True, exist_ok=True)

        with open(filename, "w") as outfile:
            json.dump(self.neutronics_description(include_plasma=include_plasma), outfile, indent=4)

        print("saved geometry description to ", Pfilename)

        return filename

    def export_stp(self, output_folder=""):
        """Writes stp files (CAD geometry) for each Shape object in the reactor

        :param output_folder: the folder for saving the stp files to
        :type output_folder: str

        :return: a list of stp filenames created
        :rtype: list
        """

        filenames = []
        for entry in self.shapes_and_components:
            if entry.stp_filename is None:
                raise ValueError(
                    "set .stp_filename property for \
                                 Shapes before using the export_stp method"
                )
            filenames.append(str(Path(output_folder) / Path(entry.stp_filename)))
            entry.export_stp(Path(output_folder) / Path(entry.stp_filename))

        # creates a graveyard (bounding shell volume) which is needed for nuetronics simulations
        self.make_graveyard()
        filenames.append(str(Path(output_folder) / Path(self.graveyard.stp_filename)))
        self.graveyard.export_stp(
            Path(output_folder) / Path(self.graveyard.stp_filename)
        )

        print("exported stp files ", filenames)

        return filenames

    def export_physical_groups(self, output_folder=""):
        """Exports several JSON files containing a look up table
        which is useful for identifying faces and volumes. The
        output file names are generated from .stp_filename properties.

        Args:
            output_folder (str, optional): directory of outputfiles.
                Defaults to "".

        Raises:
            ValueError: if one .stp_filename property is set to None

        Returns:
            list: list of output file names
        """
        filenames = []
        for entry in self.shapes_and_components:
            if entry.stp_filename is None:
                raise ValueError(
                    "set .stp_filename property for \
                                 Shapes before using the export_stp method"
                )
            filenames.append(str(Path(output_folder) / Path(entry.stp_filename)))
            entry.export_physical_groups(Path(output_folder) / Path(entry.stp_filename))
        return filenames

    def export_svg(self, filename):
        """Exports an svg file for the Reactor.solid.
        If the provided filename doesn't end with .svg it will be added

        :param filename: the filename of the svg
        :type filename: str
        """

        Pfilename = Path(filename)

        if Pfilename.suffix != ".svg":
            Pfilename = Pfilename.with_suffix(".svg")

        Pfilename.parents[0].mkdir(parents=True, exist_ok=True)

        with open(Pfilename, "w") as f:
            exporters.exportShape(self.solid, "SVG", f)
        print("Saved file as ", Pfilename)

    def export_graveyard(self, filename="Graveyard.stp"):
        """Writes a stp file (CAD geometry) for the reactor graveyard.
           Thich is needed for DAGMC simulations

        :param filename: the filename for saving the stp file to
        :type filename: str

        :return: the stp filename created
        :rtype: str
        """
        self.make_graveyard()
        self.graveyard.export_stp(Path(filename))
        return filename

    def make_graveyard(self):
        """Creates a graveyard volume (bounding box) that encapsulates all
           volumes. This is required by DAGMC when performing neutronics
           simulations.

        :return: graveyard 3d volume object
        :rtype: CadQuery solid
        """

        for component in self.shapes_and_components:
            if component.solid is None:
                component.create_solid()

        # finds the largest dimenton in all the Shapes that are in the reactor
        largest_dimension = 0
        for component in self.shapes_and_components:
            if component.solid.largestDimension() > largest_dimension:
                largest_dimension = component.solid.largestDimension()

        # creates a small box that surrounds the geometry
        inner_box = cq.Workplane("front").box(
            largest_dimension, largest_dimension, largest_dimension
        )
        offset = 500

        # creates a large box that surrounds the smaller box
        outer_box = cq.Workplane("front").box(
            largest_dimension + offset,
            largest_dimension + offset,
            largest_dimension + offset,
        )

        # subtracts the two boxes to leave a hollow box
        graveyard_part = outer_box.cut(inner_box)

        graveyard_shape = Shape()
        graveyard_shape.name = "Graveyard"
        graveyard_shape.material_tag = "Graveyard"
        graveyard_shape.stp_filename = "Graveyard.stp"
        graveyard_shape.solid = graveyard_part

        self.graveyard = graveyard_shape

        return graveyard_shape

    def export_2d_image(
        self, filename="2d_slice.png", xmin=0.0, xmax=900.0, ymin=-600.0, ymax=600.0
    ):
        """Creates a 2D slice image (png) of the reactor
        :param filename: output filename of the image created
        :type filename: str

        :return: Png filename created
        :rtype: str
        """

        Pfilename = Path(filename)

        if Pfilename.suffix != ".png":
            Pfilename = Pfilename.with_suffix(".png")

        Pfilename.parents[0].mkdir(parents=True, exist_ok=True)

        fig, ax = plt.subplots()

        # creates indvidual patches for each Shape which are combined together
        for entry in self.shapes_and_components:
            p = entry._create_patch()
            ax.add_collection(p)

        ax.axis("equal")
        ax.set(xlim=(xmin, xmax), ylim=(ymin, ymax))
        ax.set_aspect("equal", "box")

        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(filename, dpi=100)
        plt.close()

        print("\n saved 2d image to ", str(Pfilename))

        return str(Pfilename)

    def export_3d_image(self, filename="3d_render.png", tolerance=0.1):
        """Creates a 3D rendered image (png) of the reactor

        :param filename: output filename of the image created
        :type filename: [ParamType](, optional)
        :param tolerance: the mesh tolerance
        :type tolerance: float

        :return: filename of the created image
        :rtype: str
        """

        scene = pyrender.Scene(ambient_light=np.array([0.1, 0.1, 0.1, 1.0]))
        for entry in self.shapes_and_components:
            if entry.render_mesh is None:
                scene.add(entry._create_render_mesh(tolerance))

        # sets the field of view (fov) and the aspect ratio of the image
        camera = pyrender.camera.PerspectiveCamera(
            yfov=math.radians(90.0), aspectRatio=2.0
        )

        # sets the position of the camera using a matrix
        c = 2 ** -0.5
        camera_pose = np.array(
            [[1, 0, 0, 0], [0, c, -c, -1200], [0, c, c, 1200], [0, 0, 0, 1]]
        )
        scene.add(camera, pose=camera_pose)

        # adds some basic lighting to the scene
        light = pyrender.DirectionalLight(color=np.ones(3), intensity=1.0)
        scene.add(light, pose=camera_pose)

        # Render the scene
        renderer = pyrender.OffscreenRenderer(1000, 500)
        colours, depth = renderer.render(scene)

        image = Image.fromarray(colours, "RGB")

        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        image.save(filename, "PNG")
        print("\n saved 3d image to ", filename)

        return filename

    def export_html(self, filename="reactor.html"):
        """Creates a html graph representation of the points
           for the Shape objects that make up the reactor.

         Note:
             If provided filename doesn't end with .html with will be appended

        :param filename: the filename to save the html graph
        :type filename: str

        :return: figure object
        :rtype: plotly figure
        """

        Pfilename = Path(filename)

        if Pfilename.suffix != ".html":
            Pfilename = Pfilename.with_suffix(".html")

        Pfilename.parents[0].mkdir(parents=True, exist_ok=True)

        fig = go.Figure()
        fig.update_layout(
            {"title": "coordinates of components", "hovermode": "closest"}
        )

        # accesses the Shape traces for each Shape and adds them to the figure
        for entry in self.shapes_and_components:
            fig.add_trace(entry._trace())

        fig.write_html(str(Pfilename))
        print("Exported html graph to ", str(Pfilename))

        return fig
