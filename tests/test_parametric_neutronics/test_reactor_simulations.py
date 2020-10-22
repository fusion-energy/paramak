
import unittest
import os
import neutronics_material_maker as nmm
import paramak
import pytest


class test_neutronics_BallReactor(unittest.TestCase):

    def test_tbr_simulation(self):
        """Makes a BallReactor neutronics model and simulates the TBR"""

#     #TODO the x 10e3 is needed for now as the units are wrong

        # makes the 3d geometry
        my_reactor = paramak.BallReactor(
            inner_bore_radial_thickness=1e2,
            inboard_tf_leg_radial_thickness=30e2,
            center_column_shield_radial_thickness=60e2,
            divertor_radial_thickness=50e2,
            inner_plasma_gap_radial_thickness=30e2,
            plasma_radial_thickness=300e2,
            outer_plasma_gap_radial_thickness=30e2,
            firstwall_radial_thickness=3e2,
            blanket_radial_thickness=100e2,
            blanket_rear_wall_radial_thickness=3e2,
            elongation=2.75,
            triangularity=0.5,
            rotation_angle=360,
        )

        # makes a homogenised material for the blanket from lithium lead and
        # eurofer
        blanket_material = nmm.MultiMaterial(
            fracs=[0.8, 0.2],
            materials=[
                nmm.Material(
                    'Pb842Li158',
                    enrichment=90,
                    temperature_in_K=500),
                nmm.Material('eurofer')
            ])

        # makes the neutronics material
        neutronics_model = paramak.NeutronicsModelFromReactor(
            reactor=my_reactor,
            materials={
                'inboard_tf_coils_mat': 'copper',
                'center_column_shield_mat': 'WC',
                'divertor_mat': 'eurofer',
                'firstwall_mat': 'eurofer',
                'blanket_mat': blanket_material,  # use of homogenised material
                'blanket_rear_wall_mat': 'eurofer'},
            outputs=['TBR'],
            simulation_batches=5,
            simulation_particles_per_batch=1e3,
        )

        # starts the neutronics simulation
        neutronics_model.simulate()

        assert neutronics_model.results['TBR'] == pytest.approx(1.0, rel=0.01)
