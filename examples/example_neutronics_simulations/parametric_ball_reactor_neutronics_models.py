"""
Example which creates a simple neutronics model using a parametric reactor
"""

import os

import openmc
from neutronics_material_maker import Material, MultiMaterial

import paramak

def make_cad_model_with_paramak():
    """
    Makes a reactor object from using theparametric
    BallReactor. Exports the neutronics description
    and stp files for the reactor
    """
    my_reactor = paramak.BallReactor(
                                    inner_bore_radial_thickness=50,
                                    inboard_tf_leg_radial_thickness = 200,
                                    center_column_shield_radial_thickness= 50,
                                    divertor_radial_thickness=50,
                                    inner_plasma_gap_radial_thickness = 50,
                                    plasma_radial_thickness = 100,
                                    outer_plasma_gap_radial_thickness = 50,
                                    firstwall_radial_thickness=5,
                                    blanket_radial_thickness=100,
                                    blanket_rear_wall_radial_thickness=10,
                                    elongation=2,
                                    triangularity=0.55,
                                    number_of_tf_coils=16,
                                    rotation_angle=360
    )

    my_reactor.export_stp()

    my_reactor.export_neutronics_description()

    return my_reactor

def convert_stp_files_to_neutronics_geometry():
    """
    Uses Trelis together with a python script to
    reading the stp files assign material tags to
    the volumes and create a watertight h5m DAGMC
    file which can be used as neutronics geometry.
    """

    os.system('trelis -batch -nographics make_faceteted_neutronics_model.py')

    os.system('make_watertight dagmc_notwatertight.h5m -o dagmc.h5m')


def make_other_aspects_of_neutronics_model(my_reactor):
    """
    Makes and runs a simple OpenMC neutronics model with
    the materials with the same tags as the DAGMC neutronics
    geometry. The model also specifies the computational
    intensity (particles and batches) and the tally to record
    """

    # this is the underlying geometry container that is filled with the faceteted CAD model
    universe = openmc.Universe()
    geom = openmc.Geometry(universe)



    center_column_shield_material = MultiMaterial(material_tag='center_column_shield_mat',
                                                  materials=[Material(material_name=center_column_shield_coolant_material,
                                                                      temperature_in_C=center_column_shield_coolant_temperature_C,
                                                                      pressure_in_Pa=center_column_shield_coolant_pressure_Pa),
                                                             Material(material_name=center_column_shield_structural_material)],
                                                  fracs = [center_column_shield_coolant_fraction, center_column_shield_structural_fraction],
                                                  percent_type='vo', packing_fraction=1.0).openmc_material


    firstwall_material = MultiMaterial(material_tag='firstwall_mat',
                                       materials=[Material(material_name=firstwall_coolant_material,
                                                          temperature_in_C=firstwall_coolant_temperature_C,
                                                          pressure_in_Pa=firstwall_coolant_pressure_Pa),
                                                  Material(material_name=firstwall_structural_material),
                                                  Material(material_name=firstwall_armour_material)],
                                      fracs = [firstwall_coolant_fraction, firstwall_structural_fraction, firstwall_armour_fraction],
                                      percent_type='vo', packing_fraction=1.0).openmc_material

    blanket_material = MultiMaterial(material_tag='blanket_mat',
                                     materials=[Material(material_name=blanket_coolant_material,
                                                         temperature_in_C=blanket_coolant_temperature_C,
                                                         pressure_in_Pa=blanket_coolant_pressure_Pa),
                                                  Material(material_name=blanket_structural_material),
                                                  Material(material_name=blanket_multiplier_material,
                                                           packing_fraction=blanket_multiplier_packing_fraction),
                                                  Material(material_name=blanket_breeder_material,
                                                           enrichment=blanket_lithium6_enrichment_percent,
                                                           packing_fraction=blanket_breeder_packing_fraction,
                                                           temperature_in_C=blanket_breeder_temperature_C,
                                                           pressure_in_Pa=blanket_breeder_pressure_Pa)],
                                      fracs = [blanket_coolant_fraction, blanket_structural_fraction,
                                               blanket_multiplier_fraction, blanket_breeder_fraction],
                                      percent_type='vo', packing_fraction=1.0).openmc_material


    divertor_material = MultiMaterial(material_tag='divertor_mat',
                                      materials=[Material(material_name=divertor_coolant_material,
                                                          temperature_in_C=divertor_coolant_temperature_C,
                                                          pressure_in_Pa=divertor_coolant_pressure_Pa),
                                                 Material(material_name=divertor_structural_material)],
                                      fracs = [divertor_coolant_fraction, divertor_structural_fraction],
                                      percent_type='vo', packing_fraction=1.0).openmc_material

    inboard_tf_coils_material = MultiMaterial(material_tag='inboard_tf_coils_mat',
                                            materials=[Material(material_name=inboard_tf_coils_coolant_material,
                                                                temperature_in_C=inboard_tf_coils_coolant_temperature_C,
                                                                pressure_in_Pa=inboard_tf_coils_coolant_pressure_Pa),
                                                       Material(material_name=inboard_tf_coils_conductor_material),
                                                       Material(material_name=inboard_tf_coils_structure_material)],
                                            fracs = [inboard_tf_coils_coolant_fraction, inboard_tf_coils_conductor_fraction, inboard_tf_coils_structure_fraction],
                                            percent_type='vo', packing_fraction=1.0).openmc_material

    blanket_rear_wall_material = MultiMaterial(material_tag='blanket_rear_wall_mat',
                                            materials=[Material(material_name=blanket_rear_wall_coolant_material,
                                                                temperature_in_C=blanket_rear_wall_coolant_temperature_C,
                                                                pressure_in_Pa=blanket_rear_wall_coolant_pressure_Pa),
                                                       Material(material_name=blanket_rear_wall_structural_material)],
                                            fracs = [blanket_rear_wall_coolant_fraction, blanket_rear_wall_structural_fraction],
                                            percent_type='vo', packing_fraction=1.0).openmc_material


    mats = openmc.Materials([center_column_shield_material,
                            firstwall_material,
                            blanket_material,
                            divertor_material,
                            inboard_tf_coils_material,
                            blanket_rear_wall_material])


    # settings for the number of neutrons to simulate
    settings = openmc.Settings()
    settings.batches = 10
    settings.inactive = 0
    settings.particles = 100
    settings.run_mode = 'fixed source'
    settings.dagmc = True 

    # details of the birth locations and energy of the neutronis
    source = openmc.Source()
    source.space = openmc.stats.Point((my_reactor.major_radius, 0, 0))
    source.angle = openmc.stats.Isotropic()
    source.energy = openmc.stats.Discrete([14e6], [1])
    settings.source = source

    # details about what neutrons interactions to keep track of (called a tally)
    tallies = openmc.Tallies()
    material_filter = openmc.MaterialFilter(blanket_material)
    tbr_tally = openmc.Tally(name='TBR')
    tbr_tally.filters = [material_filter]
    tbr_tally.scores = ['(n,Xt)'] # where X is a wild card
    tallies.append(tbr_tally)

    # make the model from gemonetry, materials, settings and tallies
    model = openmc.model.Model(geom, mats, settings, tallies)

    # run the simulation
    output_filename = model.run()

    return output_filename

