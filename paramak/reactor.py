import collections
import json
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import List, Optional, Tuple, Union

import cadquery as cq
import matplotlib.pyplot as plt
from cadquery import Compound, exporters

import paramak
from paramak.utils import _replace, get_hash


class Reactor:
    """The Reactor object allows shapes and components to be added and then
    collective operations to be performed on them. Combining all the shapes is
    required for creating images of the whole reactor and creating a Graveyard
    (bounding box) that is useful for neutronics simulations.

    Args:
        shapes_and_components: list of paramak.Shape objects
        graveyard_size: The dimension of cube shaped the graveyard region used
            by DAGMC. This attribute is used preferentially over
            graveyard_offset.
        graveyard_offset: The distance between the graveyard and the largest
            shape. If graveyard_size is set the this is ignored.
        largest_shapes: Identifying the shape(s) with the largest size in each
            dimension (x,y,z) can speed up the production of the graveyard.
            Defaults to None which finds the largest shapes by looping through
            all the shapes and creating bounding boxes. This can be slow and
            that is why the user is able to provide a subsection of shapes to
            use when calculating the graveyard dimensions.
    """

    def __init__(
        self,
        shapes_and_components: List[paramak.Shape] = [],
        graveyard_size: Optional[float] = 20_000,
        graveyard_offset: Optional[float] = None,
        largest_shapes: Optional[List[paramak.Shape]] = None,
    ):

        self.shapes_and_components = shapes_and_components
        self.graveyard_offset = graveyard_offset
        self.graveyard_size = graveyard_size
        self.largest_shapes = largest_shapes

        self.input_variable_names = [
            # 'shapes_and_components', commented out to avoid calculating solids
            "graveyard_size",
            "graveyard_offset",
            "largest_shapes",
        ]

        self.stp_filenames = []
        self.stl_filenames = []

        self.tet_meshes = []
        self.graveyard = None
        self.solid = None

        self.reactor_hash_value = None

    @property
    def input_variables(self):
        all_input_variables = {}
        for name in self.input_variable_names:
            all_input_variables[name] = getattr(self, name)
        return all_input_variables

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
    def largest_dimension(self):
        """Calculates a bounding box for the Reactor and returns the largest
        absolute value of the largest dimension of the bounding box"""
        largest_dimension = 0

        if self.largest_shapes is None:
            shapes_to_bound = self.shapes_and_components
        else:
            shapes_to_bound = self.largest_shapes

        for component in shapes_to_bound:
            largest_dimension = max(
                largest_dimension,
                component.largest_dimension)
        # self._largest_dimension = largest_dimension
        return largest_dimension

    @largest_dimension.setter
    def largest_dimension(self, value):
        self._largest_dimension = value

    @property
    def tet_meshes(self):
        values = []
        for shape_or_component in self.shapes_and_components:
            values.append(shape_or_component.tet_mesh)
        return values

    @tet_meshes.setter
    def tet_meshes(self, value):
        self._tet_meshes = value

    @property
    def largest_shapes(self):
        return self._largest_shapes

    @largest_shapes.setter
    def largest_shapes(self, value):
        if not isinstance(value, (list, tuple, type(None))):
            raise ValueError(
                "paramak.Reactor.largest_shapes should be a "
                "list of paramak.Shapes")
        self._largest_shapes = value

    @property
    def shapes_and_components(self):
        """Adds a list of parametric shape(s) and or parametric component(s)
        to the Reactor object. This allows collective operations to be
        performed on all the shapes in the reactor."""
        if hasattr(self, "create_solids"):
            ignored_keys = ["reactor_hash_value"]
            if get_hash(self, ignored_keys) != self.reactor_hash_value:
                self.create_solids()
                self.reactor_hash_value = get_hash(self, ignored_keys)
        return self._shapes_and_components

    @shapes_and_components.setter
    def shapes_and_components(self, value):
        if not isinstance(value, (Iterable, str)):
            raise ValueError("shapes_and_components must be a list")
        self._shapes_and_components = value

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
        """This combines all the parametric shapes and components in the
        reactor object.
        """

        list_of_cq_vals = []
        for shape_or_compound in self.shapes_and_components:
            if isinstance(
                shape_or_compound.solid,
                (cq.occ_impl.shapes.Shape, cq.occ_impl.shapes.Compound),
            ):
                for solid in shape_or_compound.solid.Solids():
                    list_of_cq_vals.append(solid)
            else:
                list_of_cq_vals.append(shape_or_compound.solid.val())

        compound = cq.Compound.makeCompound(list_of_cq_vals)

        return compound

    @property
    def name(self):
        """Returns a list of names of the individual Shapes that make up the
        reactor"""

        all_names = []
        for shape in self.shapes_and_components:
            all_names.append(shape.name)

        return all_names

    @solid.setter
    def solid(self, value):
        self._solid = value

    def show(self, default_edgecolor: Tuple[float, float, float] = (0, 0, 0)):
        """Shows / renders the CadQuery the 3d object in Jupyter Lab. Imports
        show from jupyter_cadquery.cadquery and returns show(Reactor.solid)

        Args:
            default_edgecolor: the color to use for the edges, passed to
                jupyter_cadquery.cadquery show. Tuple of three values expected
                individual values in the tuple should be floats between 0. and
                1.

        Returns:
            jupyter_cadquery.cadquery.show object
        """

        try:
            from jupyter_cadquery.cadquery import Part, PartGroup, show
        except ImportError:
            msg = (
                "To use Reactor.show() you must install jupyter_cadquery. To"
                'install jupyter_cadquery type "pip install jupyter_cadquery"'
                " in the terminal"
            )
            raise ImportError(msg)

        parts = []
        for shape_or_compound in self.shapes_and_components:

            if shape_or_compound.name is None:
                name = "Shape.name not set"
            else:
                name = shape_or_compound.name

            scaled_color = [int(i * 255) for i in shape_or_compound.color[0:3]]
            scaled_edge_color = [int(i * 255) for i in default_edgecolor[0:3]]
            if isinstance(
                shape_or_compound.solid,
                (cq.occ_impl.shapes.Shape, cq.occ_impl.shapes.Compound),
            ):
                for i, solid in enumerate(shape_or_compound.solid.Solids()):
                    parts.append(
                        Part(
                            solid,
                            name=f"{name}{i}",
                            color=scaled_color))
            else:
                parts.append(
                    Part(
                        shape_or_compound.solid.val(),
                        name=f"{name}",
                        color=scaled_color,
                    )
                )

        return show(PartGroup(parts), default_edgecolor=scaled_edge_color)

    def export_stp(
        self,
        filename: Union[List[str], str] = None,
        mode: Optional[str] = "solid",
        units: Optional[str] = "mm",
    ) -> Union[List[str], str]:
        """Exports the 3D reactor model as a stp file or files.

        Args:
            filename: Accepts a single filename as a string which exports the
                full reactor model to a single file. Alternativley filename can
                also accept a list of strings where each string is the filename
                of the the individual shapes that make it up. This will result
                in separate files for each shape in the reactor. Defaults to
                None which uses the Reactor.name with '.stp' appended to the end
                of each entry.
            mode: the object to export can be either 'solid' which exports 3D
                solid shapes or the 'wire' which exports the wire edges of the
                shape.
            units: the units of the stp file, options are 'cm' or 'mm'.
                Default is mm.
        Returns:
            The stp filename(s) created
        """

        if isinstance(filename, str):

            # exports a single file for the whole model
            assembly = cq.Assembly(name="reactor")
            for entry in self.shapes_and_components:
                if entry.color is None:
                    assembly.add(entry.solid)
                else:
                    assembly.add(entry.solid, color=cq.Color(*entry.color))

            assembly.save(filename, exportType="STEP")

            if units == "cm":
                _replace(
                    filename,
                    "SI_UNIT(.MILLI.,.METRE.)",
                    "SI_UNIT(.CENTI.,.METRE.)")

            return [filename]

        if filename is None:
            filename = [f"{name}.stp" for name in self.name]

        # exports the reactor solid as a separate stp files
        if len(filename) != len(self.shapes_and_components):
            msg = (
                f"The Reactor contains {len(self.shapes_and_components)} "
                f"Shapes and {len(filename)} filenames have be provided"
            )
            raise ValueError(msg)

        for stp_filename, entry in zip(filename, self.shapes_and_components):

            entry.export_stp(
                filename=stp_filename,
                mode=mode,
                units=units,
                verbose=False,
            )

            if units == "cm":
                _replace(
                    stp_filename,
                    "SI_UNIT(.MILLI.,.METRE.)",
                    "SI_UNIT(.CENTI.,.METRE.)")

        return filename

    def export_brep(self, filename):
        """Exports a brep file for the Reactor.solid.

        Args:
            filename: the filename of exported the brep file.
        """

        path_filename = Path(filename)

        if path_filename.suffix != ".brep":
            msg = "When exporting a brep file the filename must end with .brep"
            raise ValueError(msg)

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        self.solid.exportBrep(str(path_filename))
        # alternative method is to use BRepTools that might support imprinting
        # and merging https://github.com/CadQuery/cadquery/issues/449

        return str(path_filename)

    def export_stl(
        self,
        filename: Union[List[str], str],
        tolerance: Optional[float] = 0.001,
        angular_tolerance: Optional[float] = 0.1,
    ) -> List[str]:
        """Writes stl files (CAD geometry) for each Shape object in the reactor

        Args:
            filename: Accepts a single filename as a string which exports the
                full reactor model to a single file. Alternativley filename can
                also accept a list of strings where each string is the filename
                of the the individual shapes that make it up. This will result
                in separate files for each shape in the reactor. Defaults to
                None which uses the Reactor.name with '.stl' appended to the end
                of each entry.
            tolerance (float):  the precision of the faceting
            include_graveyard: specify if the graveyard will be included or
                not. If True the the Reactor.make_graveyard will be called
                using Reactor.graveyard_size and Reactor.graveyard_offset
                attribute values.

        Returns:
            list: a list of stl filenames created
        """

        if isinstance(filename, str):

            path_filename = Path(filename)

            if path_filename.suffix != ".stl":
                path_filename = path_filename.with_suffix(".stl")

            path_filename.parents[0].mkdir(parents=True, exist_ok=True)

            # add an include_graveyard that add graveyard if requested
            exporters.export(
                self.solid,
                str(path_filename),
                exportType="STL",
                tolerance=tolerance,
                angularTolerance=angular_tolerance,
            )
            return str(path_filename)

        if filename is None:
            filename = [f"{name}.stl" for name in self.name]

        # exports the reactor solid as a separate stl files
        if len(filename) != len(self.shapes_and_components):
            msg = (
                f"The Reactor contains {len(self.shapes_and_components)} "
                f"Shapes and {len(filename)} filenames have be provided"
            )
            raise ValueError(msg)

        for stl_filename, entry in zip(filename, self.shapes_and_components):

            entry.export_stl(
                filename=stl_filename,
                tolerance=tolerance,
                verbose=False,
            )

        return filename

    def make_sector_wedge(
        self,
        height: Optional[float] = None,
        radius: Optional[float] = None,
        rotation_angle: Optional[float] = None,
    ) -> Union[paramak.Shape, None]:
        """Creates a rotated wedge shaped object that is useful for creating
        sector models in DAGMC where reflecting surfaces are needed. If the
        rotation

        Args:
            height: The height of the rotated wedge. If None then the
                largest_dimension of the model will be used.
            radius: The radius of the rotated wedge. If None then the
                largest_dimension of the model will be used
            rotation_angle: The rotation angle of the wedge will be the
                inverse of the sector

        Returns:
            the paramak.Shape object created
        """

        if rotation_angle is None:
            if hasattr(self, "rotation_angle"):
                rotation_angle = self.rotation_angle
            if rotation_angle is None:
                Warning(
                    "No sector_wedge can be made as rotation_angle"
                    " or Reactor.rotation_angle have not been set"
                )
                return None

        if rotation_angle > 360:
            Warning("No wedge can be made for a rotation angle of 360 or above")
            return None

        if rotation_angle == 360:
            print("No sector wedge made as rotation angle is 360")
            return None

        if height is None:
            height = self.largest_dimension * 2

        if radius is None:
            radius = self.largest_dimension * 2

        sector_cutting_wedge = paramak.CuttingWedge(
            height=height,
            radius=radius,
            rotation_angle=360 - rotation_angle,
            surface_reflectivity=True,
            azimuth_placement_angle=rotation_angle,
        )

        self.sector_wedge = sector_cutting_wedge

        return sector_cutting_wedge

    def export_svg(
        self,
        filename: Optional[str] = "reactor.svg",
        projectionDir: Tuple[float, float, float] = (-1.75, 1.1, 5),
        width: Optional[float] = 1000,
        height: Optional[float] = 800,
        marginLeft: Optional[float] = 120,
        marginTop: Optional[float] = 100,
        strokeWidth: Optional[float] = None,
        strokeColor: Optional[Tuple[int, int, int]] = (0, 0, 0),
        hiddenColor: Optional[Tuple[int, int, int]] = (100, 100, 100),
        showHidden: Optional[bool] = False,
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
                the diagram. Defaults to False.
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

        exporters.export(
            self.solid,
            str(path_filename),
            exportType="SVG",
            opt=opt)

        print("Saved file as ", path_filename)

        return str(path_filename)

    def export_stp_graveyard(
        self,
        filename: Optional[str] = "graveyard.stp",
        graveyard_size: Optional[float] = None,
        graveyard_offset: Optional[float] = None,
    ) -> str:
        """Writes a stp file (CAD geometry) for the reactor graveyard. This
        is needed for DAGMC simulations. This method also calls
        Reactor.make_graveyard() with the graveyard_size and graveyard_size
        values.

        Args:
            filename (str): the filename for saving the stp file. Appends
                .stp to the filename if it is missing.
            graveyard_size: directly sets the size of the graveyard. Defaults
                to None which then uses the Reactor.graveyard_size attribute.
            graveyard_offset: the offset between the largest edge of the
                geometry and inner bounding shell created. Defaults to None
                which then uses Reactor.graveyard_offset attribute.

        Returns:
            str: the stp filename created
        """

        graveyard = self.make_graveyard(
            graveyard_offset=graveyard_offset,
            graveyard_size=graveyard_size,
        )

        path_filename = Path(filename)

        if path_filename.suffix != ".stp":
            path_filename = path_filename.with_suffix(".stp")

        graveyard.export_stp(filename=str(path_filename))

        return str(path_filename)

    def make_graveyard(
        self,
        graveyard_size: Optional[float] = None,
        graveyard_offset: Optional[float] = None,
    ) -> paramak.Shape:
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
            CadQuery solid: a shell volume that bounds the geometry, referred
            to as a graveyard in DAGMC
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
            graveyard_size_to_use = (
                self.largest_dimension * 2 + self.graveyard_offset * 2
            )

        else:
            raise ValueError(
                "the graveyard_size, Reactor.graveyard_size, \
                graveyard_offset and Reactor.graveyard_offset are all None. \
                Please specify at least one of these attributes or arguments"
            )

        graveyard_shape = paramak.HollowCube(
            length=graveyard_size_to_use,
            name="graveyard",
        )

        self.graveyard = graveyard_shape

        return graveyard_shape

    def export_2d_image(
        self,
        filename: Optional[str] = "2d_slice.png",
        xmin: Optional[float] = 0.0,
        xmax: Optional[float] = 900.0,
        ymin: Optional[float] = -600.0,
        ymax: Optional[float] = 600.0,
    ) -> str:
        """Creates a 2D slice image (png) of the reactor.

        Args:
            filename (str): output filename of the image created

        Returns:
            str: png filename created
        """

        path_filename = Path(filename)

        if path_filename.suffix != ".png":
            path_filename = path_filename.with_suffix(".png")

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        fig, ax = plt.subplots()

        # creates indvidual patches for each Shape which are combined together
        for entry in self.shapes_and_components:
            patch = entry._create_patch()
            ax.add_collection(patch)

        ax.axis("equal")
        ax.set(xlim=(xmin, xmax), ylim=(ymin, ymax))
        ax.set_aspect("equal", "box")

        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(filename, dpi=100)
        plt.close()

        print("\n saved 2d image to ", str(path_filename))

        return str(path_filename)

    def export_html_3d(
        self,
        filename: Optional[str] = "reactor_3d.html",
    ) -> str:
        """Saves an interactive 3d html view of the Reactor to a html file.

        Args:
            filename: the filename used to save the html graph. Defaults to
                reactor_3d.html

        Returns:
            str: filename of the created html file
        """

        from ipywidgets.embed import embed_minimal_html

        view = self.show()

        if view is None:
            return None

        embed_minimal_html(
            filename,
            views=[
                view.cq_view.renderer],
            title="Renderer")

        return filename

    def export_html(
        self,
        filename: Optional[str] = "reactor.html",
        facet_splines: Optional[bool] = True,
        facet_circles: Optional[bool] = True,
        tolerance: Optional[float] = 1.0,
        view_plane: Optional[str] = "RZ",
    ):
        """Creates a html graph representation of the points for the Shape
        objects that make up the reactor. Shapes are colored by their .color
        property. Shapes are also labelled by their .name. If filename provided
        doesn't end with .html then .html will be added.

        Args:
            filename: the filename used to save the html graph. Defaults to
                reactor.html
            facet_splines: If True then spline edges will be faceted. Defaults
                to True.
            facet_circles: If True then circle edges will be faceted. Defaults
                to True.
            tolerance: faceting toleranceto use when faceting cirles and
                splines. Defaults to 1e-3.
            view_plane: The plane to project. Options are 'XZ', 'XY', 'YZ',
                'YX', 'ZY', 'ZX', 'RZ' and 'XYZ'. Defaults to 'RZ'. Defaults to
                'RZ'.
        Returns:
            plotly.Figure(): figure object
        """

        fig = paramak.utils.export_wire_to_html(
            wires=self.solid.Edges(),
            filename=filename,
            view_plane=view_plane,
            facet_splines=facet_splines,
            facet_circles=facet_circles,
            tolerance=tolerance,
            title="coordinates of the "
            + self.__class__.__name__
            + " reactor, viewed from the "
            + view_plane
            + " plane",
            mode="lines",
        )

        return fig

    def volume(self, split_compounds: bool = False) -> List[float]:
        """Get the volumes of the Shapes in the Reactor.

        Args:
            split_compounds: If the Shape is a compound of Shapes and therefore
                contains multiple volumes. This option allows access to the separate
                volumes of each component within a Shape (True) or the volumes of
                compounds can be summed (False).

        Returns:
            The the volumes of the Shapes
        """

        all_volumes = []
        for shape in self.shapes_and_components:
            all_volumes.append(shape.volume(split_compounds=split_compounds))
        return all_volumes
