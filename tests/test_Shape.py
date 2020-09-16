import os
import unittest
from pathlib import Path

import pytest

import paramak

# test command
# pytest tests -v --cov=paramak --cov-report term --cov-report html:htmlcov --cov-report xml --junitxml=test-reports/junit.xml
# from head paramak directory


class test_object_properties(unittest.TestCase):
    def test_shape_default_properties(self):
        """creates a Shape object and checks that the points attribute has
        a default of None"""

        test_shape = paramak.Shape()

        assert test_shape.points is None

    def test_incorrect_workplane(self):
        """creates Shape object with incorrect workplane and checks ValueError
        is raised"""

        test_shape = paramak.Shape()

        def incorrect_workplane():
            """creates Shape object with unacceptable workplane"""

            test_shape.workplane = "ZY"

        self.assertRaises(ValueError, incorrect_workplane)

    def test_incorrect_points(self):
        """creates Shape objects and checks errors are raised correctly when
        specifying points"""

        test_shape = paramak.Shape()

        def incorrect_points_end_point_is_start_point():
            """checks ValueError is raised when the start and end points are
            the same"""

            test_shape.points = [(0, 200), (200, 100), (0, 0), (0, 200)]

        self.assertRaises(
            ValueError,
            incorrect_points_end_point_is_start_point)

        def incorrect_points_missing_z_value():
            """checks ValueError is raised when a point is missing a z value"""

            test_shape.points = [(0, 200), (200), (0, 0), (0, 50)]

        self.assertRaises(ValueError, incorrect_points_missing_z_value)

        def incorrect_points_not_a_list():
            """checks ValueError is raised when the points are not a list"""

            test_shape.points = (0, 0), (0, 20), (20, 20), (20, 0)

        self.assertRaises(ValueError, incorrect_points_not_a_list)

        def incorrect_points_wrong_number_of_entries():
            """checks ValueError is raised when individual points dont have 2 or
            3 entries"""

            test_shape.points = [(0, 0), (0, 20), (20, 20, 20, 20)]

        self.assertRaises(ValueError, incorrect_points_wrong_number_of_entries)

        def incorrect_x_point_value_type():
            """checks ValueError is raised when X point is not a number"""

            test_shape.points = [("string", 0), (0, 20), (20, 20)]

        self.assertRaises(ValueError, incorrect_x_point_value_type)

        def incorrect_y_point_value_type():
            """checks ValueError is raised when Y point is not a number"""

            test_shape.points = [(0, "string"), (0, 20), (20, 20)]

        self.assertRaises(ValueError, incorrect_y_point_value_type)

    def test_create_limits(self):
        """creates a Shape object and checks that the create_limits function
        returns the expected values for x_min, x_max, z_min and z_max"""

        test_shape = paramak.Shape()

        test_shape.points = [
            (0, 0),
            (0, 10),
            (0, 20),
            (10, 20),
            (20, 20),
            (20, 10),
            (20, 0),
            (10, 0),
        ]

        assert test_shape.create_limits() == (0.0, 20.0, 0.0, 20.0)

    def test_export_2d_image(self):
        """creates a Shape object and checks that a png file of the object with
        the correct suffix can be exported using the export_2d_image method"""

        test_shape = paramak.Shape()
        test_shape.points = [(0, 0), (0, 20), (20, 20), (20, 0)]
        os.system("rm filename.png")
        test_shape.export_2d_image("filename")
        assert Path("filename.png").exists() is True
        os.system("rm filename.png")
        test_shape.export_2d_image("filename.png")
        assert Path("filename.png").exists() is True
        os.system("rm filename.png")

    def test_initial_solid_construction(self):
        """creates a shape and checks that a cadquery solid with a unique hash value
        is created when .solid is called"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], rotation_angle=360
        )

        assert test_shape.hash_value is None
        assert test_shape.solid is not None
        assert type(test_shape.solid).__name__ == "Workplane"
        assert test_shape.hash_value is not None

    def test_solid_return(self):
        """checks that the same cadquery solid with the same unique has value is returned when
        shape.solid is called again after no changs have been made to the Shape"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], rotation_angle=360
        )

        assert test_shape.solid is not None
        initial_hash_value = test_shape.hash_value
        assert test_shape.solid is not None
        assert initial_hash_value == test_shape.hash_value

    def test_conditional_solid_reconstruction(self):
        """checks that a new cadquery solid with a new unique hash value is constructed when
        shape.solid is called after changes to the Shape have been made"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], rotation_angle=360
        )

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.rotation_angle = 180

        assert test_shape.solid is not None
        assert test_shape.hash_value is not None
        assert initial_hash_value != test_shape.hash_value

    def test_hash_value_update(self):
        """checks that the hash value of a Shape is not updated until a new cadquery solid has
        been created"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20)], rotation_angle=360
        )
        test_shape.solid
        assert test_shape.hash_value is not None
        initial_hash_value = test_shape.hash_value

        test_shape.rotation_angle = 180
        assert test_shape.hash_value == initial_hash_value
        test_shape.solid
        assert test_shape.hash_value != initial_hash_value

    def test_material_tag_warning(self):
        """checks that a warning is raised when a Shape has a material tag > 28 characters"""

        test_shape = paramak.Shape()

        def warning_material_tag():

            test_shape.material_tag = "abcdefghijklmnopqrstuvwxyz12345"

        self.assertWarns(UserWarning, warning_material_tag)

    def test_invalid_material_tag(self):
        """checks a ValueError is raised when a Shape has an invalid material tag"""

        test_shape = paramak.Shape()

        def invalid_material_tag():

            test_shape.material_tag = 123

        self.assertRaises(ValueError, invalid_material_tag)

    def test_export_html(self):
        """checks a plotly figure of the Shape is exported by the export_html method with
        the correct filename with RGB and RGBA colors"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)], rotation_angle=360
        )

        os.system("rm filename.html")
        test_shape.export_html('filename')
        assert Path("filename.html").exists() is True
        os.system("rm filename.html")
        test_shape.color = (1, 0, 0, 0.5)
        test_shape.export_html('filename')
        assert Path("filename.html").exists() is True
        os.system("rm filename.html")

    def test_invalid_stp_filename(self):
        """checks ValueError is raised when invalid stp filenames are used"""

        def invalid_filename_suffix():

            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stp_filename="filename.invalid_suffix"
            )

        self.assertRaises(ValueError, invalid_filename_suffix)

        def invalid_filename_type():

            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stp_filename=123456
            )

        self.assertRaises(ValueError, invalid_filename_type)

    def test_invalid_stl_filename(self):
        """checks ValueError is raised when invalid stl filenames are used"""

        def invalid_filename_suffix():

            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stl_filename="filename.invalid_suffix"
            )

        self.assertRaises(ValueError, invalid_filename_suffix)

        def invalid_filename_type():

            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                stl_filename=123456
            )

        self.assertRaises(ValueError, invalid_filename_type)

    def test_invalid_color(self):
        """checks ValueError is raised when invalid colors are used"""

        def invalid_color_type():

            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                color=255
            )

        self.assertRaises(ValueError, invalid_color_type)

        def invalid_color_length():

            test_shape = paramak.RotateStraightShape(
                points=[(0, 0), (0, 20), (20, 20)],
                color=(255, 255, 255, 1, 1)
            )

        self.assertRaises(ValueError, invalid_color_length)


if __name__ == "__main__":
    unittest.main()
