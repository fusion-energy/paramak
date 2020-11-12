import os
import unittest
from pathlib import Path

import pytest

from paramak import SweepSplineShape, RotateStraightShape


class test_object_properties(unittest.TestCase):
    def test_solid_construction(self):
        """checks that a SweepSplineShape solid can be created"""

        test_shape = SweepSplineShape(
            points=[
                (-20, 20),
                (20, 20),
                (20, -20),
                (-20, -20)
            ],
            path_points=[
                (50, 0),
                (20, 200),
                (50, 400)
            ]
        )
        test_shape.create_solid()

        assert test_shape.solid is not None

    def test_relative_shape_volume(self):
        """creates two SweepSplineShapes and checks that their relative volumes
        are correct"""

        test_shape_1 = SweepSplineShape(
            points=[
                (-20, 20),
                (20, 20),
                (20, -20),
                (-20, -20)
            ],
            path_points=[
                (50, 0),
                (30, 50),
                (60, 100),
                (50, 150)
            ]
        )
        test_shape_1.create_solid()

        test_shape_2 = SweepSplineShape(
            points=[
                (-10, 10),
                (10, 10),
                (10, -10),
                (-10, -10)
            ],
            path_points=[
                (50, 0),
                (30, 50),
                (60, 100),
                (50, 150)
            ]
        )
        test_shape_2.create_solid()

        assert test_shape_1.volume == pytest.approx(
            test_shape_2.volume * 4, abs=1)

    def test_iterable_azimuthal_placement(self):
        """checks that swept solids can be placed at multiple azimuth placement angles"""

        test_shape = SweepSplineShape(
            points=[
                (-10, 10),
                (10, 10),
                (10, -10),
                (-10, -10)
            ],
            path_points=[
                (50, 0),
                (30, 50),
                (60, 100),
                (50, 150)
            ]
        )
        test_shape.create_solid()

        test_volume = test_shape.volume

        test_shape.azimuth_placement_angle = [0, 90, 180, 270]

        assert test_shape.volume == pytest.approx(test_volume * 4, rel=0.01)

    def test_workplane_path_workplane_error_raises(self):
        """checks that errors are raised when disallowed workplane and path_workplane
        combinations are used"""

        def workplane_and_path_workplane_equal():
            test_shape = SweepSplineShape(
                points=[(-20, 20), (20, 20), (20, -20), (-20, -20)],
                path_points=[(50, 0), (30, 50), (60, 100), (50, 150)],
                workplane="XZ",
                path_workplane="XZ"
            )

        def invalid_relative_workplane_and_path_workplane():
            test_shape = SweepSplineShape(
                points=[(-20, 20), (20, 20), (20, -20), (-20, -20)],
                path_points=[(50, 0), (30, 50), (60, 100), (50, 150)],
                workplane="XZ",
                path_workplane="YZ"
            )

        self.assertRaises(ValueError, workplane_and_path_workplane_equal)
        self.assertRaises(
            ValueError,
            invalid_relative_workplane_and_path_workplane)

    def test_workplane_opposite_direction(self):
        """Checks that a solid can be created with workplane XZ and path_workplane XY"""

        test_shape = SweepSplineShape(
            points=[(-10, 10), (10, 10), (10, -10), (-10, -10)],
            path_points=[(50, 0), (30, 50), (50, 100)],
            workplane="XZ",
            path_workplane="XY"
        )
        assert test_shape.solid is not None

    def test_force_cross_section(self):
        """Checks that a solid with the same cross-section at each path_point is created
        when force_cross_section = True"""

        test_shape = SweepSplineShape(
            points=[(-10, 10), (10, 10), (10, -10), (-10, -10)],
            path_points=[(50, 0), (30, 50), (50, 100), (70, 150)],
            workplane="XY",
            path_workplane="XZ",
            force_cross_section=True,
        )
        
        test_area = round(min(test_shape.areas))

        assert test_shape.areas.count(pytest.approx(test_area, rel=0.01)) == 2

        cutting_shape = RotateStraightShape(
            points=[(0, 50), (0, 200), (100, 200), (100, 50)]
        )
        test_shape.cut = cutting_shape

        assert test_shape.areas.count(pytest.approx(test_area, rel=0.01)) == 2

        cutting_shape.points = [(0, 100), (0, 200), (100, 200), (100, 100)]
        test_shape.cut = cutting_shape

        assert test_shape.areas.count(pytest.approx(test_area, rel=0.01)) == 2

    def test_force_cross_section_volume(self):
        """Checks that when force_cross_section = True, a solid is created which has 
        a larger volume than a solid created when force_cross_section = False"""

        test_shape = SweepSplineShape(
            points=[(-10, 10), (10, 10), (10, -10), (-10, -10)],
            path_points=[(50, 0), (30, 50), (50, 100)],
            force_cross_section=False
        )
        test_volume = test_shape.volume
        test_shape.force_cross_section=True
        assert test_shape.volume > test_volume

    def test_surface_count(self):
        """Creates a solid and checks that it has the correct number of surfaces"""

        test_shape = SweepSplineShape(
            points=[(-10, 10), (10, 10), (10, -10), (-10, -10)],
            path_points=[(50, 0), (30, 50), (50, 100)]
        )

        assert len(test_shape.areas) == 3



if __name__ == "__main__":
    unittest.main()
