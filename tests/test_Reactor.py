
import json
import os
import unittest
from pathlib import Path

import cadquery as cq
import paramak
import pytest


class TestReactor(unittest.TestCase):

    def test_adding_shape_with_material_tag_to_reactor(self):
        """Checks that a shape object can be added to a Reactor object with
        the correct material tag property."""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], material_tag="mat1"
        )
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([test_shape])
        assert len(test_reactor.material_tags) == 1
        assert test_reactor.material_tags[0] == "mat1"

    def test_adding_multiple_shapes_with_material_tag_to_reactor(self):
        """Checks that multiple shape objects can be added to a Reactor object
        with the correct material tag properties."""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], material_tag="mat1"
        )
        test_shape2 = paramak.RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20)], material_tag="mat2"
        )
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([test_shape, test_shape2])
        assert len(test_reactor.material_tags) == 2
        assert "mat1" in test_reactor.material_tags
        assert "mat2" in test_reactor.material_tags

    def test_adding_shape_with_stp_filename_to_reactor(self):
        """Checks that a shape object can be added to a Reactor object with the
        correct stp filename property."""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], stp_filename="filename.stp"
        )
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([test_shape])
        assert len(test_reactor.stp_filenames) == 1
        assert test_reactor.stp_filenames[0] == "filename.stp"

    def test_adding_multiple_shape_with_stp_filename_to_reactor(self):
        """Checks that multiple shape objects can be added to a Reactor object
        with the correct stp filename properties."""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], stp_filename="filename.stp"
        )
        test_shape2 = paramak.RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20)], stp_filename="filename2.stp"
        )
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([test_shape, test_shape2])
        assert len(test_reactor.stp_filenames) == 2
        assert test_reactor.stp_filenames[0] == "filename.stp"
        assert test_reactor.stp_filenames[1] == "filename2.stp"

    def test_adding_shape_with_duplicate_stp_filename_to_reactor(self):
        """Adds shapes to a Reactor object to check errors are raised
        correctly."""

        def test_stp_filename_duplication():
            """Checks ValueError is raised when shapes with the same stp
            filenames are added to a reactor object"""

            test_shape_1 = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)], stp_filename="filename.stp"
            )
            test_shape_2 = paramak.RotateSplineShape(
                points=[(0, 0), (0, 20), (20, 20)], stp_filename="filename.stp"
            )
            test_shape_1.rotation_angle = 90
            my_reactor = paramak.Reactor([test_shape_1, test_shape_2])
            my_reactor.export_stp()

        self.assertRaises(ValueError, test_stp_filename_duplication)

    def test_adding_shape_with_None_stp_filename_to_reactor(self):
        """adds shapes to a Reactor object to check errors are raised correctly"""

        def test_stp_filename_None():
            """checks ValueError is raised when RotateStraightShapes with duplicate
            stp filenames are added"""

            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)], stp_filename="filename.stp"
            )
            test_shape2 = paramak.RotateSplineShape(
                points=[(0, 0), (0, 20), (20, 20)], stp_filename=None
            )
            test_shape.create_solid()
            my_reactor = paramak.Reactor([test_shape, test_shape2])
            my_reactor.export_stp()

        self.assertRaises(ValueError, test_stp_filename_None)

    def test_adding_shape_with_duplicate_stl_filename_to_reactor(self):
        """Adds shapes to a Reactor object to checks errors are raised
        correctly"""

        def test_stl_filename_duplication():
            """Checks ValueError is raised when shapes with the same stl
            filenames are added to a reactor object"""

            test_shape_1 = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)], stl_filename="filename.stl"
            )
            test_shape_2 = paramak.RotateSplineShape(
                points=[(0, 0), (0, 20), (20, 20)], stl_filename="filename.stl"
            )
            test_shape_1.rotation_angle = 90
            my_reactor = paramak.Reactor([test_shape_1, test_shape_2])
            my_reactor.export_stl()

        self.assertRaises(ValueError, test_stl_filename_duplication)

    def test_adding_shape_with_the_same_default_stl_filename_to_reactor(self):
        """Adds shapes to a Reactor object to check errors are raised
        correctly."""

        def test_stl_filename_duplication_rotate_straight():
            """checks ValueError is raised when RotateStraightShapes with
            duplicate stl filenames (defaults) are added"""

            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)])
            test_shape2 = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)])
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            my_reactor = paramak.Reactor([test_shape, test_shape2])
            my_reactor.export_stl()

        self.assertRaises(
            ValueError,
            test_stl_filename_duplication_rotate_straight)

        def test_stl_filename_duplication_rotate_spline():
            """Checks ValueError is raised when RotateSplineShapes with
            duplicate stl filenames are added."""

            test_shape = paramak.RotateSplineShape(
                points=[(0, 0), (0, 20), (20, 20)], stl_filename="filename.stl"
            )
            test_shape2 = paramak.RotateSplineShape(
                points=[(0, 0), (0, 20), (20, 20)], stl_filename="filename.stl"
            )
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            my_reactor = paramak.Reactor([test_shape, test_shape2])
            my_reactor.export_stl()

        self.assertRaises(
            ValueError,
            test_stl_filename_duplication_rotate_spline)

        def test_stl_filename_duplication_rotate_mixed():
            """Checks ValueError is raised when RotateMixedShapes with
            duplicate stl filenames are added."""

            test_shape = paramak.RotateMixedShape(
                points=[(0, 0, "straight"), (0, 20, "straight"), (20, 20, "straight")],
                stl_filename="filename.stl",
            )
            test_shape2 = paramak.RotateMixedShape(
                points=[(0, 0, "straight"), (0, 20, "straight"), (20, 20, "straight")],
                stl_filename="filename.stl",
            )
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            my_reactor = paramak.Reactor([test_shape, test_shape2])
            my_reactor.export_stl()

        self.assertRaises(
            ValueError,
            test_stl_filename_duplication_rotate_mixed)

        def test_stl_filename_duplication_Rotate_Circle():
            """Checks ValueError is raised when RotateCircleShapes with
            duplicate stl filenames are added."""

            test_shape = paramak.RotateCircleShape(
                points=[(20, 20)],
                radius=10,
                rotation_angle=180,
                stl_filename="filename.stl",
            )
            test_shape2 = paramak.RotateCircleShape(
                points=[(20, 20)],
                radius=10,
                rotation_angle=180,
                stl_filename="filename.stl",
            )
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            my_reactor = paramak.Reactor([test_shape, test_shape2])
            my_reactor.export_stl()

        self.assertRaises(
            ValueError,
            test_stl_filename_duplication_Rotate_Circle)

        def test_stl_filename_duplication_Extrude_straight():
            """Checks ValueError is raised when ExtrudeStraightShapes with
            duplicate stl filenames are added."""

            test_shape = paramak.ExtrudeStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                distance=10,
                stl_filename="filename.stl",
            )
            test_shape2 = paramak.ExtrudeStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                distance=10,
                stl_filename="filename.stl",
            )
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            my_reactor = paramak.Reactor([test_shape, test_shape2])
            my_reactor.export_stl()

        self.assertRaises(
            ValueError,
            test_stl_filename_duplication_Extrude_straight)

        def test_stl_filename_duplication_Extrude_spline():
            """Checks ValueError is raised when ExtrudeSplineShapes with
            duplicate stl filenames are added."""

            test_shape = paramak.ExtrudeSplineShape(
                points=[(0, 0), (0, 20), (20, 20)],
                distance=10,
                stl_filename="filename.stl",
            )
            test_shape2 = paramak.ExtrudeSplineShape(
                points=[(0, 0), (0, 20), (20, 20)],
                distance=10,
                stl_filename="filename.stl",
            )
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            my_reactor = paramak.Reactor([test_shape, test_shape2])
            my_reactor.export_stl()

        self.assertRaises(
            ValueError,
            test_stl_filename_duplication_Extrude_spline)

        def test_stl_filename_duplication_Extrude_mixed():
            """checks ValueError is raised when ExtrudeMixedShapes with duplicate
            stl filenames are added"""

            test_shape = paramak.ExtrudeMixedShape(
                points=[(0, 0, "straight"), (0, 20, "straight"), (20, 20, "straight")],
                distance=10,
                stl_filename="filename.stl",
            )
            test_shape2 = paramak.ExtrudeMixedShape(
                points=[(0, 0, "straight"), (0, 20, "straight"), (20, 20, "straight")],
                distance=10,
                stl_filename="filename.stl",
            )
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            my_reactor = paramak.Reactor([test_shape, test_shape2])
            my_reactor.export_stl()

        self.assertRaises(
            ValueError,
            test_stl_filename_duplication_Extrude_mixed)

        def test_stl_filename_duplication_Extrude_Circle():
            """checks ValueError is raised when ExtrudeCircleShapes with duplicate
            stl filenames are added"""

            test_shape = paramak.ExtrudeCircleShape(
                points=[(20, 20)], radius=10, distance=10, stl_filename="filename.stl"
            )
            test_shape2 = paramak.ExtrudeCircleShape(
                points=[(20, 20)], radius=10, distance=10, stl_filename="filename.stl"
            )
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            my_reactor = paramak.Reactor([test_shape, test_shape2])
            my_reactor.export_stl()

        self.assertRaises(
            ValueError,
            test_stl_filename_duplication_Extrude_Circle)

        def test_stl_filename_None():
            test_shape = paramak.ExtrudeCircleShape(
                points=[(20, 20)], radius=10, distance=10, stl_filename=None
            )
            my_reactor = paramak.Reactor([test_shape])
            my_reactor.export_stl()

        self.assertRaises(
            ValueError,
            test_stl_filename_None)

    def test_reactor_creation_with_default_properties(self):
        """creates a Reactor object and checks that it has no default properties"""

        test_reactor = paramak.Reactor([])

        assert test_reactor is not None

    def test_adding_component_to_reactor(self):
        """creates a Reactor object and checks that shapes can be added to it"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([])
        assert len(test_reactor.shapes_and_components) == 0
        test_reactor = paramak.Reactor([test_shape])
        assert len(test_reactor.shapes_and_components) == 1

    def test_Graveyard_exists(self):
        """creates a Reactor object with one shape and checks that a graveyard
        can be produced using the make_graveyard method"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([test_shape])
        test_reactor.make_graveyard()

        assert isinstance(test_reactor.graveyard, paramak.Shape)

    def test_Graveyard_exists_solid_is_None(self):
        """creates a Reactor object with one shape and checks that a graveyard
        can be produced using the make_graveyard method when the solid
        attribute of the shape is None"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([test_shape])
        test_reactor.shapes_and_components[0].solid = None
        test_reactor.make_graveyard()

        assert isinstance(test_reactor.graveyard, paramak.Shape)

    def test_export_graveyard(self):
        """creates a Reactor object with one shape and checks that a graveyard
        can be exported to a specified location using the make_graveyard method"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        os.system("rm my_graveyard.stp")
        os.system("rm Graveyard.stp")
        test_shape.stp_filename = "test_shape.stp"
        test_reactor = paramak.Reactor([test_shape])

        test_reactor.export_graveyard()
        test_reactor.export_graveyard(filename="my_graveyard.stp")

        for filepath in ["Graveyard.stp", "my_graveyard.stp"]:
            assert Path(filepath).exists() is True
            os.system("rm " + filepath)

        assert test_reactor.graveyard is not None
        assert test_reactor.graveyard.__class__.__name__ == "HollowCube"

    def test_export_graveyard_offset(self):
        """checks that the graveyard can be exported with the correct default parameters
        and that these parameters can be changed"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        os.system("rm Graveyard.stp")
        test_reactor = paramak.Reactor([test_shape])
        test_reactor.export_graveyard()
        assert test_reactor.graveyard_offset == 100
        graveyard_volume_1 = test_reactor.graveyard.volume

        test_reactor.export_graveyard(graveyard_offset=50)
        assert test_reactor.graveyard.volume < graveyard_volume_1
        graveyard_volume_2 = test_reactor.graveyard.volume

        test_reactor.export_graveyard(graveyard_offset=200)
        assert test_reactor.graveyard.volume > graveyard_volume_1
        assert test_reactor.graveyard.volume > graveyard_volume_2

    def test_exported_stp_files_exist(self):
        """creates a Reactor object with one shape and checks that a stp file
        of the reactor can be exported to a specified location using the export_stp
        method"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        os.system("rm test_reactor/test_shape.stp")
        os.system("rm test_reactor/Graveyard.stp")
        test_shape.stp_filename = "test_shape.stp"
        test_reactor = paramak.Reactor([test_shape])

        test_reactor.export_stp(output_folder="test_reactor")

        for filepath in [
            "test_reactor/test_shape.stp",
                "test_reactor/Graveyard.stp"]:
            assert Path(filepath).exists() is True
            os.system("rm " + filepath)

    def test_exported_stl_files_exist(self):
        """creates a Reactor object with one shape and checks that a stl file
        of the reactor can be exported to a specified location using the
        export_stl method"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        os.system("rm test_reactor/test_shape.stl")
        os.system("rm test_reactor/Graveyard.stl")
        test_shape.stl_filename = "test_shape.stl"
        test_reactor = paramak.Reactor([test_shape])

        test_reactor.export_stl(output_folder="test_reactor")

        for filepath in [
            "test_reactor/test_shape.stl",
                "test_reactor/Graveyard.stl"]:
            assert Path(filepath).exists() is True
            os.system("rm " + filepath)

    def test_exported_svg_files_exist(self):
        """Creates a Reactor object with one shape and checks that a svg file
        of the reactor can be exported to a specified location using the
        export_svg method."""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        os.system("rm test_svg_image.svg")
        test_reactor = paramak.Reactor([test_shape])

        test_reactor.export_svg("test_svg_image.svg")

        assert Path("test_svg_image.svg").exists() is True
        os.system("rm test_svg_image.svg")

    def test_exported_svg_files_exist_no_extension(self):
        """creates a Reactor object with one shape and checks that an svg file
        of the reactor can be exported to a specified location using the export_svg
        method"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        os.system("rm test_svg_image.svg")
        test_reactor = paramak.Reactor([test_shape])

        test_reactor.export_svg("test_svg_image")

        assert Path("test_svg_image.svg").exists() is True
        os.system("rm test_svg_image.svg")

    def test_neutronics_description(self):
        """Creates reactor objects to check errors are raised correctly when
        exporting the neutronics description."""

        def test_neutronics_description_without_material_tag():
            """Checks ValueError is raised when the neutronics description is
            exported without material_tag."""

            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)])
            test_shape.rotation_angle = 360
            test_shape.stp_filename = "test.stp"
            test_reactor = paramak.Reactor([test_shape])
            test_reactor.neutronics_description()

        self.assertRaises(
            ValueError,
            test_neutronics_description_without_material_tag)

        def test_neutronics_description_without_stp_filename():
            """Checks ValueError is raised when the neutronics description is
            exported without stp_filename."""

            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)])
            test_shape.rotation_angle = 360
            test_shape.material_tag = "test_material"
            test_shape.stp_filename = None
            test_reactor = paramak.Reactor([test_shape])
            test_reactor.neutronics_description()

        self.assertRaises(
            ValueError,
            test_neutronics_description_without_stp_filename)

    def test_neutronics_description_without_plasma(self):
        """Creates a Reactor object and checks that the neutronics description
        is exported with the correct material_tag and stp_filename."""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.material_tag = "test_material"
        test_shape.stp_filename = "test.stp"
        test_reactor = paramak.Reactor([test_shape])
        neutronics_description = test_reactor.neutronics_description()

        assert len(neutronics_description) == 2
        assert "stp_filename" in neutronics_description[0].keys()
        assert "material" in neutronics_description[0].keys()
        assert neutronics_description[0]["material"] == "test_material"
        assert neutronics_description[0]["stp_filename"] == "test.stp"
        assert neutronics_description[1]["material"] == "Graveyard"
        assert neutronics_description[1]["stp_filename"] == "Graveyard.stp"

    def test_export_neutronics_description(self):
        """Creates a Reactor object and checks that the neutronics description
        is exported to a json file with the correct material_name and
        stp_filename."""

        os.system("rm manifest_test.json")

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.material_tag = "test_material"
        test_shape.stp_filename = "test.stp"
        test_shape.tet_mesh = "size 60"
        test_reactor = paramak.Reactor([test_shape])
        returned_filename = test_reactor.export_neutronics_description(
            filename="manifest_test.json"
        )
        with open("manifest_test.json") as json_file:
            neutronics_description = json.load(json_file)

        assert returned_filename == "manifest_test.json"
        assert Path("manifest_test.json").exists() is True
        assert len(neutronics_description) == 2
        assert "stp_filename" in neutronics_description[0].keys()
        assert "material" in neutronics_description[0].keys()
        assert "tet_mesh" in neutronics_description[0].keys()
        assert neutronics_description[0]["material"] == "test_material"
        assert neutronics_description[0]["stp_filename"] == "test.stp"
        assert neutronics_description[0]["tet_mesh"] == "size 60"
        assert neutronics_description[1]["material"] == "Graveyard"
        assert neutronics_description[1]["stp_filename"] == "Graveyard.stp"
        os.system("rm manifest_test.json")

    def test_export_neutronics_description_with_plasma(self):
        """Creates a Reactor object and checks that the neutronics description
        is exported to a json file with the correct entries, including the
        optional plasma."""

        os.system("rm manifest_test.json")

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            rotation_angle=360,
            material_tag="test_material",
            stp_filename="test.stp",
        )
        test_shape.tet_mesh = "size 60"
        test_plasma = paramak.Plasma(
            major_radius=500,
            minor_radius=100,
            stp_filename="plasma.stp",
            material_tag="DT_plasma",
        )
        test_reactor = paramak.Reactor([test_shape, test_plasma])
        returned_filename = test_reactor.export_neutronics_description(
            include_plasma=True
        )
        with open("manifest.json") as json_file:
            neutronics_description = json.load(json_file)

        assert returned_filename == "manifest.json"
        assert Path("manifest.json").exists() is True
        assert len(neutronics_description) == 3
        assert "stp_filename" in neutronics_description[0].keys()
        assert "material" in neutronics_description[0].keys()
        assert "tet_mesh" in neutronics_description[0].keys()
        assert "stp_filename" in neutronics_description[1].keys()
        assert "material" in neutronics_description[1].keys()
        assert "tet_mesh" not in neutronics_description[1].keys()
        assert neutronics_description[0]["material"] == "test_material"
        assert neutronics_description[0]["stp_filename"] == "test.stp"
        assert neutronics_description[0]["tet_mesh"] == "size 60"
        assert neutronics_description[1]["material"] == "DT_plasma"
        assert neutronics_description[1]["stp_filename"] == "plasma.stp"
        assert neutronics_description[2]["material"] == "Graveyard"
        assert neutronics_description[2]["stp_filename"] == "Graveyard.stp"
        os.system("rm manifest.json")

    def test_export_neutronics_description_without_plasma(self):
        """Creates a Reactor object and checks that the neutronics description is
        exported to a json file with the correct entires, exluding the optional
        plasma."""

        os.system("rm manifest_test.json")

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            rotation_angle=360,
            material_tag="test_material",
            stp_filename="test.stp",
        )
        test_shape.tet_mesh = "size 60"
        test_plasma = paramak.Plasma(major_radius=500, minor_radius=100)
        test_reactor = paramak.Reactor([test_shape, test_plasma])
        returned_filename = test_reactor.export_neutronics_description()
        with open("manifest.json") as json_file:
            neutronics_description = json.load(json_file)

        assert returned_filename == "manifest.json"
        assert Path("manifest.json").exists() is True
        assert len(neutronics_description) == 2
        assert "stp_filename" in neutronics_description[0].keys()
        assert "material" in neutronics_description[0].keys()
        assert "tet_mesh" in neutronics_description[0].keys()
        assert neutronics_description[0]["material"] == "test_material"
        assert neutronics_description[0]["stp_filename"] == "test.stp"
        assert neutronics_description[0]["tet_mesh"] == "size 60"
        assert neutronics_description[1]["material"] == "Graveyard"
        assert neutronics_description[1]["stp_filename"] == "Graveyard.stp"
        os.system("rm manifest.json")

    def test_export_neutronics_without_extension(self):
        """checks a json file is created if filename has no extension"""

        os.system("rm manifest_test.json")
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.material_tag = "test_material"
        test_shape.stp_filename = "test.stp"
        test_shape.tet_mesh = "size 60"
        test_reactor = paramak.Reactor([test_shape])
        returned_filename = test_reactor.export_neutronics_description(
            filename="manifest_test"
        )
        assert returned_filename == "manifest_test.json"
        assert Path("manifest_test.json").exists() is True
        os.system("rm manifest_test.json")

    def test_export_2d_image(self):
        """Creates a Reactor object and checks that a png file of the reactor
        with the correct filename can be exported using the export_2D_image
        method."""

        os.system("rm 2D_test_image.png")
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape])
        returned_filename = test_reactor.export_2d_image(
            filename="2D_test_image.png")

        assert Path(returned_filename).exists() is True
        os.system("rm 2D_test_image.png")

    def test_export_2d_image_without_extension(self):
        """creates a Reactor object and checks that a png file of the reactor
        with the correct filename can be exported using the export_2d_image
        method"""

        os.system("rm 2d_test_image.png")
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape])
        returned_filename = test_reactor.export_2d_image(
            filename="2d_test_image")

        assert Path(returned_filename).exists() is True
        os.system("rm 2d_test_image.png")

    def test_export_html(self):
        """Creates a Reactor object and checks that a html file of the reactor
        with the correct filename can be exported using the export_html
        method."""

        os.system("rm test_html.html")
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape])
        test_reactor.export_html(filename="test_html.html")

        assert Path("test_html.html").exists() is True
        os.system("rm test_html.html")
        test_reactor.export_html(filename="test_html")

        assert Path("test_html.html").exists() is True
        os.system("rm test_html.html")

    def test_tet_meshes_error(self):
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape])
        assert test_reactor.tet_meshes is not None

    def test_largest_dimention(self):
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape])
        assert pytest.approx(test_reactor.largest_dimension, rel=0.1 == 20)
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (30, 20)])
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape])
        assert pytest.approx(test_reactor.largest_dimension, rel=0.1 == 30)

    def test_shapes_and_components(self):
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])

        def incorrect_shapes_and_components():
            paramak.Reactor(test_shape)
        self.assertRaises(ValueError, incorrect_shapes_and_components)

    def test_graveyard_error(self):
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_reactor = paramak.Reactor([test_shape])

        def str_graveyard_offset():
            test_reactor.graveyard_offset = 'coucou'
        self.assertRaises(TypeError, str_graveyard_offset)

        def negative_graveyard_offset():
            test_reactor.graveyard_offset = -2
        self.assertRaises(ValueError, negative_graveyard_offset)

        def list_graveyard_offset():
            test_reactor.graveyard_offset = [1.2]
        self.assertRaises(TypeError, list_graveyard_offset)

    def test_compound_in_shapes(self):
        shape1 = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        shape2 = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        shape3 = paramak.Shape()
        shape3.solid = cq.Compound.makeCompound(
            [a.val() for a in [shape1.solid, shape2.solid]]
        )
        test_reactor = paramak.Reactor([shape3])
        assert test_reactor.solid is not None

    def test_adding_shape_with_None_stp_filename_physical_groups(self):
        """adds shapes to a Reactor object to check errors are raised
        correctly"""

        def test_stp_filename_None():
            """checks ValueError is raised when RotateStraightShapes with
            None as stp filenames are added"""

            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)], stp_filename="filename.stp"
            )
            test_shape2 = paramak.RotateSplineShape(
                points=[(0, 0), (0, 20), (20, 20)], stp_filename=None
            )
            test_shape.create_solid()
            my_reactor = paramak.Reactor([test_shape, test_shape2])
            my_reactor.export_physical_groups()

        self.assertRaises(ValueError, test_stp_filename_None)


if __name__ == "__main__":
    unittest.main()
