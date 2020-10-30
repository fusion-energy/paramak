
import paramak
import unittest


class test_CuttingWedgeFS(unittest.TestCase):
    def test_CuttingWedgeFS_shape_construction_and_volume(self):
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

    def test_CuttingWedgeFS_error(self):
        """Checks that errors are raised when invalid arguments are set
        """
        shape = paramak.ExtrudeStraightShape(1, points=[(0, 0)])
        cutter = paramak.CuttingWedgeFS(
            shape=shape,
            azimuth_placement_angle=0,
        )

        def incorrect_rotation_angle():
            shape.rotation_angle = 360
            cutter.solid

        def incorrect_shape_points():
            shape.rotation_angle = 180
            cutter.shape.points = [(0, 0, 'straight')]
            print(shape.points)
            cutter.solid

        self.assertRaises(ValueError, incorrect_rotation_angle)
        self.assertRaises(ValueError, incorrect_shape_points)
