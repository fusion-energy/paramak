import paramak


class BallReactor(paramak.BallReactor):
    """Creates a neuronics model of the ball reactor geometry with assigned
    materials, plasma source and neutronics tallies. Materials can be sepcified
    as strings (in which case they must be avaialbe in the 
    neutronics_material_maker package).

    Arguments:
        inboard_tf_leg_material (string): the material to use for the component 
        center_column_shield (string): the material to use for the component 
        divertor_material (string): the material to use for the component 
        firstwall_material (string): the material to use for the component 
        blanket_material (string): the material to use for the component 
        blanket_rear_wall_material (string): the material to use for the component 
        pf_coil_material (string): the material to use for the component 
        outboard_tf_coil_material (string): the material to use for the component 

        plasma

        inner_bore_radial_thickness (float): the radial thickness of the
            inner bore (cm)
        inboard_tf_leg_radial_thickness (float): the radial thickness of the
            inner leg of the toroidal field coils (cm)
        center_column_shield_radial_thickness (float): the radial thickness of
            the center column shield (cm)
        divertor_radial_thickness (float): the radial thickness of the divertor
            (cm), this fills the gap between the center column shield and
            blanket
        inner_plasma_gap_radial_thickness (float): the radial thickness of the
            inboard gap between the plasma and the center column shield (cm)
        plasma_radial_thickness (float): the radial thickness of the plasma
        outer_plasma_gap_radial_thickness (float): the radial thickness of the
            outboard gap between the plasma and firstwall (cm)
        firstwall_radial_thickness (float): the radial thickness of the first
            wall (cm)
        blanket_radial_thickness (float): the radial thickness of the blanket
            (cm)
        blanket_rear_wall_radial_thickness (float): the radial thickness of the
            rear wall of the blanket (cm)
        elongation (float): the elongation of the plasma
        triangularity (float): the triangularity of the plasma
        number_of_tf_coils (int): the number of tf coils
        pf_coil_to_rear_blanket_radial_gap (float): the radial distance between
            the rear blanket and the closest poloidal field coil (optional)
        pf_coil_radial_thicknesses (list of floats): the radial thickness of
            each poloidal field coil (optional)
        pf_coil_vertical_thicknesses (list of floats): the vertical thickness of
            each poloidal field coil (optional)
        pf_coil_to_tf_coil_radial_gap (float): the radial distance between the
            rear of the poloidal field coil and the toroidal field coil
            (optional)
        outboard_tf_coil_radial_thickness (float): the radial thickness of the
            toroidal field coil (optional)
        outboard_tf_coil_poloidal_thickness (float): the poloidal thickness of
            the toroidal field coil (optional)
        rotation_angle (float): the angle of the sector that is desired

    Returns:
        a paramak neutronics model object: a neutronics model object that has
        generic functionality such as .simulate and .tbr
    """

    def __init__(
        self,
        inboard_tf_leg_material,
        center_column_shield,
        divertor_material,
        firstwall_material,
        blanket_material,
        blanket_rear_wall_material,
        pf_coil_material,
        outboard_tf_coil_material,
        inner_bore_radial_thickness,
        inboard_tf_leg_radial_thickness,
        center_column_shield_radial_thickness,
        divertor_radial_thickness,
        inner_plasma_gap_radial_thickness,
        plasma_radial_thickness,
        outer_plasma_gap_radial_thickness,
        firstwall_radial_thickness,
        blanket_radial_thickness,
        blanket_rear_wall_radial_thickness,
        elongation,
        triangularity,
        number_of_tf_coils,
        pf_coil_to_rear_blanket_radial_gap=None,
        pf_coil_radial_thicknesses=None,
        pf_coil_vertical_thicknesses=None,
        pf_coil_to_tf_coil_radial_gap=None,
        outboard_tf_coil_radial_thickness=None,
        outboard_tf_coil_poloidal_thickness=None,
        rotation_angle=360,
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
    
