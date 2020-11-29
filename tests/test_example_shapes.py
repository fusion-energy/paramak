
import os
import sys
import unittest
from pathlib import Path

from examples.example_parametric_shapes import (
    make_blanket_from_parameters, make_blanket_from_points,
    make_CAD_from_points, make_can_reactor_from_parameters,
    make_can_reactor_from_points)

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))


class TestExampleShapes(unittest.TestCase):

    def test_make_blanket_from_points(self):
        """Runs the example and checks the output files are produced"""
        filename = "blanket_from_points.stp"
        os.system("rm " + filename)
        make_blanket_from_points.main(filename=filename)
        assert Path(filename).exists() is True
        os.system("rm " + filename)

    def test_make_blanket_parametrically(self):
        """Runs the example and checks the output files are produced"""
        filename = "blanket_from_parameters.stp"
        os.system("rm " + filename)
        make_blanket_from_parameters.main(filename=filename)
        assert Path(filename).exists() is True
        os.system("rm " + filename)

    def test_make_cad_from_points(self):
        """Runs the example and checks the output files are produced"""
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
        make_CAD_from_points.main()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_can_reactor_from_parameters(self):
        """Runs the example and checks the output files are produced"""
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
        make_can_reactor_from_parameters.main()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_can_reactor_from_points(self):
        """Runs the example and checks the output files are produced"""
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
        make_can_reactor_from_points.main()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)


if __name__ == "__main__":
    unittest.main()
