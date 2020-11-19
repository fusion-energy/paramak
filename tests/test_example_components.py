
import os
import unittest
from pathlib import Path

cwd = os.getcwd()


class test_object_properties(unittest.TestCase):

    def test_make_all_parametric_components(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_components"))
        output_filenames = [
            'plasma_shape.stp',
            'blanket_constant_thickness_outboard_plasma.stp',
            'blanket_constant_thickness_inboard_plasma.stp',
            'blanket_constant_thickness_plasma.stp',
            'center_column_shield_cylinder.stp',
            'firstwall_from_center_column_shield_cylinder.stp',
            'center_column_shield_hyperbola.stp',
            'firstwall_from_center_column_shield_hyperbola.stp',
            'center_column_shield_circular.stp',
            'firstwall_from_center_column_shield_circular.stp',
            'center_column_shield_flat_top_hyperbola.stp',
            'firstwall_from_center_column_shield_flat_top_hyperbola.stp',
            'center_column_shield_flat_top_Circular.stp',
            'firstwall_from_center_column_shield_flat_top_Circular.stp',
            'center_column_shield_plasma_hyperbola.stp',
            'firstwall_from_center_column_shield_plasma_hyperbola.stp',
            'inner_tf_coils_circular.stp',
            'inner_tf_coils_flat.stp',
            'pf_coil_case_set.stp',
            'pf_coil_set.stp',
            'pf_coil_cases_set.stp',
            'poloidal_field_coil.stp',
            'pf_coil_cases_set_fc.stp',
            'poloidal_field_coil_case_fc.stp',
            'poloidal_field_coil_case.stp',
            'blanket_arc_v.stp',
            'blanket_arc_h.stp',
            'tf_coil_rectangle.stp',
            'toroidal_field_coil_coat_hanger.stp',
            'toroidal_field_coil_triple_arc.stp',
            'toroidal_field_coil_princeton_d.stp',
            'ITER_type_divertor.stp']
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python make_all_parametric_components.py")
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_plasma(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_components"))
        output_filenames = [
            "ITER_plasma.html",
            "EU_DEMO_plasma.html",
            "ST_plasma.html",
            "AST_plasma.html",
            "ITER_plasma.stp",
            "EU_DEMO_plasma.stp",
            "ST_plasma.stp",
            "AST_plasma.stp",
            "ITER_plasma.png",
            "EU_DEMO_plasma.png",
            "ST_plasma.png",
            "AST_plasma.png",
            "all_plasma_and_points.html",
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python make_plasmas.py")
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_demo_style_blanket(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_components"))
        output_filename = "blanket.stp"
        os.system("rm " + output_filename)
        os.system("python make_demo_style_blankets.py")
        assert Path(output_filename).exists() is True
        os.system("rm " + output_filename)

    def test_make_segmented_firstwall(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_components"))
        output_filename = "segmented_firstwall.stp"
        os.system("rm " + output_filename)
        os.system("python make_firstwall_for_neutron_wall_loading.py")
        assert Path(output_filename).exists() is True
        os.system("rm " + output_filename)

    def test_make_segmented_firstwall(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_components"))
        output_filenames = [
            "vacuum_vessel_with_ports.stp",
            "vacuum_vessel_with_ports.svg",
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python make_vacuum_vessel_with_ports.py")
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)


if __name__ == "__main__":
    unittest.main()
