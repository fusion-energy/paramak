import unittest
import pytest
from paramak.parametric_reactors.negative_triangularity_reactor import (
    NegativeTriangularityReactor,
)


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
            triangularity=0.6,
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
            pf_coil_center_points=[
                (350, 850),
                (1350, 650),
                (1400, 0),
                (1350, -650),
                (350, -850),
            ],
            pf_coil_casing_thickness=[5, 5, 5, 5, 5],
            low_aspect=True,
        )
        self.test_reactor.create_solid()

    def test_input_variable_names(self):
        """tests for the number of inputs variables"""
        assert len(self.test_reactor.input_variable_names) == 26

    def test_bore_radius_small(self):
        """Creates the reactor with 0cm inner bore checks if the right
        amount of components are adding to the object."""
        self.test_reactor.inner_bore_radius = 0
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_bore_radius_large(self):
        """Creates the reactor with 500cm inner bore checks if the
        right amount of components are adding to the object."""
        self.test_reactor.inner_bore_radius = 500
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_bore_radius_type(self):
        """Checks for bore radius input type"""
        with pytest.raises(TypeError):
            self.test_reactor.inner_bore_radius = "asd"
        assert self.test_reactor.solid is not None

    def test_inner_tf_leg_small(self):
        """Creates the reactor with small thickness inner tf coil"""
        self.test_reactor.inner_tf_coil_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_inner_tf_leg_large(self):
        """Creates the reactor with large thickness inner tf coil"""
        self.test_reactor.inner_tf_coil_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_inner_tf_leg(self):
        """Checks inner tf coil input type"""
        with pytest.raises(TypeError):
            self.test_reactor.inner_tf_coil_thickness = "asd"
        assert self.test_reactor.solid is not None

    def test_vacuum_vessel_thickness_small(self):
        """Creates the reactor with small thickness vacuum vessel"""
        self.test_reactor.vacuum_vessel_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_vacuum_vessel_thickness_large(self):
        """Creates the reactor with large thickness vacuum vessel"""
        self.test_reactor.vacuum_vessel_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_vacuum_vessel_thickness(self):
        """Checks vacuum vessel input type"""
        with pytest.raises(TypeError):
            self.test_reactor.vacuum_vessel_thickness = "asd"
        assert self.test_reactor.solid is not None

    def test_central_shield_thickness_small(self):
        """Creates the reactor with small thickness inner shield"""
        self.test_reactor.central_shield_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_central_shield_thickness_large(self):
        """Creates the reactor with large thickness inner shield"""
        self.test_reactor.central_shield_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_central_shield_thickness(self):
        """Checks inner shield input type"""
        with pytest.raises(TypeError):
            self.test_reactor.central_shield_thickness = "asd"
        assert self.test_reactor.solid is not None

    def test_wall_to_plasma_gap_small(self):
        """Creates the reactor with small plasma gap"""
        self.test_reactor.wall_to_plasma_gap = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_wall_to_plasma_gap_large(self):
        """Creates the reactor with large plasma gap"""
        self.test_reactor.wall_to_plasma_gap = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_wall_to_plasma_gap(self):
        """Checks plasma gap input type"""
        with pytest.raises(TypeError):
            self.test_reactor.wall_to_plasma_gap = "asd"
        assert self.test_reactor.solid is not None

    def test_plasma_radial_thickness_small(self):
        """Creates the reactor with small radial thickness plasma"""
        self.test_reactor.plasma_radial_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_plasma_radial_thickness_large(self):
        """Creates the reactor with large radial thickness plasma"""
        self.test_reactor.plasma_radial_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_plasma_radial_thickness(self):
        """Checks input type of radial plasma thickness"""
        with pytest.raises(TypeError):
            self.test_reactor.plasma_radial_thickness = "asd"
        assert self.test_reactor.solid is not None

    def test_elongation_small(self):
        """Creates the reactor with small elongation"""
        self.test_reactor.elongation = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_elongation_large(self):
        """Creates the reactor with large elongation"""
        self.test_reactor.elongation = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_elongation(self):
        """Checks input type of elongation"""
        with pytest.raises(TypeError):
            self.test_reactor.elongation = "asd"
        assert self.test_reactor.solid is not None

    def test_triangularity_small(self):
        """Creates the reactor with small triangularity"""
        with pytest.raises(ValueError):
            self.test_reactor.triangularity = -5
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_triangularity_large(self):
        """Creates the reactor with large triangularity"""
        with pytest.raises(ValueError):
            self.test_reactor.triangularity = 5
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_triangularity(self):
        """Checks input type of triangularity"""
        with pytest.raises(TypeError):
            self.test_reactor.triangularity = "asd"
        assert self.test_reactor.solid is not None

    def test_inner_wall_thickness_small(self):
        """Creates the reactor with small inner wall thickness"""
        self.test_reactor.inner_wall_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_inner_wall_thickness_large(self):
        """Creates the reactor with large inner wall thickness"""
        self.test_reactor.inner_wall_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_inner_wall_thickness(self):
        """Checks input type of inner wall thickness"""
        with pytest.raises(TypeError):
            self.test_reactor.inner_wall_thickness = "asd"
        assert self.test_reactor.solid is not None

    def test_blanket_thickness_small(self):
        """Creates the reactor with small blanket thickness"""
        self.test_reactor.blanket_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_blanket_thickness_large(self):
        """Creates the reactor with large blanket thickness"""
        self.test_reactor.blanket_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_blanket_thickness(self):
        """Checks input type of blanket thickness"""
        with pytest.raises(TypeError):
            self.test_reactor.blanket_thickness = "asd"
        assert self.test_reactor.solid is not None

    def test_rear_wall_thickness_small(self):
        """Creates the reactor with small rear wall thickness"""
        self.test_reactor.rear_wall_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_rear_wall_thickness_large(self):
        """Creates the reactor with large rear wall thickness"""
        self.test_reactor.rear_wall_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_rear_wall_thickness(self):
        """Checks input type of rear wall thickness"""
        with pytest.raises(TypeError):
            self.test_reactor.rear_wall_thickness = "asd"
        assert self.test_reactor.solid is not None

    def test_divertor_radial_thickness_small(self):
        """Creates the reactor with small divertor radial thickness"""
        self.test_reactor.divertor_radial_thickness = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_divertor_radial_thickness_large(self):
        """Creates the reactor with large divertor radial thickness"""
        self.test_reactor.divertor_radial_thickness = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_divertor_radial_thickness(self):
        """Checks input type of divertor radial thickness"""
        with pytest.raises(TypeError):
            self.test_reactor.divertor_radial_thickness = "asd"
        assert self.test_reactor.solid is not None

    def test_divertor_height_small(self):
        """Creates the reactor with small divertor height"""
        self.test_reactor.divertor_height = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_divertor_height_large(self):
        """Creates the reactor with large divertor height"""
        self.test_reactor.divertor_height = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_divertor_height(self):
        """Checks input type of divertor height"""
        with pytest.raises(TypeError):
            self.test_reactor.divertor_height = "asd"
        assert self.test_reactor.solid is not None

    def test_tf_width_small(self):
        """Creates the reactor with small toroidal field coil width"""
        self.test_reactor.tf_width = 1
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_tf_width_large(self):
        """Creates the reactor with large toroidal field coil width"""
        self.test_reactor.tf_width = 1000
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_tf_width(self):
        """Checks input type of toroidal field coil width"""
        with pytest.raises(TypeError):
            self.test_reactor.tf_width = "asd"
        assert self.test_reactor.solid is not None

    def test_port_side_lengths_list(self):
        """Checks port side lengths is a list"""
        self.test_reactor.port_side_lengths = [1, 1, 1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_port_side_lengths_val_small(self):
        """Creates the reactor with small port side lengths"""
        self.test_reactor.port_side_lengths = [5, 5, 5]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_port_side_lengths_val_large(self):
        """Creates the reactor with large port side lengths"""
        self.test_reactor.port_side_lengths = [50, 50, 50]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_port_side_lengths_val(self):
        """Checks input type of port side lengths"""
        with pytest.raises(TypeError):
            self.test_reactor.port_side_lengths = "asd"
        assert self.test_reactor.solid is not None

    def test_port_thickness_list(self):
        """Checks if list is the same length as the other port related lists"""
        self.test_reactor.port_heights = [1, 1, 1, 1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_port_thickness_val_small(self):
        """Creates the reactor with small port thickness"""
        self.test_reactor.port_heights = [5, 5, 5]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_port_thickness_val_large(self):
        """Creates the reactor with large port thickness"""
        self.test_reactor.port_heights = [50, 50, 50]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_port_thickness_val(self):
        """Checks input type of port thickness"""
        with pytest.raises(TypeError):
            self.test_reactor.port_heights = "asd"
        assert self.test_reactor.solid is not None

    def test_ports_angles_list(self):
        """Checks if list is the same length as the other port related lists"""
        self.test_reactor.port_angles = [1, 1, 1, 1, 1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_ports_angles_val_small(self):
        """Creates the reactor with small port angles"""
        self.test_reactor.port_angles = [5, 5, 5]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_ports_angles_val_large(self):
        """Creates the reactor with large port angles"""
        self.test_reactor.port_angles = [250, 250, 250]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_ports_angles_val(self):
        """Checks input type of port angles"""
        with pytest.raises(TypeError):
            self.test_reactor.port_angles = "asd"
        assert self.test_reactor.solid is not None

    def test_port_z_pos_list(self):
        """Checks if the input lists for port Z-positions are the same length"""
        self.test_reactor.port_z_pos = [1, 1, 1, 1, 1, 1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_port_z_pos_val_small(self):
        """Creates the reactor with positive Z-position of ports"""
        self.test_reactor.port_z_pos = [10, 150, 200]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_port_z_pos_val_large(self):
        """Creates the reactor with negative Z-position of ports"""
        self.test_reactor.port_z_pos = [-10, -150, -200]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_port_z_pos_val(self):
        """Checks input type of Z-position of ports"""
        with pytest.raises(TypeError):
            self.test_reactor.port_z_pos = "asd"
        assert self.test_reactor.solid is not None

    def test_pf_coil_heights_list(self):
        """Checks if the input lists for poloidal field coil height are the same length"""
        self.test_reactor.pf_coil_heights = [1, 1, 1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_pf_coil_heights_val_small(self):
        """Creates the reactor with small poloidal field coil heights"""
        self.test_reactor.pf_coil_heights = [5, 5, 5]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_pf_coil_heights_val_large(self):
        """Creates the reactor with large poloidal field coil heights"""
        self.test_reactor.pf_coil_heights = [50, 50, 50]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_pf_coil_heights_val(self):
        """Checks input type of poloidal field coil heights"""
        with pytest.raises(TypeError):
            self.test_reactor.pf_coil_heights = "asd"
        assert self.test_reactor.solid is not None

    def test_pf_coil_widths_list(self):
        """Checks if the input lists for poloidal field coil widths are the same length"""
        self.test_reactor.pf_coil_widths = [1, 1, 1, 1, 1, 1, 1, 1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_pf_coil_widths_val_small(self):
        """Creates the reactor with small poloidal field coil widths"""
        self.test_reactor.pf_coil_widths = [5, 5, 5]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_pf_coil_widths_val_large(self):
        """Creates the reactor with large poloidal field coil widths"""
        self.test_reactor.pf_coil_widths = [50, 50, 50]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_pf_coil_widths_val(self):
        """Checks input type of poloidal field coil widths"""
        with pytest.raises(TypeError):
            self.test_reactor.pf_coil_widths = "asd"
        assert self.test_reactor.solid is not None

    def test_pf_coil_center_points_list(self):
        """Checks if the input lists for poloidal field coil center points are the same length"""
        self.test_reactor.pf_coil_center_points = [
            (10, 10),
            (10, 10),
            (10, 10),
            (10, 10),
        ]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_pf_coil_center_points_val_small(self):
        """Creates the reactor with small poloidal field coil center points"""
        self.test_reactor.pf_coil_center_points = [(5, 5), (5, 5), (5, 5)]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_pf_coil_center_points_val_large(self):
        """Creates the reactor with large poloidal field coil center points"""
        self.test_reactor.pf_coil_center_points = [(500, 500), (500, 500), (500, 500)]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_pf_coil_center_points_val(self):
        """Checks input type of poloidal field coil center points"""
        with pytest.raises(TypeError):
            self.test_reactor.pf_coil_center_points = "asd"
        assert self.test_reactor.solid is not None

    def test_pf_casing_thickness_list(self):
        """Checks if the input lists for poloidal field coils are the same length"""
        self.test_reactor.pf_coil_casing_thickness = [1, 1, 1]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_pf_casing_thickness_val_small(self):
        """Creates the reactor with small poloidal field coil casing thickness"""
        self.test_reactor.pf_coil_casing_thickness = [5, 5, 5]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_pf_casing_thickness_val_large(self):
        """Creates the reactor with large poloidal field coil casing thickness"""
        self.test_reactor.pf_coil_casing_thickness = [50, 50, 50]
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 12

    def test_pf_casing_thickness_val(self):
        """Checks input type of poloidal field coil casing thickness"""
        with pytest.raises(TypeError):
            self.test_reactor.pf_coil_casing_thickness = "asd"
        assert self.test_reactor.solid is not None
