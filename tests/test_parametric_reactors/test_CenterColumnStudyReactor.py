
import os
import unittest
import warnings
from pathlib import Path

import paramak
import pytest


class test_CenterColumnStudyReactor(unittest.TestCase):
    def test_creation_with_narrow_divertor(self):
        """Creates a ball reactor using the CenterColumnStudyReactor parametric_reactor and checks
        the correct number of components are created."""

        test_reactor = paramak.CenterColumnStudyReactor(
            inner_bore_radial_thickness=20,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness_mid=50,
            center_column_shield_radial_thickness_upper=100,
            inboard_firstwall_radial_thickness=20,
            divertor_radial_thickness=100,
            inner_plasma_gap_radial_thickness=80,
            plasma_radial_thickness=200,
            outer_plasma_gap_radial_thickness=90,
            elongation=2.3,
            triangularity=0.45,
            plasma_gap_vertical_thickness=40,
            center_column_arc_vertical_thickness=520,
            rotation_angle=180)

        test_reactor.export_stp()

        assert len(test_reactor.shapes_and_components) == 6

    def test_svg_creation(self):
        """Creates a ball reactor using the CenterColumnStudyReactor parametric_reactor and checks
        an svg image of the reactor can be exported."""

        os.system("rm test_image.svg")

        test_reactor = paramak.CenterColumnStudyReactor(
            inner_bore_radial_thickness=30,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness_mid=50,
            center_column_shield_radial_thickness_upper=100,
            inboard_firstwall_radial_thickness=30,
            divertor_radial_thickness=10,
            inner_plasma_gap_radial_thickness=80,
            plasma_radial_thickness=200,
            outer_plasma_gap_radial_thickness=90,
            elongation=2.3,
            triangularity=0.45,
            plasma_gap_vertical_thickness=40,
            center_column_arc_vertical_thickness=520,
            rotation_angle=180)

        test_reactor.export_svg("test_image.svg")

        assert Path("test_image.svg").exists() is True
        os.system("rm test_image.svg")

    def test_rotation_angle_impacts_volume(self):
        """Creates a CenterColumnStudyReactor reactor with a rotation angle of
        90 and another reactor with a rotation angle of 180. Then checks the
        volumes of all the components is double in the 180 reactor."""

        test_reactor_90 = paramak.CenterColumnStudyReactor(
            inner_bore_radial_thickness=30,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness_mid=50,
            center_column_shield_radial_thickness_upper=100,
            inboard_firstwall_radial_thickness=30,
            divertor_radial_thickness=10,
            inner_plasma_gap_radial_thickness=80,
            plasma_radial_thickness=200,
            outer_plasma_gap_radial_thickness=90,
            elongation=2.3,
            triangularity=0.45,
            plasma_gap_vertical_thickness=40,
            center_column_arc_vertical_thickness=520,
            rotation_angle=90)

        test_reactor_180 = paramak.CenterColumnStudyReactor(
            inner_bore_radial_thickness=30,
            inboard_tf_leg_radial_thickness=50,
            center_column_shield_radial_thickness_mid=50,
            center_column_shield_radial_thickness_upper=100,
            inboard_firstwall_radial_thickness=30,
            divertor_radial_thickness=10,
            inner_plasma_gap_radial_thickness=80,
            plasma_radial_thickness=200,
            outer_plasma_gap_radial_thickness=90,
            elongation=2.3,
            triangularity=0.45,
            plasma_gap_vertical_thickness=40,
            center_column_arc_vertical_thickness=520,
            rotation_angle=180)

        for r90, r180 in zip(test_reactor_90.shapes_and_components,
                             test_reactor_180.shapes_and_components):
            assert r90.volume == pytest.approx(r180.volume * 0.5, rel=0.1)

    def test_rotation_angle_warning(self):
        """Checks that the correct warning message is printed when
        rotation_angle = 360."""

        def warning_trigger():
            try:
                reactor = paramak.CenterColumnStudyReactor(
                    inner_bore_radial_thickness=20,
                    inboard_tf_leg_radial_thickness=50,
                    center_column_shield_radial_thickness_mid=50,
                    center_column_shield_radial_thickness_upper=100,
                    inboard_firstwall_radial_thickness=20,
                    divertor_radial_thickness=100,
                    inner_plasma_gap_radial_thickness=80,
                    plasma_radial_thickness=200,
                    outer_plasma_gap_radial_thickness=90,
                    elongation=2.3,
                    triangularity=0.45,
                    plasma_gap_vertical_thickness=40,
                    center_column_arc_vertical_thickness=520,
                    rotation_angle=360)
                reactor.shapes_and_components
            except BaseException:
                pass

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warning_trigger()
            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert "360 degree rotation may result in a Standard_ConstructionError or AttributeError" in str(
                w[-1].message)
