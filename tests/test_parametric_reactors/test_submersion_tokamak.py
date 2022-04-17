import os
import unittest
from pathlib import Path

import pytest

import paramak


class TestSubmersionTokamak(unittest.TestCase):
    """Tests functionality of the SubmersionTokamak class"""

    def setUp(self):
        self.test_reactor = paramak.SubmersionTokamak(
            inner_bore_radial_thickness=10,
            inboard_tf_leg_radial_thickness=30,
            center_column_shield_radial_thickness=60,
            divertor_radial_thickness=50,
            inner_plasma_gap_radial_thickness=30,
            plasma_radial_thickness=300,
            outer_plasma_gap_radial_thickness=30,
            firstwall_radial_thickness=30,
            blanket_rear_wall_radial_thickness=30,
            support_radial_thickness=20,
            inboard_blanket_radial_thickness=20,
            outboard_blanket_radial_thickness=20,
            elongation=2.3,
            triangularity=0.45,
            rotation_angle=359,
        )

    def test_input_variable_names(self):
        """tests that the number of inputs variables is correct"""

        assert len(self.test_reactor.input_variables.keys()) == 26
        assert len(self.test_reactor.input_variable_names) == 26

    def test_svg_creation(self):
        """Creates a SubmersionTokamak and checks that an svg file of the
        reactor can be exported using the export_svg method."""

        os.system("rm test_image.svg")
        self.test_reactor.export_svg("test_image.svg")

        assert Path("test_image.svg").exists() is True
        os.system("rm test_image.svg")

    def test_minimal_creation(self):
        """Creates a SubmersionTokamak and checks that the correct number of
        components are created."""

        assert len(self.test_reactor.shapes_and_components) == 9

    def test_with_tf_coils_creation(self):
        """Creates a SubmersionTokamak with tf coils and checks that the correct
        number of components are created."""

        self.test_reactor.outboard_tf_coil_radial_thickness = 50
        self.test_reactor.rear_blanket_to_tf_gap = 50
        self.test_reactor.pf_coil_radial_position = [100]
        self.test_reactor.pf_coil_vertical_position = [100]
        self.test_reactor.outboard_tf_coil_poloidal_thickness = 70
        self.test_reactor.number_of_tf_coils = 4

        assert len(self.test_reactor.shapes_and_components) == 10

    def test_with_tf_and_pf_coils_creation(self):
        """Creates a SubmersionTokamak with tf and pf coils and checks that the
        correct number of components are created."""

        self.test_reactor.outboard_tf_coil_radial_thickness = 50
        self.test_reactor.outboard_tf_coil_poloidal_thickness = 70
        self.test_reactor.pf_coil_vertical_thicknesses = [50, 50, 50, 50, 50]
        self.test_reactor.pf_coil_radial_thicknesses = [40, 40, 40, 40, 40]
        self.test_reactor.pf_coil_radial_position = [100, 100, 200, 200, 100]
        self.test_reactor.pf_coil_vertical_position = [100, -100, 200, -200, 0]
        self.test_reactor.pf_coil_case_thicknesses = [10, 10, 10, 10, 10]
        self.test_reactor.rear_blanket_to_tf_gap = 50
        self.test_reactor.number_of_tf_coils = 4

        assert len(self.test_reactor.shapes_and_components) == 20

    def test_minimal_stp_creation(self):
        """Creates a SubmersionTokamak and checks that stp files of all
        components can be exported using the export_stp method."""

        os.system("rm -r *.stp")
        output_filenames = [
            "plasma.stp",
            "center_column_shield.stp",
            "outboard_firstwall.stp",
            "blanket.stp",
            "divertor_upper.stp",
            "divertor_lower.stp",
            "supports.stp",
            "outboard_rear_blanket_wall.stp",
            "inboard_tf_coils.stp",
        ]
        self.test_reactor.export_stp(filename=output_filenames)

        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm -r *.stp")

    def test_stp_creation_with_tf(self):
        """Creates a SubmersionTokamak and checks that stp files of all
        components can be exported using the export_stp method."""

        os.system("rm -r *.stp")
        self.test_reactor.number_of_tf_coils = 4
        self.test_reactor.outboard_tf_coil_radial_thickness = 10
        self.test_reactor.outboard_tf_coil_poloidal_thickness = 10
        self.test_reactor.rear_blanket_to_tf_gap = 10
        output_filenames = [
            "plasma.stp",
            "center_column_shield.stp",
            "outboard_firstwall.stp",
            "blanket.stp",
            "divertor_upper.stp",
            "divertor_lower.stp",
            "supports.stp",
            "outboard_rear_blanket_wall.stp",
            "inboard_tf_coils.stp",
            "tf_coils.stp",
        ]
        self.test_reactor.export_stp(filename=output_filenames)

        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm -r *.stp")

    def test_with_pf_coils_stp_creation(self):
        """Creates a SubmersionTokamak with pf coils and checks that stp files
        of all components can be exported using the export_stp method."""

        os.system("rm -r pf_SubmersionTokamak")

        self.test_reactor.outboard_tf_coil_radial_thickness = 50
        self.test_reactor.pf_coil_vertical_thicknesses = [50, 50]
        self.test_reactor.pf_coil_radial_thicknesses = [40, 40]
        self.test_reactor.pf_coil_radial_position = [100, 100]
        self.test_reactor.pf_coil_vertical_position = [100, -100]

        output_filenames = [
            "pf_coil_1.stp",
            "pf_coil_2.stp",
            "plasma.stp",
            "center_column_shield.stp",
            "outboard_firstwall.stp",
            "blanket.stp",
            "divertor_lower.stp",
            "supports.stp",
            "outboard_rear_blanket_wall.stp",
            "inboard_tf_coils.stp",
            "tf_coils.stp",
        ]

        self.test_reactor.export_stp(filename=output_filenames)

        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm -r pf_SubmersionTokamak")

    def test_with_tf_and_pf_coils_stp_creation(self):
        """Creates a SubmersionTokamak with tf and pf coils and checks that
        stp files of all components can be exported using the export_stp method."""

        os.system("rm -r *.stp")

        self.test_reactor.outboard_tf_coil_radial_thickness = 50
        self.test_reactor.outboard_tf_coil_poloidal_thickness = 70
        self.test_reactor.pf_coil_vertical_thicknesses = [50, 50]
        self.test_reactor.pf_coil_radial_thicknesses = [40, 40]
        self.test_reactor.pf_coil_radial_position = [100, 100]
        self.test_reactor.pf_coil_vertical_position = [100, -100]
        self.test_reactor.rear_blanket_to_tf_gap = 50
        self.test_reactor.pf_coil_case_thicknesses = [10, 10]
        self.test_reactor.number_of_tf_coils = 4

        output_filenames = [
            "pf_coil_1.stp",
            "pf_coil_2.stp",
            "pf_coil_case_1.stp",
            "pf_coil_case_2.stp",
            "plasma.stp",
            "center_column_shield.stp",
            "outboard_firstwall.stp",
            "blanket.stp",
            "divertor_upper.stp",
            "divertor_lower.stp",
            "supports.stp",
            "outboard_rear_blanket_wall.stp",
            "inboard_tf_coils.stp",
            "tf_coils.stp",
        ]
        self.test_reactor.export_stp(filename=output_filenames)

        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm -r *.stp")

    def test_rotation_angle_warning(self):
        """Creates a SubmersionTokamak with rotation_angle = 360 and checks that the
        correct warning message is printed."""

        def warning_trigger():
            try:
                self.test_reactor.rotation_angle = 360
                self.test_reactor._rotation_angle_check()
            except BaseException:
                pass

        msg = "360 degree rotation may result in a " + "Standard_ConstructionError or AttributeError"
        with pytest.warns(UserWarning, match=msg):
            warning_trigger()

    def test_submersion_reactor_hash_value(self):
        """Creates a submersion reactor and checks that all shapes in the reactor are created
        when .shapes_and_components is first called. Checks that when .shapes_and_components
        is called again with no changes to the reactor, the shapes in the reactor are
        reconstructed and the previously constructed shapes are returned. Checks that when
        .shapes_and_components is called again with no changes to the reactor, the shapes in
        the reactor are reconstructed and these new shapes are returned. Checks that the
        reactor_hash_value is only updated when the reactor is reconstructed."""

        self.test_reactor.pf_coil_radial_thicknesses = [30, 30, 30, 30]
        self.test_reactor.pf_coil_vertical_thicknesses = [30, 30, 30, 30]
        self.test_reactor.pf_coil_radial_position = [100, 100, 200, 200]
        self.test_reactor.pf_coil_vertical_position = [100, -100, 200, -200]
        self.test_reactor.pf_coil_case_thicknesses = [10, 10, 10, 10]
        self.test_reactor.rear_blanket_to_tf_gap = 50
        self.test_reactor.outboard_tf_coil_radial_thickness = 30
        self.test_reactor.outboard_tf_coil_poloidal_thickness = 30
        self.test_reactor.number_of_tf_coils = 16

        assert self.test_reactor.reactor_hash_value is None
        # commented out as code inspector suggests all attributs should be
        # declaired in class init
        # for key in [
        #     "_inboard_tf_coils",
        #     "_center_column_shield",
        #     "_plasma",
        #     "_inboard_firstwall",
        #     "_inboard_blanket",
        #     "_firstwall",
        #     "_divertor_upper",
        #     "_divertor_lower",
        #     "_blanket",
        #     "_supports",
        #     "_outboard_rear_blanket_wall_upper",
        #     "_outboard_rear_blanket_wall_lower",
        #     "_outboard_rear_blanket_wall",
        #     "_tf_coil",
        #     "_pf_coils",
        #     "_pf_coils_casing",
        # ]:
        #     assert key not in self.test_reactor.__dict__

        assert self.test_reactor.shapes_and_components is not None
        for key in [
            "_inboard_tf_coils",
            "_center_column_shield",
            "_plasma",
            "_inboard_firstwall",
            "_inboard_blanket",
            "_firstwall",
            "_divertor_upper",
            "_divertor_lower",
            "_blanket",
            "_supports",
            "_outboard_rear_blanket_wall_upper",
            "_outboard_rear_blanket_wall_lower",
            "_outboard_rear_blanket_wall",
            "_tf_coil",
            "_pf_coils",
            "_pf_coils_casing",
        ]:
            assert key in self.test_reactor.__dict__.keys()

        assert len(self.test_reactor.shapes_and_components) == 18
        assert self.test_reactor.reactor_hash_value is not None
        initial_hash_value = self.test_reactor.reactor_hash_value
        self.test_reactor.rotation_angle = 270
        assert self.test_reactor.reactor_hash_value == initial_hash_value
        assert self.test_reactor.shapes_and_components is not None
        assert self.test_reactor.reactor_hash_value != initial_hash_value

    def test_error_divertor_pos(self):
        """Checks an invalid divertor and support
        position raises the correct ValueError."""

        def invalid_divertor_position():
            self.test_reactor.divertor_position = "coucou"

        self.assertRaises(ValueError, invalid_divertor_position)

        def invalid_support_position():
            self.test_reactor.support_position = "coucou"

        self.assertRaises(ValueError, invalid_support_position)

    def test_error_coil_case_thickness(self):
        """checks an invalid number of coil case thicknesses raises the correct
        ValueError."""

        def invalid_pf_coil_case_thicknesses():
            self.test_reactor.pf_coil_radial_thicknesses = [30, 30, 30, 30]
            self.test_reactor.pf_coil_vertical_thicknesses = [30, 30, 30, 30]
            self.test_reactor.pf_coil_radial_position = [100, 100, 200, 200]
            self.test_reactor.pf_coil_vertical_position = [100, -100, 200, -200]
            self.test_reactor.pf_coil_case_thicknesses = [10, 10]
            self.test_reactor.create_solids()

        self.assertRaises(ValueError, invalid_pf_coil_case_thicknesses)

    def test_divertors_supports(self):
        """Checks that SubmersionTokamaks with lower and upper supports
        and divertors can be created."""

        self.test_reactor.divertor_position = "lower"
        self.test_reactor.support_position = "lower"
        assert self.test_reactor.solid is not None

        self.test_reactor.divertor_position = "lower"
        self.test_reactor.support_position = "upper"
        assert self.test_reactor.solid is not None

        self.test_reactor.divertor_position = "upper"
        self.test_reactor.support_position = "lower"
        assert self.test_reactor.solid is not None

        self.test_reactor.divertor_position = "upper"
        self.test_reactor.support_position = "upper"
        assert self.test_reactor.solid is not None
