import os
import unittest
from pathlib import Path

import pytest

import paramak


class test_BlanketConstantThicknessArcV(unittest.TestCase):
    def test_BlanketConstantThickness_creation(self):
        """creates a blanket using the BlanketConstantThicknessArcV parametric component
        and checks that a cadquery solid is created"""

        test_shape = paramak.BlanketConstantThicknessArcV(
            inner_lower_point=(300, -200),
            inner_mid_point=(500, 0),
            inner_upper_point=(300, 200),
            thickness=20,
            rotation_angle=180,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_BlanketConstantThicknessArcH(unittest.TestCase):
    def test_BlanketConstantThickness_creation(self):
        """creates a blanket using the BlanketConstantThicknessArcH parametric component
        and checks that a cadquery solid is created"""

        test_shape = paramak.BlanketConstantThicknessArcH(
            inner_lower_point=(300, -200),
            inner_mid_point=(500, 0),
            inner_upper_point=(300, 200),
            thickness=20,
            rotation_angle=180,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_BlanketFP(unittest.TestCase):
    def test_BlanketFP_creation_plasma(self):
        """checks that a cadquery solid can be created by passing a plasma to the
        BlanketFP parametric component"""

        plasma = paramak.Plasma(
            major_radius=300, minor_radius=50, triangularity=0.5, elongation=2,
        )
        test_shape = paramak.BlanketFP(
            plasma=plasma,
            thickness=200,
            stop_angle=90,
            start_angle=270,
            offset_from_plasma=30,
            rotation_angle=180,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketFP_creation_noplasma(self):
        """checks that a cadquery solid can be created using the BlanketFP parametric
        component when no plasma is passed"""

        test_shape = paramak.BlanketFP(
            major_radius=300,
            minor_radius=50,
            triangularity=0.5,
            elongation=2,
            thickness=200,
            stop_angle=360,
            start_angle=0,
            rotation_angle=180
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketFP_full_cov_full_rotation(self):
        """checks BlanketFP cannot have full coverage and 360 rotation at the same time"""
        def create_shape():
            test_shape = paramak.BlanketFP(
                major_radius=300,
                minor_radius=50,
                triangularity=0.5,
                elongation=2,
                thickness=200,
                stop_angle=360,
                start_angle=0,
                rotation_angle=360
            )
            test_shape.solid
        self.assertRaises(
            ValueError, create_shape)

    def test_BlanketFP_creation_variable_thickness_from_tuple(self):
        """checks that a cadquery solid can be created using the BlanketFP parametric
        component when a tuple of thicknesses is passed"""

        test_shape = paramak.BlanketFP(
            major_radius=300,
            minor_radius=50,
            triangularity=0.5,
            elongation=2,
            thickness=(100, 200),
            stop_angle=90,
            start_angle=270,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketFP_creation_variable_thickness_function(self):
        """checks that a cadquery solid can be created using the BlanketFP parametric
        component when a thickness function is passed"""

        def thickness(theta):
            return 100 + 3 * theta

        test_shape = paramak.BlanketFP(
            major_radius=300,
            minor_radius=50,
            triangularity=0.5,
            elongation=2,
            thickness=thickness,
            stop_angle=90,
            start_angle=270,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_BlanketFP_physical_groups(self):
        """creates a blanket using the BlanketFP parametric component and checks that
        physical groups can be exported using the export_physical_groups method"""

        test_shape = paramak.BlanketFP(100, stop_angle=90, start_angle=270,)
        test_shape.export_physical_groups("tests/blanket.json")

    def test_BlanketFP_full_cov_stp_export(self):
        """creates a blanket using the BlanketFP parametric component and checks that
        an stp file with full coverage can be exported using the export_stp method"""

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


class test_ToroidalFieldCoilCoatHanger(unittest.TestCase):
    def test_ToroidalFieldCoilCoatHanger_creation(self):
        """creates a tf coil using the ToroidalFieldCoilCoatHanger parametric component
        and checks that a cadquery solid is created"""

        test_shape = paramak.ToroidalFieldCoilCoatHanger(
            horizontal_start_point=(200, 500),
            horizontal_length=400,
            vertical_start_point=(700, 50),
            vertical_length=500,
            thickness=50,
            distance=50,
            number_of_coils=5,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_PoloidalFieldCoilCase(unittest.TestCase):
    def test_PoloidalFieldCoilCase_creation(self):
        """creates a pf coil case using the PoloidalFieldCoilCase parametric component and
        checks that a cadquery solid is created"""

        test_shape = paramak.PoloidalFieldCoilCase(
            casing_thickness=5,
            coil_height=50,
            coil_width=50,
            center_point=(
                1000,
                500))

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_Plasma(unittest.TestCase):
    def test_plasma_attributes(self):
        """creates a plasma object using the Plasma parametric component and checks that
        its attributes can be set correctly"""

        test_plasma = paramak.Plasma()

        assert isinstance(test_plasma.elongation, float)

        def test_plasma_elongation_min_setting():
            """checks ValueError is raised when an elongation < 0 is specified"""

            test_plasma.elongation = -1

        self.assertRaises(ValueError, test_plasma_elongation_min_setting)

        def test_plasma_elongation_max_setting():
            """checks ValueError is raised when an elongation > 4 is specified"""

            test_plasma.elongation = 400

        self.assertRaises(ValueError, test_plasma_elongation_max_setting)

    def test_plasma_x_points(self):
        """creates several plasmas with different configurations using the Plasma parametric
        component and checks the location of the x point for each"""

        for (
            triangularity,
            elongation,
            minor_radius,
            major_radius,
            vertical_displacement,
        ) in zip(
            [-0.7, 0, 0.5],  # triangularity
            [1, 1.5, 2],  # elongation
            [100, 200, 300],  # minor radius
            [300, 400, 600],  # major radius
            [0, -10, 5],
        ):  # displacement

            for config in ["non-null", "single-null", "double-null"]:

                # Run
                test_plasma = paramak.Plasma(
                    configuration=config,
                    triangularity=triangularity,
                    elongation=elongation,
                    minor_radius=minor_radius,
                    major_radius=major_radius,
                    vertical_displacement=vertical_displacement,
                )

                # Expected
                expected_lower_x_point, expected_upper_x_point = None, None
                if config == "single-null" or config == "double-null":
                    expected_lower_x_point = (1 -
                                              (1 +
                                               test_plasma.x_point_shift) *
                                              triangularity *
                                              minor_radius, -
                                              (1 +
                                               test_plasma.x_point_shift) *
                                              elongation *
                                              minor_radius +
                                              vertical_displacement, )

                    if config == "double-null":
                        expected_upper_x_point = (
                            expected_lower_x_point[0],
                            (1 +
                             test_plasma.x_point_shift) *
                            elongation *
                            minor_radius +
                            vertical_displacement,
                        )

                # Check
                for point, expected_point in zip(
                    [test_plasma.lower_x_point, test_plasma.upper_x_point],
                    [expected_lower_x_point, expected_upper_x_point],
                ):
                    assert point == expected_point

    def test_plasma_x_points_plasmaboundaries(self):
        """creates several plasmas with different configurations using the PlasmaBoundaries
        parametric component and checks the location of the x point for each"""

        for A, triangularity, elongation, minor_radius, major_radius in zip(
            [0, 0.05, 0.05],  # A
            [-0.7, 0, 0.5],  # triangularity
            [1, 1.5, 2],  # elongation
            [100, 200, 300],  # minor radius
            [300, 400, 600],
        ):  # major radius

            for config in ["non-null", "single-null", "double-null"]:

                # Run
                test_plasma = paramak.PlasmaBoundaries(
                    configuration=config,
                    A=A,
                    triangularity=triangularity,
                    elongation=elongation,
                    minor_radius=minor_radius,
                    major_radius=major_radius,
                )

                # Expected
                expected_lower_x_point, expected_upper_x_point = None, None
                if config == "single-null" or config == "double-null":
                    expected_lower_x_point = (1 -
                                              (1 +
                                               test_plasma.x_point_shift) *
                                              triangularity *
                                              minor_radius, -
                                              (1 +
                                               test_plasma.x_point_shift) *
                                              elongation *
                                              minor_radius, )

                    if config == "double-null":
                        expected_upper_x_point = (
                            expected_lower_x_point[0],
                            -expected_lower_x_point[1],
                        )

                # Check
                for point, expected_point in zip(
                    [test_plasma.lower_x_point, test_plasma.upper_x_point],
                    [expected_lower_x_point, expected_upper_x_point],
                ):
                    assert point == expected_point
                assert test_plasma.solid is not None

    def test_export_plasma_source(self):
        """creates a plasma using the Plasma parametric component and checks an stp file
        of the shape can be exported using the export_stp method"""

        test_plasma = paramak.Plasma()

        os.system("rm plasma.stp")

        test_plasma.export_stp("plasma.stp")

        assert Path("plasma.stp").exists()
        os.system("rm plasma.stp")

    def test_export_plasma_from_points_export(self):
        """creates a plasma using the PlasmaFromPoints parametric component and checks an
        stp file of the shape can be exported using the export_stp method"""

        test_plasma = paramak.PlasmaFromPoints(
            outer_equatorial_x_point=500,
            inner_equatorial_x_point=300,
            high_point=(400, 200),
            rotation_angle=180,
        )

        os.system("rm plasma.stp")

        test_plasma.export_stp("plasma.stp")

        assert Path("plasma.stp").exists()
        os.system("rm plasma.stp")


class test_DivertorITER(unittest.TestCase):
    def test_DivertorITER_creation(self):
        """creates an ITER-type divertor using the ITERtypeDivertor parametric component and
        checks that a cadquery solid is created"""

        test_shape = paramak.ITERtypeDivertor()
        assert test_shape.solid is not None

    def test_DivertorITER_STP_export(self):
        """creates an ITER-type divertor using the ITERtypeDivertor parametric component and
        checks that an stp file of the shape can be exported using the export_stp method"""

        test_shape = paramak.ITERtypeDivertor()
        test_shape.export_stp("tests/ITER_div")


class test_DivertorITERNoDome(unittest.TestCase):
    def test_DivertorITER_creation(self):
        """creates an ITER-type divertor using the ITERtypeDivertorNoDome parametric component and
        checks that a cadquery solid is created"""

        test_shape = paramak.ITERtypeDivertorNoDome()
        assert test_shape.solid is not None

    def test_DivertorITER_STP_export(self):
        """creates an ITER-type divertor using the ITERtypeDivertorNoDome parametric component and
        checks that an stp file of the shape can be exported using the export_stp method"""

        test_shape = paramak.ITERtypeDivertorNoDome()
        test_shape.export_stp("tests/ITER_div_no_dome")


class test_CenterColumnShieldFlatTopHyperbola(unittest.TestCase):
    def test_CenterColumnShieldFlatTopHyperbola_creation(self):
        """creates a center column shield using the CenterColumnShieldFlatTopHyperbola parametric
        component and checks that a cadquery solid is created"""

        test_shape = paramak.CenterColumnShieldFlatTopHyperbola(
            height=500,
            arc_height=300,
            inner_radius=50,
            mid_radius=100,
            outer_radius=150,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_CenterColumnShieldPlasmaHyperbola(unittest.TestCase):
    def test_CenterColumnShieldPlasmaHyperbola_creation(self):
        """creates a center column shield using the CenterColumnShieldPlasmaHyperbola parametric
        component and checks that a cadquery solid is created"""

        test_shape = paramak.CenterColumnShieldPlasmaHyperbola(
            inner_radius=50, height=800, mid_offset=40, edge_offset=30
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_CenterColumnShieldHyperbola(unittest.TestCase):
    def test_CenterColumnShieldHyperbola_creation(self):
        """creates a center column shield using the CenterColumnShieldHyperbola parametric component
        and checks that a cadquery solid is created"""

        test_shape = paramak.CenterColumnShieldHyperbola(
            height=100, inner_radius=50, mid_radius=80, outer_radius=100
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_PoloidalFieldCoil(unittest.TestCase):
    def test_PoloidalFieldCoil_creation(self):
        """creates a pf coil using the PoloidalFieldCoil parametric component and checks that a cadquery
        solid is created"""

        test_shape = paramak.PoloidalFieldCoil(
            height=50, width=60, center_point=(1000, 500)
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_ToroidalFieldCoilRectangle(unittest.TestCase):
    def test_ToroidalFieldCoilRectangle_creation(self):
        """creates a tf coil using the ToroidalFieldCoilRectangle parametric component and checks that a
        cadquery solid is created"""

        test_shape = paramak.ToroidalFieldCoilRectangle(
            inner_upper_point=(100, 700),
            inner_mid_point=(800, 0),
            inner_lower_point=(100, -700),
            thickness=150,
            distance=50,
            number_of_coils=8,
        )
        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_ToroidalFieldCoilTripleArc(unittest.TestCase):
    def test_ToroidalFieldCoilTripleArc_creation(self):
        """creates a ToroidalFieldCoilTripleArc object and checks a solid is created"""

        test_shape = paramak.ToroidalFieldCoilTripleArc(
            R1=1,
            h=1,
            radii=(1, 2),
            coverages=(10, 60),
            thickness=0.1,
            distance=0.5,
            number_of_coils=6,
            vertical_displacement=0.1)
        assert test_shape.solid is not None


class test_ToroidalFieldCoilPrincetonD(unittest.TestCase):
    def test_ToroidalFieldCoilPrincetonD_creation(self):
        """creates a ToroidalFieldCoilPrincetonD object and checks a solid is created"""

        test_shape = paramak.ToroidalFieldCoilPrincetonD(
            R1=100,
            R2=300,
            thickness=50,
            distance=50,
            number_of_coils=8,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_CenterColumnShieldCircular(unittest.TestCase):
    def test_CenterColumnShieldCircular_creation(self):
        """creates a center column shield using the CenterColumnShieldCircular parametric component and
        checks that a cadquery solid is created"""

        test_shape = paramak.CenterColumnShieldCircular(
            height=600, inner_radius=100, mid_radius=150, outer_radius=200
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_CenterColumnShieldFlatTopCircular(unittest.TestCase):
    def test_CenterColumnShieldFlatTopCircular_creation(self):
        """creates a center column shield using the CenterColumnShieldFlatTopCircular parametric component
        and checks that a cadquery solid is created"""

        test_shape = paramak.CenterColumnShieldFlatTopCircular(
            height=600,
            arc_height=200,
            inner_radius=100,
            mid_radius=150,
            outer_radius=200,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_CenterColumnShieldCylinder(unittest.TestCase):
    def test_CenterColumnShieldCylinder_creation(self):
        """creates a center column shield using the CenterColumnShieldCylinder parametric component and
        checks that a cadquery solid is created"""

        test_shape = paramak.CenterColumnShieldCylinder(
            height=600, inner_radius=100, outer_radius=200
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000

    def test_volume_CenterColumnShieldCylinder(self):
        """creates a CenterColumnShieldCylinder shape and checks that the volume is correct"""

        test_shape = paramak.CenterColumnShieldCylinder(
            rotation_angle=360,
            height=15,
            inner_radius=5,
            outer_radius=10,
            azimuth_placement_angle=0,
        )

        assert test_shape.volume == pytest.approx(3534.29)

        test_shape = paramak.CenterColumnShieldCylinder(
            rotation_angle=180,
            height=15,
            inner_radius=5,
            outer_radius=10,
            azimuth_placement_angle=95,
        )

        assert test_shape.volume == pytest.approx(3534.29 / 2.0)

    def test_export_stp_CenterColumnShieldCylinder(self):
        """creates a CenterColumnShieldCylinder shape and checks that an stp file of the shape
        can be exported using the export_stp method"""

        test_shape = paramak.CenterColumnShieldCylinder(
            rotation_angle=360,
            height=15,
            inner_radius=5,
            outer_radius=10,
            azimuth_placement_angle=0,
        )

        os.system("rm center_column_shield.stp")

        test_shape.export_stp("center_column_shield.stp")

        assert Path("center_column_shield.stp").exists()

        os.system("rm center_column_shield.stp")


class test_PoloidalFieldCoilCaseFC(unittest.TestCase):
    def test_PoloidalFieldCoilCaseFC_creation(self):
        """creates a pf coil case using the PoloidalFieldCoilCaseFC parametric component and
        checks that a cadquery solid is created"""

        pf_coil = paramak.PoloidalFieldCoil(
            height=50, width=60, center_point=(1000, 500)
        )

        test_shape = paramak.PoloidalFieldCoilCaseFC(
            pf_coil=pf_coil, casing_thickness=5
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_InnerTfCoilsFlat(unittest.TestCase):
    def test_InnerTfCoilsFlat_creation(self):
        """creates an inner tf coil using the InnerTFCoilsFlat parametric component and checks
        that a cadquery solid is created"""

        test_shape = paramak.InnerTfCoilsFlat(
            height=500,
            inner_radius=50,
            outer_radius=150,
            number_of_coils=6,
            gap_size=5,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


class test_InnerTfCoilsCircular(unittest.TestCase):
    def test_InnerTfCoilsCircular_creation(self):
        """creates an inner tf coil using the InnerTfCoilsCircular parametric component and checks
        that a cadquery solid is created"""

        test_shape = paramak.InnerTfCoilsCircular(
            height=500,
            inner_radius=50,
            outer_radius=150,
            number_of_coils=6,
            gap_size=5,
        )

        assert test_shape.solid is not None
        assert test_shape.volume > 1000


if __name__ == "__main__":
    unittest.main()
