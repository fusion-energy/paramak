
import collections
import json
import os
import shutil
from collections.abc import Iterable
from pathlib import Path
from typing import List, Optional, Tuple, Union

import cadquery as cq
import matplotlib.pyplot as plt
from cadquery import exporters

import paramak
from paramak.utils import get_hash, _replace, add_stl_to_moab_core, define_moab_core_and_tags, export_vtk


class Reactor:
    """The Reactor object allows shapes and components to be added and then
    collective operations to be performed on them. Combining all the shapes is
    required for creating images of the whole reactor and creating a Graveyard
    (bounding box) that is needed for neutronics simulations. There are two
    methods available for producing the the DAGMC h5m file. The PyMoab option
    is able to produce non imprinted and non merged geometry so is more suited
    to individual components or reactors without touching surfaces. Trelis is
    the able to produce imprinted and merged DAGMC h5m geometry. Further
    details on imprinting and merging are available on the DAGMC homepage
    https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html . Trelis
    (also known as Cubit) is available from the CoreForm website
    https://www.coreform.com/ version 17.1 is the version of Trelis used when
    testing the Paramak code.

    Args:
        shapes_and_components (list): list of paramak.Shape objects or the
            filename of json file that contains the neutronics description of
            the geometry. The list of dictionaries should each have a
            "material" key containing a material_tag value and a "stp_filename"
            key containing the path to the stp file. See the
            external_stp_file_simulation.py neutronics for a complete example.
            https://github.com/ukaea/paramak/blob/main/examples/example_neutronics_simulations/external_stp_file_simulation.py
        faceting_tolerance: the tolerance to use when faceting surfaces.
        merge_tolerance: the tolerance to use when merging surfaces.
        method: The method to use when making the h5m geometry. Options are
            "trelis" or "pymoab".
        graveyard_size: The dimention of cube shaped the graveyard region used
            by DAGMC. This attribtute is used preferentially over
            graveyard_offset.
        graveyard_offset: The distance between the graveyard and the largest
            shape. If graveyard_size is set the this is ignored.
        largest_shapes: Identifying the shape(s) with the largest size in each
            dimention (x,y,z) can speed up the production of the graveyard.
            Defaults to None which finds the largest shapes by looping through
            all the shapes and creating bounding boxes. This can be slow and
            that is why the user is able to provide a subsection of shapes to
            use when calculating the graveyard dimentions.
        include_graveyard
        include_sector_wedge
    """

    def __init__(
            self,
            shapes_and_components: Union[List[paramak.Shape], str],
            method: str = 'pymoab',
            faceting_tolerance: Optional[float] = 1e-2,
            merge_tolerance: Optional[float] = 1e-4,
            graveyard_size: Optional[float] = 20_000,
            graveyard_offset: Optional[float] = None,
            largest_shapes: Optional[List[paramak.Shape]] = None,
    ):

        self.shapes_and_components = shapes_and_components
        self.graveyard_offset = graveyard_offset
        self.graveyard_size = graveyard_size
        self.largest_shapes = largest_shapes
        self.faceting_tolerance = faceting_tolerance
        self.merge_tolerance = merge_tolerance
        self.method = method

        self.stp_filenames = []
        self.stl_filenames = []
        self.h5m_filename = None
        self.tet_meshes = []
        self.graveyard = None
        self.solid = None

        self.reactor_hash_value = None

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
    def faceting_tolerance(self):
        return self._faceting_tolerance

    @faceting_tolerance.setter
    def faceting_tolerance(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(
                "Reactor.faceting_tolerance should be a\
                number (floats or ints are accepted)")
        if value < 0:
            raise ValueError(
                "Reactor.faceting_tolerance should be a\
                positive number")
        self._faceting_tolerance = value

    @property
    def merge_tolerance(self):
        return self._merge_tolerance

    @merge_tolerance.setter
    def merge_tolerance(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(
                "Reactor.merge_tolerance should be a\
                number (floats or ints are accepted)")
        if value < 0:
            raise ValueError(
                "Reactor.merge_tolerance should be a\
                positive number")
        self._merge_tolerance = value

    @property
    def stp_filenames(self):
        values = []
        if isinstance(self.shapes_and_components, str):
            with open(self.shapes_and_components) as json_file:
                data = json.load(json_file)
            for entry in data:
                if 'stp_filename' in entry.keys():
                    values.append(entry['stp_filename'])
                else:
                    raise ValueError(
                        'Entry is missing stp_filename key', entry)
        else:
            for shape_or_component in self.shapes_and_components:
                values.append(shape_or_component.stp_filename)

        return values

    @stp_filenames.setter
    def stp_filenames(self, value):
        self._stp_filenames = value

    @property
    def stl_filenames(self):
        values = []
        if isinstance(self.shapes_and_components, str):
            with open(self.shapes_and_components) as json_file:
                data = json.load(json_file)
            for entry in data:
                if 'stl_filename' in entry.keys():
                    values.append(entry['stl_filename'])
                else:
                    raise ValueError(
                        'Entry is missing stl_filename key', entry)
        else:
            for shape_or_component in self.shapes_and_components:
                values.append(shape_or_component.stl_filename)

        return values

    @stl_filenames.setter
    def stl_filenames(self, value):
        self._stl_filenames = value

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
            raise ValueError('paramak.Reactor.largest_shapes should be a '
                             'list of paramak.Shapes')
        self._largest_shapes = value

    @property
    def shapes_and_components(self):
        """Adds a list of parametric shape(s) and or parametric component(s)
        to the Reactor object. This allows collective operations to be
        performed on all the shapes in the reactor. When adding a shape or
        component the stp_filename of the shape or component should be unique"""
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
        """This combines all the parametric shapes and compents in the reactor
        object.
        """

        if isinstance(self.shapes_and_components, str):
            list_of_cq_vals = []
            for entry in self.stp_filenames:
                # When loading an stp file the solid object is the first part
                # of the tuple, hence the [0]
                loaded_shape = paramak.utils.load_stp_file(entry)[0]
                list_of_cq_vals.append(loaded_shape)

        else:

            list_of_cq_vals = []
            for shape_or_compound in self.shapes_and_components:
                if isinstance(
                    shape_or_compound.solid,
                    (cq.occ_impl.shapes.Shape,
                        cq.occ_impl.shapes.Compound)):
                    for solid in shape_or_compound.solid.Solids():
                        list_of_cq_vals.append(solid)
                else:
                    list_of_cq_vals.append(shape_or_compound.solid.val())

        compound = cq.Compound.makeCompound(list_of_cq_vals)

        return compound

    @ solid.setter
    def solid(self, value):
        self._solid = value

    def show(self):
        """Shows / renders the CadQuery the 3d object in Jupyter Lab. Imports
        show from jupyter_cadquery.cadquery and returns show(Reactor.solid)"""

        from jupyter_cadquery.cadquery import Part, PartGroup

        parts = []
        for shape_or_compound in self.shapes_and_components:

            if shape_or_compound.name is None:
                name = 'Shape.name not set'
            else:
                name = shape_or_compound.name

            scaled_color = [int(i * 255) for i in shape_or_compound.color[0:3]]
            if isinstance(
                    shape_or_compound.solid,
                    (cq.occ_impl.shapes.Shape, cq.occ_impl.shapes.Compound)):
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
                        color=scaled_color))
        return PartGroup(parts)

    def neutronics_description(
            self,
            include_plasma: Optional[bool] = False,
            include_graveyard: Optional[bool] = True,
            include_sector_wedge: Optional[bool] = True,
    ) -> dict:
        """A description of the reactor containing material tags, stp filenames,
        and tet mesh instructions. This is used for neutronics simulations
        which require linkage between volumes, materials and identification of
        which volumes to tet mesh. The plasma geometry is not included by
        default as it is typically not included in neutronics simulations. The
        reason for this is that the low number density results in minimal
        interaction with neutrons. However, it can be added if the
        include_plasma argument is set to True.

        Args:
            include_plasma: Should the plasma material be included in the JSON
                returned.

        Returns:
            dictionary: a dictionary of materials and filenames for the reactor
        """

        neutronics_description = []

        for entry in self.shapes_and_components:

            if include_plasma is False and (isinstance(
                entry,
                (paramak.Plasma,
                 paramak.PlasmaFromPoints,
                 paramak.PlasmaBoundaries)) is True or entry.name == 'plasma'):
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

            neutronics_description.append(entry.neutronics_description())

        # This add the neutronics description for the graveyard which is
        # special as it is automatically calculated instead of being added by
        # the user. Also the graveyard must have 'graveyard' as the material
        # name for using in DAGMC with OpenMC
        if include_graveyard:
            # this only takes the json values so the actual size doesn't matter
            self.make_graveyard(graveyard_size=1)
            neutronics_description.append(
                self.graveyard.neutronics_description())

        # This add the neutronics description for the sector which is
        # special as it is automatically calculated instead of being added by
        # the user. Also the graveyard must have 'Vaccum' as the material
        # name for using in DAGMC with OpenMC
        if include_sector_wedge:
            # this only takes the json values so the actual size doesn't matter
            sector_wedge = self.make_sector_wedge(height=1, radius=1)
            if sector_wedge is not None:
                neutronics_description.append(
                    sector_wedge.neutronics_description())

        return neutronics_description

    def material_tags(
            self,
            include_plasma: Optional[bool] = False
    ) -> List[str]:
        """Returns a set of all the materials_tags used in the Reactor
        optionally with or without the plasma.

        Args:
            include_plasma: Should the plasma material be included in the list
                of materials returned.

        Returns:
            A list of the material tags
        """
        values = []
        for shape_or_component in self.shapes_and_components:
            if include_plasma is False:
                if not isinstance(
                    shape_or_component,
                    (paramak.Plasma,
                     paramak.PlasmaFromPoints,
                     paramak.PlasmaBoundaries)):
                    values.append(shape_or_component.material_tag)
            else:
                values.append(shape_or_component.material_tag)

        return values

    def export_neutronics_description(
            self,
            filename: Optional[str] = "manifest.json",
            include_plasma: Optional[bool] = False,
            include_graveyard: Optional[bool] = True,
            include_sector_wedge: Optional[bool] = False,
    ) -> str:
        """
        Saves Reactor.neutronics_description to a json file. The resulting json
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
            include_plasma: should the plasma be included. Defaults to False
                as the plasma volume and material has very little impact on
                the neutronics results due to the low density. Including the
                plasma does however slow down the simulation.
            include_graveyard: should the graveyard be included. Defaults to
                True as this is needed for DAGMC models.
            include_sector_wedge: should the sector wedge be included.
                Defaults to False as this is only needed for DAGMC sector
                models.

        Returns:
            filename of the neutronics description file saved
        """

        path_filename = Path(filename)

        if path_filename.suffix != ".json":
            path_filename = path_filename.with_suffix(".json")

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        with open(path_filename, "w") as outfile:
            json.dump(
                self.neutronics_description(
                    include_plasma=include_plasma,
                    include_graveyard=include_graveyard,
                    include_sector_wedge=include_sector_wedge,
                ),
                outfile,
                indent=4,
            )

        print("saved geometry description to ", path_filename)

        return str(path_filename)

    def export_stp(
            self,
            output_folder: Optional[str] = "",
            mode: Optional[str] = 'solid',
            include_graveyard: Optional[bool] = True,
            include_sector_wedge: Optional[bool] = True,
            units: Optional[str] = 'mm',
            filename: Optional[str] = None
    ) -> List[str]:
        """Writes stp files (CAD geometry) for each Shape object in the reactor
        and the graveyard.

        Args:
            output_folder: the folder for saving the stp files to
            mode: the object to export can be either 'solid' which exports 3D
                solid shapes or the 'wire' which exports the wire edges of the
                shape.
            include_graveyard: specifiy if the graveyard will be included or
                not. If True the the Reactor.make_graveyard will be called
                using Reactor.graveyard_size and Reactor.graveyard_offset
                attribute values.
            include_sector_wedge: specifies if a sector_wedge will be exported.
                This wedge is useful when constructing reflectin surfaces in
                DAGMC geometry. If set to True the the self.rotation_agle must
                also be set.
            units: the units of the stp file, options are 'cm' or 'mm'.
                Default is mm.
            filename: If specified all the shapes will be combined into a
                single file. If left as Default (None) then the seperate shapes
                are saved as seperate files using their shape.stp_filename
                attribute. output_folder is ignored if filename is set.
        Returns:
            list: a list of stp filenames created
        """

        if filename is None:
            if len(self.stp_filenames) != len(set(self.stp_filenames)):
                print([item for item, count in collections.Counter(
                    self.stp_filenames).items() if count > 1])
                raise ValueError(
                    "Set Reactor already contains shapes with the "
                    "same stp_filename")

            filenames = []
            for entry in self.shapes_and_components:
                if entry.stp_filename is None:
                    raise ValueError(
                        "set .stp_filename property for \
                                    Shapes before using the export_stp method"
                    )
                filenames.append(
                    str(Path(output_folder) / Path(entry.stp_filename)))
                entry.export_stp(
                    filename=Path(output_folder) / Path(entry.stp_filename),
                    mode=mode,
                    units=units,
                    verbose=False,
                )

            if include_sector_wedge:
                sector_wedge = self.make_sector_wedge()
                # if the self.rotation_angle is 360 then None is returned
                if sector_wedge is not None:
                    filename = sector_wedge.export_stp(filename=str(
                        Path(output_folder) / sector_wedge.stp_filename))
                    filenames.append(filename)

            # creates a graveyard (bounding shell volume) which is needed for
            # neutronics simulations with default Reactor attributes.
            if include_graveyard:
                graveyard = self.make_graveyard()
                filename = self.graveyard.export_stp(
                    filename=str(Path(output_folder) / graveyard.stp_filename)
                )
                filenames.append(filename)

            return filenames

        # exports a single file for the whole model
        assembly = cq.Assembly(name='reactor')
        for entry in self.shapes_and_components:
            if entry.color is None:
                assembly.add(entry.solid)
            else:
                assembly.add(entry.solid, color=cq.Color(*entry.color))

        assembly.save(filename, exportType='STEP')

        if units == 'cm':
            _replace(
                filename,
                'SI_UNIT(.MILLI.,.METRE.)',
                'SI_UNIT(.CENTI.,.METRE.)')

        return [filename]

    def export_stl(
            self,
            output_folder: Optional[str] = "",
            tolerance: Optional[float] = 0.001,
            include_graveyard: Optional[bool] = True,
    ) -> List[str]:
        """Writes stl files (CAD geometry) for each Shape object in the reactor

        Args:
            output_folder (str): the folder for saving the stl files to
            tolerance (float):  the precision of the faceting
            include_graveyard: specifiy if the graveyard will be included or
                not. If True the the Reactor.make_graveyard will be called
                using Reactor.graveyard_size and Reactor.graveyard_offset
                attribute values.

        Returns:
            list: a list of stl filenames created
        """

        if len(self.stl_filenames) != len(set(self.stl_filenames)):
            raise ValueError(
                "Set Reactor already contains a shape or component \
                         with this stl_filename",
                self.stl_filenames,
            )

        filenames = []
        for entry in self.shapes_and_components:
            if entry.stl_filename is None:
                raise ValueError(
                    "set .stl_filename attribute for Shapes before using the Reactor.export_stl method"
                )

            filename = entry.export_stl(
                filename=Path(output_folder) / entry.stl_filename,
                tolerance=tolerance,
                verbose=False,
            )
            filenames.append(filename)

        # creates a graveyard (bounding shell volume) which is needed for
        # neutronics simulations with default Reactor attributes.
        if include_graveyard:
            graveyard = self.make_graveyard()
            filename = self.graveyard.export_stl(
                Path(output_folder) / graveyard.stl_filename)
            filenames.append(filename)

        return filenames

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
            filename: Optional[str] = 'dagmc.h5m',
            include_graveyard: Optional[bool] = True,
            include_plasma: Optional[bool] = False,
            method: Optional[str] = None,
            merge_tolerance: Optional[float] = None,
            faceting_tolerance: Optional[float] = None,
    ) -> str:
        """Produces a h5m neutronics geometry compatable with DAGMC
        simulations. Tags the volumes with their material_tag attributes. Sets
        the Reactor.h5m_filename to the filename of the h5m file produced.

        Arguments:
            filename: filename of h5m outputfile.
            include_graveyard: specifiy if the graveyard will be included or
                not. If True the the Reactor.make_graveyard will be called
                using Reactor.graveyard_size and Reactor.graveyard_offset
                attribute values.
            method: The method to use when making the imprinted and
                merged geometry. Options are "trelis" and "pymoab" Defaults to
                None which uses the Reactor.method attribute.
            merge_tolerance: the allowable distance between edges and surfaces
                before merging these CAD objects into a single CAD object. See
                https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html
                for more details. Defaults to None which uses the
                Reactor.merge_tolerance attribute.
            faceting_tolerance: the allowable distance between facetets
                before merging these CAD objects into a single CAD object See
                https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html
                for more details. Defaults to None which uses the
                Reactor.faceting_tolerance attribute.

        Returns:
            The filename of the DAGMC file created
        """

        if merge_tolerance is None:
            merge_tolerance = self.merge_tolerance

        if faceting_tolerance is None:
            faceting_tolerance = self.faceting_tolerance

        if method is None:
            method = self.method

        os.system('rm ' + filename)

        if method == 'trelis':
            output_filename = self.export_h5m_with_trelis(
                filename=filename,
                merge_tolerance=merge_tolerance,
                faceting_tolerance=faceting_tolerance,
                include_plasma=include_plasma,
            )
        elif method == 'pymoab':
            output_filename = self.export_h5m_with_pymoab(
                filename=filename,
                include_graveyard=include_graveyard,
                faceting_tolerance=faceting_tolerance,
                include_plasma=include_plasma,
            )

        else:
            raise ValueError("the method using in should be either trelis, \
                pymoab. {} is not an option".format(method))

        return output_filename

    def make_sector_wedge(
            self,
            height: Optional[float] = None,
            radius: Optional[float] = None,
            rotation_angle: Optional[float] = None,
            material_tag='vacuum',
            stp_filename: Optional[str] = 'sector_wedge.stp',
            stl_filename: Optional[str] = 'sector_wedge.stl'
    ) -> Union[paramak.Shape, None]:
        """Creates a rotated wedge shaped object that is useful for creating
        sector models in DAGMC where reflecting surfaces are needed. If the
        rotation

        Args:
            height: The height of the rotated wedge. If None then the
                largest_dimention of the model will be used.
            radius: The radius of the rotated wedge. If None then the
                largest_dimention of the model will be used
            rotation_angle: The rotation angle of the wedge will be the
                inverse of the sector
            stp_filename:

        Returns:
            the paramak.Shape object created
        """

        if rotation_angle is None:
            if hasattr(self, 'rotation_angle'):
                rotation_angle = self.rotation_angle
            if rotation_angle is None:
                Warning('No sector_wedge can be made as rotation_angle'
                        ' or Reactor.rotation_angle have not been set')
                return None

        if rotation_angle > 360:
            Warning(
                'No wedge can be made for a rotation angle of 360 or above')
            return None

        if rotation_angle == 360:
            print('No sector wedge made as rotation angle is 360')
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
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            azimuth_placement_angle=rotation_angle,
            material_tag=material_tag,
        )

        self.sector_wedge = sector_cutting_wedge

        return sector_cutting_wedge

    def export_h5m_with_trelis(
            self,
            filename: Optional[str] = 'dagmc.h5m',
            merge_tolerance: Optional[float] = None,
            faceting_tolerance: Optional[float] = None,
            include_plasma: Optional[bool] = False,
    ) -> str:
        """Produces a dagmc.h5m neutronics file compatable with DAGMC
        simulations using Coreform Trelis.

        Arguments:
            filename: filename of h5m outputfile.
            merge_tolerance: the allowable distance between edges and surfaces
                before merging these CAD objects into a single CAD object. See
                https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html
                for more details. Defaults to None which uses the
                Reactor.merge_tolerance attribute.
            faceting_tolerance: the allowable distance between facetets
                before merging these CAD objects into a single CAD object See
                https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html
                for more details. Defaults to None which uses the
                Reactor.faceting_tolerance attribute.

        Returns:
            filename of the DAGMC file produced
        """

        if merge_tolerance is None:
            merge_tolerance = self.merge_tolerance
        if faceting_tolerance is None:
            faceting_tolerance = self.faceting_tolerance

        if isinstance(self.shapes_and_components, list):
            self.export_neutronics_description(
                include_graveyard=True,
                include_sector_wedge=True,
                include_plasma=include_plasma,
            )
            self.export_stp(
                include_graveyard=True,
                include_sector_wedge=True,
            )
        elif isinstance(self.shapes_and_components, str):
            if not Path(self.shapes_and_components).is_file():
                raise FileNotFoundError("The filename entered as the geometry \
                    argument {} does not exist".format(self.shapes_and_components))
            if self.shapes_and_components != 'manifest.json':
                shutil.copy(
                    src=self.shapes_and_components,
                    dst='manifest.json')
        else:
            raise ValueError(
                "shapes_and_components must be a list of paramak.Shape or a filename")

        not_watertight_file = paramak.utils.trelis_command_to_create_dagmc_h5m(
            faceting_tolerance=faceting_tolerance, merge_tolerance=merge_tolerance)

        water_tight_h5m_filename = paramak.utils.make_watertight(
            input_filename=not_watertight_file[0],
            output_filename=filename
        )

        self.h5m_filename = water_tight_h5m_filename

        return water_tight_h5m_filename

    def export_h5m_with_pymoab(
            self,
            filename: Optional[str] = 'dagmc.h5m',
            include_graveyard: Optional[bool] = True,
            faceting_tolerance: Optional[float] = None,
            include_plasma: Optional[bool] = False,
    ) -> str:
        """Converts stl files into DAGMC compatible h5m file using PyMOAB. The
        DAGMC file produced has not been imprinted and merged unlike the other
        supported method which uses Trelis to produce an imprinted and merged
        DAGMC geometry. If the provided filename doesn't end with .h5m it will
        be added

        Arguments:
            filename: filename of h5m outputfile.
            include_graveyard: specifiy if the graveyard will be included or
                not. If True the the Reactor.make_graveyard will be called
                using Reactor.graveyard_size and Reactor.graveyard_offset
                attribute values.
            faceting_tolerance: the precision of the faceting.
            include_plasma: Should the plasma material be included in the h5m
                file.

        Returns:
            The filename of the DAGMC file created
        """

        if faceting_tolerance is None:
            faceting_tolerance = self.faceting_tolerance

        path_filename = Path(filename)

        if path_filename.suffix != ".h5m":
            path_filename = path_filename.with_suffix(".h5m")

        path_filename.parents[0].mkdir(parents=True, exist_ok=True)

        moab_core, moab_tags = define_moab_core_and_tags()

        surface_id = 1
        volume_id = 1

        if isinstance(self.shapes_and_components, list):
            for entry in self.shapes_and_components:

                if include_plasma is False and (
                    isinstance(
                        entry,
                        (paramak.Plasma,
                         paramak.PlasmaFromPoints,
                         paramak.PlasmaBoundaries)) is True or entry.name == 'plasma'):
                    continue

                entry.export_stl(
                    entry.stl_filename,
                    tolerance=faceting_tolerance)
                moab_core = add_stl_to_moab_core(
                    moab_core,
                    surface_id,
                    volume_id,
                    entry.material_tag,
                    moab_tags,
                    entry.stl_filename)
                volume_id += 1
                surface_id += 1
        else:
            # loads up the json file
            with open(self.shapes_and_components) as json_file:
                manifest = json.load(json_file)

            # gets all the stp files and loads them into shapes
            for entry in manifest:
                new_shape = paramak.Shape()
                # loads the stp file into a Shape object
                new_shape.from_stp_file(entry['stp_filename'])
                new_shape.material_tag = entry['material_tag']
                new_shape.stl_filename = str(
                    Path(entry['stp_filename']).stem) + '.stl'

                new_shape.export_stl(
                    new_shape.stl_filename,
                    tolerance=faceting_tolerance)

                moab_core = add_stl_to_moab_core(
                    moab_core,
                    surface_id,
                    volume_id,
                    new_shape.material_tag,
                    moab_tags,
                    new_shape.stl_filename)
                volume_id += 1
                surface_id += 1

        if include_graveyard:
            self.make_graveyard()
            self.graveyard.export_stl()
            volume_id += 1
            surface_id += 1
            moab_core = add_stl_to_moab_core(
                moab_core,
                surface_id,
                volume_id,
                self.graveyard.material_tag,
                moab_tags,
                self.graveyard.stl_filename
            )

        all_sets = moab_core.get_entities_by_handle(0)

        file_set = moab_core.create_meshset()

        moab_core.add_entities(file_set, all_sets)

        moab_core.write_file(str(path_filename))

        self.h5m_filename = str(path_filename)

        return str(path_filename)

    def export_physical_groups(
            self,
            output_folder: Optional[str] = "",
    ) -> List[str]:
        """Exports several JSON files containing a look up table which is
        useful for identifying faces and volumes. The output file names are
        generated from .stp_filename properties.

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
            filenames.append(
                str(Path(output_folder) / Path(entry.stp_filename)))
            entry.export_physical_groups(
                Path(output_folder) / Path(entry.stp_filename))
        return filenames

    def export_svg(
            self,
            filename: Optional[str] = 'reactor.svg',
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
            "showHidden": showHidden
        }

        if strokeWidth is not None:
            opt["strokeWidth"] = strokeWidth

        exporters.export(self.solid, str(path_filename), exportType='SVG',
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
        vaules.

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
            graveyard_size_to_use = self.largest_dimension * 2 + self.graveyard_offset * 2

        else:
            raise ValueError("the graveyard_size, Reactor.graveyard_size, \
                graveyard_offset and Reactor.graveyard_offset are all None. \
                Please specify at least one of these attributes or agruments")

        graveyard_shape = paramak.HollowCube(
            length=graveyard_size_to_use,
            name="graveyard",
            material_tag="graveyard",
            stp_filename="graveyard.stp",
            stl_filename="graveyard.stl",
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
    ):
        """Saves an interactive 3d html view of the Reactor to a html file.

        Args:
            filename: the filename used to save the html graph. Defaults to
                reactor_3d.html

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
            filename: Optional[str] = "reactor.html",
            facet_splines: Optional[bool] = True,
            facet_circles: Optional[bool] = True,
            tolerance: Optional[float] = 1.,
            view_plane: Optional[str] = 'RZ'):
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
            title="coordinates of the " + self.__class__.__name__ +
            " reactor, viewed from the " + view_plane + " plane",
            mode="lines",
        )

        return fig
