from pathlib import Path
from typing import List, Optional, Tuple, Union

import cadquery as cq
import matplotlib.pyplot as plt
from cadquery import exporters

import paramak
from paramak.utils import (
    _replace,
    export_solids_to_brep,
    export_solids_to_dagmc_h5m,
)

from typing import Union, Optional, List, Dict, Any
from cadquery.occ_impl.geom import Location
from cadquery.occ_impl.assembly import Color

from cadquery import Workplane
from cadquery.occ_impl.shapes import Shape, Compound

AssemblyObjects = Union[Shape, Workplane, None]


class Reactor(cq.Assembly):
    """The Reactor object is an extended CadQuery Assembly object. The
    additional functionality allows shapes and components to be exported to
    a variety of additional formats

    Args:
        shapes_and_components: list of paramak.Shape objects
    """

    def __init__(
        self,
        obj: AssemblyObjects = None,
        loc: Optional[Location] = None,
        name: Optional[str] = None,
        color: Optional[Color] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):

        super().__init__(obj, loc, name, color, metadata)

    # def __init__(
    #     self
    # ):

    # self.name="reactor"
    # super().__init__()

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

        return show(self, **kwargs)

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
        """

        output_filename = export_solids_to_dagmc_h5m(
            solids=self,
            filename=filename,
            min_mesh_size=min_mesh_size,
            max_mesh_size=max_mesh_size,
            verbose=verbose,
            volume_atol=volume_atol,
            center_atol=center_atol,
            bounding_box_atol=bounding_box_atol,
            tags=[child.name for child in self.children],
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
    ) -> str:
        """Exports a brep file for the Reactor.

        Args:
            filename: the filename of exported the brep file.

        Returns:
            filename of the brep created
        """

        geometry_to_save = [shape.solid for shape in self.shapes_and_components]

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

        Returns:
            list: a list of stl filenames created
        """

        if isinstance(filename, str):

            path_filename = Path(filename)

            if path_filename.suffix != ".stl":
                path_filename = path_filename.with_suffix(".stl")

            path_filename.parents[0].mkdir(parents=True, exist_ok=True)

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
