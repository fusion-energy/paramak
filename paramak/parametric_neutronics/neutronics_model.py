
import json
import os
import warnings
from pathlib import Path
from typing import List, Optional, Tuple, Union

import paramak
from paramak import get_neutronics_results_from_statepoint_file
from paramak.neutronics_utils import (create_inital_particles,
                                      extract_points_from_initial_source)
from paramak.utils import plotly_trace

try:
    import openmc
    from openmc.data import REACTION_MT, REACTION_NAME
except ImportError:
    warnings.warn('OpenMC not found, NeutronicsModelFromReactor.simulate \
            method not available', UserWarning)

try:
    import neutronics_material_maker as nmm
except ImportError:
    warnings.warn("neutronics_material_maker not found, \
            NeutronicsModelFromReactor.materials can't accept strings or \
            neutronics_material_maker objects", UserWarning)


class NeutronicsModel():
    """Creates a neutronics model of the provided shape geometry with assigned
    materials, source and neutronics tallies.

    Arguments:
        geometry: The geometry to convert to a neutronics model. e.g.
            geometry=paramak.RotateMixedShape() or
            geometry=paramak.BallReactor().
        source (openmc.Source()): the particle source to use during the
            OpenMC simulation.
        materials: Where the dictionary keys are the material tag
            and the dictionary values are either a string, openmc.Material,
            neutronics-material-maker.Material or
            neutronics-material-maker.MultiMaterial. All components within the
            geometry object must be accounted for. Material tags required
            for a Reactor or Shape can be obtained with .material_tags() and
            material_tag respectively.
        simulation_batches: the number of batch to simulate.
        simulation_particles_per_batch: particles per batch.
        cell_tallies: the cell based tallies to calculate, options include
            TBR, heating, flux, MT numbers and OpenMC standard scores such as
            (n,Xa) which is helium production are also supported
            https://docs.openmc.org/en/latest/usersguide/tallies.html#scores
        mesh_tally_2d: the 2D mesh based tallies to calculate, options include
            heating and flux , MT numbers and OpenMC standard scores such as
            (n,Xa) which is helium production are also supported
            https://docs.openmc.org/en/latest/usersguide/tallies.html#scores
        mesh_tally_3d: the 3D mesh based tallies to calculate,
            options include heating and flux , MT numbers and OpenMC standard
            scores such as (n,Xa) which is helium production are also supported
            https://docs.openmc.org/en/latest/usersguide/tallies.html#scores
        mesh_3d_resolution: The 3D mesh resolution in the height, width and
            depth directions. The larger the resolution the finer the mesh and
            the more computational intensity is required to converge each mesh
            element.
        mesh_2d_resolution: The 3D mesh resolution in the height and width
            directions. The larger the resolution the finer the mesh and more
            computational intensity is required to converge each mesh element.
        mesh_2d_corners: The upper and lower corner locations for the 2d
            mesh. This sets the location of the mesh. Defaults to None which
            uses the NeutronicsModel.geometry.largest_dimension property to set
            the corners.
        mesh_3d_corners: The upper and lower corner locations for the 3d
            mesh. This sets the location of the mesh. Defaults to None which
            uses the NeutronicsModel.geometry.largest_dimension property to set
            the corners.
        fusion_power: the power in watts emitted by the fusion reaction
            recalling that each DT fusion reaction emitts 17.6 MeV or
            2.819831e-12 Joules
    """

    def __init__(
        self,
        geometry: Union[paramak.Reactor, paramak.Shape],
        source,
        materials: dict,
        simulation_batches: Optional[int] = 100,
        simulation_particles_per_batch: Optional[int] = 10000,
        cell_tallies: Optional[List[str]] = None,
        mesh_tally_2d: Optional[List[str]] = None,
        mesh_tally_3d: Optional[List[str]] = None,
        mesh_2d_resolution: Optional[Tuple[int, int, int]] = (400, 400),
        mesh_3d_resolution: Optional[Tuple[int, int, int]] = (100, 100, 100),
        mesh_2d_corners: Optional[Tuple[Tuple[float, float,
                                              float], Tuple[float, float, float]]] = None,
        mesh_3d_corners: Optional[Tuple[Tuple[float, float,
                                              float], Tuple[float, float, float]]] = None,
        fusion_power: Optional[float] = 1e9,
        # convert from watts to activity source_activity
        max_lost_particles: Optional[int] = 10,
    ):

        self.materials = materials
        self.geometry = geometry
        self.source = source
        self.cell_tallies = cell_tallies
        self.mesh_tally_2d = mesh_tally_2d
        self.mesh_tally_3d = mesh_tally_3d
        self.simulation_batches = simulation_batches
        self.simulation_particles_per_batch = simulation_particles_per_batch
        self.max_lost_particles = max_lost_particles

        self.mesh_2d_resolution = mesh_2d_resolution
        self.mesh_3d_resolution = mesh_3d_resolution
        self.mesh_2d_corners = mesh_2d_corners
        self.mesh_3d_corners = mesh_3d_corners
        self.fusion_power = fusion_power

        self.model = None
        self.results = None
        self.tallies = None
        self.output_filename = None
        self.statepoint_filename = None

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        if isinstance(value, (paramak.Shape, paramak.Reactor, type(None))):
            self._geometry = value
        else:
            raise TypeError(
                "NeutronicsModelFromReactor.geometry should be a \
                paramak.Shape(), paramak.Reactor()")

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        if not isinstance(value, (openmc.Source, type(None))):
            raise TypeError(
                "NeutronicsModelFromReactor.source should be an \
                openmc.Source() object")
        self._source = value

    @property
    def cell_tallies(self):
        return self._cell_tallies

    @cell_tallies.setter
    def cell_tallies(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise TypeError(
                    "NeutronicsModelFromReactor.cell_tallies should be a\
                    list")
            output_options = ['TBR', 'heating', 'flux', 'spectra', 'absorption'] + \
                list(REACTION_MT.keys()) + list(REACTION_NAME.keys())
            for entry in value:
                if entry not in output_options:
                    raise ValueError(
                        "NeutronicsModelFromReactor.cell_tallies argument",
                        entry,
                        "not allowed, the following options are supported",
                        output_options)
        self._cell_tallies = value

    @property
    def mesh_tally_2d(self):
        return self._mesh_tally_2d

    @mesh_tally_2d.setter
    def mesh_tally_2d(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise TypeError(
                    "NeutronicsModelFromReactor.mesh_tally_2d should be a\
                    list")
            output_options = ['heating', 'flux', 'absorption'] + \
                list(REACTION_MT.keys()) + list(REACTION_NAME.keys())
            for entry in value:
                if entry not in output_options:
                    raise ValueError(
                        "NeutronicsModelFromReactor.mesh_tally_2d argument",
                        entry,
                        "not allowed, the following options are supported",
                        output_options)
        self._mesh_tally_2d = value

    @property
    def mesh_tally_3d(self):
        return self._mesh_tally_3d

    @mesh_tally_3d.setter
    def mesh_tally_3d(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise TypeError(
                    "NeutronicsModelFromReactor.mesh_tally_3d should be a\
                    list")
            output_options = ['heating', 'flux', 'absorption'] + \
                list(REACTION_MT.keys()) + list(REACTION_NAME.keys())
            for entry in value:
                if entry not in output_options:
                    raise ValueError(
                        "NeutronicsModelFromReactor.mesh_tally_3d argument",
                        entry,
                        "not allowed, the following options are supported",
                        output_options)
        self._mesh_tally_3d = value

    @property
    def materials(self):
        return self._materials

    @materials.setter
    def materials(self, value):
        if not isinstance(value, dict):
            raise TypeError("NeutronicsModelFromReactor.materials should be a\
                dictionary")
        self._materials = value

    @property
    def simulation_batches(self):
        return self._simulation_batches

    @simulation_batches.setter
    def simulation_batches(self, value):
        if isinstance(value, float):
            value = int(value)
        if not isinstance(value, int):
            raise TypeError(
                "NeutronicsModelFromReactor.simulation_batches should be an int")
        if value < 2:
            raise ValueError(
                "The minimum of setting for simulation_batches is 2"
            )
        self._simulation_batches = value

    @property
    def simulation_particles_per_batch(self):
        return self._simulation_particles_per_batch

    @simulation_particles_per_batch.setter
    def simulation_particles_per_batch(self, value):
        if isinstance(value, float):
            value = int(value)
        if not isinstance(value, int):
            raise TypeError(
                "NeutronicsModelFromReactor.simulation_particles_per_batch\
                    should be an int")
        self._simulation_particles_per_batch = value

    def create_material(self, material_tag: str, material_entry):
        if isinstance(material_entry, str):
            openmc_material = nmm.Material(
                material_entry,
                material_tag=material_tag).openmc_material
        elif isinstance(material_entry, openmc.Material):
            # sets the material name in the event that it had not been set
            material_entry.name = material_tag
            openmc_material = material_entry
        elif isinstance(material_entry, (nmm.Material, nmm.MultiMaterial)):
            # sets the material tag in the event that it had not been set
            material_entry.material_tag = material_tag
            openmc_material = material_entry.openmc_material
        else:
            raise TypeError("materials must be either a str, \
                openmc.Material, nmm.MultiMaterial or nmm.Material object \
                not a ", type(material_entry), material_entry)
        return openmc_material

    def create_openmc_materials(self):
        # # checks all the required materials are present
        # for reactor_material in self.geometry.material_tags:
        #     if reactor_material not in self.materials.keys():
        #         raise ValueError(
        #             "material included by the reactor model has not \
        #             been added", reactor_material)

        # # checks that no extra materials we added
        # for reactor_material in self.materials.keys():
        #     if reactor_material not in self.geometry.material_tags:
        #         raise ValueError(
        #             "material has been added that is not needed for this \
        #             reactor model", reactor_material)

        os.system('rm materials.xml')

        openmc_materials = {}
        for material_tag, material_entry in self.materials.items():
            openmc_material = self.create_material(
                material_tag, material_entry)
            openmc_materials[material_tag] = openmc_material

        self.openmc_materials = openmc_materials

        self.mats = openmc.Materials(list(self.openmc_materials.values()))

        self.mats.export_to_xml()

        return self.mats

    def export_xml(
            self,
            simulation_batches: Optional[int] = None,
            source=None,
            max_lost_particles: Optional[int] = None,
            simulation_particles_per_batch: Optional[int] = None,
            mesh_tally_3d: Optional[float] = None,
            mesh_tally_2d: Optional[float] = None,
            cell_tallies: Optional[float] = None,
            mesh_2d_resolution: Optional[Tuple[int, int, int]] = None,
            mesh_3d_resolution: Optional[Tuple[int, int, int]] = None,
            mesh_2d_corners: Optional[Tuple[Tuple[float, float, float], Tuple[float, float, float]]] = None,
            mesh_3d_corners: Optional[Tuple[Tuple[float, float, float], Tuple[float, float, float]]] = None,
    ):
        """Uses OpenMC python API to make a neutronics model, including tallies
        (cell_tallies and mesh_tally_2d), simulation settings (batches,
        particles per batch).

        Arguments:
            simulation_batches: the number of batch to simulate.
            source: (openmc.Source): the particle source to use during the
                OpenMC simulation. Defaults to NeutronicsModel.source
            max_lost_particles: The maximum number of particles that can be
                lost during the simuation before terminating the simulation.
                Defaults to None which uses the
                NeutronicsModel.max_lost_particles attribute.
            simulation_particles_per_batch: particles simulated per batch.
                Defaults to None which uses the
                NeutronicsModel.simulation_particles_per_batch attribute.
            mesh_tally_3d: the 3D mesh based tallies to calculate, options
                include heating and flux , MT numbers and OpenMC standard
                scores such as (n,Xa) which is helium production are also supported
                https://docs.openmc.org/en/latest/usersguide/tallies.html#scores.
                Defaults to None which uses the NeutronicsModel.mesh_tally_3d
                attribute.
            mesh_tally_2d: . the 2D mesh based tallies to calculate, options
                include heating and flux , MT numbers and OpenMC standard
                scores such as (n,Xa) which is helium production are also supported
                https://docs.openmc.org/en/latest/usersguide/tallies.html#scores .
                Defaults to None which uses the NeutronicsModel.mesh_tally_2d
                attribute.
            cell_tallies: the cell based tallies to calculate, options include
                TBR, heating, flux, MT numbers and OpenMC standard scores such
                as (n,Xa) which is helium production are also supported
                https://docs.openmc.org/en/latest/usersguide/tallies.html#scores.
                Defaults to None which uses the NeutronicsModel.cell_tallies
                attribute.
            mesh_2d_resolution: The 2D mesh resolution in the height and
                width directions. The larger the resolution the finer the mesh
                and more computational intensity is required to converge each
                mesh element. Defaults to None which uses the
                NeutronicsModel.mesh_2d_resolution attribute
            mesh_3d_resolution: The 3D mesh resolution in the height, width
                and depth directions. The larger the resolution the finer the
                mesh and the more computational intensity is required to
                converge each mesh element. Defaults to None which uses the
                NeutronicsModel.mesh_3d_resolution attribute.
            mesh_2d_corners: The upper and lower corner locations for the 2d
                mesh. Defaults to None which uses the
                NeutronicsModel.mesh_2d_corners
            mesh_3d_corners: The upper and lower corner locations for the 2d
                mesh. Defaults to None which uses the
                NeutronicsModel.mesh_2d_corners

        Returns:
            openmc.model.Model(): The openmc model object created
        """

        if simulation_batches is None:
            simulation_batches = self.simulation_batches
        if source is None:
            source = self.source
        if max_lost_particles is None:
            max_lost_particles = self.max_lost_particles
        if simulation_particles_per_batch is None:
            simulation_particles_per_batch = self.simulation_particles_per_batch
        if mesh_tally_3d is None:
            mesh_tally_3d = self.mesh_tally_3d
        if mesh_tally_2d is None:
            mesh_tally_2d = self.mesh_tally_2d
        if cell_tallies is None:
            cell_tallies = self.cell_tallies
        if mesh_2d_resolution is None:
            mesh_2d_resolution = self.mesh_2d_resolution
        if mesh_3d_resolution is None:
            mesh_3d_resolution = self.mesh_3d_resolution
        if mesh_2d_corners is None:
            mesh_2d_corners = self.mesh_2d_corners
        if mesh_3d_corners is None:
            mesh_3d_corners = self.mesh_3d_corners

        # this removes any old file from previous simulations
        os.system('rm geometry.xml')
        os.system('rm settings.xml')
        os.system('rm tallies.xml')

        # materials.xml is removed in this function
        self.create_openmc_materials()

        # this is the underlying geometry container that is filled with the
        # faceteted DGAMC CAD model
        self.universe = openmc.Universe()
        geom = openmc.Geometry(self.universe)

        # settings for the number of neutrons to simulate
        settings = openmc.Settings()
        settings.batches = self.simulation_batches
        settings.inactive = 0
        settings.particles = self.simulation_particles_per_batch
        settings.run_mode = "fixed source"
        settings.dagmc = True
        settings.photon_transport = True
        settings.source = self.source
        settings.max_lost_particles = self.max_lost_particles

        # details about what neutrons interactions to keep track of (tally)
        self.tallies = openmc.Tallies()

        if self.mesh_tally_3d is not None:
            mesh_xyz = openmc.RegularMesh(mesh_id=1, name='3d_mesh')
            mesh_xyz.dimension = self.mesh_3d_resolution
            if self.mesh_3d_corners is None:
                mesh_xyz.lower_left = [
                    -self.geometry.largest_dimension,
                    -self.geometry.largest_dimension,
                    -self.geometry.largest_dimension
                ]

                mesh_xyz.upper_right = [
                    self.geometry.largest_dimension,
                    self.geometry.largest_dimension,
                    self.geometry.largest_dimension
                ]
            else:
                mesh_xyz.lower_left = self.mesh_3d_corners[0]
                mesh_xyz.upper_right = self.mesh_3d_corners[1]

            for standard_tally in self.mesh_tally_3d:
                score = standard_tally
                prefix = standard_tally
                mesh_filter = openmc.MeshFilter(mesh_xyz)
                tally = openmc.Tally(name=prefix + '_on_3D_mesh')
                tally.filters = [mesh_filter]
                tally.scores = [score]
                self.tallies.append(tally)

        if self.mesh_tally_2d is not None:

            # Create mesh which will be used for tally
            mesh_xz = openmc.RegularMesh(mesh_id=2, name='2d_mesh_xz')

            mesh_xz.dimension = [
                self.mesh_2d_resolution[1],
                1,
                self.mesh_2d_resolution[0]
            ]

            if self.mesh_2d_corners is None:
                mesh_xz.lower_left = [
                    -self.geometry.largest_dimension,
                    -1,
                    -self.geometry.largest_dimension
                ]

                mesh_xz.upper_right = [
                    self.geometry.largest_dimension,
                    1,
                    self.geometry.largest_dimension
                ]
            else:
                mesh_xz.lower_left = self.mesh_2d_corners[0]
                mesh_xz.upper_right = self.mesh_2d_corners[1]

            mesh_xy = openmc.RegularMesh(mesh_id=3, name='2d_mesh_xy')
            mesh_xy.dimension = [
                self.mesh_2d_resolution[1],
                self.mesh_2d_resolution[0],
                1
            ]

            if self.mesh_2d_corners is None:
                mesh_xy.lower_left = [
                    -self.geometry.largest_dimension,
                    -self.geometry.largest_dimension,
                    -1
                ]

                mesh_xy.upper_right = [
                    self.geometry.largest_dimension,
                    self.geometry.largest_dimension,
                    1
                ]
            else:
                mesh_xy.lower_left = self.mesh_2d_corners[0]
                mesh_xy.upper_right = self.mesh_2d_corners[1]

            mesh_yz = openmc.RegularMesh(mesh_id=4, name='2d_mesh_yz')
            mesh_yz.dimension = [
                1,
                self.mesh_2d_resolution[1],
                self.mesh_2d_resolution[0]
            ]

            if self.mesh_2d_corners is None:
                mesh_yz.lower_left = [
                    -1,
                    -self.geometry.largest_dimension,
                    -self.geometry.largest_dimension
                ]

                mesh_yz.upper_right = [
                    1,
                    self.geometry.largest_dimension,
                    self.geometry.largest_dimension
                ]
            else:
                mesh_yz.lower_left = self.mesh_2d_corners[0]
                mesh_yz.upper_right = self.mesh_2d_corners[1]

            for standard_tally in self.mesh_tally_2d:
                score = standard_tally
                prefix = standard_tally

                for mesh_filter, plane in zip(
                        [mesh_xz, mesh_xy, mesh_yz], ['xz', 'xy', 'yz']):
                    mesh_filter = openmc.MeshFilter(mesh_filter)
                    tally = openmc.Tally(name=prefix + '_on_2D_mesh_' + plane)
                    tally.filters = [mesh_filter]
                    tally.scores = [score]
                    self.tallies.append(tally)

        if self.cell_tallies is not None:

            for standard_tally in self.cell_tallies:
                if standard_tally == 'TBR':
                    score = '(n,Xt)'  # where X is a wild card
                    sufix = 'TBR'
                    tally = openmc.Tally(name='TBR')
                    tally.scores = [score]
                    self.tallies.append(tally)
                    self._add_tally_for_every_material(sufix, score)

                elif standard_tally == 'spectra':
                    neutron_particle_filter = openmc.ParticleFilter([
                                                                    'neutron'])
                    photon_particle_filter = openmc.ParticleFilter(['photon'])
                    energy_bins = openmc.mgxs.GROUP_STRUCTURES['CCFE-709']
                    energy_filter = openmc.EnergyFilter(energy_bins)

                    self._add_tally_for_every_material(
                        'neutron_spectra',
                        'flux',
                        [neutron_particle_filter, energy_filter]
                    )

                    self._add_tally_for_every_material(
                        'photon_spectra',
                        'flux',
                        [photon_particle_filter, energy_filter]
                    )
                else:
                    score = standard_tally
                    sufix = standard_tally
                    self._add_tally_for_every_material(sufix, score)

        # make the model from geometry, materials, settings and tallies
        model = openmc.model.Model(
            geom, self.mats, settings, self.tallies)

        geom.export_to_xml()
        settings.export_to_xml()
        self.tallies.export_to_xml()

        self.model = model
        return model

    def _add_tally_for_every_material(self, sufix: str, score: str,
                                      additional_filters: List = None) -> None:
        """Adds a tally to self.tallies for every material.

        Arguments:
            sufix: the string to append to the end of the tally name to help
                identify the tally later.
            score: the openmc.Tally().scores value that contribute to the tally
        """
        if additional_filters is None:
            additional_filters = []
        for key, value in self.openmc_materials.items():
            if key != 'DT_plasma':
                material_filter = openmc.MaterialFilter(value)
                tally = openmc.Tally(name=key + '_' + sufix)
                tally.filters = [material_filter] + additional_filters
                tally.scores = [score]
                self.tallies.append(tally)

    def simulate(
            self,
            verbose: Optional[bool] = True,
            cell_tally_results_filename: Optional[str] = 'results.json',
            threads: Optional[int] = None,
            export_h5m: Optional[bool] = True,
            export_xml: Optional[bool] = True,
    ) -> str:
        """Run the OpenMC simulation. Deletes existing simulation output
        (summary.h5) if files exists.

        Arguments:
            verbose: Print the output from OpenMC (True) to the terminal or
                don't print the OpenMC output (False).
            cell_tally_results_filename: the filename to use when saving the
                cell tallies to file.
            threads: Sets the number of OpenMP threads used for the simulation.
                 None takes all available threads by default.
            export_h5m: controls the creation of the DAGMC geometry
                file (dagmc.h5m). Set to True to create the DAGMC geometry
                file with the default settings as determined by the
                NeutronicsModel.geometry.method attributes or set to False and
                run the export_h5m() method yourself with more
                direct control over the settings.
            export_xml: controls the creation of the OpenMC model
                files (xml files). Set to True to create the OpenMC files with
                the default settings as determined by the NeutronicsModel
                attributes or set to False and use existing xml files or run
                the export_xml() method yourself with more
                direct control over the settings and creation of the xml files.

        Returns:
            The h5 simulation output filename
        """
        if export_xml is True:
            self.export_xml()

        if export_h5m is True:
            os.system('rm *.h5')
            self.geometry.export_h5m()

        # checks all the nessecary files are found
        for required_file in ['geometry.xml', 'materials.xml', 'settings.xml',
                              'tallies.xml']:
            if not Path(required_file).is_file():
                msg = "{} file was not found. Please set export_xml \
                    to True or use the export_xml() \
                    method to create the xml files".format(required_file)
                raise FileNotFoundError(msg)

        if not Path('dagmc.h5m').is_file():
            msg = """dagmc.h5m file was not found. Please set export_h5m to
                  True or use the export_h5m() methods to create the dagmc.h5m
                  file"""
            raise FileNotFoundError(msg)

        # Deletes summary.h5m if it already exists.
        # This avoids permission problems when trying to overwrite the file
        os.system('rm summary.h5')
        os.system('rm statepoint.' + str(self.simulation_batches) + '.h5')

        self.statepoint_filename = self.model.run(
            output=verbose, threads=threads
        )
        self.results = get_neutronics_results_from_statepoint_file(
            statepoint_filename=self.statepoint_filename,
            fusion_power=self.fusion_power
        )

        with open(cell_tally_results_filename, 'w') as outfile:
            json.dump(self.results, outfile, indent=4, sort_keys=True)

        return self.statepoint_filename

    def export_html(
            self,
            filename: Optional[str] = "neutronics_model.html",
            facet_splines: Optional[bool] = True,
            facet_circles: Optional[bool] = True,
            tolerance: Optional[float] = 1.,
            view_plane: Optional[str] = 'RZ',
            number_of_source_particles: Optional[int] = 1000):
        """Creates a html graph representation of the points for the Shape
        objects that make up the reactor and optionally the source. Shapes
        are colored by their .color property. Shapes are also labelled by their
        .name. If filename provided doesn't end with .html then .html will be
        added.

        Args:
            filename: the filename used to save the html graph. Defaults to
                neutronics_model.html
            facet_splines: If True then spline edges will be faceted. Defaults
                to True.
            facet_circles: If True then circle edges will be faceted. Defaults
                to True.
            tolerance: faceting toleranceto use when faceting cirles and
                splines. Defaults to 1e-3.
            view_plane: The plane to project. Options are 'XZ', 'XY', 'YZ',
                'YX', 'ZY', 'ZX', 'RZ' and 'XYZ'. Defaults to 'RZ'. Defaults to
                'RZ'.
            number_of_source_particles
        Returns:
            plotly.Figure(): figure object
        """

        fig = self.geometry.export_html(
            filename=None,
            facet_splines=facet_splines,
            facet_circles=facet_circles,
            tolerance=tolerance,
            view_plane=view_plane,
        )

        if number_of_source_particles != 0:
            source_filename = create_inital_particles(
                self.source, number_of_source_particles)
            points = extract_points_from_initial_source(
                source_filename, view_plane)

            fig.add_trace(
                plotly_trace(
                    points=points,
                    mode="markers",
                    name='source'
                )
            )

        if filename is not None:

            Path(filename).parents[0].mkdir(parents=True, exist_ok=True)

            path_filename = Path(filename)

            if path_filename.suffix != ".html":
                path_filename = path_filename.with_suffix(".html")

            fig.write_html(str(path_filename))

            print("Exported html graph to ", path_filename)

        return fig
