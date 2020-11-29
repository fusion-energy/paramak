
import unittest

import neutronics_material_maker as nmm
import paramak
import pytest


class test_neutronics_BallReactor(unittest.TestCase):

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
        rotation_angle=360,
    )

    # makes a homogenised material for the blanket from lithium lead and
    # eurofer
    blanket_material = nmm.MultiMaterial(
        fracs=[0.8, 0.2],
        materials=[
            nmm.Material('SiC'),
            nmm.Material('eurofer')
        ])

    def test_neutronics_model_attributes(self):
        """Makes a BallReactor neutronics model and simulates the TBR"""

        # makes the neutronics material
        neutronics_model = paramak.NeutronicsModelFromReactor(
            reactor=self.my_reactor,
            materials={
                'inboard_tf_coils_mat': 'copper',
                'center_column_shield_mat': 'WC',
                'divertor_mat': 'eurofer',
                'firstwall_mat': 'eurofer',
                'blanket_mat': self.blanket_material,  # use of homogenised material
                'blanket_rear_wall_mat': 'eurofer'},
            cell_tallies=['TBR', 'flux', 'heating'],
            simulation_batches=42,
            simulation_particles_per_batch=84,
        )

        assert neutronics_model.reactor == self.my_reactor

        assert neutronics_model.materials == {
            'inboard_tf_coils_mat': 'copper',
            'center_column_shield_mat': 'WC',
            'divertor_mat': 'eurofer',
            'firstwall_mat': 'eurofer',
            'blanket_mat': self.blanket_material,
            'blanket_rear_wall_mat': 'eurofer'}

        assert neutronics_model.cell_tallies == ['TBR', 'flux', 'heating']

        assert neutronics_model.simulation_batches == 42
        assert isinstance(neutronics_model.simulation_batches, int)

        assert neutronics_model.simulation_particles_per_batch == 84
        assert isinstance(neutronics_model.simulation_particles_per_batch, int)

    def test_reactor_from_shapes(self):
        """Makes a reactor from two shapes, then mades a neutronics model
        and tests the TBR simulation value"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat1',
        )
        test_shape2 = paramak.RotateSplineShape(
            points=[(100, 100), (100, -100), (200, -100), (200, 100)],
            material_tag='blanket_mat',
            rotation_angle=180
        )

        test_reactor = paramak.Reactor([test_shape, test_shape2])
        test_reactor.rotation_angle = 360
        test_reactor.minor_radius = 5
        test_reactor.major_radius = 12
        test_reactor.elongation = 2
        test_reactor.triangularity = 0.55

        neutronics_model = paramak.NeutronicsModelFromReactor(
            reactor=test_reactor,
            materials={
                'mat1': 'copper',
                'blanket_mat': 'Li4SiO4',
            },
            cell_tallies=['TBR', 'heating', 'flux'],
            simulation_batches=5,
            simulation_particles_per_batch=1e3,
        )

        # starts the neutronics simulation using trelis
        neutronics_model.simulate(method='pymoab')

        assert pytest.approx(
            neutronics_model.results['TBR']['result'],
            abs=0.1) == 0.7
        assert pytest.approx(
            neutronics_model.results['blanket_mat_heating']['MeV per source particle']['result'],
            abs=1) == 12
        assert pytest.approx(
            neutronics_model.results['blanket_mat_flux']['Flux per source particle']['result'],
            abs=10) == 169

    # def test_tbr_simulation(self):

    # def test_tbr_simulation(self):
    #     """Makes a BallReactor neutronics model and simulates the TBR"""

        # makes the neutronics material
        # neutronics_model = paramak.NeutronicsModelFromReactor(
        #     reactor=my_reactor,
        #     materials={
        #         'inboard_tf_coils_mat': 'copper',
        #         'center_column_shield_mat': 'WC',
        #         'divertor_mat': 'eurofer',
        #         'firstwall_mat': 'eurofer',
        #         'blanket_mat': blanket_material,  # use of homogenised material
        #         'blanket_rear_wall_mat': 'eurofer'},
        #     cell_tallies=['TBR'],
        #     simulation_batches=5,
        #     simulation_particles_per_batch=1e3,
        # )

        # starts the neutronics simulation using trelis
        # neutronics_model.simulate(method='trelis')

        # assert neutronics_model.results['TBR']['result'] == pytest.approx(
        #     1.168, rel=0.2)


if __name__ == "__main__":
    unittest.main()
