
import os
import time
import unittest
import warnings
from pathlib import Path

import paramak


class TestBallReactor(unittest.TestCase):

    def setUp(self):
        self.test_reactor = paramak.BallReactor(
            inner_bore_radial_thickness=50,
            inboard_tf_leg_radial_thickness=200,
            center_column_shield_radial_thickness=50,
            divertor_radial_thickness=100,
            inner_plasma_gap_radial_thickness=150,
            plasma_radial_thickness=100,
            outer_plasma_gap_radial_thickness=50,
            firstwall_radial_thickness=50,
            blanket_radial_thickness=100,
            blanket_rear_wall_radial_thickness=10,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            rotation_angle=180,
        )

    def test_creation_with_narrow_divertor(self):
        """Creates a BallReactor with a narrow divertor and checks that the correct
        number of components are created."""

        self.test_reactor.divertor_radial_thickness = 50

        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 7

    def test_creation_with_narrow_divertor(self):
        """Creates a BallReactor with a wide divertor and checks that the correct
        number of components are created."""

        self.test_reactor.divertor_radial_thickness = 172.5

        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 7

    def test_svg_creation(self):
        """Creates a BallReactor and checks that an svg image of the reactor can be
        exported using the export_svg method."""

        os.system("rm test_ballreactor_image.svg")
        self.test_reactor.export_svg("filename.svg")
        assert Path("filename.svg").exists() is True
        os.system("rm filename.svg")

    def test_with_pf_coils(self):
        """Checks that a BallReactor with optional pf coils can be created and that
        the correct number of components are created."""

        self.test_reactor.pf_coil_radial_thicknesses = [50, 50, 50, 50]
        self.test_reactor.pf_coil_vertical_thicknesses = [50, 50, 50, 50]
        self.test_reactor.pf_coil_to_rear_blanket_radial_gap = 50
        self.test_reactor.pf_coil_case_thickness = 10

        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 9

    def test_pf_coil_thicknesses_error(self):
        """Checks that an error is raised when invalid pf_coil_radial_thicknesses and
        pf_coil_vertical_thicknesses are specified."""

        def invalid_pf_coil_radial_thicknesses():
            self.test_reactor.pf_coil_radial_thicknesses = 2
        self.assertRaises(ValueError, invalid_pf_coil_radial_thicknesses)

        def invalid_pf_coil_vertical_thicknesses():
            self.test_reactor.pf_coil_vertical_thicknesses = 2
        self.assertRaises(ValueError, invalid_pf_coil_vertical_thicknesses)

    def test_with_pf_and_tf_coils(self):
        """Checks that a BallReactor with optional pf and tf coils can be created and
        that the correct number of components are created."""

        self.test_reactor.pf_coil_radial_thicknesses = [50, 50, 50, 50]
        self.test_reactor.pf_coil_vertical_thicknesses = [50, 50, 50, 50]
        self.test_reactor.pf_coil_to_rear_blanket_radial_gap = 50
        self.test_reactor.pf_coil_to_tf_coil_radial_gap = 50
        self.test_reactor.pf_coil_case_thickness = 10
        self.test_reactor.outboard_tf_coil_radial_thickness = 50
        self.test_reactor.outboard_tf_coil_poloidal_thickness = 50

        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 10

    def test_with_pf_and_tf_coils_export_physical_groups(self):
        """Creates a BallReactor and checks that the export_physical_groups method
        works correctly."""

        self.test_reactor.export_physical_groups()

        # insert assertion

    def test_rotation_angle_warning(self):
        """Creates a BallReactor with rotation_angle = 360 and checks that the correct
        warning message is printed."""

        def warning_trigger():
            self.test_reactor.rotation_angle = 360
            self.test_reactor._rotation_angle_check()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warning_trigger()
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "360 degree rotation may result in a Standard_ConstructionError or AttributeError" in str(
                w[-1].message)

    def test_ball_reactor_hash_value(self):
        """Creates a ball reactor and checks that all shapes in the reactor are created
        when .shapes_and_components is first called. Checks that when .shapes_and_components
        is called again with no changes to the reactor, the shapes in the reactor are not
        reconstructed and the previously constructed shapes are returned. Checks that when
        .shapes_and_components is called again with changes to the reactor, the shapes
        in the reactor are reconstructed and these new shapes are returned. Checks that
    the reactor_hash_value is only updated when the reactor is
    reconstructed."""

        self.test_reactor.pf_coil_radial_thicknesses = [50, 50, 50, 50]
        self.test_reactor.pf_coil_vertical_thicknesses = [50, 50, 50, 50]
        self.test_reactor.pf_coil_to_rear_blanket_radial_gap = 50
        self.test_reactor.pf_coil_to_tf_coil_radial_gap = 50
        self.test_reactor.pf_coil_case_thickness = 10
        self.test_reactor.outboard_tf_coil_radial_thickness = 100
        self.test_reactor.outboard_tf_coil_poloidal_thickness = 50

        assert self.test_reactor.reactor_hash_value is None
        for key in [
            "_plasma",
            "_inboard_tf_coils",
            "_center_column_shield",
            "_divertor",
            "_firstwall",
            "_blanket",
            "_blanket_rear_wall",
            "_pf_coil",
            "_pf_coils_casing",
            "_tf_coil"
        ]:
            assert key not in self.test_reactor.__dict__.keys()
        assert self.test_reactor.shapes_and_components is not None

        for key in [
            "_plasma",
            "_inboard_tf_coils",
            "_center_column_shield",
            "_divertor",
            "_firstwall",
            "_blanket",
            "_blanket_rear_wall",
            "_pf_coil",
            "_pf_coils_casing",
            "_tf_coil"
        ]:
            assert key in self.test_reactor.__dict__.keys()
        assert len(self.test_reactor.shapes_and_components) == 10
        assert self.test_reactor.reactor_hash_value is not None
        initial_hash_value = self.test_reactor.reactor_hash_value
        self.test_reactor.rotation_angle = 270
        assert self.test_reactor.reactor_hash_value == initial_hash_value
        assert self.test_reactor.shapes_and_components is not None
        assert self.test_reactor.reactor_hash_value != initial_hash_value

    def test_hash_value_time_saving(self):
        """Checks that use of conditional reactor reconstruction via the hash value
        gives the expected time saving."""

        self.test_reactor.pf_coil_radial_thicknesses = [50, 50, 50, 50]
        self.test_reactor.pf_coil_vertical_thicknesses = [50, 50, 50, 50]
        self.test_reactor.pf_coil_to_rear_blanket_radial_gap = 50
        self.test_reactor.pf_coil_to_tf_coil_radial_gap = 50
        self.test_reactor.pf_coil_case_thickness = 10
        self.test_reactor.outboard_tf_coil_radial_thickness = 100
        self.test_reactor.outboard_tf_coil_poloidal_thickness = 50

        start_time = time.time()
        self.test_reactor.shapes_and_components
        stop_time = time.time()
        initial_construction_time = stop_time - start_time

        start_time = time.time()
        self.test_reactor.shapes_and_components
        stop_time = time.time()
        reconstruction_time = stop_time - start_time

        assert reconstruction_time < initial_construction_time
        # assert reconstruction_time < initial_construction_time * 0.01

    def test_divertor_position_error(self):
        """checks an invalid divertor position raises the correct
        ValueError."""

        def invalid_position():
            self.test_reactor.divertor_position = "coucou"

        self.assertRaises(ValueError, invalid_position)

    def test_divertor_upper_lower(self):
        """Checks that BallReactors with coils with lower and upper divertors
        can be created."""
        self.test_reactor.pf_coil_radial_thicknesses = [50, 50, 50, 50]
        self.test_reactor.pf_coil_vertical_thicknesses = [50, 50, 50, 50]
        self.test_reactor.pf_coil_to_rear_blanket_radial_gap = 50
        self.test_reactor.pf_coil_to_tf_coil_radial_gap = 50
        self.test_reactor.pf_coil_case_thickness = 10
        self.test_reactor.outboard_tf_coil_radial_thickness = 50
        self.test_reactor.outboard_tf_coil_poloidal_thickness = 50

        self.test_reactor.divertor_position = "lower"
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 10

        self.test_reactor.divertor_position = "upper"
        assert self.test_reactor.solid is not None
        assert len(self.test_reactor.shapes_and_components) == 10

    def test_export_stp(self):
        """Exports and stp file with mode = solid and wire and checks
        that the outputs folders exist."""

        os.system("rm -rf reactor_solids")
        os.system("rm -rf reactor_wires")

        self.test_reactor.export_stp(
            output_folder='reactor_solids',
            mode='solid'
        )

        self.test_reactor.export_stp(
            output_folder='reactor_wires',
            mode='wire'
        )

        assert Path("reactor_wires").exists() is True
        assert Path("reactor_solids").exists() is True
