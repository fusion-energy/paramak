import os
import json
from collections import defaultdict

try:
    from parametric_plasma_source import PlasmaSource, SOURCE_SAMPLING_PATH
except BaseException:
    raise Warning(
        'parametric_plasma_source not found distributed plasma sources \
        are not avaialbe in Neutronics simulations')

try:
    import openmc
except BaseException:
    raise Warning(
        'OpenMC not found, NeutronicsModelFromReactor.simulate method \
        not available')

try:
    import neutronics_material_maker as nmm
except BaseException:
    raise Warning("neutronics_material_maker not found, \
        NeutronicsModelFromReactor.materials can't accept strings or \
        neutronics_material_maker objects")


class NeutronicsModelFromReactor():
    """Creates a neuronics model of the provided reactor geometry with assigned
    materials, plasma source and neutronics tallies.

    Arguments:
        reactor: (paramak.Reactor): The reactor object to convert to a
            neutronics model. e.g. reactor=paramak.BallReactor() or
            reactor=paramak.SubmersionReactor() .
        materials: (dict): Where the dictionary keys are the material tag
            and the dictionary values are either a string, openmc.Material or
            neutronics-material-maker. All components within the
            Reactor() object must be accounted for. Material tags required
            for the reactor can be obtained with Reactor().materials.
        tallies: (list of strings): the tallies to calculate, options include
            TBR, blanket_heat, center_column_shield_heat
        fusion_power: (float): the power in watts emitted by the fusion reaction
            recalling that each DT fusion reaction emitts 17.6 MeV or
            2.819831e-12 Joules
        simulation_batches: (int): the number of batch to simulate
        simulation_particles_per_batch: (int): particles per batch
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

    Returns:
        a paramak neutronics model object: a neutronics model object that has
        generic functionality such as .simulate and .tbr
    """

    def __init__(
        self,
        reactor,
        materials,
        outputs,
        fusion_power=1e9,
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
        max_lost_particles=10
    ):
        # input by user
        self.reactor = reactor
        self.materials = materials
        self.outputs = outputs
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
        self.max_lost_particles = max_lost_particles
        self.simulation_batches = simulation_batches
        self.simulation_particles_per_batch = simulation_particles_per_batch

        self.model = None
        self.fusion_power = fusion_power

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, value):
        if not isinstance(value, list):
            raise ValueError("NeutronicsModelFromReactor.outputs should be a\
                list")
        output_options = ['TBR', 'heat', 'flux', 'fast flux', 'dose']
        for entry in value:
            if entry not in output_options:
                raise ValueError(
                    "NeutronicsModelFromReactor.outputs argument",
                    entry,
                    "not allowed, the following options are supported",
                    output_options)
        self._outputs = value

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
        for reactor_material in self.reactor.material_tags:
            if reactor_material not in self.materials.keys():
                raise ValueError(
                    "material included by the reactor model has not \
                    been added", reactor_material)

        if len(self.reactor.material_tags) is not len(self.materials.keys()):
            raise ValueError("materials must contain an entry for every \
                material in the reactor", self.reactor.material_tags)
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

    def create_neutronics_geometry(self, method='trelis'):
        """Produces a h5m neutronics geometry compatable with DAGMC simulations.
        This is done by first exporting the stp files for the whole reactor,
        then exporting the neutronics description of the reactor, then there
        are two methods available for producing the imprinted and merged h5m
        geometry. The next step is to make the geometry watertight which uses
        make_watertight from DAGMC. If using the Trelis option you must have
        the make_faceteted_neutronics_model.py in the same directory as your
        Python script.

        Arguments:
            method: (str): The method to use when making the imprinted and
                merged geometry. Options are 'trelis' or 'ppp'. Further details
                on imprinting and merging are available on the DAGMC homepage
                https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html
                The Parallel-PreProcessor is an open-source tool available
                https://github.com/ukaea/parallel-preprocessor and can be used
                in conjunction with the OCC_faceter
                (https://github.com/makeclean/occ_faceter) to create imprinted
                and merged geometry while Trelis (also known as Cubit) is
                avaialbe from the CoreForm website https://www.coreform.com/
        """

        if method not in ['ppp', 'trelis']:
            raise ValueError("the method using in create_neutronics_geometry \
                should be either ppp or trelis not", method)

        self.reactor.export_stp()
        self.reactor.export_neutronics_description()

        if method == 'ppp':
            os.system('/usr/bin/python /usr/bin/geomPipeline.py config.json')
            os.system('./occ_faceter brep')

        if method == 'trelis':
            os.system(
                "trelis -batch -nographics make_faceteted_neutronics_model.py")

        if os.system(
                "make_watertight dagmc_notwatertight.h5m -o dagmc.h5m") != 0:
            raise ValueError(
                "make_watertight failed, check DAGMC is install and the \
                    DAGMC/bin folder is in the path directory")

        print('neutronics model saved as dagmc.h5m')

    def create_neutronics_model(self, method='trelis'):
        """Uses OpenMC python API to make a neutronics model, including tallies
        (outputs), simulation settings (batches, particles per batch)

        Arguments:
            method: (str): The method to use when making the imprinted and
                merged geometry. Options are 'trelis' or 'ppp'. Further details
                on imprinting and merging are available on the DAGMC homepage
                https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html
                The Parallel-PreProcessor is an open-source tool available
                https://github.com/ukaea/parallel-preprocessor and can be used
                in conjunction with the OCC_faceter
                (https://github.com/makeclean/occ_faceter) to create imprinted
                and merged geometry while Trelis (also known as Cubit) is
                avaialbe from the CoreForm website https://www.coreform.com/
        """

        self.create_materials()
        self.create_plasma_source()
        self.create_neutronics_geometry(method=method)

        # this is the underlying geometry container that is filled with the
        # faceteted DGAMC CAD model
        universe = openmc.Universe()
        geom = openmc.Geometry(universe)

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

        if 'TBR' in self.outputs:
            blanket_mat = self.openmc_materials['blanket_mat']
            material_filter = openmc.MaterialFilter(blanket_mat)
            tally = openmc.Tally(name="TBR")
            tally.filters = [material_filter]
            tally.scores = ["(n,Xt)"]  # where X is a wild card
            tallies.append(tally)

        if 'heat' in self.outputs:

            for key, value in self.openmc_materials.items():
                if key != 'DT_plasma':
                    material_filter = openmc.MaterialFilter(value)
                    tally = openmc.Tally(name=key + "_heat")
                    tally.filters = [material_filter]
                    tally.scores = ["heating"]
                    tallies.append(tally)

        if 'flux' in self.outputs:
            for key, value in self.openmc_materials.items():
                if key != 'DT_plasma':
                    material_filter = openmc.MaterialFilter(value)
                    tally = openmc.Tally(name=key + "_flux")
                    tally.filters = [material_filter]
                    tally.scores = ["flux"]
                    tallies.append(tally)

        # make the model from gemonetry, materials, settings and tallies
        self.model = openmc.model.Model(geom, self.mats, settings, tallies)

    def simulate(self, verbose=True):
        """Run the OpenMC simulation with the specified simulation_batches and
        simulation_particles_per_batch and tallies. Terminal output can
        disabled by setting verbose=False.

        Arguments:
            verbose: (Boolean): Preint the output from OpenMC (true) to the
                terminal and don't print the OpenMC output (false). Defaults
                to True.
        """

        if self.model is None:
            self.create_neutronics_model()
        self.output_filename = self.model.run(output=verbose)
        self.results = self.get_results()

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

            df = tally.get_pandas_dataframe()
            tally_result = df["mean"].sum()
            tally_std_dev = df['std. dev.'].sum()

            if tally.name == 'TBR':

                results[tally.name] = {
                    'result': tally_result,
                    'std. dev.': tally_std_dev,
                }

            if tally.name.endswith('heat'):

                results[tally.name]['MeV per source particle'] = {
                    'result': tally_result / 1e6,
                    'std. dev.': tally_std_dev / 1e6,
                }
                results[tally.name]['Watts'] = {
                    'result': tally_result * 1.602176487e-19 * (self.fusion_power / ((17.58 * 1e6) / 6.2415090744e18)),
                    'std. dev.': tally_std_dev * 1.602176487e-19 * (self.fusion_power / ((17.58 * 1e6) / 6.2415090744e18)),
                }

        self.results = json.dumps(results, indent=4, sort_keys=True)

        return results
