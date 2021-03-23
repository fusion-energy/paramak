
import math
import openmc
import paramak as p 

my_reactor = p.BallReactorLayeredBlanket(
    inner_bore_radial_thickness=10,
    inboard_tf_leg_radial_thickness=30,
    center_column_shield_radial_thickness=60,
    divertor_radial_thickness=150,
    inner_plasma_gap_radial_thickness=30,
    plasma_radial_thickness=300,
    outer_plasma_gap_radial_thickness=30,
    firstwall_radial_thickness=30,
    blanket_radial_thickness=50,
    number_of_blanket_layers=4,
    blanket_rear_wall_radial_thickness=30,
    elongation=2,
    triangularity=0.55,
    number_of_tf_coils=16,
    rotation_angle=360,
    pf_coil_radial_thicknesses=[50, 50, 50, 50],
    pf_coil_vertical_thicknesses=[50, 50, 50, 50],
    pf_coil_to_rear_blanket_radial_gap=50,
    pf_coil_to_tf_coil_radial_gap=50,
    outboard_tf_coil_radial_thickness=100,
    outboard_tf_coil_poloidal_thickness=50
)

# Ring source at plasma major radius (requires updated OpenMC)
source = openmc.Source()
radius = openmc.stats.Discrete([my_reactor.major_radius], [1])
z_values = openmc.stats.Discrete([0], [1])
angle = openmc.stats.Uniform(a=0., b=my_reactor.rotation_angle * math.pi / 180)

source.space = openmc.stats.CylindricalIndependent(r=radius, phi=angle, z=z_values, origin=(0.0, 0.0, 0.0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])   # 14 MeV monoenergetic

my_model = p.NeutronicsModel(
    geometry=my_reactor,
    source=source,
    materials={
        "inboard_tf_coils_mat": "copper",
        "center_column_shield_mat": "WC",
        "divertor_mat": "tungsten",
        "firstwall_mat": "eurofer",
        "blanket_layer_1_mat": "Li4SiO4",    # insert materials for all blanket layers in same form
        "blanket_layer_2_mat": "Li4SiO4",
        "blanket_layer_3_mat": "Li4SiO4",
        "blanket_layer_4_mat": "Li4SiO4",
        "blanket_rear_wall_mat": "eurofer",
        "pf_coil_mat": "copper",
        "pf_coil_case_mat": "copper",
        "tf_coil_mat": "copper"
    },
    cell_tallies=["TBR"],
    simulation_batches=10,
    simulation_particles_per_batch=1000
)

my_model.simulate(method="trelis")
