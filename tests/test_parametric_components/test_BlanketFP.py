
import os
import unittest
import warnings
from pathlib import Path

import paramak


class TestBlanketFP(unittest.TestCase):

    def setUp(self):
        self.plasma = paramak.Plasma(
            major_radius=450,
            minor_radius=150,
            triangularity=0.55,
            elongation=2
        )

        self.test_shape = paramak.BlanketFP(
            thickness=150,
            start_angle=-90,
            stop_angle=240,
        )

    def test_default_parameters(self):
        """Checks that the default parameters of a BlanketFP are correct."""

        assert self.test_shape.plasma is None
        assert self.test_shape.minor_radius == 150
        assert self.test_shape.major_radius == 450
        assert self.test_shape.triangularity == 0.55
        assert self.test_shape.elongation == 2
        assert self.test_shape.vertical_displacement == 0
        assert self.test_shape.offset_from_plasma == 0
        assert self.test_shape.num_points == 50
        assert self.test_shape.stp_filename == "BlanketFP.stp"
        assert self.test_shape.stl_filename == "BlanketFP.stl"
        assert self.test_shape.material_tag == "blanket_mat"

    def test_creation_plasma(self):
        """Checks that a cadquery solid can be created by passing a plasma to
        the BlanketFP parametric component."""

        self.test_shape.plasma = self.plasma
        self.test_shape.offset_from_plasma = 30

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_faces(self):
        """creates a blanket using the BlanketFP parametric component and checks
        that a solid with the correct number of faces is created"""

        self.test_shape.plasma = self.plasma
        self.test_shape.offset_from_plasma = 30

        assert len(self.test_shape.areas) == 4
        assert len(set([round(i) for i in self.test_shape.areas])) == 4

        self.test_shape.rotation_angle = 180
        assert len(self.test_shape.areas) == 6
        assert len(set([round(i) for i in self.test_shape.areas])) == 5

    def test_creation_noplasma(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when no plasma is passed."""

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_creation_variable_thickness_from_tuple(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when a tuple of thicknesses is passed as an
        argument."""

        self.test_shape.thickness = (100, 200)

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_creation_variable_thickness_from_2_lists(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when a list of angles and a list of thicknesses
        are passed as an argument."""

        self.test_shape.thickness = [(-90, 240), [10, 30]]

        assert self.test_shape.solid is not None

    def test_creation_variable_thickness_function(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when a thickness function is passed as an
        argument."""

        def thickness(theta):
            return 10 + 0.1 * theta

        self.test_shape.thickness = thickness

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_creation_variable_offset_from_tuple(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when a tuple of offsets is passed as an
        argument."""

        self.test_shape.offset_from_plasma = (0, 10)

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_creation_variable_offset_from_2_lists(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when a list of offsets and a list of angles are
        passed as an argument."""

        self.test_shape.start_angle = 90
        self.test_shape.stop_angle = 270
        self.test_shape.offset_from_plasma = [[270, 100, 90], [0, 5, 10]]

        assert self.test_shape.solid is not None

    def test_creation_variable_offset_error(self):
        """Checks that an error is raised when two lists with different
        lengths are passed in offset_from_plasma as an argument."""

        def test_different_lengths():
            self.test_shape.start_angle = 90
            self.test_shape.stop_angle = 270
            self.test_shape.offset_from_plasma = [
                [270, 100, 90], [0, 5, 10, 15]]
            self.test_shape.solid

        self.assertRaises(ValueError, test_different_lengths)

    def test_creation_variable_offset_function(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when an offset function is passed."""

        def offset(theta):
            return 10 + 0.1 * theta

        self.test_shape.offset_from_plasma = offset

        assert self.test_shape.solid is not None
        assert self.test_shape.volume > 1000

    def test_physical_groups(self):
        """Creates a blanket using the BlanketFP parametric component and
        checks that physical groups can be exported using the
        export_physical_groups method"""

        outfile = "tests/blanket.json"

        # 180 coverage, full rotation
        test_shape = paramak.BlanketFP(100, stop_angle=180, start_angle=0,)
        test_shape.export_physical_groups(outfile)

        # full coverage, 180 rotation
        test_shape = paramak.BlanketFP(
            100, stop_angle=0, start_angle=360,
            rotation_angle=180)
        test_shape.export_physical_groups(outfile)

        # 180 coverage, 180 rotation
        test_shape = paramak.BlanketFP(
            100, stop_angle=180, start_angle=0,
            rotation_angle=180)
        test_shape.export_physical_groups(outfile)
        os.system("rm " + outfile)

    def test_full_cov_stp_export(self):
        """Creates a blanket using the BlanketFP parametric component with full
        coverage and checks that an stp file can be exported using the export_stp
        method."""

        self.test_shape.rotation_angle = 180
        self.test_shape.start_angle = 0
        self.test_shape.stop_angle = 360

        self.test_shape.export_stp("test_blanket_full_cov.stp")
        assert Path("test_blanket_full_cov.stp").exists()
        os.system("rm test_blanket_full_cov.stp")

    def test_full_cov_full_rotation(self):
        """Creates a blanket using the BlanketFP parametric component with full
        coverage and full rotation and checks that an stp file can be exported using
        the export_stp method."""

        self.test_shape.rotation_angle = 360
        self.test_shape.start_angle = 0
        self.test_shape.stop_angle = 360

        self.test_shape.export_stp("test_blanket_full_cov_full_rot.stp")
        assert Path("test_blanket_full_cov_full_rot.stp").exists()
        os.system("rm test_blanket_full_cov_full_rot.stp")

    def test_overlapping(self):
        """Creates an overlapping geometry and checks that a warning is raised.
        """

        test_shape = paramak.BlanketFP(
            major_radius=100,
            minor_radius=100,
            triangularity=0.5,
            elongation=2,
            thickness=200,
            stop_angle=360,
            start_angle=0,
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            assert test_shape.solid is not None
            assert len(w) == 1
