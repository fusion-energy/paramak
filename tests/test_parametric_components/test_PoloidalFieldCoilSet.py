
import paramak
import unittest


class test_PoloidalFieldCoilSet(unittest.TestCase):

    def test_PoloidalFieldCoilSet_creation(self):
        """creates a solid using the PoloidalFieldCoilSet parametric component
        and checks that a cadquery solid is created"""
        test_shape = paramak.PoloidalFieldCoilSet(heights=[10, 10, 10],
                                                  widths=[20, 20, 20],
                                                  center_points=[(100, 100),
                                                                 (200, 200),
                                                                 (300, 300)])
        assert test_shape.solid is not None
        assert len(test_shape.solid.Solids()) == 3

    def test_PoloidalFieldCoilSet_incorrect_args(self):
        """creates a solid using the PoloidalFieldCoilSet parametric component
        and checks that a cadquery solid is created"""
        def test_PoloidalFieldCoilSet_incorrect_height():
            """Checks  PoloidalFieldCoilSet with height as the wrong type"""
            paramak.PoloidalFieldCoilSet(
                heights=10, widths=[
                    20, 20, 20], center_points=[
                    (100, 100), (200, 200), (300, 300)])

        self.assertRaises(
            ValueError,
            test_PoloidalFieldCoilSet_incorrect_height)

        def test_PoloidalFieldCoilSet_incorrect_width():
            """Checks  PoloidalFieldCoilSet with width as the wrong type"""
            paramak.PoloidalFieldCoilSet(
                heights=[
                    10, 10, 10], widths=20, center_points=[
                    (100, 100), (200, 200), (300, 300)])

        self.assertRaises(
            ValueError,
            test_PoloidalFieldCoilSet_incorrect_width)

        def test_PoloidalFieldCoilSet_incorrect_center_points():
            """Checks  PoloidalFieldCoilSet with center_points as the wrong type"""
            paramak.PoloidalFieldCoilSet(heights=[10, 10, 10],
                                         widths=[20, 20, 20],
                                         center_points=100)

        self.assertRaises(
            ValueError,
            test_PoloidalFieldCoilSet_incorrect_center_points)

        def test_PoloidalFieldCoilSet_incorrect_width_length():
            """Checks  PoloidalFieldCoilSet with not enough entries in width"""
            paramak.PoloidalFieldCoilSet(
                heights=[
                    10, 10, 10], widths=[
                    20, 20], center_points=[
                    (100, 100), (200, 200), (300, 300)])

        self.assertRaises(
            ValueError,
            test_PoloidalFieldCoilSet_incorrect_width_length)
