
import os
import unittest
from pathlib import Path

import paramak


class TestDemo2015Reactor(unittest.TestCase):

    def test_make_demo_2015_reactor(self):
        output_filenames = [
            'blanket.stp',
            'divertor.stp',
            'Graveyard.stp',
            'outboard_pf_coils.stp',
            'pf_coils_1.stp',
            'pf_coils_2.stp',
            'pf_coils_3.stp',
            'pf_coils_4.stp',
            'pf_coils_5.stp',
            'tf_coil_casing.stp',
            'vacvessel.stp',
        ]
        os.system("rm *.stp")
        my_reactor = paramak.EuDemoFrom2015PaperDiagram(number_of_tf_coils=1)
        my_reactor.export_stp()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm *.stp")

    def test_make_parametric_demo_2015_rector(self):
        """Runs the example to check the output files are produced"""
        output_filenames = [
            'blanket.stp',
            'divertor.stp',
            'Graveyard.stp',
            'outboard_pf_coils.stp',
            'pf_coils_1.stp',
            'pf_coils_2.stp',
            'pf_coils_3.stp',
            'pf_coils_4.stp',
            'pf_coils_5.stp',
            'tf_coil_casing.stp',
            'vacvessel.stp',
        ]
        os.system("rm *.stp")
        my_reactor = paramak.EuDemoFrom2015PaperDiagram(
            number_of_tf_coils=1, rotation_angle=90)
        my_reactor.export_stp()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm *.stp")
