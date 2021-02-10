
import os
import sys
import unittest
from pathlib import Path

from examples.example_parametric_shapes import (
    make_blanket_from_parameters, make_blanket_from_points,
    make_CAD_from_points, make_can_reactor_from_parameters,
    make_can_reactor_from_points, make_html_diagram_from_stp_file,
)

import paramak

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))


class TestExampleShapes(unittest.TestCase):

    def test_make_blanket_from_points(self):
        """Runs the example and checks the output files are produced"""
        filename = "blanket_from_points.stp"
        os.system("rm *.stp")
        make_blanket_from_points.main(filename=filename)
        assert Path(filename).exists() is True
        os.system("rm *.stp")

    def test_make_blanket_parametrically(self):
        """Runs the example and checks the output files are produced"""
        filename = "blanket_from_parameters.stp"
        os.system("rm *.stp")
        make_blanket_from_parameters.main(filename=filename)
        assert Path(filename).exists() is True
        os.system("rm *.stp")

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
        os.system("rm *.stp")
        make_CAD_from_points.main()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True

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
        os.system("rm *.stp")
        os.system("rm *.html")
        make_can_reactor_from_parameters.main()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True

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
        os.system("rm *.stp")
        os.system("rm *.html")
        make_can_reactor_from_points.main()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True

    def test_make_html_diagram_from_stp_file(self):
        """Runs the example and checks the output files are produced"""
        output_filenames = [
            "example_shape.stp",
            "example_shape_RZ.html",
            "example_shape_XYZ.html",
            "example_shape_XZ.html",
            "example_shape_from_stp_RZ.html",
            "example_shape_from_stp_XZ.html",
            "example_shape_from_stp_XYZ.html",
        ]
        os.system("rm *.stp")
        os.system("rm *.html")
        make_html_diagram_from_stp_file.make_stp_file()
        make_html_diagram_from_stp_file.load_stp_file_and_plot()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True

    def test_list_of_wires_can_be_exported(self):
        """Checks than a list of wires is an acceptable input
        for export_wire_to_html wires argument.
        """

        example_shape = paramak.ExtrudeMixedShape(
            distance=1,
            points=[
                (150, 100, "spline"),
                (140, 75, "spline"),
                (110, 45, "spline"),
            ]
        )

        fig = paramak.utils.export_wire_to_html(
            wires=[example_shape.wire],
            tolerance=0.1,
            view_plane="XY",
            facet_splines=True,
            facet_circles=True,
            filename="example_shape_from_stp.html",
        )

        assert fig is not None

    def test_incorrect_view_plane(self):
        """Checks than an error is raised when incorrect values of the
        view_plane is set
        """

        def set_value():
            example_shape = paramak.ExtrudeMixedShape(
                distance=1,
                points=[
                    (100, 0, "straight"),
                    (200, 0, "circle"),
                    (250, 50, "circle"),
                    (200, 100, "straight"),
                    (150, 100, "spline"),
                    (140, 75, "spline"),
                    (110, 45, "spline"),
                ]
            )

            paramak.utils.export_wire_to_html(
                wires=example_shape.wire,
                tolerance=0.1,
                view_plane="coucou",
                facet_splines=True,
                facet_circles=True,
                filename="example_shape_from_stp.html",
            )

        self.assertRaises(ValueError, set_value)


if __name__ == "__main__":
    unittest.main()
