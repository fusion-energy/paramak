"""
This file is part of PARAMAK which is a design tool capable
of creating 3D CAD models compatible with automated neutronics
analysis.

PARAMAK is released under GNU General Public License v3.0.
Go to https://github.com/Shimwell/paramak/blob/master/LICENSE
for full license details.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Copyright (C) 2019  UKAEA

THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
"""
import os
from pathlib import Path
import unittest
import json

from paramak import RotateStraightShape, Shape, Reactor


class test_object_properties(unittest.TestCase):
    def test_reactor_creation_with_default_properties(self):
        """creates a Reactor object and checks that it has \
                no default properties"""

        test_reactor = Reactor()

        assert test_reactor is not None

    def test_adding_component_to_reactor(self):
        """creates a Reactor object and checks that shapes \
                can be added to it"""

        test_shape = RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = Reactor()
        assert len(test_reactor) == 0
        test_reactor.add_shape(test_shape)
        assert len(test_reactor) == 1

    def test_Graveyard_exists(self):
        """checks that make_graveyard() creates a graveyard \
                using the shapes in the Reactor object"""

        test_shape = RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = Reactor()
        test_reactor.add_shape(test_shape)
        test_reactor.make_graveyard()

        assert type(test_reactor.graveyard) == Shape

    def test_exported_stp_files_exist(self):
        """checks that export_stp() creates stp file in the \
                specified location"""

        test_shape = RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        os.system("rm test_reactor/test_shape.stp")
        os.system("rm test_reactor/Graveyard.stp")
        test_shape.stp_filename = "test_shape.stp"
        test_reactor = Reactor()
        test_reactor.add_shape(test_shape)

        test_reactor.export_stp(output_folder="test_reactor")

        for filepath in ["test_reactor/test_shape.stp", "test_reactor/Graveyard.stp"]:
            assert Path(filepath).exists() is True
            os.system("rm " + filepath)

    def test_neutronics_desscription(self):
        def test_neutronics_description_without_material_tag():
            """checks that a ValueError is raised when the neutronics description \
                        is exported without material_tag"""

            test_shape = RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
            test_shape.rotation_angle = 360
            test_shape.stp_filename = "test.stp"
            test_reactor = Reactor()
            test_reactor.add_shape(test_shape)
            neutronics_description = test_reactor.neutronics_description()

        self.assertRaises(ValueError, test_neutronics_description_without_material_tag)

        def test_neutronics_description_without_stp_filename():
            """checks that a ValueError is raised when the neutronics description \
                        is exported without stp_filename"""

            test_shape = RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
            test_shape.rotation_angle = 360
            test_shape.material_tag = "test_material"
            test_reactor = Reactor()
            test_reactor.add_shape(test_shape)
            neutronics_description = test_reactor.neutronics_description()

        self.assertRaises(ValueError, test_neutronics_description_without_stp_filename)

    def test_neutronics_description_without_plasma(self):
        """checks that the neutronics description is exported with correct \
                material_tag and filename"""

        test_shape = RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.material_tag = "test_material"
        test_shape.stp_filename = "test.stp"
        test_reactor = Reactor()
        test_reactor.add_shape(test_shape)
        neutronics_description = test_reactor.neutronics_description()

        assert len(neutronics_description) == 2
        assert "filename" in neutronics_description[0].keys()
        assert "material" in neutronics_description[0].keys()
        assert neutronics_description[0]["material"] == "test_material"
        assert neutronics_description[0]["filename"] == "test.stp"
        assert neutronics_description[1]["material"] == "Graveyard"
        assert neutronics_description[1]["filename"] == "Graveyard.stp"

    def test_export_neutronics_description(self):
        """checks that the neutronics description is exported to a json file with \
                the correct material name and filename"""

        os.system("rm manifest_test.json")

        test_shape = RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.material_tag = "test_material"
        test_shape.stp_filename = "test.stp"
        test_reactor = Reactor()
        test_reactor.add_shape(test_shape)
        returned_filename = test_reactor.export_neutronics_description(
            filename="manifest_test.json"
        )
        with open("manifest_test.json") as json_file:
            neutronics_description = json.load(json_file)

        assert returned_filename == "manifest_test.json"
        assert Path("manifest_test.json").exists() is True
        assert len(neutronics_description) == 2
        assert "filename" in neutronics_description[0].keys()
        assert "material" in neutronics_description[0].keys()
        assert neutronics_description[0]["material"] == "test_material"
        assert neutronics_description[0]["filename"] == "test.stp"
        assert neutronics_description[1]["material"] == "Graveyard"
        assert neutronics_description[1]["filename"] == "Graveyard.stp"
        os.system("rm manifest_test.json")

    def test_export_2d_image(self):
        """checks that export_2d_image() exports a png file with \
                the correct filename"""

        os.system("rm 2d_test_image.png")
        test_shape = RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_reactor = Reactor()
        test_reactor.add_shape(test_shape)
        returned_filename = test_reactor.export_2d_image(filename="2d_test_image.png")

        assert Path(returned_filename).exists() is True
        os.system("rm 2d_test_image.png")

    def test_export_html(self):
        """checks that export_html() exports a html file with \
                the correct filename"""

        os.system("rm test_html.html")
        test_shape = RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_reactor = Reactor()
        test_reactor.add_shape(test_shape)
        test_reactor.export_html(filename="test_html.html")

        assert Path("test_html.html").exists() is True
        os.system("rm test_html.html")


if __name__ == "__main__":
    unittest.main()
