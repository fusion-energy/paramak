
import unittest

import numpy as np
import paramak


class TestCuttingWedgeFS(unittest.TestCase):

    def test_shape_construction_and_volume(self):
        """Makes cutting cylinders from shapes and checks the
        volume of the cutter shape is larger than the shape it
        encompasses."""

        hoop_shape = paramak.PoloidalFieldCoil(height=20,
                                               width=20,
                                               center_point=(50, 200),
                                               rotation_angle=180)

        cutter = paramak.CuttingWedgeFS(
            shape=hoop_shape,
            azimuth_placement_angle=0,
        )

        assert cutter.volume > hoop_shape.volume

    def test_error(self):
        """Checks that errors are raised when invalid arguments are set
        """
        shape = paramak.ExtrudeStraightShape(
            1,
            points=[(0, 0), (0, 1), (1, 1)],
            rotation_angle=180
        )
        cutter = paramak.CuttingWedgeFS(
            shape=shape,
            azimuth_placement_angle=0,
        )

        def incorrect_rotation_angle():
            shape.rotation_angle = 360
            print(cutter.shape.rotation_angle)
            cutter.solid

        def incorrect_shape_points():
            shape.rotation_angle = 180
            cutter.shape.points = [(0, 0, 'straight')]
            print(shape.points)
            cutter.solid

        def incorrect_shape_rotation_angle():
            shape.rotation_angle = 360
            cutter.shape = shape

        self.assertRaises(ValueError, incorrect_rotation_angle)
        self.assertRaises(ValueError, incorrect_shape_points)
        self.assertRaises(ValueError, incorrect_shape_rotation_angle)

    def test_different_workplanes(self):
        """Test that checks the cutting wedge can be correctly applied to a
        shape with non-default workplane and rotation_axis
        """
        rectangle = paramak.ExtrudeStraightShape(
            2,
            points=[(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)],
            workplane="XY",
            rotation_axis="Z"
        )
        rectangle.rotation_angle = 360
        volume_full = rectangle.volume
        assert np.isclose(volume_full, 2)
        rectangle.rotation_angle = 90
        volume_quarter = rectangle.volume
        assert np.isclose(volume_quarter, 0.5)
