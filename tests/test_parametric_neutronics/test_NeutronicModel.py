
import os
import unittest
from pathlib import Path

import neutronics_material_maker as nmm
import openmc
import paramak


class TestShape(unittest.TestCase):
    """Tests the NeutronicsModel with a Shape as the geometry input
    including neutronics simulations using"""

    def setUp(self):
        self.my_shape = paramak.CenterColumnShieldHyperbola(
            height=500,
            inner_radius=50,
            mid_radius=60,
            outer_radius=100,
            material_tag='center_column_shield_mat'
        )

        # makes the openmc neutron source at x,y,z 0, 0, 0 with isotropic
        # diections
        self.source = openmc.Source()
        self.source.space = openmc.stats.Point((0, 0, 0))
        self.source.angle = openmc.stats.Isotropic()

    def test_neutronics_component_simulation_with_openmc_mat(self):
        """Makes a neutronics model and simulates with a cell tally"""

        test_mat = openmc.Material()
        test_mat.add_element('Fe', 1.0)
        test_mat.set_density(units='g/cm3', density=4.2)

        # converts the geometry into a neutronics geometry
        my_model = paramak.NeutronicsModel(
            geometry=self.my_shape,
            source=self.source,
            materials={'center_column_shield_mat': test_mat},
            cell_tallies=['heating'],
            simulation_batches=2,
            simulation_particles_per_batch=2
        )

        # performs an openmc simulation on the model
        my_model.simulate(method='pymoab')

        # extracts the heat from the results dictionary
        heat = my_model.results['center_column_shield_mat_heating']['Watts']['result']

        assert heat > 0

    def test_neutronics_component_simulation_with_nmm(self):
        """Makes a neutronics model and simulates with a cell tally"""

        test_mat = nmm.Material('Be')

        # converts the geometry into a neutronics geometry
        my_model = paramak.NeutronicsModel(
            geometry=self.my_shape,
            source=self.source,
            materials={'center_column_shield_mat': test_mat},
            cell_tallies=['heating'],
            simulation_batches=2,
            simulation_particles_per_batch=2
        )

        # performs an openmc simulation on the model
        my_model.simulate(method='pymoab')

        # extracts the heat from the results dictionary
        heat = my_model.results['center_column_shield_mat_heating']['Watts']['result']

        assert heat > 0

    def test_incorrect_args(self):
        """Checks that an error is raised when the shape is
        defined as ."""

        def incorrect_faceting_tolerance():
            "Tries to set faceting_tolerance as a string"
            paramak.NeutronicsModel(
                geometry=self.my_shape,
                source=self.source,
                materials={'center_column_shield_mat': 'eurofer'},
                faceting_tolerance='coucou'
            )

        self.assertRaises(
            ValueError,
            incorrect_faceting_tolerance
        )

        def incorrect_faceting_tolerance_too_small():
            "Tries to set faceting_tolerance as a negative number"
            paramak.NeutronicsModel(
                geometry=self.my_shape,
                source=self.source,
                materials={'center_column_shield_mat': 'eurofer'},
                faceting_tolerance=-3
            )

        self.assertRaises(
            ValueError,
            incorrect_faceting_tolerance_too_small
        )

        def incorrect_merge_tolerance():
            "Tries to set merge_tolerance as a string"
            paramak.NeutronicsModel(
                geometry=self.my_shape,
                source=self.source,
                materials={'center_column_shield_mat': 'eurofer'},
                merge_tolerance='coucou'
            )

        self.assertRaises(
            ValueError,
            incorrect_merge_tolerance
        )

        def incorrect_merge_tolerance_too_small():
            "Tries to set merge_tolerance as a negative number"
            paramak.NeutronicsModel(
                geometry=self.my_shape,
                source=self.source,
                materials={'center_column_shield_mat': 'eurofer'},
                merge_tolerance=-3
            )

        self.assertRaises(
            ValueError,
            incorrect_merge_tolerance_too_small
        )

        def incorrect_cell_tallies():
            "Tries to set a cell tally that is not accepted"
            paramak.NeutronicsModel(
                geometry=self.my_shape,
                source=self.source,
                materials={'center_column_shield_mat': 'eurofer'},
                cell_tallies=['coucou'],
            )

        self.assertRaises(
            ValueError,
            incorrect_cell_tallies
        )

        def incorrect_mesh_tally_2D():
            "Tries to set a mesh_tally_2D that is not accepted"
            paramak.NeutronicsModel(
                geometry=self.my_shape,
                source=self.source,
                materials={'center_column_shield_mat': 'eurofer'},
                mesh_tally_2D=['coucou'],
            )

        self.assertRaises(
            ValueError,
            incorrect_mesh_tally_2D
        )

        def incorrect_materials():
            "Tries to set a material that is not accepted"
            paramak.NeutronicsModel(
                geometry=self.my_shape,
                source=self.source,
                materials='coucou',
            )

        self.assertRaises(
            ValueError,
            incorrect_materials
        )

        def incorrect_simulation_batches_to_small():
            """The simulation batch must be above 2"""
            paramak.NeutronicsModel(
                geometry=self.my_shape,
                source=self.source,
                materials={'center_column_shield_mat': 'eurofer'},
                simulation_batches=1
            )

        self.assertRaises(
            ValueError,
            incorrect_simulation_batches_to_small
        )

    def test_neutronics_component_cell_simulation(self):
        """Makes a neutronics model and simulates with a cell tally"""

        # converts the geometry into a neutronics geometry
        my_model = paramak.NeutronicsModel(
            geometry=self.my_shape,
            source=self.source,
            materials={'center_column_shield_mat': 'Be'},
            cell_tallies=['heating'],
            simulation_batches=2,
            simulation_particles_per_batch=2
        )

        # performs an openmc simulation on the model
        my_model.simulate(method='pymoab')

        # extracts the heat from the results dictionary
        heat = my_model.results['center_column_shield_mat_heating']['Watts']['result']

        assert heat > 0

    def test_neutronics_component_2d_mesh_simulation(self):
        """Makes a neutronics model and simulates with a 2D mesh tally"""

        os.system('rm *_on_2D_mesh_*.png')

        # converts the geometry into a neutronics geometry
        my_model = paramak.NeutronicsModel(
            geometry=self.my_shape,
            source=self.source,
            materials={'center_column_shield_mat': 'Be'},
            mesh_tally_2D=['heating'],
            simulation_batches=2,
            simulation_particles_per_batch=2
        )

        # performs an openmc simulation on the model
        my_model.simulate(method='pymoab')

        assert Path("heating_on_2D_mesh_xz.png").exists() is True
        assert Path("heating_on_2D_mesh_xy.png").exists() is True
        assert Path("heating_on_2D_mesh_yz.png").exists() is True


