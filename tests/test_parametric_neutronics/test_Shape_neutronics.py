
import os
import unittest
from pathlib import Path

import paramak


class test_object_properties(unittest.TestCase):

    def setUp(self):
        self.test_shape = paramak.ExtrudeMixedShape(
            points=[
                (50, 0, "straight"),
                (50, 50, "spline"),
                (60, 70, "spline"),
                (70, 50, "circle"),
                (60, 25, "circle"),
                (70, 0, "straight")],
            distance=50
        )

    def test_export_h5m_creates_file(self):
        """Tests the Shape.export_h5m method results in an outputfile."""
        os.system('rm test_shape.h5m')
        self.test_shape.export_h5m(filename='test_shape.h5m')
        assert Path("test_shape.h5m").exists() is True

    def test_export_h5m_creates_file_even_without_extention(self):
        """Tests the Shape.export_h5m method results in an outputfile even
        when the filename does not include the .h5m"""
        os.system('rm test_shape.h5m')
        self.test_shape.export_h5m(filename='test_shape')
        assert Path("test_shape.h5m").exists() is True

    def test_offset_from_graveyard_sets_attribute(self):
        os.system('rm test_shape.h5m')
        self.test_shape.export_h5m(
            filename='test_shape.h5m',
            graveyard_offset=101)
        assert self.test_shape.graveyard_offset == 101

    def test_tolerance_increases_filesize(self):
        os.system('rm test_shape.h5m')
        self.test_shape.export_h5m(
            filename='test_shape_0001.h5m',
            tolerance=0.001)
        self.test_shape.export_h5m(
            filename='test_shape_001.h5m',
            tolerance=0.01)
        assert Path('test_shape_0001.h5m').stat().st_size > Path(
            'test_shape_001.h5m').stat().st_size

    def test_skipping_graveyard_decreases_filesize(self):
        os.system('rm test_shape.h5m')
        self.test_shape.export_h5m(filename='skiped.h5m', skip_graveyard=True)
        self.test_shape.export_h5m(
            filename='not_skipped.h5m',
            skip_graveyard=False)
        assert Path('not_skipped.h5m').stat().st_size > Path(
            'skiped.h5m').stat().st_size

    def test_graveyard_offset_increases_voulme(self):
        os.system('rm test_shape.h5m')
        self.test_shape.make_graveyard(graveyard_offset=100)
        small_offset = self.test_shape.graveyard.volume
        self.test_shape.make_graveyard(graveyard_offset=1000)
        large_offset = self.test_shape.graveyard.volume
        assert small_offset < large_offset


if __name__ == "__main__":
    unittest.main()