def read_simulation_results(output_filename):
    """
    Reads the output file from the neutronics simulation
    and prints the TBR tally result to screen
    """

    # open the results file
    sp = openmc.StatePoint(output_filename)

    # access the tally
    tbr_tally = sp.get_tally(name='TBR')
    df = tbr_tally.get_pandas_dataframe()
    tbr_tally_result = df['mean'].sum()

    # print result
    print('The tritium breeding ratio was found, TBR = ', tbr_tally_result)
    # return tbr_tally_result



if __name__ == "__main__":

    firstwall_radial_thickness = 3.
    firstwall_armour_material = 'tungsten'
    firstwall_coolant_material = 'H2O'
    firstwall_structural_material = 'eurofer'
    firstwall_armour_fraction = 0.1 # needs change to ref value
    firstwall_coolant_fraction = 0.2 # needs change to ref value
    firstwall_coolant_temperature_C = 500 # needs change to ref value
    firstwall_coolant_pressure_Pa = 1e6 # needs change to ref value
    firstwall_structural_fraction = 0.7 # needs change to ref value


    blanket_rear_wall_coolant_material = 'H2O'
    blanket_rear_wall_structural_material = 'eurofer'
    blanket_rear_wall_coolant_fraction = 0.2
    blanket_rear_wall_structural_fraction = 0.8
    blanket_rear_wall_coolant_temperature_C = 500
    blanket_rear_wall_coolant_pressure_Pa = 1e6


    blanket_lithium6_enrichment_percent = 60
    blanket_breeder_material = 'Li4SiO4'
    blanket_coolant_material = 'H2O'
    blanket_multiplier_material = 'Be12Ti'
    blanket_structural_material = 'eurofer'
    blanket_breeder_fraction = 0.15
    blanket_coolant_fraction = 0.05
    blanket_multiplier_fraction = 0.6
    blanket_structural_fraction = 0.2
    blanket_breeder_packing_fraction = 0.64
    blanket_multiplier_packing_fraction = 0.64
    blanket_coolant_temperature_C = 500
    blanket_coolant_pressure_Pa = 1e6
    blanket_breeder_temperature_C = 600
    blanket_breeder_pressure_Pa = 1e6

    divertor_coolant_fraction = 0.05
    divertor_structural_fraction = 0.95
    divertor_coolant_material = 'H2O'
    divertor_structural_material = 'eurofer'
    divertor_coolant_temperature_C = 500
    divertor_coolant_pressure_Pa = 1e6

    center_column_shield_coolant_fraction = 0.1
    center_column_shield_structural_fraction = 0.9
    center_column_shield_coolant_material = 'H2O'
    center_column_shield_structural_material = 'eurofer'
    center_column_shield_coolant_temperature_C = 500
    center_column_shield_coolant_pressure_Pa = 1e6

    inboard_tf_coils_conductor_fraction = 0.8
    inboard_tf_coils_coolant_fraction = 0.1
    inboard_tf_coils_structure_fraction = 0.1
    inboard_tf_coils_conductor_material = 'ReBCO'
    inboard_tf_coils_coolant_material = 'He'
    inboard_tf_coils_structure_material = 'eurofer'
    inboard_tf_coils_coolant_temperature_C = -200
    inboard_tf_coils_coolant_pressure_Pa = 1e6

    inner_bore_radial_thickness=50,
    inboard_tf_leg_radial_thickness = 200,
    center_column_shield_radial_thickness= 50,
    divertor_radial_thickness=50,
    inner_plasma_gap_radial_thickness = 50,
    plasma_radial_thickness = 100,
    outer_plasma_gap_radial_thickness = 50,
    firstwall_radial_thickness=5,
    blanket_radial_thickness=100,
    blanket_rear_wall_radial_thickness=10,
    elongation=2,
    triangularity=0.55,
    number_of_tf_coils=16,
    rotation_angle=360

    my_reactor = make_cad_model_with_paramak()
    convert_stp_files_to_neutronics_geometry()
    output_filename = make_other_aspects_of_neutronics_model(my_reactor)
    read_simulation_results(output_filename)
