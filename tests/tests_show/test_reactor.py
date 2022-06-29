import os
import unittest
from pathlib import Path

import paramak


class TestReactor(unittest.TestCase):
    """Tests the show attribute of the Reactor class which requires
    jupyter_cadquery"""

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

    def test_export_3d_html(self):
        """Checks the 3d html file is exported by the export_html_3d method
        with the correct filename"""

        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)])
        test_shape.rotation_angle = 360
        test_reactor = paramak.Reactor([test_shape])

        os.system("rm filename.html")
        filename = test_reactor.export_html_3d("filename.html")
        if filename is not None:
            assert Path("filename.html").exists() is True

    def test_show_runs_without_error(self):
        """checks that the jupyter notebook (with cadquery addition) runs
        without error."""

        self.test_reactor.show()

    def test_show_runs_without_error_when_names_are_set(self):
        """checks that the jupyter notebook (with cadquery addition) runs
        without error even when the .name property is set"""

        self.test_reactor.shapes_and_components[0].name = "test"
        self.test_reactor.show()

    def test_show_runs_without_error_when_compounds_are_used(self):
        """checks that the jupyter notebook (with cadquery addition) runs
        without error even when the .name property is set"""

        test_shape = paramak.PoloidalFieldCoilCaseSet(
            heights=[10, 20],
            widths=[10, 20],
            casing_thicknesses=10,
            center_points=[(100, 200), (400, 400)],
            name="test name",
        )

        test_reactor = paramak.Reactor([test_shape])
        test_reactor.show()


if __name__ == "__main__":
    unittest.main()
