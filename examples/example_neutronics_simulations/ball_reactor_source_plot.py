"""This example makes a reactor geometry and a neutronics model. A homogenised
material made of enriched lithium lead and eurofer is being used as the blanket
material for this simulation in order to demonstrate the use of more complex
materials."""

import neutronics_material_maker as nmm
import openmc
import paramak
from parametric_plasma_source import SOURCE_SAMPLING_PATH, PlasmaSource


def make_model_and_simulate():
    """Makes a neutronics Reactor model and simulates the TBR"""

    # makes the 3d geometry
    my_reactor = paramak.BallReactor(
        inner_bore_radial_thickness=1,
        inboard_tf_leg_radial_thickness=30,
        center_column_shield_radial_thickness=60,
        divertor_radial_thickness=50,
        inner_plasma_gap_radial_thickness=30,
        plasma_radial_thickness=300,
        outer_plasma_gap_radial_thickness=30,
        firstwall_radial_thickness=3,
        blanket_radial_thickness=100,
        blanket_rear_wall_radial_thickness=3,
        elongation=2.75,
        triangularity=0.5,
        number_of_tf_coils=16,
        rotation_angle=360,
    )

    # creates a parametric plasma source, more details
    # https://github.com/open-radiation-sources/parametric-plasma-source
    my_plasma = PlasmaSource(
        ion_density_origin=1.09e20,
        ion_density_peaking_factor=1,
        ion_density_pedestal=1.09e20,
        ion_density_separatrix=3e19,
        ion_temperature_origin=45.9,
        ion_temperature_peaking_factor=8.06,
        ion_temperature_pedestal=6.09,
        ion_temperature_separatrix=0.1,
        elongation=2,
        triangularity=0.55,
        major_radius=2.5,  # note the source takes m arguments
        minor_radius=1.,  # note the source takes m arguments
        pedestal_radius=0.8 * 100,  # note the source takes m arguments
        plasma_id=1,
        shafranov_shift=0.44789,
        ion_temperature_beta=6
    )

    # assigns parametric plasma source as source
    source = openmc.Source()
    source.library = SOURCE_SAMPLING_PATH
    source.parameters = str(my_plasma)

    # makes the neutronics material
    neutronics_model = paramak.NeutronicsModel(
        geometry=my_reactor,
        source=source,
        materials={
            'inboard_tf_coils_mat': 'copper',
            'center_column_shield_mat': 'WC',
            'divertor_mat': 'eurofer',
            'firstwall_mat': 'eurofer',
            'blanket_mat': 'eurofer',
            'blanket_rear_wall_mat': 'eurofer'},
    )

    # exports the geometry and source in 2d (RZ) viewplane where R stands for
    # radius
    neutronics_model.export_html(
        filename='2d_source.html',
        view_plane='RZ'
    )

    # exports the geometry and source in 3d (XYZ) viewplane
    neutronics_model.export_html(
        filename='3d_source.html',
        view_plane='XYZ',
        number_of_source_particles=1000
    )


if __name__ == "__main__":
    make_model_and_simulate()