class TestNeutronicsBallReactor(unittest.TestCase):
    """Tests the NeutronicsModel with a BallReactor as the geometry input
    including neutronics simulations"""

    def setUp(self):
        # makes the 3d geometry
        self.my_reactor = paramak.BallReactor(
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
        self.blanket_material = nmm.MultiMaterial(
            fracs=[0.8, 0.2],
            materials=[
                nmm.Material('SiC'),
                nmm.Material('eurofer')
            ])

        self.source = openmc.Source()
        # sets the location of the source to x=0 y=0 z=0
        self.source.space = openmc.stats.Point((0, 0, 0))
        # sets the direction to isotropic
        self.source.angle = openmc.stats.Isotropic()
        # sets the energy distribution to 100% 14MeV neutrons
        self.source.energy = openmc.stats.Discrete([14e6], [1])

    def test_neutronics_model_attributes(self):
        """Makes a BallReactor neutronics model and simulates the TBR"""

        # makes the neutronics material
        neutronics_model = paramak.NeutronicsModel(
            geometry=self.my_reactor,
            source=openmc.Source(),
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

        assert neutronics_model.geometry == self.my_reactor

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

    def test_reactor_from_shapes_cell_tallies(self):
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

        neutronics_model = paramak.NeutronicsModel(
            geometry=test_reactor,
            source=self.source,
            materials={
                'mat1': 'copper',
                'blanket_mat': 'FLiNaK',  # used as O18 is not in nndc nuc data
            },
            cell_tallies=['TBR', 'heating', 'flux'],
            simulation_batches=2,
            simulation_particles_per_batch=10,
        )

        # starts the neutronics simulation using trelis
        neutronics_model.simulate(verbose=False, method='pymoab')

    def test_reactor_from_shapes_2d_mesh_tallies(self):
        """Makes a reactor from two shapes, then mades a neutronics model
        and tests the TBR simulation value"""

        os.system('rm *_on_2D_mesh_*.png')

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

        neutronics_model = paramak.NeutronicsModel(
            geometry=test_reactor,
            source=self.source,
            materials={
                'mat1': 'copper',
                'blanket_mat': 'FLiNaK',  # used as O18 is not in nndc nuc data
            },
            mesh_tally_2D=['tritium_production', 'heating', 'flux'],
            simulation_batches=2,
            simulation_particles_per_batch=10,
        )

        # starts the neutronics simulation using trelis
        neutronics_model.simulate(verbose=False, method='pymoab')
        neutronics_model.get_results()

        assert Path("tritium_production_on_2D_mesh_xz.png").exists() is True
        assert Path("tritium_production_on_2D_mesh_xy.png").exists() is True
        assert Path("tritium_production_on_2D_mesh_yz.png").exists() is True
        assert Path("heating_on_2D_mesh_xz.png").exists() is True
        assert Path("heating_on_2D_mesh_xy.png").exists() is True
        assert Path("heating_on_2D_mesh_yz.png").exists() is True
        assert Path("flux_on_2D_mesh_xz.png").exists() is True
        assert Path("flux_on_2D_mesh_xy.png").exists() is True
        assert Path("flux_on_2D_mesh_yz.png").exists() is True

    def test_incorrect_settings(self):
        """Creates NeutronicsModel objects and checks errors are
        raised correctly when arguments are incorrect."""

        def test_incorrect_method():
            """Makes a BallReactor neutronics model and simulates the TBR"""

            # makes the neutronics material
            neutronics_model = paramak.NeutronicsModel(
                geometry=self.my_reactor,
                source=self.source,
                materials={
                    'inboard_tf_coils_mat': 'copper',
                    'center_column_shield_mat': 'WC',
                    'divertor_mat': 'eurofer',
                    'firstwall_mat': 'eurofer',
                    'blanket_mat': 'FLiNaK',  # used as O18 is not in nndc nuc data
                    'blanket_rear_wall_mat': 'eurofer'},
                cell_tallies=['TBR', 'flux', 'heating'],
                simulation_batches=42,
                simulation_particles_per_batch=84,
            )

            neutronics_model.create_neutronics_geometry(method='incorrect')

        self.assertRaises(ValueError, test_incorrect_method)


if __name__ == "__main__":
    unittest.main()
