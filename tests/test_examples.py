import os
import unittest
from pathlib import Path

cwd = os.getcwd()


class test_object_properties(unittest.TestCase):
    def test_make_parametric_ball_rector(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_reactors"))
        output_filenames = [
            "plasma.stp",
            "inboard_tf_coils.stp",
            "center_column_shield.stp",
            "divertor.stp",
            "firstwall.stp",
            "blanket.stp",
            "blanket_rear_wall.stp",
            "Graveyard.stp",
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python make_parametric_ball_reactor.py")
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_parametric_single_null_ball_reactor(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_reactors"))
        output_filenames = [
            "blanket_rear_wall.stp",
            "blanket.stp",
            "center_column_shield.stp",
            "divertor.stp",
            "firstwall.stp",
            "Graveyard.stp",
            "inboard_tf_coils.stp",
            "pf_coil_0.stp",
            "pf_coil_1.stp",
            "pf_coil_2.stp",
            "pf_coil_3.stp",
            "plasma.stp",
            "tf_coil.stp"
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python make_parametric_single_null_ball_reactor.py")
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_parametric_single_null_submersion_reactor(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_reactors"))
        output_filenames = [
            'inboard_tf_coils.stp',
            'center_column_shield.stp',
            'plasma.stp',
            'divertor.stp',
            'supports.stp',
            'outboard_firstwall.stp',
            'blanket.stp',
            'outboard_rear_blanket_wall.stp',
            'outboard_tf_coil.stp',
            'pf_coil_0.stp',
            'pf_coil_1.stp',
            'pf_coil_2.stp',
            'pf_coil_3.stp',
            'Graveyard.stp'
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python make_parametric_single_null_submersion_ball_reactor.py")
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_blanket_from_points(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_shapes"))
        output_filename = "blanket_from_points.stp"
        os.system("rm " + output_filename)
        os.system("python make_blanket_from_points.py")
        assert Path(output_filename).exists() is True
        os.system("rm " + output_filename)

    def test_make_blanket_parametrically(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_shapes"))
        output_filename = "blanket_from_parameters.stp"
        os.system("rm " + output_filename)
        os.system("python make_blanket_from_parameters.py")
        assert Path(output_filename).exists() is True
        os.system("rm " + output_filename)

    def test_make_CAD_from_points(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_shapes"))
        output_filenames = [
            "extruded_mixed.stp",
            "extruded_straight.stp",
            "extruded_spline.stp",
            "rotated_mixed.stp",
            "rotated_spline.stp",
            "rotated_straights.stp",
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python make_CAD_from_points.py")
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_all_parametric_components(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_components"))
        output_filenames = [
            "blanket_constant_thickness_outboard_plasma.stp",
            "blanket_constant_thickness_inboard_plasma.stp",
            "blanket_constant_thickness_plasma.stp",
            "center_column_shield_cylinder.stp",
            "center_column_shield_hyperbola.stp",
            "center_column_shield_flat_top_hyperbola.stp",
            "center_column_shield_plasma_hyperbola.stp",
            "poloidal_field_coil.stp",
            "poloidal_field_coil_case_fc.stp",
            "poloidal_field_coil_case.stp",
            "inner_tf_coils_circular.stp",
            "inner_tf_coils_flat.stp",
            "blanket_arc_v.stp",
            "blanket_arc_h.stp",
            "tf_coil_rectangle.stp",
            "toroidal_field_coil_coat_hanger.stp",
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python make_all_parametric_components.py")
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_can_reactor_from_parameters(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_shapes"))
        output_filenames = [
            "can_reactor_from_parameters/plasma.stp",
            "can_reactor_from_parameters/centre_column.stp",
            "can_reactor_from_parameters/blanket.stp",
            "can_reactor_from_parameters/firstwall.stp",
            "can_reactor_from_parameters/divertor_bottom.stp",
            "can_reactor_from_parameters/divertor_top.stp",
            "can_reactor_from_parameters/core.stp",
            "can_reactor_from_parameters/reactor.html",
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python make_can_reactor_from_parameters.py")
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_can_reactor_from_points(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_shapes"))
        output_filenames = [
            "can_reactor_from_points/plasma.stp",
            "can_reactor_from_points/centre_column.stp",
            "can_reactor_from_points/blanket.stp",
            "can_reactor_from_points/firstwall.stp",
            "can_reactor_from_points/divertor_bottom.stp",
            "can_reactor_from_points/divertor_top.stp",
            "can_reactor_from_points/core.stp",
            "can_reactor_from_points/reactor.html",
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python make_can_reactor_from_points.py")
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


if __name__ == "__main__":
    unittest.main()
