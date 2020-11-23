
import os
import unittest
import warnings

import paramak


class test_BlanketFP(unittest.TestCase):
    
    def setUp(self):
        self.plasma = paramak.Plasma(
            major_radius=450,
            minor_radius=150,
            triangularity=0.55,
            elongation=2
        )

        self.test_shape = paramak.BlanketFP(
            # plasma=self.plasma,
            thickness=150,
            start_angle=-90,
            stop_angle=240,
            offset_from_plasma=30,
        )
    
    def test_default_parameters(self):
        """Checks that the default parameters of a BlanketFP are correct."""

        assert self.test_shape.plasma == None
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
        
    def test_BlanketFP_creation_plasma(self):
        """Checks that a cadquery solid can be created by passing a plasma to
        the BlanketFP parametric component."""

        plasma = paramak.Plasma(
            major_radius=450,
            minor_radius=150,
            triangularity=0.55,
            elongation=2,
        )
        test_shape = paramak.BlanketFP(
            plasma=plasma,
            thickness=150,
            start_angle=-90,
            stop_angle=240,
            offset_from_plasma=30,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketFP_faces(self):
        """creates a blanket using the BlanketFP parametric component and checks
        that a solid with the correct number of faces is created"""

        plasma = paramak.Plasma(
            major_radius=450,
            minor_radius=150,
            triangularity=0.55,
            elongation=2,
        )

        test_shape = paramak.BlanketFP(
            plasma=plasma,
            thickness=150,
            start_angle=-90,
            stop_angle=240,
            offset_from_plasma=30,
        )
        assert len(test_shape.areas) == 4
        assert len(set(test_shape.areas)) == 4

        test_shape.rotation_angle = 180
        assert len(test_shape.areas) == 6
        assert len(set(test_shape.areas)) == 5

    def test_BlanketFP_creation_noplasma(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when no plasma is passed."""

        test_shape = paramak.BlanketFP(
            major_radius=450,
            minor_radius=150,
            triangularity=0.55,
            elongation=2,
            thickness=150,
            stop_angle=-90,
            start_angle=240,
            rotation_angle=180
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketFP_creation_variable_thickness_from_tuple(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when a tuple of thicknesses is passed as an
        argument."""

        test_shape = paramak.BlanketFP(
            major_radius=450,
            minor_radius=150,
            triangularity=0.55,
            elongation=2,
            thickness=(100, 200),
            start_angle=-90,
            stop_angle=240
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketFP_creation_variable_thickness_from_2_lists(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when a list of angles and a list of thicknesses
        are passed as an argument."""

        test_shape = paramak.BlanketFP(
            major_radius=450,
            minor_radius=150,
            triangularity=0.55,
            elongation=2,
            thickness=[(-90, 240), [10, 30]],
            start_angle=-90,
            stop_angle=240,
        )

        assert test_shape.solid is not None

    def test_BlanketFP_creation_variable_thickness_function(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when a thickness function is passed as an
        argument."""

        def thickness(theta):
            return 10 + 0.1 * theta

        test_shape = paramak.BlanketFP(
            major_radius=200,
            minor_radius=50,
            triangularity=0.5,
            elongation=2,
            thickness=thickness,
            stop_angle=10,
            start_angle=270,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketFP_creation_variable_offset_from_tuple(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when a tuple of offsets is passed as an
        argument."""

        test_shape = paramak.BlanketFP(
            major_radius=300,
            minor_radius=50,
            triangularity=0.5,
            elongation=2,
            thickness=100,
            offset_from_plasma=(0, 10),
            stop_angle=90,
            start_angle=270,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketFP_creation_variable_offset_from_2_lists(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when a list of offsets and a list of angles are
        passed as an argument."""

        test_shape = paramak.BlanketFP(
            major_radius=300,
            minor_radius=50,
            triangularity=0.5,
            elongation=2,
            thickness=100,
            offset_from_plasma=[[270, 100, 90], [0, 5, 10]],
            stop_angle=90,
            start_angle=270,
        )

        assert test_shape.solid is not None

    def test_BlanketFP_creation_variable_offset_error(self):
        """Checks that an error is raised when two lists with different
        lengths are passed in offset_from_plasma as an argument."""

        def test_different_lengths():
            test_shape = paramak.BlanketFP(
                major_radius=300,
                minor_radius=50,
                triangularity=0.5,
                elongation=2,
                thickness=100,
                offset_from_plasma=[[270, 100, 90], [0, 5, 10, 15]],
                stop_angle=90,
                start_angle=270,
            )
            test_shape.solid

        self.assertRaises(ValueError, test_different_lengths)

    def test_BlanketFP_creation_variable_offset_function(self):
        """Checks that a cadquery solid can be created using the BlanketFP
        parametric component when an offset function is passed."""

        def offset(theta):
            return 10 + 0.1 * theta

        test_shape = paramak.BlanketFP(
            major_radius=300,
            minor_radius=50,
            triangularity=0.5,
            elongation=2,
            thickness=100,
            stop_angle=90,
            start_angle=270,
            offset_from_plasma=offset
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketFP_physical_groups(self):
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

    def test_BlanketFP_full_cov_stp_export(self):
        """Creates a blanket using the BlanketFP parametric component and
        checks that a stp file with full coverage can be exported using the
        export_stp method"""

        test_shape = paramak.BlanketFP(
            major_radius=300,
            minor_radius=50,
            triangularity=0.5,
            elongation=2,
            thickness=200,
            stop_angle=360,
            start_angle=0,
            rotation_angle=180,
        )

        test_shape.export_stp("tests/test_blanket_full_cov")

    def test_full_cov_full_rotation(self):
        """Creates a blanket with full rotation and full coverage
        """
        test_shape = paramak.BlanketFP(
            major_radius=300,
            minor_radius=50,
            triangularity=0.5,
            elongation=2,
            thickness=200,
            stop_angle=360,
            start_angle=0,
            rotation_angle=360,
        )

        assert test_shape.solid is not None

    def test_overlapping(self):
        """Creates an overlapping geometry and checks that a warning is raised
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
