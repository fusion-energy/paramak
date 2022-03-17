import os
import unittest
from pathlib import Path

import paramak


class TestShape(unittest.TestCase):
    """Tests the show attribute of the Shape class which requires
    jupyter_cadquery"""

    def setUp(self):

        self.my_shape = paramak.CenterColumnShieldHyperbola(
            height=500,
            inner_radius=50,
            mid_radius=60,
            outer_radius=100,
        )

        self.test_rotate_mixed_shape = paramak.RotateMixedShape(
            rotation_angle=1,
            points=[
                (100, 0, "straight"),
                (200, 0, "circle"),
                (250, 50, "circle"),
                (200, 100, "straight"),
                (150, 100, "straight"),
                (140, 75, "straight"),
                (110, 45, "straight"),
            ],
        )
        self.test_extrude_mixed_shape = paramak.ExtrudeMixedShape(
            distance=1,
            points=[
                (100, 0, "straight"),
                (200, 0, "circle"),
                (250, 50, "circle"),
                (200, 100, "straight"),
                (150, 100, "straight"),
                (140, 75, "straight"),
                (110, 45, "straight"),
            ],
        )

    def test_show_runs_without_error(self):
        """checks that the jupyter notebook (with cadquery addition) runs
        without error."""

        self.test_extrude_mixed_shape.show()

    def test_export_3d_html(self):
        """Checks the 3d html file is exported by the export_html_3d method
        with the correct filename"""

        test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20), (20, 0)], rotation_angle=360)

        os.system("rm filename.html")
        filename = test_shape.export_html_3d("filename.html")
        if filename is not None:
            assert Path("filename.html").exists() is True


if __name__ == "__main__":
    unittest.main()
