import os
import unittest
from pathlib import Path

import paramak


class TestCenterColumnStudyReactor(unittest.TestCase):
    """Test functionality of the CenterColumnStudyReactor class"""

    def setUp(self):
        self.test_reactor = paramak.CenterColumnStudyReactor(
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
            rotation_angle=359,
        )

    def test_html_file_creation(self):
        """Creates a reactor with exports the step files and check they exist"""

        os.system("rm *.html")
        self.test_reactor.export_html_3d("cylinder.html")
        assert Path("cylinder.html").is_file()
