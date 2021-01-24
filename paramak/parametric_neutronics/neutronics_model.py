
import json
import os
import pathlib
import shutil
import warnings
from pathlib import Path
from typing import List

from paramak import get_neutronics_results_from_statepoint_file

try:
    import openmc
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
    """Creates a neuronics model of the provided shape geometry with assigned
    materials, source and neutronics tallies. There are three methods
    available for producing the the DAGMC h5m file. The PyMoab option is able
    to produce non imprinted and non merged geometry so is more suited to
    individual components or reactors without touching surfaces. Trelis is
    the only method currently able to produce imprinted and merged DAGMC h5m
    geometry. PPP is a experimental route that has not been fully demonstrated
    yet but is partly intergrated to test this promising new method.
    make_watertight is also used to seal the DAGMC geoemtry produced by Trelis.
    Further details on imprinting and merging are available on the
    DAGMC homepage
    https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html
    The Parallel-PreProcessor is an open-source tool available
    https://github.com/ukaea/parallel-preprocessor and can be used in
    conjunction with the OCC_faceter
    (https://github.com/makeclean/occ_faceter) to create imprinted and
    merged geometry while Trelis (also known as Cubit) is available from
    the CoreForm website https://www.coreform.com/ version 17.1 is the version
    of Trelis used when testing the Paramak code.

    Arguments:
        geometry (paramak.Shape, paramak.Rector): The geometry to convert to a
            neutronics model. e.g. geometry=paramak.RotateMixedShape() or
            reactor=paramak.BallReactor() .
        cell_tallies (list of strings): the cell based tallies to calculate,
            options include TBR, heating and flux
        materials (dict): Where the dictionary keys are the material tag
            and the dictionary values are either a string, openmc.Material,
            neutronics-material-maker.Material or
            neutronics-material-maker.MultiMaterial. All components within the
            geometry object must be accounted for. Material tags required
            for a Reactor or Shape can be obtained with .material_tags.
        mesh_tally_2d (list of str): the 2D mesh based tallies to calculate,
            options include tritium_production, heating and flux.
        mesh_tally_3d (list of str): the 3D mesh based tallies to calculate,
            options include tritium_production, heating and flux.
        fusion_power (float): the power in watts emitted by the fusion
            reaction recalling that each DT fusion reaction emitts 17.6 MeV or
            2.819831e-12 Joules
        simulation_batches (int): the number of batch to simulate.
        simulation_particles_per_batch: (int): particles per batch.
        source (openmc.Source()): the particle source to use during the
            OpenMC simulation.
        merge_tolerance (float): the tolerance to use when merging surfaces.
            Defaults to 1e-4.
        faceting_tolerance (float): the tolerance to use when faceting surfaces.
            Defaults to 1e-1.
        mesh_2D_resolution (tuple of ints): The 3D mesh resolution in the height
            and width directions. The larger the resolution the finer the mesh
            and more computational intensity is required to converge each mesh
            element.
        mesh_3D_resolution (tuple of int): The 3D mesh resolution in the height,
            width and depth directions. The larger the resolution the finer the
            mesh and the more computational intensity is required to converge each
            mesh element.
    """

    def __init__(
        self,
        geometry,
        source,
        materials,
        cell_tallies=None,
        mesh_tally_2d=None,
        mesh_tally_3d=None,
        simulation_batches: int = 100,
        simulation_particles_per_batch: int = 10000,
        max_lost_particles: int = 10,
        faceting_tolerance: float = 1e-1,
        merge_tolerance: float = 1e-4,
        mesh_2D_resolution: float = (400, 400),
        mesh_3D_resolution: float = (100, 100, 100),
        fusion_power: float = 1e9  # convert from watts to activity source_activity
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
        self.faceting_tolerance = faceting_tolerance
        self.merge_tolerance = merge_tolerance
        self.mesh_2D_resolution = mesh_2D_resolution
        self.mesh_3D_resolution = mesh_3D_resolution
        self.fusion_power = fusion_power
        self.model = None
        self.results = None
        self.tallies = None
        self.output_filename = None
        self.statepoint_filename = None

    @property
    def faceting_tolerance(self):
        return self._faceting_tolerance

    @faceting_tolerance.setter
    def faceting_tolerance(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(
                "NeutronicsModelFromReactor.faceting_tolerance should be a\
                number (floats or ints are accepted)")
        if value < 0:
            raise ValueError(
                "NeutronicsModelFromReactor.faceting_tolerance should be a\
                positive number")
        self._faceting_tolerance = value

    @property
    def merge_tolerance(self):
        return self._merge_tolerance

    @merge_tolerance.setter
    def merge_tolerance(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(
                "NeutronicsModelFromReactor.merge_tolerance should be a\
                number (floats or ints are accepted)")
        if value < 0:
            raise ValueError(
                "NeutronicsModelFromReactor.merge_tolerance should be a\
                positive number")
        self._merge_tolerance = value

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
            output_options = ['TBR', 'heating', 'flux', 'spectra', 'dose']
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
            output_options = ['tritium_production', 'heating', 'flux',
                              'fast flux', 'dose']
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
            output_options = ['tritium_production', 'heating', 'flux',
                              'fast flux', 'dose']
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

    def create_materials(self):
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

        openmc_materials = {}
        for material_tag, material_entry in self.materials.items():
            openmc_material = self.create_material(
                material_tag, material_entry)
            openmc_materials[material_tag] = openmc_material

        self.openmc_materials = openmc_materials

        self.mats = openmc.Materials(list(self.openmc_materials.values()))

        return self.mats

    def create_neutronics_geometry(self, method: str = None):
        """Produces a dagmc.h5m neutronics file compatable with DAGMC
        simulations.

        Arguments:
            method: (str): The method to use when making the imprinted and
                merged geometry. Options are "ppp", "trelis", "pymoab" and
                None.  Defaults to None.
        """

        if method in ['ppp', 'trelis', 'pymoab']:
            os.system('rm dagmc_not_watertight.h5m')
            os.system('rm dagmc.h5m')
        elif method is None and Path('dagmc.h5m').is_file():
            print('Using previously made dagmc.h5m file')
        else:
            raise ValueError(
                "the method using in create_neutronics_geometry \
                should be either ppp, trelis, pymoab or None.", method)

        if method == 'ppp':

            raise NotImplementedError(
                "PPP + OCC Faceter / Gmesh option is under development and not \
                ready to be implemented. Further details on the repositories \
                https://github.com/makeclean/occ_faceter/ \
                https://github.com/ukaea/parallel-preprocessor ")

            # TODO when the development is ready to test
            # self.geometry.export_stp()
            # self.geometry.export_neutronics_description()
            # # as the installer connects to the system python not the conda
            # # python this full path is needed for now
            # if os.system(
            #         '/usr/bin/python3 /usr/bin/geomPipeline.py manifest.json') != 0:
            #     raise ValueError(
            #         "geomPipeline.py failed, check PPP is installed")

            # # TODO allow tolerance to be user controlled
            # if os.system(
            #         'occ_faceter manifest_processed/manifest_processed.brep') != 0:
            #     raise ValueError(
            #         "occ_faceter failed, check occ_faceter is install and the \
            #         occ_faceter/bin folder is in the path directory")
            # self._make_watertight()

        elif method == 'trelis':
            self.geometry.export_stp()
            self.geometry.export_neutronics_description()

            shutil.copy(
                src=pathlib.Path(__file__).parent.absolute() /
                'make_faceteted_neutronics_model.py',
                dst=pathlib.Path().absolute())

            if not Path("make_faceteted_neutronics_model.py").is_file():
                raise FileNotFoundError(
                    "The make_faceteted_neutronics_model.py was \
                    not found in the directory")
            os.system("trelis -batch -nographics make_faceteted_neutronics_model.py \"faceting_tolerance='" +
                      str(self.faceting_tolerance) + "'\" \"merge_tolerance='" + str(self.merge_tolerance) + "'\"")

            if not Path("dagmc_not_watertight.h5m").is_file():
                raise FileNotFoundError(
                    "The dagmc_not_watertight.h5m was not found \
                    in the directory, the Trelis stage has failed")
            self._make_watertight()

        elif method == 'pymoab':

            self.geometry.export_h5m(
                filename='dagmc.h5m',
                tolerance=self.faceting_tolerance
            )
        return 'dagmc.h5m'

    def _make_watertight(self):
        """Runs the DAGMC make_watertight script thatt seals the facetets of
        the geometry"""

        if not Path("dagmc_not_watertight.h5m").is_file():
            raise ValueError(
                "Failed to create a dagmc_not_watertight.h5m file")

        if os.system(
                "make_watertight dagmc_not_watertight.h5m -o dagmc.h5m") != 0:
            raise ValueError(
                "make_watertight failed, check DAGMC is install and the \
                    DAGMC/bin folder is in the path directory")

    def create_neutronics_model(self, method: str = None):
        """Uses OpenMC python API to make a neutronics model, including tallies
        (cell_tallies and mesh_tally_2d), simulation settings (batches,
        particles per batch).

        Arguments:
            method: (str): The method to use when making the imprinted and
                merged geometry. Options are "ppp", "trelis", "pymoab".
                Defaults to None.
        """

        self.create_materials()

        self.create_neutronics_geometry(method=method)

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
            mesh_xyz.dimension = self.mesh_3D_resolution
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

            for standard_tally in self.mesh_tally_3d:
                if standard_tally == 'tritium_production':
                    score = '(n,Xt)'  # where X is a wild card
                    prefix = 'tritium_production'
                else:
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
                self.mesh_2D_resolution[1],
                1,
                self.mesh_2D_resolution[0]
            ]

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

            mesh_xy = openmc.RegularMesh(mesh_id=3, name='2d_mesh_xy')
            mesh_xy.dimension = [
                self.mesh_2D_resolution[1],
                self.mesh_2D_resolution[0],
                1
            ]

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

            mesh_yz = openmc.RegularMesh(mesh_id=4, name='2d_mesh_yz')
            mesh_yz.dimension = [
                1,
                self.mesh_2D_resolution[1],
                self.mesh_2D_resolution[0]
            ]

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

            for standard_tally in self.mesh_tally_2d:
                if standard_tally == 'tritium_production':
                    score = '(n,Xt)'  # where X is a wild card
                    prefix = 'tritium_production'
                else:
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

        # make the model from gemonetry, materials, settings and tallies
        self.model = openmc.model.Model(
            geom, self.mats, settings, self.tallies)

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

    def simulate(self, verbose: bool = True, method: str = None,
                 cell_tally_results_filename: str = 'results.json'):
        """Run the OpenMC simulation. Deletes exisiting simulation output
        (summary.h5) if files exists.

        Arguments:
            verbose (Boolean, optional): Print the output from OpenMC (true)
                to the terminal and don't print the OpenMC output (false).
                Defaults to True.
            method (str): The method to use when making the imprinted and
                merged geometry. Options are "ppp", "trelis", "pymoab".
                Defaults to pymoab.

        Returns:
            dict: the simulation output filename
        """

        self.create_neutronics_model(method=method)

        # Deletes summary.h5m if it already exists.
        # This avoids permission problems when trying to overwrite the file
        os.system('rm summary.h5')
        os.system('rm statepoint.' + str(self.simulation_batches) + '.h5')

        # this removes any old file from previous simulations
        os.system('rm geometry.xml')
        os.system('rm materials.xml')
        os.system('rm settings.xml')
        os.system('rm tallies.xml')

        self.statepoint_filename = self.model.run(output=verbose)
        self.results = get_neutronics_results_from_statepoint_file(
            statepoint_filename=self.statepoint_filename,
            fusion_power=self.fusion_power
        )

        with open(cell_tally_results_filename, 'w') as outfile:
            json.dump(self.results, outfile, indent=4, sort_keys=True)

        return self.statepoint_filename
