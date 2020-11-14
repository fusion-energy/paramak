import os
import unittest
from pathlib import Path

cwd = os.getcwd()


class test_object_properties(unittest.TestCase):

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


if __name__ == "__main__":
    unittest.main()
