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


if __name__ == "__main__":
    unittest.main()
