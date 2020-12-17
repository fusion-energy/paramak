
import unittest

import paramak


class TestShellFS(unittest.TestCase):

    def setUp(self):
        # this is the shape that gets shelled
        self.test_shape = paramak.PoloidalFieldCoil(
            height=50,
            width=50,
            rotation_angle=90,
            center_point=(100, 100)
        )

    def test_creation_with_different_kinds(self):

        casing_int = paramak.ShellFS(
            shape=self.test_shape, kind='intersection')
        casing_int.export_stp('int.stp')
        casing_arc = paramak.ShellFS(shape=self.test_shape, kind='arc')
        casing_arc.export_stp('arc.stp')

        assert casing_int.solid is not None
        assert casing_int.solid is not None
        assert casing_int.volume > casing_arc.volume

    def test_creation_with_different_thickness(self):

        casing_small = paramak.ShellFS(shape=self.test_shape, thickness=5)

        casing_large = paramak.ShellFS(shape=self.test_shape, thickness=20)

        assert casing_small.solid is not None
        assert casing_large.solid is not None
        assert casing_large.volume > casing_small.volume
