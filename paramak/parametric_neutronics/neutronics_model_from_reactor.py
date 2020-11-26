
import json
import os
import warnings
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

try:
    from parametric_plasma_source import PlasmaSource, SOURCE_SAMPLING_PATH
except BaseException:
    warnings.warn('parametric_plasma_source not found distributed plasma \
            sources are not avaialbe in Neutronics simulations', UserWarning)

try:
    import openmc
except BaseException:
    warnings.warn('OpenMC not found, NeutronicsModelFromReactor.simulate \
            method not available', UserWarning)

try:
    import neutronics_material_maker as nmm
except BaseException:
    warnings.warn("neutronics_material_maker not found, \
            NeutronicsModelFromReactor.materials can't accept strings or \
            neutronics_material_maker objects", UserWarning)


class NeutronicsModelFromReactor():
    """Creates a neuronics model of the provided reactor geometry with assigned
    materials, plasma source and neutronics tallies.

    Arguments:
        reactor: (paramak.Reactor): The reactor object to convert to a
            neutronics model. e.g. reactor=paramak.BallReactor() or
            reactor=paramak.SubmersionReactor() .
        materials: (dict): Where the dictionary keys are the material tag
            and the dictionary values are either a string, openmc.Material,
            neutronics-material-maker.Material or
            neutronics-material-maker.MultiMaterial. All components within the
            Reactor() object must be accounted for. Material tags required
            for the reactor can be obtained with Reactor().material_tags.
        cell_tallies: (list of strings): the cell based tallies to calculate,
            options include TBR, heating and flux
        mesh_tally_2D: (list of strings): the mesh based tallies to calculate,
            options include tritium_production, heating and flux
        fusion_power: (float): the power in watts emitted by the fusion
            reaction recalling that each DT fusion reaction emitts 17.6 MeV or
            2.819831e-12 Joules
        method: (str): The method to use when making the imprinted and
            merged geometry. Options are 'trelis' or 'ppp'. Further details
            on imprinting and merging are available on the DAGMC homepage
            https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html
            The Parallel-PreProcessor is an open-source tool available
            https://github.com/ukaea/parallel-preprocessor and can be used
            in conjunction with the OCC_faceter
            (https://github.com/makeclean/occ_faceter) to create imprinted
            and merged geometry while Trelis (also known as Cubit) is
            available from the CoreForm website https://www.coreform.com/
        simulation_batches: (int): the number of batch to simulate.
        simulation_particles_per_batch: (int): particles per batch.
        ion_density_origin: (float): 1.09e20,
        ion_density_peaking_factor: (float): 1,
        ion_density_pedestal: (float): 1.09e20,
        ion_density_separatrix: (float): 3e19,
        ion_temperature_origin: (float): 45.9,
        ion_temperature_peaking_factor: (float): 8.06,
        ion_temperature_pedestal: (float): 6.09,
        ion_temperature_separatrix: (float): 0.1,
        pedestal_radius: (float): 0.8 * 2.92258,
        shafranov_shift: (float): 0.44789,
        triangularity: (float): 0.270,
        ion_temperature_beta: (float): 6,
        merge_tolerance(float): the tolerance to use when merging surfaces.
            Defaults to 1e-4.
        faceting_tolerance(float): the tolerance to use when faceting surfaces.
            Defaults to 1e-1.
        mesh_2D_resolution (tuple of ints): The mesh resolution in the height
            and width directions. The larger the resolution the finer the mesh
            and more computational intensity is required to converge each mesh
            element.
    """

    def __init__(
        self,
        reactor,
        materials,
        cell_tallies=None,
        mesh_tally_2D=None,
        fusion_power=1e9,
        method='ppp',
        simulation_batches=100,
        simulation_particles_per_batch=10000,
        ion_density_peaking_factor=1,
        ion_density_origin=1.09e20,
        ion_density_pedestal=1.09e20,
        ion_density_separatrix=3e19,
        ion_temperature_origin=45.9,
        ion_temperature_peaking_factor=8.06,
        ion_temperature_pedestal=6.09,
        ion_temperature_separatrix=0.1,
        pedestal_radius_factor=0.8,
        shafranov_shift=0.44789,
        ion_temperature_beta=6,
        max_lost_particles=10,
        faceting_tolerance=1e-1,
        merge_tolerance=1e-4,
        mesh_2D_resolution=(400, 400)
    ):

        self.reactor = reactor
        self.materials = materials
        self.cell_tallies = cell_tallies
        self.mesh_tally_2D = mesh_tally_2D
        self.ion_density_origin = ion_density_origin
        self.ion_density_peaking_factor = ion_density_peaking_factor
        self.ion_density_pedestal = ion_density_pedestal
        self.ion_density_separatrix = ion_density_separatrix
        self.ion_temperature_origin = ion_temperature_origin
        self.ion_temperature_peaking_factor = ion_temperature_peaking_factor
        self.ion_temperature_pedestal = ion_temperature_pedestal
        self.ion_temperature_separatrix = ion_temperature_separatrix
        self.pedestal_radius_factor = pedestal_radius_factor
        self.shafranov_shift = shafranov_shift
        self.ion_temperature_beta = ion_temperature_beta
        self.method = 'ppp'
        self.simulation_batches = simulation_batches
        self.simulation_particles_per_batch = simulation_particles_per_batch
        self.max_lost_particles = max_lost_particles
        self.faceting_tolerance = faceting_tolerance
        self.merge_tolerance = merge_tolerance
        self.mesh_2D_resolution = mesh_2D_resolution

        self.model = None
        self.fusion_power = fusion_power

        # Only 360 degree models are supported for now as reflecting surfaces
        # are needed for sector models and they are not currently supported
        if reactor.rotation_angle != 360:
            reactor.rotation_angle = 360
            print('remaking reactor as it was not set to 360 degrees')
            reactor.solid
            # TODO make use of reactor.create_solids() here

    @property
    def faceting_tolerance(self):
        return self._faceting_tolerance

    @faceting_tolerance.setter
    def faceting_tolerance(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError(
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
            raise ValueError(
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
                raise ValueError(
                    "NeutronicsModelFromReactor.cell_tallies should be a\
                    list")
            output_options = ['TBR', 'heating', 'flux', 'fast flux', 'dose']
            for entry in value:
                if entry not in output_options:
                    raise ValueError(
                        "NeutronicsModelFromReactor.cell_tallies argument",
                        entry,
                        "not allowed, the following options are supported",
                        output_options)
        self._cell_tallies = value

    @property
    def mesh_tally_2D(self):
        return self._mesh_tally_2D

    @mesh_tally_2D.setter
    def mesh_tally_2D(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise ValueError(
                    "NeutronicsModelFromReactor.mesh_tally_2D should be a\
                    list")
            output_options = ['tritium_production', 'heating', 'flux',
                              'fast flux', 'dose']
            for entry in value:
                if entry not in output_options:
                    raise ValueError(
                        "NeutronicsModelFromReactor.mesh_tally_2D argument",
                        entry,
                        "not allowed, the following options are supported",
                        output_options)
        self._mesh_tally_2D = value

    @property
    def materials(self):
        return self._materials

    @materials.setter
    def materials(self, value):
        if not isinstance(value, dict):
            raise ValueError("NeutronicsModelFromReactor.materials should be a\
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
            raise ValueError(
                "NeutronicsModelFromReactor.simulation_batches should be an int")
        self._simulation_batches = value

    @property
    def simulation_particles_per_batch(self):
        return self._simulation_particles_per_batch

    @simulation_particles_per_batch.setter
    def simulation_particles_per_batch(self, value):
        if isinstance(value, float):
            value = int(value)
        if not isinstance(value, int):
            raise ValueError(
                "NeutronicsModelFromReactor.simulation_particles_per_batch\
                    should be an int")
        self._simulation_particles_per_batch = value

    def create_materials(self):
        # checks all the required materials are present
        for reactor_material in self.reactor.material_tags:
            if reactor_material not in self.materials.keys():
                raise ValueError(
                    "material included by the reactor model has not \
                    been added", reactor_material)

        # checks that no extra materials we added
        for reactor_material in self.materials.keys():
            if reactor_material not in self.reactor.material_tags:
                raise ValueError(
                    "material has been added that is not needed for this \
                    reactor model", reactor_material)

        openmc_materials = {}
        for material_tag, material_entry in self.materials.items():
            if isinstance(material_entry, str):
                material = nmm.Material(
                    material_entry, material_tag=material_tag)
                openmc_materials[material_tag] = material.openmc_material
            elif isinstance(material_entry, openmc.Material):
                # sets the material name in the event that it had not been set
                material_entry.name = material_tag
                openmc_materials[material_tag] = material_entry
            elif isinstance(material_entry, (nmm.Material, nmm.MultiMaterial)):
                # sets the material tag in the event that it had not been set
                material_entry.material_tag = material_tag
                openmc_materials[material_tag] = material_entry.openmc_material
            else:
                raise ValueError("materials must be either a str, \
                    openmc.Material, nmm.MultiMaterial or nmm.Material object \
                    not a ", type(material_entry), material_entry)

        self.openmc_materials = openmc_materials

        self.mats = openmc.Materials(list(self.openmc_materials.values()))

        return self.mats

    def create_plasma_source(self):
        """Uses the parametric-plasma-source to create a ditributed neutron
        source for use in the simulation"""

        self.pedestal_radius = self.pedestal_radius_factor * \
            (self.reactor.minor_radius / 100)

        my_plasma = PlasmaSource(
            elongation=self.reactor.elongation,
            ion_density_origin=self.ion_density_origin,
            ion_density_peaking_factor=self.ion_density_peaking_factor,
            ion_density_pedestal=self.ion_density_pedestal,
            ion_density_separatrix=self.ion_density_separatrix,
            ion_temperature_origin=self.ion_temperature_origin,
            ion_temperature_peaking_factor=self.ion_temperature_peaking_factor,
            ion_temperature_pedestal=self.ion_temperature_pedestal,
            ion_temperature_separatrix=self.ion_temperature_separatrix,
            major_radius=self.reactor.major_radius / 100,
            minor_radius=self.reactor.minor_radius / 100,
            pedestal_radius=self.pedestal_radius,
            plasma_id=1,
            shafranov_shift=self.shafranov_shift,
            triangularity=self.reactor.triangularity,
            ion_temperature_beta=self.ion_temperature_beta,
        )

        source = openmc.Source()
        source.library = SOURCE_SAMPLING_PATH
        source.parameters = str(my_plasma)

        self.source = source

        return source

    def create_neutronics_geometry(self, method=None):
        """Produces a dagmc.h5m neutronics file compatable with DAGMC
        simulations. This is done by first exporting the stp files for the
        whole reactor, then exporting the neutronics description of the reactor
        , then there are two methods available for producing the imprinted and
        merged h5m geometry. The next step is to make the geometry watertight
        which uses make_watertight from DAGMC. If using the Trelis option you
        must have the make_faceteted_neutronics_model.py in the same directory
        as your Python script.

        Arguments:
            method: (str): The method to use when making the imprinted and
                merged geometry. Options are PPP or Trelis. Defaults to
                NeutronicsModelFromReactor.method. where options ae further
                described.
        """

        os.system('rm dagmc_not_watertight.h5m')
        os.system('rm dagmc.h5m')

        self.reactor.export_stp()
        self.reactor.export_neutronics_description()

        if method is None:
            method = self.method
            if method not in ['ppp', 'trelis']:
                raise ValueError(
                    "the method using in create_neutronics_geometry \
                    should be either ppp or trelis not", method)

        if method == 'ppp':
            # as the installer connects to the system python not the conda python
            # this full path is needed for now
            if os.system(
                    '/usr/bin/python3 /usr/bin/geomPipeline.py manifest.json') != 0:
                raise ValueError(
                    "geomPipeline.py failed, check PPP is installed")

            # TODO allow tolerance to be user controlled
            if os.system(
                    'occ_faceter manifest_processed/manifest_processed.brep') != 0:
                raise ValueError(
                    "occ_faceter failed, check occ_faceter is install and the \
                    occ_faceter/bin folder is in the path directory")

        elif method == 'trelis':

            if not Path("make_faceteted_neutronics_model.py").is_file():
                raise ValueError("The make_faceteted_neutronics_model.py was \
                    not found in the directory")
            os.system("trelis -batch -nographics make_faceteted_neutronics_model.py \"faceting_tolerance='" +
                      str(self.faceting_tolerance) + "'\" \"merge_tolerance='" + str(self.merge_tolerance) + "'\"")

            if not Path("dagmc_not_watertight.h5m").is_file():
                raise ValueError("The dagmc_not_watertight.h5m was not found \
                    in the directory, the Trelis stage has failed")

        if not Path("dagmc_not_watertight.h5m").is_file():
            raise ValueError(
                "The" +
                method +
                "failed to create a dagmc_not_watertight.h5m file")

        if os.system(
                "make_watertight dagmc_not_watertight.h5m -o dagmc.h5m") != 0:
            raise ValueError(
                "make_watertight failed, check DAGMC is install and the \
                    DAGMC/bin folder is in the path directory")

        print('neutronics model saved as dagmc.h5m')

    def create_neutronics_model(self, method=None):
        """Uses OpenMC python API to make a neutronics model, including tallies
        (cell_tallies and mesh_tally_2D), simulation settings (batches,
        particles per batch)

        Arguments:
            method: (str): The method to use when making the imprinted and
                merged geometry. Options are PPP or Trelis. Defaults to
                NeutronicsModelFromReactor.method. where options ae further
                described.
        """

        self.create_materials()
        self.create_plasma_source()
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
        tallies = openmc.Tallies()

        if self.mesh_tally_2D is not None:

            # Create mesh which will be used for tally
            mesh_xz = openmc.RegularMesh()
            mesh_xz.dimension = [
                self.mesh_2D_resolution[1],
                1,
                self.mesh_2D_resolution[0]]
            mesh_xz.lower_left = [-self.reactor.largest_dimension, -
                                  1, -self.reactor.largest_dimension]
            mesh_xz.upper_right = [
                self.reactor.largest_dimension,
                1,
                self.reactor.largest_dimension]

            mesh_xy = openmc.RegularMesh()
            mesh_xy.dimension = [
                self.mesh_2D_resolution[1],
                self.mesh_2D_resolution[0],
                1]
            mesh_xy.lower_left = [-self.reactor.largest_dimension, -
                                  self.reactor.largest_dimension, -1]
            mesh_xy.upper_right = [
                self.reactor.largest_dimension,
                self.reactor.largest_dimension,
                1]

            mesh_yz = openmc.RegularMesh()
            mesh_yz.dimension = [1,
                                 self.mesh_2D_resolution[1],
                                 self.mesh_2D_resolution[0]]
            mesh_yz.lower_left = [-1, -self.reactor.largest_dimension, -
                                  self.reactor.largest_dimension]
            mesh_yz.upper_right = [1,
                                   self.reactor.largest_dimension,
                                   self.reactor.largest_dimension]

            if 'tritium_production' in self.mesh_tally_2D:
                mesh_filter = openmc.MeshFilter(mesh_xz)
                mesh_tally = openmc.Tally(
                    name='tritium_production_on_2D_mesh_xz')
                mesh_tally.filters = [mesh_filter]
                mesh_tally.scores = ['(n,Xt)']
                tallies.append(mesh_tally)

                mesh_filter = openmc.MeshFilter(mesh_xy)
                mesh_tally = openmc.Tally(
                    name='tritium_production_on_2D_mesh_xy')
                mesh_tally.filters = [mesh_filter]
                mesh_tally.scores = ['(n,Xt)']
                tallies.append(mesh_tally)

                mesh_filter = openmc.MeshFilter(mesh_yz)
                mesh_tally = openmc.Tally(
                    name='tritium_production_on_2D_mesh_yz')
                mesh_tally.filters = [mesh_filter]
                mesh_tally.scores = ['(n,Xt)']
                tallies.append(mesh_tally)

            if 'heating' in self.mesh_tally_2D:
                mesh_filter = openmc.MeshFilter(mesh_xz)
                mesh_tally = openmc.Tally(name='heating_on_2D_mesh_xz')
                mesh_tally.filters = [mesh_filter]
                mesh_tally.scores = ['heating']
                tallies.append(mesh_tally)

                mesh_filter = openmc.MeshFilter(mesh_xy)
                mesh_tally = openmc.Tally(name='heating_on_2D_mesh_xy')
                mesh_tally.filters = [mesh_filter]
                mesh_tally.scores = ['heating']
                tallies.append(mesh_tally)

                mesh_filter = openmc.MeshFilter(mesh_yz)
                mesh_tally = openmc.Tally(name='heating_on_2D_mesh_yz')
                mesh_tally.filters = [mesh_filter]
                mesh_tally.scores = ['heating']
                tallies.append(mesh_tally)

            if 'flux' in self.mesh_tally_2D:
                mesh_filter = openmc.MeshFilter(mesh_xz)
                mesh_tally = openmc.Tally(name='flux_on_2D_mesh_xz')
                mesh_tally.filters = [mesh_filter]
                mesh_tally.scores = ['flux']
                tallies.append(mesh_tally)

                mesh_filter = openmc.MeshFilter(mesh_xy)
                mesh_tally = openmc.Tally(name='flux_on_2D_mesh_xy')
                mesh_tally.filters = [mesh_filter]
                mesh_tally.scores = ['flux']
                tallies.append(mesh_tally)

                mesh_filter = openmc.MeshFilter(mesh_yz)
                mesh_tally = openmc.Tally(name='flux_on_2D_mesh_yz')
                mesh_tally.filters = [mesh_filter]
                mesh_tally.scores = ['flux']
                tallies.append(mesh_tally)

        if self.cell_tallies is not None:

            if 'TBR' in self.cell_tallies:
                blanket_mat = self.openmc_materials['blanket_mat']
                material_filter = openmc.MaterialFilter(blanket_mat)
                tally = openmc.Tally(name="TBR")
                tally.filters = [material_filter]
                tally.scores = ["(n,Xt)"]  # where X is a wild card
                tallies.append(tally)

            if 'heating' in self.cell_tallies:
                for key, value in self.openmc_materials.items():
                    if key != 'DT_plasma':
                        material_filter = openmc.MaterialFilter(value)
                        tally = openmc.Tally(name=key + "_heating")
                        tally.filters = [material_filter]
                        tally.scores = ["heating"]
                        tallies.append(tally)

            if 'flux' in self.cell_tallies:
                for key, value in self.openmc_materials.items():
                    if key != 'DT_plasma':
                        material_filter = openmc.MaterialFilter(value)
                        tally = openmc.Tally(name=key + "_flux")
                        tally.filters = [material_filter]
                        tally.scores = ["flux"]
                        tallies.append(tally)

        # make the model from gemonetry, materials, settings and tallies
        self.model = openmc.model.Model(geom, self.mats, settings, tallies)

    def simulate(self, verbose=True, method=None):
        """Run the OpenMC simulation. Deletes exisiting simulation output
        (summary.h5) if files exists.

        Arguments:
            verbose: (Boolean, optional): Print the output from OpenMC (true)
                to the terminal and don't print the OpenMC output (false).
                Defaults to True.
            method: (str): The method to use when making the imprinted and
                merged geometry. Options are PPP or Trelis. Defaults to
                NeutronicsModelFromReactor.method.

        Returns:
            dict: the simulation output filename
        """

        if self.model is None:
            self.create_neutronics_model(method=method)

        # Deletes summary.h5m if it already exists.
        # This avoids permission problems when trying to overwrite the file
        os.system('rm summary.h5')

        self.output_filename = self.model.run(output=verbose)
        self.results = self.get_results()

        return self.output_filename

    def get_results(self):
        """Reads the output file from the neutronics simulation
        and prints the TBR tally result to screen

        Returns:
            dict: a dictionary of the simulation results
        """

        # open the results file
        sp = openmc.StatePoint(self.output_filename)

        results = defaultdict(dict)

        # access the tallies
        for key, tally in sp.tallies.items():

            if tally.name == 'TBR':

                df = tally.get_pandas_dataframe()
                tally_result = df["mean"].sum()
                tally_std_dev = df['std. dev.'].sum()
                results[tally.name] = {
                    'result': tally_result,
                    'std. dev.': tally_std_dev,
                }

            if tally.name.endswith('heating'):

                df = tally.get_pandas_dataframe()
                tally_result = df["mean"].sum()
                tally_std_dev = df['std. dev.'].sum()
                results[tally.name]['MeV per source particle'] = {
                    'result': tally_result / 1e6,
                    'std. dev.': tally_std_dev / 1e6,
                }
                results[tally.name]['Watts'] = {
                    'result': tally_result * 1.602176487e-19 * (self.fusion_power / ((17.58 * 1e6) / 6.2415090744e18)),
                    'std. dev.': tally_std_dev * 1.602176487e-19 * (self.fusion_power / ((17.58 * 1e6) / 6.2415090744e18)),
                }

            if tally.name.endswith('flux'):

                df = tally.get_pandas_dataframe()
                tally_result = df["mean"].sum()
                tally_std_dev = df['std. dev.'].sum()
                results[tally.name]['Flux per source particle'] = {
                    'result': tally_result,
                    'std. dev.': tally_std_dev,
                }

            if tally.name.startswith('tritium_production_on_2D_mesh'):

                my_tally = sp.get_tally(name=tally.name)
                my_slice = my_tally.get_slice(scores=['(n,Xt)'])

                my_slice.mean.shape = self.mesh_2D_resolution

                fig = plt.subplot()
                fig.imshow(my_slice.mean).get_figure().savefig(
                    'tritium_production_on_2D_mesh' + tally.name[-3:], dpi=300)
                fig.clear()

            if tally.name.startswith('heating_on_2D_mesh'):

                my_tally = sp.get_tally(name=tally.name)
                my_slice = my_tally.get_slice(scores=['heating'])

                my_slice.mean.shape = self.mesh_2D_resolution

                fig = plt.subplot()
                fig.imshow(my_slice.mean).get_figure().savefig(
                    'heating_on_2D_mesh' + tally.name[-3:], dpi=300)
                fig.clear()

            if tally.name.startswith('flux_on_2D_mesh'):

                my_tally = sp.get_tally(name=tally.name)
                my_slice = my_tally.get_slice(scores=['flux'])

                my_slice.mean.shape = self.mesh_2D_resolution

                fig = plt.subplot()
                fig.imshow(my_slice.mean).get_figure().savefig(
                    'flux_on_2D_mesh' + tally.name[-3:], dpi=300)
                fig.clear()

        self.results = json.dumps(results, indent=4, sort_keys=True)

        return results
