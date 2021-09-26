import os
import unittest
from pathlib import Path

import paramak


class TestCylinderReactor(unittest.TestCase):
    """Tests the CylinderReactor functionality"""

    def setUp(self):
        self.test_reactor = paramak.CylinderReactor(
            inner_blanket_radius=100,
            blanket_thickness=60,
            blanket_height=500,
            lower_blanket_thickness=50,
            upper_blanket_thickness=40,
            blanket_vv_gap=20,
            upper_vv_thickness=10,
            vv_thickness=10,
            lower_vv_thickness=10,
            rotation_angle=180,
        )

    def test_input_variable_names(self):
        """tests that the number of inputs variables is correct"""

        assert len(self.test_reactor.input_variables.keys()) == 13
        assert len(self.test_reactor.input_variable_names) == 13

    def test_stp_file_creation(self):
        """Creates a reactor with exports the step files and check they exist"""

        os.system('rm *.stp')
        self.test_reactor.export_stp(filename='cylinder.stp')
        assert Path('cylinder.stp').is_file()

    def test_html_file_creation(self):
        """Creates a reactor with exports the step files and check they exist"""

        os.system('rm *.html')
        self.test_reactor.export_html_3d('cylinder.html')
        assert Path('cylinder.html').is_file()

    def test_export_brep(self):
        """Exports a brep file and checks that the output exist"""

        os.system("rm test_reactor.brep")

        self.test_reactor.export_brep(filename='test_reactor.brep')

        assert Path("test_reactor.brep").exists() is True

        os.system("rm test_reactor.brep")

    def test_export_brep_without_extention(self):
        """Exports a brep file without the extention and checks that the
        output exist"""

        def missing_extention():

            self.test_reactor.export_brep(filename='test_reactor_missing')

        self.assertRaises(
            ValueError,
            missing_extention
        )
