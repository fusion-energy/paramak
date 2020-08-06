
import os
from pathlib import Path
import unittest
import json

import paramak

class test_object_properties(unittest.TestCase):

    def test_export_h5m(self):
        """Makes two shapes and adds them to a reactor for export as h5m files"""
        os.system('rm small_dagmc.h5m')
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat1')
        test_shape2= paramak.RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat2')
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape, test_shape2])      
        test_reactor.export_h5m(filename='small_dagmc.h5m', tolerance=0.01)
        test_reactor.export_h5m(filename='small_dagmc_without_graveyard.h5m', tolerance=0.01, skip_graveyard=True)
        test_reactor.export_h5m(filename='large_dagmc.h5m', tolerance=0.001)

        assert Path("small_dagmc.html").exists() is True
        assert Path("small_dagmc_with_graveyard.html").exists() is True
        assert Path("large_dagmc.html").exists() is True
        assert Path("large_dagmc.html").stat().st_size > Path("small_dagmc.html").stat().st_size
        assert Path("small_dagmc_without_graveyard.html").stat().st_size < Path("small_dagmc.html").stat().st_size


    def test_adding_shape_with_material_tag_to_reactor(self):
        """adds a shape to the reactor and checks that the material_tag
        property works as designed"""
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat1')
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([test_shape])
        assert len(test_reactor.material_tags) == 1
        assert test_reactor.material_tags[0] == 'mat1'

    def test_adding_multiple_shapes_with_material_tag_to_reactor(self):
        """adds a shape to the reactor and checks that the material_tag
        property works as designed"""
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat1')
        test_shape2= paramak.RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20)],
            material_tag='mat2')
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([test_shape, test_shape2])
        assert len(test_reactor.material_tags) == 2
        assert test_reactor.material_tags[0] == 'mat1'
        assert test_reactor.material_tags[1] == 'mat2'

    def test_adding_shape_with_stp_filename_to_reactor(self):
        """adds a shape to the reactor and checks that the stp_filename
        property works as designed"""
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            stp_filename='filename.stp')
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([test_shape])
        assert len(test_reactor.stp_filenames) == 1
        assert test_reactor.stp_filenames[0] == 'filename.stp'


    def test_adding_multiple_shape_with_stp_filename_to_reactor(self):
        """adds a shape to the reactor and checks that the stp_filename
        property works as designed"""
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            stp_filename='filename.stp')
        test_shape2 = paramak.RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20)],
            stp_filename='filename2.stp')
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([test_shape,test_shape2])
        assert len(test_reactor.stp_filenames) == 2
        assert test_reactor.stp_filenames[0] == 'filename.stp'
        assert test_reactor.stp_filenames[1] == 'filename2.stp'

    def test_adding_shape_with_duplicate_stp_filename_to_reactor(self):
        """creates reactor and addes to shapes with the same stp filename"""

        def test_stp_filename_duplication():
            """checks ValueError is raised when a duplicate filename is added"""
            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stp_filename='filename.stp')
            test_shape2 = paramak.RotateSplineShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stp_filename='filename.stp')
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            paramak.Reactor([test_shape, test_shape2])

        self.assertRaises(ValueError, test_stp_filename_duplication)  

    def test_adding_shape_with_duplicate_stl_filename_to_reactor(self):
        """creates reactor and addes to shapes with the same stl filename"""

        def test_stl_filename_duplication_rotate_straight():
            """checks ValueError is raised when a duplicate filename is added"""
            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stl_filename='filename.stl')
            test_shape2 = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stl_filename='filename.stl')
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            paramak.Reactor([test_shape, test_shape2])

        self.assertRaises(ValueError, test_stl_filename_duplication_rotate_straight)  

        def test_stl_filename_duplication_rotate_spline():
            """checks ValueError is raised when a duplicate filename is added"""
            test_shape = paramak.RotateSplineShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stl_filename='filename.stl')
            test_shape2 = paramak.RotateSplineShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stl_filename='filename.stl')
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            paramak.Reactor([test_shape, test_shape2])

        self.assertRaises(ValueError, test_stl_filename_duplication_rotate_spline)  

        def test_stl_filename_duplication_rotate_mixed():
            """checks ValueError is raised when a duplicate filename is added"""
            test_shape = paramak.RotateMixedShape(
                points=[(0, 0, 'straight'), (0, 20, 'straight'), (20, 20, 'straight')],
                stl_filename='filename.stl')
            test_shape2 = paramak.RotateMixedShape(
                points=[(0, 0, 'straight'), (0, 20, 'straight'), (20, 20, 'straight')],
                stl_filename='filename.stl')
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            paramak.Reactor([test_shape, test_shape2])

        self.assertRaises(ValueError, test_stl_filename_duplication_rotate_mixed)

        def test_stl_filename_duplication_Rotate_Circle():
            """checks ValueError is raised when a duplicate filename is added"""
            test_shape = paramak.RotateCircleShape(
                points=[(20, 20)],
                radius=10,
                rotation_angle=180,
                stl_filename='filename.stl')
            test_shape2 = paramak.RotateCircleShape(
                points=[(20, 20)],
                radius=10,
                rotation_angle=180,
                stl_filename='filename.stl')
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            paramak.Reactor([test_shape, test_shape2])

        self.assertRaises(ValueError, test_stl_filename_duplication_Rotate_Circle)  

        def test_stl_filename_duplication_Extrude_straight():
            """checks ValueError is raised when a duplicate filename is added"""
            test_shape = paramak.ExtrudeStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                distance=10,
                stl_filename='filename.stl')
            test_shape2 = paramak.ExtrudeStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                distance=10,
                stl_filename='filename.stl')
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            paramak.Reactor([test_shape, test_shape2])

        self.assertRaises(ValueError, test_stl_filename_duplication_Extrude_straight)  

        def test_stl_filename_duplication_Extrude_spline():
            """checks ValueError is raised when a duplicate filename is added"""
            test_shape = paramak.ExtrudeSplineShape(
                points=[(0, 0), (0, 20), (20, 20)],
                distance=10,
                stl_filename='filename.stl')
            test_shape2 = paramak.ExtrudeSplineShape(
                points=[(0, 0), (0, 20), (20, 20)],
                distance=10,
                stl_filename='filename.stl')
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            paramak.Reactor([test_shape, test_shape2])

        self.assertRaises(ValueError, test_stl_filename_duplication_Extrude_spline)  

        def test_stl_filename_duplication_Extrude_mixed():
            """checks ValueError is raised when a duplicate filename is added"""
            test_shape = paramak.ExtrudeMixedShape(
                points=[(0, 0, 'straight'), (0, 20, 'straight'), (20, 20, 'straight')],
                distance=10,
                stl_filename='filename.stl')
            test_shape2 = paramak.ExtrudeMixedShape(
                points=[(0, 0, 'straight'), (0, 20, 'straight'), (20, 20, 'straight')],
                distance=10,
                stl_filename='filename.stl')
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            paramak.Reactor([test_shape, test_shape2])

        self.assertRaises(ValueError, test_stl_filename_duplication_Extrude_mixed)  

        def test_stl_filename_duplication_Extrude_Circle():
            """checks ValueError is raised when a duplicate filename is added"""
            test_shape = paramak.ExtrudeCircleShape(
                points=[(20, 20)],
                radius=10,
                distance=10,
                stl_filename='filename.stl')
            test_shape2 = paramak.ExtrudeCircleShape(
                points=[(20, 20)],
                radius=10,
                distance=10,
                stl_filename='filename.stl')
            test_shape.rotation_angle = 360
            test_shape.create_solid()
            paramak.Reactor([test_shape, test_shape2])

        self.assertRaises(ValueError, test_stl_filename_duplication_Extrude_Circle)  


    def test_reactor_creation_with_default_properties(self):
        """creates a Reactor object and checks that it has \
                no default properties"""

        test_reactor = paramak.Reactor([])

        assert test_reactor is not None

    def test_adding_component_to_reactor(self):
        """creates a Reactor object and checks that shapes \
                can be added to it"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([])
        assert len(test_reactor.shapes_and_components) == 0
        test_reactor = paramak.Reactor([test_shape])
        assert len(test_reactor.shapes_and_components) == 1

    def test_Graveyard_exists(self):
        """checks that make_graveyard() creates a graveyard \
                using the shapes in the Reactor object"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([test_shape])
        test_reactor.make_graveyard()

        assert type(test_reactor.graveyard) == paramak.Shape

    def test_exported_graveyard_creates_stp_file(self):
        """checks that export_graveyard() creates stp file in the \
                specified location"""

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

    def test_exported_stp_files_exist(self):
        """checks that export_stp() creates stp file in the \
                specified location"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        os.system("rm test_reactor/test_shape.stp")
        os.system("rm test_reactor/Graveyard.stp")
        test_shape.stp_filename = "test_shape.stp"
        test_reactor = paramak.Reactor([test_shape])

        test_reactor.export_stp(output_folder="test_reactor")

        for filepath in ["test_reactor/test_shape.stp", "test_reactor/Graveyard.stp"]:
            assert Path(filepath).exists() is True
            os.system("rm " + filepath)

    def test_exported_stl_files_exist(self):
        """checks that export_stl() creates stl file in the \
                specified location"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        os.system("rm test_reactor/test_shape.stl")
        os.system("rm test_reactor/Graveyard.stl")
        test_shape.stl_filename = "test_shape.stl"
        test_reactor = paramak.Reactor([test_shape])

        test_reactor.export_stl(output_folder="test_reactor")

        for filepath in ["test_reactor/test_shape.stl", "test_reactor/Graveyard.stl"]:
            assert Path(filepath).exists() is True
            os.system("rm " + filepath)

    def test_exported_svg_files_exist(self):
        """checks that export_stp() creates stp file in the \
                specified location"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        os.system("rm test_svg_image.svg")
        test_reactor = paramak.Reactor([test_shape])

        test_reactor.export_svg("test_svg_image.svg")

        assert Path("test_svg_image.svg").exists() is True
        os.system("rm test_svg_image.svg")

    def test_neutronics_desscription(self):
        def test_neutronics_description_without_material_tag():
            """checks that a ValueError is raised when the neutronics description \
                        is exported without material_tag"""

            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)])
            test_shape.rotation_angle = 360
            test_shape.stp_filename = "test.stp"
            test_reactor = paramak.Reactor([test_shape])
            neutronics_description = test_reactor.neutronics_description()

        self.assertRaises(ValueError, test_neutronics_description_without_material_tag)

        def test_neutronics_description_without_stp_filename():
            """checks that a ValueError is raised when the neutronics description \
                        is exported without stp_filename"""

            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)])
            test_shape.rotation_angle = 360
            test_shape.material_tag = "test_material"
            test_shape.stp_filename = None
            test_reactor = paramak.Reactor([test_shape])
            neutronics_description = test_reactor.neutronics_description()

        self.assertRaises(ValueError, test_neutronics_description_without_stp_filename)

    def test_neutronics_description_without_plasma(self):
        """checks that the neutronics description is exported with correct \
                material_tag and stp_filename"""

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
        """checks that the neutronics description is exported to a json file with \
                the correct material name and stp_filename"""

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
        """checks that the neutronics description is exported to a json file with \
                the correct entries (including the optional plasma)"""

        os.system("rm manifest_test.json")

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            rotation_angle = 360,
            material_tag = "test_material",
            stp_filename = "test.stp")
        test_shape.tet_mesh = "size 60"
        test_plasma = paramak.Plasma(major_radius=500,
                                     minor_radius=100,
                                     stp_filename='plasma.stp',
                                     material_tag='DT_plasma')
        test_reactor = paramak.Reactor([test_shape, test_plasma])
        returned_filename = test_reactor.export_neutronics_description(include_plasma=True)
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
        """checks that the neutronics description is exported to a json file with \
                the correct entries (the optional plasma is not included)"""

        os.system("rm manifest_test.json")

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
            rotation_angle = 360,
            material_tag = "test_material",
            stp_filename = "test.stp")
        test_shape.tet_mesh = "size 60"
        test_plasma = paramak.Plasma(major_radius=500,
                                     minor_radius=100)
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

    def test_export_2d_image(self):
        """checks that export_2d_image() exports a png file with \
                the correct filename"""

        os.system("rm 2d_test_image.png")
        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape])
        returned_filename = test_reactor.export_2d_image(filename="2d_test_image.png")

        assert Path(returned_filename).exists() is True
        os.system("rm 2d_test_image.png")

    def test_export_html(self):
        """checks that export_html() exports a html file with \
                the correct filename"""

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

if __name__ == "__main__":
    unittest.main()
