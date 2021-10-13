
import pytest
import unittest
from paramak.parametric_reactors.negative_triangularity_reactor import NegativeTriangularityReactor

class TestNegativeTriangularityReactor(unittest.TestCase):

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

            port_side_lengths=[200,200,400],
            port_heights=[200,100,400],
            port_angles=[75, 170, 0],
            port_z_pos=[500,-500, 0],

            pf_coil_heights=[75,75,150,75,75],
            pf_coil_widths=[75,75,150,75,75],
            pf_coil_center_points=[(350,850), (1350,650), (1400,0), (1350,-650), (350,-850)],
            pf_coil_casing_thickness=[5,5,5,5,5],

            show_plasma=False,
            low_aspect=True,
        )
        self.test_reactor.create_solid()
    
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

    #def test_narrow_divertor(self):
    #    """Creates a negative triangularity reactor with minimal divertor size 
    #    that is overwritten by the automated algorithm to size divertor to at 
    #    least the size that lines up with the blanket's outer wall."""
    #    self.test_reactor.divertor


#obj = TestNegativeTriangularityReactor()
#obj.setUp()
#
#obj.test_bore_radius()
