"""Demonstrates the use of reaction rates in the cell tally.
(n,Xp) is MT number 203 and scores all proton (hydrogen) production
(n,Xt) is MT number 205 and scores all tritium production
(n,Xa) is MT number 207 and scores all alpha paticle (helium) production
https://docs.openmc.org/en/latest/usersguide/tallies.html#scores
"""


import openmc
import paramak


def main():
    my_shape = paramak.CenterColumnShieldHyperbola(
        height=500,
        inner_radius=50,
        mid_radius=60,
        outer_radius=100,
        material_tag='center_column_shield_mat',
        method='pymoab'
    )

    # makes the openmc neutron source at x,y,z 0, 0, 0 with isotropic
    # directions
    source = openmc.Source()
    source.space = openmc.stats.Point((0, 0, 0))
    source.energy = openmc.stats.Discrete([14e6], [1])
    source.angle = openmc.stats.Isotropic()

    # converts the geometry into a neutronics geometry
    my_model = paramak.NeutronicsModel(
        geometry=my_shape,
        source=source,
        materials={'center_column_shield_mat': 'Be'},
        cell_tallies=['(n,Xa)', '(n,Xt)', '(n,Xp)'],
        mesh_tally_3d=['(n,Xa)', '(n,Xt)', '(n,Xp)'],
        mesh_tally_2d=['(n,Xa)', '(n,Xt)', '(n,Xp)'],
        simulation_batches=2,
        simulation_particles_per_batch=10,
    )

    # performs an openmc simulation on the model
    my_model.simulate()

    # this extracts the values from the results dictionary
    print(my_model.results)


if __name__ == "__main__":
    main()
