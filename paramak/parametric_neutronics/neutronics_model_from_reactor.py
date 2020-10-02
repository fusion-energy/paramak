import paramak


class NeutronModelFromReactor():
    """Creates a neuronics model of the provided reactor geometry with assigned
    materials, plasma source and neutronics tallies. Materials can be sepcified
    as strings (in which case they must be avaialbe in the 
    neutronics_material_maker package).

    Arguments:
        materials: (dict): Where the dictionary keys are the material tag
            and the dictionary values are either a string, openmc.Material or
            neutronics-material-maker. All components within the
            Reactor() object must be accounted for. Material tags required
            for the reactor can be obtained with Reactor().materials.
        plasma

        simulation_batches
        simulation_particles_per_batches

    Returns:
        a paramak neutronics model object: a neutronics model object that has
        generic functionality such as .simulate and .tbr
    """

    def __init__(
        self,
        reactor,
        materials,
        plasam,
        tallies, 
    ):


        super().__init__([])


    def create_materials(self):
    def create_plasma_source(self):
    def create_neutronics_geometry(self):
    def create_neutronics_model(self):
        """Uses OpenMC python API to make a neutronics model, including tallies
        (outputs), simulation settings (batches, particles per batch)"""
    def simulate(self):
    
    def get_results(self):
    
