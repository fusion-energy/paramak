import paramak
import neutronics_material_maker as nmm

class NeutronicsModelFromReactor():
    """Creates a neuronics model of the provided reactor geometry with assigned
    materials, plasma source and neutronics tallies.

    Arguments:
        materials: (dict): Where the dictionary keys are the material tag
            and the dictionary values are either a string, openmc.Material or
            neutronics-material-maker. All components within the
            Reactor() object must be accounted for. Material tags required
            for the reactor can be obtained with Reactor().materials.
        simulation_batches: (int): the number of batch to simulate
        simulation_particles_per_batches: (int): particles per batch
        tallies: (list of strings): the tallies to calculate, options include
            TBR, blanket_heat, center_column_heat
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
        tallies,
        ion_density_origin,
        ion_density_peaking_factor,
        ion_density_pedestal,
        ion_density_separatrix,
        ion_temperature_origin,
        ion_temperature_peaking_factor,
        ion_temperature_pedestal,
        ion_temperature_separatrix,
        pedestal_radius,
        shafranov_shift,
        triangularity,
        ion_temperature_beta,
    ):

        self.reactor = reactor
        self.materials = materials
        self.tallies = tallies
        self.ion_density_origin = ion_density_origin
        self.ion_density_peaking_factor = ion_density_peaking_factor
        self.ion_density_pedestal = ion_density_pedestal
        self.ion_density_separatrix = ion_density_separatrix
        self.ion_temperature_origin = ion_temperature_origin
        self.ion_temperature_peaking_factor = ion_temperature_peaking_factor
        self.ion_temperature_pedestal = ion_temperature_pedestal
        self.ion_temperature_separatrix = ion_temperature_separatrix
        self.pedestal_radius = pedestal_radius
        self.shafranov_shift = shafranov_shift
        self.triangularity = triangularity
        self.ion_temperature_beta = ion_temperature_beta


    def create_materials(self):

        openmc_materials = {}
        for material_tag, material_entry in self.materials.items(): 
            if isinstance(material_entry, str):
                material = nmm.Material(material_entry, material_tag=material_tag)
                openmc_materials[material_tag] = material.openmc_material)
            if isinstance(material_entry, openmc.Material):
                openmc_materials[material_tag] = material_entry
            if isinstance(material_entry, (nmm.Material, nmm.MultiMaterial))
                openmc_materials[material_tag] = material_entry.openmc_material

        self.openmc_materials = openmc_materials

        mats = openmc.Materials(list(self.openmc_materials.values()))
        
    def create_plasma_source(self):
        # "elongation": 1.557,
        # "major_radius": 9.06,
        # "minor_radius": 2.92258,
        # "plasma_id": 1,

        # details of the birth locations and energy of the neutronis
        source = openmc.Source()
        source.space = openmc.stats.Point((self.reactor.major_radius, 0, 0))
        source.angle = openmc.stats.Isotropic()
        source.energy = openmc.stats.Discrete([14e6], [1])
 
        self.plasma_source = source

    def create_neutronics_geometry(self):
    """
    Uses Trelis together with a python script to
    reading the stp files assign material tags to
    the volumes and create a watertight h5m DAGMC
    file which can be used as neutronics geometry.
    """

        my_reactor.export_stp()

        my_reactor.export_neutronics_description()

        os.system("trelis -batch -nographics make_faceteted_neutronics_model.py")

        os.system("make_watertight dagmc_notwatertight.h5m -o dagmc.h5m")


    def create_neutronics_model(self):
        """Uses OpenMC python API to make a neutronics model, including tallies
        (outputs), simulation settings (batches, particles per batch)"""


        # this is the underlying geometry container that is filled with the
        # faceteted CAD model
        universe = openmc.Universe()
        geom = openmc.Geometry(universe)

        # settings for the number of neutrons to simulate
        settings = openmc.Settings()
        settings.batches = self.simulation_batches
        settings.inactive = 0
        settings.particles = self.simulation_particles_per_batches
        settings.run_mode = "fixed source"
        settings.dagmc = True

        settings.source = self.plasma_source

        # details about what neutrons interactions to keep track of (called a
        # tally)
        tallies = openmc.Tallies()

        if 'TBR' in self.tallies
        material_filter = openmc.MaterialFilter(blanket_mat)
        tbr_tally = openmc.Tally(name="TBR")
        tbr_tally.filters = [material_filter]
        tbr_tally.scores = ["(n,Xt)"]  # where X is a wild card
        tallies.append(tbr_tally)
    
        # make the model from gemonetry, materials, settings and tallies
        self.model =  = openmc.model.Model(geom, mats, settings, tallies)


    def simulate(self):
        # run the simulation
        self.output_filename = self.model.run()
    
    def get_results(self):
        """
        Reads the output file from the neutronics simulation
        and prints the TBR tally result to screen
        """

        # open the results file
        sp = openmc.StatePoint(self.output_filename)

        # access the tally
        tbr_tally = sp.get_tally(name="TBR")
        df = tbr_tally.get_pandas_dataframe()
        tbr_tally_result = df["mean"].sum()

        # print result
        print("The tritium breeding ratio was found, TBR = ", tbr_tally_result)
        # return tbr_tally_result
    
    
