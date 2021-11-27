import unittest
import pytest
from paramak.parametric_reactors.negative_triangularity_reactor import NegativeTriangularityReactor


class TestNegativeTriangularityReactor(unittest.TestCase):
    """
    New Test class for the negative triangularity reactor.
    """
    def setUp(self):
        self.test_reactor = NegativeTriangularityReactor(
            inner_bore_radius=10,
            inner_tf_coil_thickness=100,
            vacuum_vessel_thickness=50,
            central_shield_thickness=20,
            wall_to_plasma_gap=50,
            plasma_radial_thickness=650,
            elongation=2,
            triangularity=.6,
            inner_wall_thickness=20,
            blanket_thickness=105,
            rear_wall_thickness=20,
            divertor_radial_thickness=300,
            divertor_height_full=350,
            rotation_angle=180,
            tf_width=75,
            number_of_coils=12,

            port_side_lengths=[200, 200, 400],
            port_heights=[200, 100, 400],
            port_angles=[75, 170, 0],
            port_z_pos=[500, -500, 0],

            pf_coil_heights=[75, 75, 150, 75, 75],
            pf_coil_widths=[75, 75, 150, 75, 75],
            pf_coil_center_points=[(350, 850), (1350, 650), (1400, 0), (1350, -650), (350, -850)],
            pf_coil_casing_thickness=[5, 5, 5, 5, 5],

            show_plasma=False,
            low_aspect=True,
        )
        self.test_reactor.create_solid()

    def test_input_variable_names(self):
        """tests for the number of inputs variables"""

        assert len(self.test_reactor.input_variable_names) == 27
        #assert len(self.test_reactor.input_variable_names) == 27

    def test_bore_radius_small(self):
        """Creates the reactor with 0cm inner bore checks if the right
        amount of components are adding to the object."""

        self.test_reactor.inner_bore_radius = 0
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_bore_radius_large(self):
        """Creates the reactor with 500cm inner bore checks if the
        right amount of components are adding to the object."""
        self.test_reactor.inner_bore_radius = 500
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_bore_radius_type(self):
        """Checks if reacor exits with set up error."""
        with pytest.raises(TypeError):
            self.test_reactor.inner_bore_radius = 'asd'
        assert self.test_reactor.solid is not None

    def test_inner_tf_leg_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor.inner_tf_coil_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_inner_tf_leg_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor.inner_tf_coil_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_inner_tf_leg(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor.inner_tf_coil_thickness = 'asd'
        assert self.test_reactor.solid is not None

    def test_vacuum_vessel_thickness_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._vacuum_vessel_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_vacuum_vessel_thickness_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._vacuum_vessel_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_vacuum_vessel_thickness(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._vacuum_vessel_thickness = 'asd'
        assert self.test_reactor.solid is not None

    def test_central_shield_thickness_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._central_shield_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_central_shield_thickness_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._central_shield_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_central_shield_thickness(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._central_shield_thickness = 'asd'
        assert self.test_reactor.solid is not None

    def test_wall_to_plasma_gap_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._wall_to_plasma_gap = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_wall_to_plasma_gap_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._wall_to_plasma_gap = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_wall_to_plasma_gap(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._wall_to_plasma_gap = 'asd'
        assert self.test_reactor.solid is not None

    def test_plasma_radial_thickness_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._plasma_radial_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_plasma_radial_thickness_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._plasma_radial_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_plasma_radial_thickness(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._plasma_radial_thickness = 'asd'
        assert self.test_reactor.solid is not None

    def test_plasma_radial_thickness_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._plasma_radial_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_plasma_radial_thickness_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._plasma_radial_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_plasma_radial_thickness(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._plasma_radial_thickness = 'asd'
        assert self.test_reactor.solid is not None


    def test_elongation_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._elongation = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_elongation_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._elongation = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_elongation(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._elongation = 'asd'
        assert self.test_reactor.solid is not None


    def test_triangularity_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._triangularity = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_triangularity_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._triangularity = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_triangularity(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._triangularity = 'asd'
        assert self.test_reactor.solid is not None

    def test_inner_wall_thickness_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._inner_wall_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_inner_wall_thickness_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._inner_wall_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_inner_wall_thickness(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._inner_wall_thickness = 'asd'
        assert self.test_reactor.solid is not None


    def test_blanket_thickness_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._blanket_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_blanket_thickness_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._blanket_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_blanket_thickness(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._blanket_thickness = 'asd'
        assert self.test_reactor.solid is not None

    def test_rear_wall_thickness_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._rear_wall_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_rear_wall_thickness_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._rear_wall_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_rear_wall_thickness(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._rear_wall_thickness = 'asd'
        assert self.test_reactor.solid is not None

    def test_divertor_radial_thickness_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._divertor_radial_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_divertor_radial_thickness_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._divertor_radial_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_divertor_radial_thickness(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._divertor_radial_thickness = 'asd'
        assert self.test_reactor.solid is not None

    def test_divertor_height_full_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._divertor_height_full = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_divertor_height_full_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._divertor_height_full = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_divertor_height_full(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._divertor_height_full = 'asd'
        assert self.test_reactor.solid is not None

    def test_tf_width_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._tf_width = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_tf_width_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._tf_width = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_tf_width(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._tf_width = 'asd'
        assert self.test_reactor.solid is not None

    def test_port_side_lengths_list(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._port_side_lengths = [1,1,1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_port_side_lengths_val_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._port_side_lengths = [5,5,5]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_port_side_lengths_val_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._port_side_lengths = [50,50,50]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_port_side_lengths_val(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._port_side_lengths = 'asd'
        assert self.test_reactor.solid is not None

    def test_port_thickness_list(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._port_thickness = [1,1,1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_port_thickness_val_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._port_thickness = [5,5,5]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_port_thickness_val_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._port_thickness = [50,50,50]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_port_thickness_val(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._port_thickness = 'asd'
        assert self.test_reactor.solid is not None

    def test_ports_angles_list(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._ports_angles = [1,1,1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_ports_angles_val_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._ports_angles = [5,5,5]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_ports_angles_val_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._ports_angles = [50,50,50]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_ports_angles_val(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._ports_angles = 'asd'
        assert self.test_reactor.solid is not None

    def test_port_z_pos_list(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._port_z_pos = [1,1,1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_port_z_pos_val_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._port_z_pos = [5,5,5]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_port_z_pos_val_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._port_z_pos = [50,50,50]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_port_z_pos_val(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._port_z_pos = 'asd'
        assert self.test_reactor.solid is not None

    def test_pf_coil_heights_list(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._pf_coil_heights = [1,1,1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_pf_coil_heights_val_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._pf_coil_heights = [5,5,5]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_pf_coil_heights_val_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._pf_coil_heights = [50,50,50]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_pf_coil_heights_val(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._pf_coil_heights = 'asd'
        assert self.test_reactor.solid is not None

    def test_pf_coil_widths_list(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._pf_coil_widths = [1,1,1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_pf_coil_widths_val_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._pf_coil_widths = [5,5,5]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_pf_coil_widths_val_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._pf_coil_widths = [50,50,50]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_pf_coil_widths_val(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._pf_coil_widths = 'asd'
        assert self.test_reactor.solid is not None

    def test_pf_coil_center_points_list(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._pf_coil_center_points = [(10,10),(10,10),(10,10)]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_pf_coil_center_points_val_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._pf_coil_center_points = [(5,5),(5,5),(5,5)]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_pf_coil_center_points_val_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._pf_coil_center_points = [(50,50),(50,50),(50,50)]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_pf_coil_center_points_val(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._pf_coil_center_points = 'asd'
        assert self.test_reactor.solid is not None

    def test_pf_casing_thickness_list(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._pf_casing_thickness = [1,1,1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_pf_casing_thickness_val_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._pf_casing_thickness = [5,5,5]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_pf_casing_thickness_val_large(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor._pf_casing_thickness = [50,50,50]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 11

    def test_pf_casing_thickness_val(self):
        """Creates the reactor with small thickness inner tf coil"""
        with pytest.raises(TypeError):
            self.test_reactor._pf_casing_thickness = 'asd'
        assert self.test_reactor.solid is not None



    ###########################################################################



















    # def test_narrow_divertor(self):
    #    """Creates a negative triangularity reactor with minimal divertor size
    #    that is overwritten by the automated algorithm to size divertor to at
    #    least the size that lines up with the blanket's outer wall."""
    #    self.test_reactor.divertor
