import os
import unittest
from pathlib import Path

import cadquery as cq
import pytest

import paramak


class TestReactor(unittest.TestCase):
    def setUp(self):
        self.test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)], name="test_shape")

        self.test_shape2 = paramak.ExtrudeStraightShape(
            points=[(100, 100), (50, 100), (50, 50)], distance=20, name="test_shape2"
        )

        test_shape_3 = paramak.PoloidalFieldCoilSet(
            heights=[2, 2], widths=[3, 3], center_points=[(50, -100), (50, 100)]
        )

        self.test_reactor = paramak.Reactor([self.test_shape])

        self.test_reactor_2 = paramak.Reactor([self.test_shape, self.test_shape2])

        # this reactor has a compound shape in the geometry
        self.test_reactor_3 = paramak.Reactor([self.test_shape, test_shape_3])

    def test_bounding_box(self):
        """checks the bounding box value"""

        bounding_box = self.test_reactor_2.bounding_box

        assert bounding_box[0][0] == pytest.approx(-20.0)
        assert bounding_box[0][1] == pytest.approx(-20.0)
        assert bounding_box[0][2] == pytest.approx(0.0)
        assert bounding_box[1][0] == pytest.approx(100.0)
        assert bounding_box[1][1] == pytest.approx(20.0)
        assert bounding_box[1][2] == pytest.approx(100.0)

    def test_reactor_export_stp_with_name_set_to_none(self):
        """Exports the reactor as separate files and as a single file"""

        def incorrect_name():
            self.test_shape.name = None

            paramak.Reactor([self.test_shape])

            self.test_reactor.export_stp()

        self.assertRaises(ValueError, incorrect_name)

    def test_reactor_export_stp(self):
        """Exports the reactor as separate files and as a single file"""
        os.system("rm *.stp")
        self.test_reactor_2.export_stp(filename=["RotateStraightShape.stp", "ExtrudeStraightShape.stp"])
        assert Path("RotateStraightShape.stp").is_file()
        assert Path("ExtrudeStraightShape.stp").is_file()
        self.test_reactor_2.export_stp(filename="single_file.stp", units="cm")
        assert Path("single_file.stp").is_file()

    def test_incorrect_graveyard_offset_too_small(self):
        def incorrect_graveyard_offset_too_small():
            """Set graveyard offset as a negative number which should raise an error"""

            self.test_reactor.make_graveyard(offset=-3)

        self.assertRaises(ValueError, incorrect_graveyard_offset_too_small)

    def test_incorrect_graveyard_offset_wrong_type(self):
        def incorrect_graveyard_offset_wrong_type():
            """Set graveyard offset as a string which should raise an error"""
            self.test_reactor.make_graveyard(offset="coucou")

        self.assertRaises(TypeError, incorrect_graveyard_offset_wrong_type)

    def test_largest_dimension_setting_and_getting_using_largest_shapes(self):
        """Makes a neutronics model and checks the default largest_dimension
        and that largest_dimension changes with largest_shapes"""

        assert pytest.approx(self.test_reactor.largest_dimension) == 20.0
        assert self.test_reactor_2.largest_dimension == 100.0

        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape2 = paramak.RotateStraightShape(points=[(0, 0), (0, 40), (40, 40)])

        test_reactor = paramak.Reactor([test_shape, test_shape2])
        assert pytest.approx(test_reactor.largest_dimension) == 40

    def test_make_sector_wedge(self):
        """Checks that the wedge is not made when rotation angle is 360"""
        sector_wedge = self.test_reactor.make_sector_wedge(height=100, radius=100, rotation_angle=360)
        assert sector_wedge is None

    def test_wrong_number_of_filenames(self):
        def test_stl_filename_list_length():
            test_shape = paramak.ExtrudeCircleShape(points=[(20, 20)], radius=10, distance=10)
            my_reactor = paramak.Reactor([test_shape])
            my_reactor.export_stl(["wrong.stl", "number_of.stl", "files.stl"])

        self.assertRaises(ValueError, test_stl_filename_list_length)

    def test_make_graveyard_accepts_offset_from_graveyard(self):
        """Creates a graveyard for a reactor and sets the graveyard_offset.
        Checks that the Reactor.graveyard property is set"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)],
        )
        test_shape2 = paramak.RotateSplineShape(
            points=[(0, 0), (0, 20), (20, 20)],
        )
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape, test_shape2])

        graveyard = test_reactor.make_graveyard(offset=101)
        assert graveyard.volume() > 0
        assert test_reactor.graveyard.volume() > 0

    def test_reactor_creation_with_default_properties(self):
        """creates a Reactor object and checks that it has no default properties"""

        test_reactor = paramak.Reactor([])

        assert test_reactor is not None

    def test_adding_component_to_reactor(self):
        """creates a Reactor object and checks that shapes can be added to it"""

        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([])
        assert len(test_reactor.shapes_and_components) == 0
        test_reactor = paramak.Reactor([test_shape])
        assert len(test_reactor.shapes_and_components) == 1

    def test_graveyard_exists(self):
        """creates a Reactor object with one shape and checks that a graveyard
        can be produced using the make_graveyard method"""

        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([test_shape])
        test_reactor.make_graveyard(size=100)

        assert isinstance(test_reactor.graveyard, paramak.Shape)

    def test_graveyard_exists_solid_is_none(self):
        """creates a Reactor object with one shape and checks that a graveyard
        can be produced using the make_graveyard method when the solid
        attribute of the shape is None"""

        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_shape.create_solid()
        test_reactor = paramak.Reactor([test_shape])
        test_reactor.shapes_and_components[0].solid = None
        test_reactor.make_graveyard(size=100)

        assert isinstance(test_reactor.graveyard, paramak.Shape)

    def test_export_graveyard(self):
        """creates a Reactor object with one shape and checks that a graveyard
        can be exported to a specified location using the make_graveyard method"""

        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        os.system("rm my_graveyard.stp")
        os.system("rm graveyard.stp")
        test_reactor = paramak.Reactor([test_shape])

        test_reactor.make_graveyard(size=100)
        test_reactor.graveyard.export_stp(filename="graveyard.stp")
        test_reactor.graveyard.export_stp(filename="my_graveyard.stp")
        test_reactor.graveyard.export_stp(filename="my_graveyard_without_ext.step")

        for filepath in [
            "graveyard.stp",
            "my_graveyard.stp",
            "my_graveyard_without_ext.step",
        ]:
            assert Path(filepath).exists() is True
            os.system("rm " + filepath)

        assert test_reactor.graveyard is not None
        assert test_reactor.graveyard.__class__.__name__ == "HollowCube"

    def test_make_graveyard_offset(self):
        """checks that the graveyard can be exported with the correct default parameters
        and that these parameters can be changed"""

        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        os.system("rm graveyard.stp")
        test_reactor = paramak.Reactor([test_shape])
        test_reactor.make_graveyard(offset=100)

        graveyard_volume_1 = test_reactor.graveyard.volume()

        test_reactor.make_graveyard(offset=50)
        assert test_reactor.graveyard.volume() < graveyard_volume_1
        graveyard_volume_2 = test_reactor.graveyard.volume()

        test_reactor.make_graveyard(offset=200)
        assert test_reactor.graveyard.volume() > graveyard_volume_1
        assert test_reactor.graveyard.volume() > graveyard_volume_2

    def test_exported_stp_files_exist(self):
        """creates a Reactor object with one shape and checks that a stp file
        of the reactor can be exported to a specified location using the export_stp
        method"""

        os.system("rm test_reactor/*.stp")
        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360

        os.system("rm test_reactor/test_shape.stp")
        os.system("rm test_reactor/graveyard.stp")

        test_reactor = paramak.Reactor([test_shape])

        test_reactor.export_stp("test_reactor/test_shape.stp")

        assert Path("test_reactor/test_shape.stp").exists() is True

    def test_exported_stl_files_exist(self):
        """creates a Reactor object with one shape and checks that a stl file
        of the reactor can be exported to a specified location using the
        export_stl method"""

        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        os.system("rm test_reactor/test_shape.stl")
        test_reactor = paramak.Reactor([test_shape])

        test_reactor.export_stl(filename="test_reactor/test_shape.stl")

        assert Path("test_reactor/test_shape.stl").exists() is True
        os.system("rm test_reactor/test_shape.stl")

    def test_reactor_export_stl_with_name_set_to_none(self):
        """Exports the reactor as separate files and as a single file"""

        def incorrect_name():
            self.test_shape.name = None

            paramak.Reactor([self.test_shape])

            self.test_reactor.export_stl()

        self.assertRaises(ValueError, incorrect_name)

    def test_exported_svg_files_exist(self):
        """Creates a Reactor object with one shape and checks that a svg file
        of the reactor can be exported to a specified location using the
        export_svg method."""

        os.system("rm test_svg_image.svg")

        self.test_reactor.export_svg("test_svg_image.svg")

        assert Path("test_svg_image.svg").exists() is True
        os.system("rm test_svg_image.svg")

    def test_exported_svg_files_exist_no_extension(self):
        """creates a Reactor object with one shape and checks that an svg file
        of the reactor can be exported to a specified location using the export_svg
        method"""

        os.system("rm test_svg_image.svg")

        self.test_reactor.export_svg("test_svg_image")

        assert Path("test_svg_image.svg").exists() is True
        os.system("rm test_svg_image.svg")

    def test_export_svg_options(self):
        """Exports the test reactor to an svg image and checks that a svg file
        can be exported with the various different export options"""

        os.system("rm *.svg")
        self.test_reactor.export_svg("r_width.svg", width=900)
        assert Path("r_width.svg").exists() is True
        self.test_reactor.export_svg("r_height.svg", height=900)
        assert Path("r_height.svg").exists() is True
        self.test_reactor.export_svg("r_marginLeft.svg", marginLeft=110)
        assert Path("r_marginLeft.svg").exists() is True
        self.test_reactor.export_svg("r_marginTop.svg", marginTop=110)
        assert Path("r_marginTop.svg").exists() is True
        self.test_reactor.export_svg("r_showAxes.svg", showAxes=True)
        assert Path("r_showAxes.svg").exists() is True
        self.test_reactor.export_svg("r_projectionDir.svg", projectionDir=(-1, -1, -1))
        assert Path("r_projectionDir.svg").exists() is True
        self.test_reactor.export_svg("r_strokeColor.svg", strokeColor=(42, 42, 42))
        assert Path("r_strokeColor.svg").exists() is True
        self.test_reactor.export_svg("r_hiddenColor.svg", hiddenColor=(42, 42, 42))
        assert Path("r_hiddenColor.svg").exists() is True
        self.test_reactor.export_svg("r_showHidden.svg", showHidden=False)
        assert Path("r_showHidden.svg").exists() is True
        self.test_reactor.export_svg("r_strokeWidth1.svg", strokeWidth=None)
        assert Path("r_strokeWidth1.svg").exists() is True
        self.test_reactor.export_svg("r_strokeWidth2.svg", strokeWidth=10)
        assert Path("r_strokeWidth2.svg").exists() is True

    def test_export_2d_image(self):
        """Creates a Reactor object and checks that a png file of the reactor
        with the correct filename can be exported using the export_2D_image
        method."""

        os.system("rm 2D_test_image.png")
        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape])
        returned_filename = test_reactor.export_2d_image(filename="2D_test_image.png")

        assert Path(returned_filename).exists() is True
        os.system("rm 2D_test_image.png")

    def test_export_2d_image_without_extension(self):
        """creates a Reactor object and checks that a png file of the reactor
        with the correct filename can be exported using the export_2d_image
        method"""

        os.system("rm 2d_test_image.png")
        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape])
        returned_filename = test_reactor.export_2d_image(filename="2d_test_image")

        assert Path(returned_filename).exists() is True
        os.system("rm 2d_test_image.png")

    def test_export_html(self):
        """Creates a Reactor object and checks that a html file of the reactor
        with the correct filename can be exported using the export_html
        method."""

        os.system("rm test_html.html")
        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape])
        test_reactor.export_html(filename="test_html.html")

        assert Path("test_html.html").exists() is True
        os.system("rm test_html.html")
        test_reactor.export_html(filename="test_html")

        assert Path("test_html.html").exists() is True
        os.system("rm test_html.html")

    def test_largest_dimension(self):
        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape])
        assert pytest.approx(test_reactor.largest_dimension, rel=0.1) == 20
        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (30, 20)])
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape])
        assert pytest.approx(test_reactor.largest_dimension, rel=0.1) == 30

    def test_shapes_and_components(self):
        """Attempts to make a reactor with a single shape instead of a list of
        shapes which should raise a ValueError"""

        def incorrect_shapes_and_components():
            test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
            paramak.Reactor(test_shape)

        self.assertRaises(ValueError, incorrect_shapes_and_components)

    def test_graveyard_size_setting_type_checking(self):
        """Attempts to make a reactor with a graveyard_size that is an float
        which should raise a ValueError"""

        def incorrect_graveyard_size_type():
            test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
            paramak.Reactor([test_shape], graveyard_size="coucou")

        self.assertRaises(TypeError, incorrect_graveyard_size_type)

    def test_graveyard_size_setting_magnitude_checking(self):
        """Attempts to make a reactor with a graveyard_size that is an int
        which should raise a ValueError"""

        def incorrect_graveyard_size_size():
            test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
            test_reactor = paramak.Reactor([test_shape])
            test_reactor.make_graveyard(size=-10)

        self.assertRaises(ValueError, incorrect_graveyard_size_size)

    def test_graveyard_offset_setting_type_checking(self):
        """Attempts to make a reactor with a graveyard offset that is an float
        which should raise a ValueError"""

        def incorrect_graveyard_offset_type():
            test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
            test_reactor = paramak.Reactor([test_shape])
            test_reactor.make_graveyard(offset="coucou")

        self.assertRaises(TypeError, incorrect_graveyard_offset_type)

    def test_graveyard_offset_setting_magnitude_checking(self):
        """Attempts to make a reactor with a graveyard offset that is an int
        which should raise a ValueError"""

        def incorrect_graveyard_offset_size():
            test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
            test_reactor = paramak.Reactor([test_shape])
            test_reactor.make_graveyard(size=-10)

        self.assertRaises(ValueError, incorrect_graveyard_offset_size)

    def test_graveyard_error(self):
        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_reactor = paramak.Reactor([test_shape])

        def str_graveyard_offset():
            test_reactor.make_graveyard(offset="coucou")

        self.assertRaises(TypeError, str_graveyard_offset)

        def negative_graveyard_offset():
            test_reactor.make_graveyard(offset=-2)

        self.assertRaises(ValueError, negative_graveyard_offset)

        def list_graveyard_offset():
            test_reactor.make_graveyard(offset=[1.2])

        self.assertRaises(TypeError, list_graveyard_offset)

    def test_compound_in_shapes(self):
        shape1 = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        shape2 = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        shape3 = paramak.Shape()
        shape3.solid = cq.Compound.makeCompound([a.val() for a in [shape1.solid, shape2.solid]])
        test_reactor = paramak.Reactor([shape3])
        assert test_reactor.solid is not None

    def test_sector_wedge_with_360_returns_none(self):
        """Tries to make a sector wedge with full 360 degree rotation and checks
        that None is returned"""

        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        my_reactor = paramak.Reactor([test_shape])
        assert my_reactor.make_sector_wedge(rotation_angle=360) is None

    def test_reactor_volume(self):
        """Checks the types returned by the .volume method are correct"""

        assert isinstance(self.test_reactor.volume(), list)
        assert isinstance(self.test_reactor.volume(), list)
        assert isinstance(self.test_reactor.volume()[0], float)
        assert isinstance(self.test_reactor_2.volume()[0], float)
        assert isinstance(self.test_reactor_2.volume()[1], float)
        assert len(self.test_reactor.volume()) == 1
        assert len(self.test_reactor_2.volume()) == 2
        assert sum(self.test_reactor_2.volume()) > sum(self.test_reactor.volume())
        assert self.test_reactor_2.volume()[0] == self.test_reactor.volume()[0]

    def test_reactor_volume_spliting_compounds(self):
        """Checks the volumes returned by the .volume method with splitting of
        compounds set to True are correct"""

        assert isinstance(self.test_reactor_3.volume(split_compounds=True), list)
        assert isinstance(self.test_reactor_3.volume(split_compounds=False), list)
        assert isinstance(self.test_reactor_3.volume(split_compounds=True)[0], list)
        assert isinstance(self.test_reactor_3.volume(split_compounds=True)[1], list)
        assert isinstance(self.test_reactor_3.volume(split_compounds=False)[0], float)
        assert isinstance(self.test_reactor_3.volume(split_compounds=False)[1], float)
        assert isinstance(self.test_reactor_3.volume(split_compounds=True)[1][0], float)
        assert isinstance(self.test_reactor_3.volume(split_compounds=True)[1][1], float)
        assert len(self.test_reactor_3.volume(split_compounds=True)) == 2
        assert len(self.test_reactor_3.volume(split_compounds=True)[1]) == 2

        vol_1 = self.test_reactor_3.volume(split_compounds=True)[1][0]
        vol_2 = self.test_reactor_3.volume(split_compounds=True)[1][1]
        assert vol_1 == vol_2
        vol_3 = self.test_reactor_3.volume(split_compounds=False)[1]
        assert pytest.approx(vol_3) == vol_1 + vol_2

    def test_reactor_names(self):
        "checks that the names attribute returns the expected results"
        assert self.test_reactor_2.name == ["test_shape", "test_shape2"]


if __name__ == "__main__":
    unittest.main()
