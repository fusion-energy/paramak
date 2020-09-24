
import os
import unittest
from pathlib import Path
import warnings

import pytest

import paramak


class test_CenterColumnStudyReactor(unittest.TestCase):
    def test_CenterColumnStudyReactor_creation_with_narrow_divertor(self):
        """creates a ball reactor using the CenterColumnStudyReactor parametric_reactor and checks
        the correct number of components are created"""

        test_reactor = paramak.CenterColumnStudyReactor(
            inner_bore_radial_thickness=20,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness_mid=50,
            center_column_shield_radial_thickness_upper=100,
            inboard_firstwall_radial_thickness=20,
            inner_plasma_gap_radial_thickness=40,
            plasma_radial_thickness=200,
            outer_plasma_gap_radial_thickness=30,
            plasma_high_point=(20 + 50 + 100 + 20, 240),
            plasma_gap_vertical_thickness=20,
            center_column_arc_vertical_thickness=520,
            rotation_angle=180)

        test_reactor.export_stp()

        assert len(test_reactor.shapes_and_components) == 4

    def test_CenterColumnStudyReactor_svg_creation(self):
        """creates a ball reactor using the CenterColumnStudyReactor parametric_reactor and checks
        an svg image of the reactor can be exported"""

        os.system("rm test_CenterColumnStudyReactor_image.svg")

        test_reactor = paramak.CenterColumnStudyReactor(
            inner_bore_radial_thickness=20,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness_mid=50,
            center_column_shield_radial_thickness_upper=100,
            inboard_firstwall_radial_thickness=20,
            inner_plasma_gap_radial_thickness=40,
            plasma_radial_thickness=200,
            outer_plasma_gap_radial_thickness=30,
            plasma_high_point=(20 + 50 + 100 + 20, 240),
            plasma_gap_vertical_thickness=20,
            center_column_arc_vertical_thickness=520,
            rotation_angle=180)

        test_reactor.export_svg("test_CenterColumnStudyReactor_image.svg")

        assert Path("test_CenterColumnStudyReactor_image.svg").exists() is True
        os.system("rm test_CenterColumnStudyReactor_image.svg")

    def test_rotation_angle_warning(self):
        """checks that the correct warning message is printed when
        rotation_angle = 360"""

        def warning_trigger():
            try:
                paramak.CenterColumnStudyReactor(
                    inner_bore_radial_thickness=20,
                    inboard_tf_leg_radial_thickness=50,
                    center_column_shield_radial_thickness_mid=50,
                    center_column_shield_radial_thickness_upper=100,
                    inboard_firstwall_radial_thickness=20,
                    inner_plasma_gap_radial_thickness=40,
                    plasma_radial_thickness=200,
                    outer_plasma_gap_radial_thickness=30,
                    plasma_high_point=(20 + 50 + 100 + 20, 240),
                    plasma_gap_vertical_thickness=20,
                    center_column_arc_vertical_thickness=520,
                    rotation_angle=360)

            except BaseException:
                pass

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warning_trigger()
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "360 degree rotation may result in a Standard_ConstructionError or AttributeError" in str(
                w[-1].message)
