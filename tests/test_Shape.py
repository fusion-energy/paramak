
import os
import unittest
from pathlib import Path

import pytest

from paramak import Shape

# test command
# pytest tests -v --cov=paramak --cov-report term --cov-report html:htmlcov --cov-report xml --junitxml=test-reports/junit.xml
# from head paramak directory

# R: the test functions/methods should all have docstrings to explain what
#   is being tested and the expected result


class test_object_properties(unittest.TestCase):
    def test_shape_default_properties(self):
        """creates a Shape object and checks the points attribute has a \
                default of None"""

        test_shape = Shape()

        assert test_shape.points is None

    def test_incorrect_points(self):

        test_shape = Shape()

        def incorrect_points_end_point_is_start_point():
            """checks a ValueError is raised when the start and end \
                        points are not the same"""

            test_shape.points = [(0, 200), (200, 100), (0, 0), (0, 200)]

        self.assertRaises(ValueError, incorrect_points_end_point_is_start_point)

        def incorrect_points_missing_z_value():
            """checks a ValueError is raised when a point is missing \
                        a z value"""

            test_shape.points = [(0, 200), (200), (0, 0), (0, 50)]

        self.assertRaises(ValueError, incorrect_points_missing_z_value)

    def test_create_limits(self):
        """checks that create_limits() function returns the expected values for \
                x_min, x_max, z_min and z_max"""

        test_shape = Shape()

        test_shape.points = [
            (0, 0),
            (0, 10),
            (0, 20),
            (10, 20),
            (20, 20),
            (20, 10),
            (20, 0),
            (10, 0)
        ]

        assert test_shape.create_limits() == (0.0, 20.0, 0.0, 20.0)

    def test_export_2d_image(self):
        """checks that export_2d_image() exports png files with the \
                correct suffix"""

        test_shape = Shape()
        test_shape.points = [(0, 0), (0, 20), (20, 20), (20, 0)]
        os.system("rm filename.png")
        test_shape.export_2d_image("filename")
        assert Path("filename.png").exists() is True
        os.system("rm filename.png")
        test_shape.export_2d_image("filename.png")
        assert Path("filename.png").exists() is True
        os.system("rm filename.png")

    def test_export_html_filename(self):
        """checks that export_html() exports html files with the \
                correct suffix"""

        test_shape = Shape()
        test_shape.points = [(0, 0), (0, 20), (20, 20), (20, 0)]
        os.system("rm filename.html")
        test_shape.export_html("filename")
        assert Path("filename.html").exists() is True
        os.system("rm filename.html")
        test_shape.export_html("filename.html")
        assert Path("filename.html").exists() is True
        os.system("rm filename.html")


if __name__ == "__main__":
    unittest.main()
