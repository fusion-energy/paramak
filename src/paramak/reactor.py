from collections.abc import Iterable
from pathlib import Path
from typing import List, Optional, Tuple, Union

import cadquery as cq
import matplotlib.pyplot as plt
from cadquery import exporters

import paramak
from paramak.utils import (
    _replace,
    get_hash,
    get_bounding_box,
    get_largest_dimension,
    export_solids_to_brep,
    export_solids_to_dagmc_h5m,
    get_center_of_bounding_box,
)


class Reactor:
    """The Reactor object allows shapes and components to be added and then
    collective operations to be performed on them. Combining all the shapes is
    required for creating images of the whole reactor and creating a Graveyard
    (bounding box) that is useful for neutronics simulations.

    Args:
        shapes_and_components: list of paramak.Shape objects
    """

    def __init__(
        self,
        shapes_and_components: List[paramak.Shape] = [],
    ):

        self.shapes_and_components = shapes_and_components

        self.input_variable_names: List[str] = [
            # 'shapes_and_components', commented out to avoid calculating solids
        ]

        self.stp_filenames: List[str] = []
        self.stl_filenames: List[str] = []

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

        largest_dimension = get_largest_dimension(self.solid)

        return largest_dimension

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

    @solid.setter
    def solid(self, value):
        self._solid = value

    @property
    def name(self):
        """Returns a list of names of the individual Shapes that make up the
        reactor"""

        all_names = []
        for shape in self.shapes_and_components:
            all_names.append(shape.name)

        return all_names

    def show(self, **kwargs):
        """Shows / renders the CadQuery the 3d object in Jupyter Lab. Imports
        show from jupyter_cadquery and returns show(Reactor.solid, kwargs)

        Args:
            kwargs: keyword arguments passed to jupyter-cadquery show()
                function. See https://github.com/bernhard-42/jupyter-cadquery#usage
                for more details on acceptable keywords


        Returns:
            jupyter_cadquery show object
        """

        try:
            from jupyter_cadquery import show
        except ImportError:
            msg = (
                "To use Reactor.show() you must install jupyter_cadquery version "
                '3.2.0 or above. To install jupyter_cadquery type "pip install '
                'jupyter_cadquery" in the terminal'
            )
            raise ImportError(msg)

        assembly = cq.Assembly(name="reactor")
        for entry in self.shapes_and_components:
            if entry.color is None:
                assembly.add(entry.solid)
            else:
                assembly.add(entry.solid, color=cq.Color(*entry.color))

        return show(assembly, **kwargs)

    def export_dagmc_h5m(
        self,
        filename: str = "dagmc.h5m",
        min_mesh_size: float = 5,
        max_mesh_size: float = 20,
        exclude: List[str] = None,
        verbose: bool = False,
        volume_atol: float = 0.000001,
        center_atol: float = 0.000001,
        bounding_box_atol: float = 0.000001,
        tags: Optional[List[str]] = None,
        include_graveyard: Optional[dict] = None,
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
            exclude: A list of shape names to not include in the exported
                geometry. 'plasma' is often excluded as not many neutron
                interactions occur within a low density plasma.
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
            include_graveyard: specify if the graveyard box will be included or
                not and how it will be sized. Leave as None if a graveyard is
                not included. If a graveyard is required then set
                include_graveyard to a dictionary with a key and value.
                Acceptable keys are 'offset' and 'size'. Each key must have a
                float value associated. For example {'size': 1000} or
                {'offset': 10}. The size simple sets the height, width, depth
                of the graveyard while the offset adds to the geometry to get
                the graveyard box size.
        """

        shapes_to_convert = []

        for shape in self.shapes_and_components:
            # allows components like the plasma to be removed
            if exclude:
                if shape.name not in exclude:
                    shapes_to_convert.append(shape)
            else:
                shapes_to_convert.append(shape)

        if include_graveyard:
            graveyard = self.make_graveyard(**include_graveyard)
            shapes_to_convert.append(graveyard)

        if tags is None:
            tags = []
            for shape in shapes_to_convert:
                tags.append(shape.name)

        output_filename = export_solids_to_dagmc_h5m(
            solids=[shape.solid for shape in shapes_to_convert],
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
                _replace(filename, "SI_UNIT(.MILLI.,.METRE.)", "SI_UNIT(.CENTI.,.METRE.)")

            return [filename]

        if filename is None:
            if None in self.name:
                msg = (
                    "Shape.name is None and therefore it can't be used "
                    "to name a stp file. Try setting Shape.name for all "
                    "shapes in the reactor"
                )
                raise ValueError(msg)
            filename = [f"{name}.stp" for name in self.name]

        # exports the reactor solid as a separate stp files
        if len(filename) != len(self.shapes_and_components):
            msg = (
                f"The Reactor contains {len(self.shapes_and_components)} "
                f"Shapes and {len(filename)} filenames have be provided. "
                f"The names of the shapes are {self.name}"
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
                _replace(stp_filename, "SI_UNIT(.MILLI.,.METRE.)", "SI_UNIT(.CENTI.,.METRE.)")

        return filename

    def export_brep(
        self,
        filename: str = "reactor.brep",
        include_graveyard: Optional[dict] = None,
    ) -> str:
        """Exports a brep file for the Reactor. Optionally including a DAGMC
        graveyard.

        Args:
            filename: the filename of exported the brep file.
            include_graveyard: specify if the graveyard box will be included or
                not and how it will be sized. Leave as None if a graveyard is
                not included. If a graveyard is required then set
                include_graveyard to a dictionary with a key and value.
                Acceptable keys are 'offset' and 'size'. Each key must have a
                float value associated. For example {'size': 1000} or
                {'offset': 10}. The size simple sets the height, width, depth
                of the graveyard while the offset adds to the geometry to get
                the graveyard box size.

        Returns:
            filename of the brep created
        """

        geometry_to_save = [shape.solid for shape in self.shapes_and_components]
        if include_graveyard:
            graveyard = self.make_graveyard(**include_graveyard)
            geometry_to_save.append(graveyard.solid)

        output_filename = export_solids_to_brep(
            solids=geometry_to_save,
            filename=filename,
        )

        return output_filename

    def export_stl(
        self,
        filename: Union[List[str], str] = None,
        tolerance: float = 0.001,
        angular_tolerance: float = 0.1,
    ) -> Union[str, List[str]]:
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
            if None in self.name:
                msg = (
                    "Shape.name is None and therefore it can't be used "
                    "to name a stl file. Try setting Shape.name for all "
                    "shapes in the reactor"
                )
                raise ValueError()
            filename = [f"{name}.stl" for name in self.name]

        # exports the reactor solid as a separate stl files
        if len(filename) != len(self.shapes_and_components):
            msg = (
                f"The Reactor contains {len(self.shapes_and_components)} "
                f"Shapes and {len(filename)} filenames have be provided. "
                f"The names of the shapes are {self.name}"
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
                Warning("No sector_wedge can be made as rotation_angle" " or Reactor.rotation_angle have not been set")
                return None

        if rotation_angle > 360:
            Warning("No wedge can be made for a rotation angle of 360 or above")
            return None

        if rotation_angle == 360:
            print("No sector wedge made as rotation angle is 360")
            return None

        # todo this should be cetered around the center point

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

        exporters.export(self.solid, str(path_filename), exportType="SVG", opt=opt)

        print("Saved file as ", path_filename)

        return str(path_filename)

    def make_graveyard(
        self,
        size: Optional[float] = None,
        offset: Optional[float] = None,
    ) -> paramak.Shape:
        """Creates a graveyard volume (bounding box) that encapsulates all
        volumes. This is required by DAGMC when performing neutronics
        simulations. The graveyard size can be ascertained in two ways. Either
        the size can be set directly using the size which is the
        quickest method. Alternativley the graveyard can be automatically sized
        to the geometry by setting a offset value. If both options
        are set then the method will default to using the size
        preferentially.

        Args:
            size: directly sets the size of the graveyard.
            offset: the offset between the largest edge of the geometry and
                inner surface of the graveyard

        Returns:
            CadQuery solid: a shell volume that bounds the geometry, referred
            to as a graveyard in DAGMC
        """

        solid = self.solid

        # makes the graveyard around the center of the geometry
        center = get_center_of_bounding_box(solid)

        if size is not None:
            graveyard_size_to_use = size
            if size <= 0:
                raise ValueError("Graveyard size should be larger than 0")
            largest_dim = get_largest_dimension(solid)
            if size < largest_dim:
                msg = f"Graveyard size should be larger than the largest shape in the Reactor. Which is {largest_dim}"
                raise ValueError(msg)

        elif offset is not None:
            graveyard_size_to_use = get_largest_dimension(solid) * 2 + offset * 2
            if offset <= 0:
                raise ValueError("Graveyard size should be larger than 0")

        else:
            raise ValueError(
                "the graveyard_size, Reactor.graveyard_size, \
                graveyard_offset and Reactor.graveyard_offset are all None. \
                Please specify at least one of these attributes or arguments"
            )

        graveyard_shape = paramak.HollowCube(length=graveyard_size_to_use, name="graveyard", center_coordinate=center)

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

    def export_html_3d(self, filename: Optional[str] = "reactor_3d.html", **kwargs) -> Optional[str]:
        """Saves an interactive 3d html view of the Reactor to a html file.

        Args:
            filename: the filename used to save the html graph. Defaults to
                reactor_3d.html
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
            title=f"coordinates of the {self.__class__.__name__} reactor, viewed from the {view_plane} plane",
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
