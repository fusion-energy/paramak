
import math
import openmc
import paramak as p 

my_reactor = p.BallReactorGradedBlanket(
    inner_bore_radial_thickness=10,
    inboard_tf_leg_radial_thickness=20,
    center_column_shield_radial_thickness=10,
    divertor_radial_thickness=130,
    inner_plasma_gap_radial_thickness=20,
    plasma_radial_thickness=250,
    outer_plasma_gap_radial_thickness=20,
    firstwall_radial_thickness=20,
    blanket_radial_thickness=50,
    blanket_rear_wall_radial_thickness=30,
    number_of_blanket_layers=4,
    elongation=2,
    triangularity=0.5,
    plasma_gap_vertical_thickness=20,
    rotation_angle=360
)

# Ring source at plasma major radius
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
        "center_column_shield_mat": "copper",
        "divertor_mat": "copper",
        "firstwall_mat": "copper",
        "blanket_layer_1_mat": "copper",    # insert materials for all blanket layers in same form
        "blanket_layer_2_mat": "copper",
        "blanket_layer_3_mat": "copper",
        "blanket_layer_4_mat": "copper",
        "blanket_rear_wall_mat": "copper"
    },
    cell_tallies=["TBR"],
    simulation_batches=10,
    simulation_particles_per_batch=1000
)

my_model.simulate(method="trelis")
