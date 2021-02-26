
import os
import unittest
from pathlib import Path

import paramak


class TestSparc2020Reactor(unittest.TestCase):

    def test_make_sparc_2020_reactor(self):
        output_filenames = [
            'inboard_pf_coils.stp',
            'outboard_pf_coils.stp',
            'div_coils.stp',
            'vs_coils.stp',
            'efccu_coils_1.stp',
            'efccu_coils_2.stp',
            'efccu_coils_3.stp',
            'efccu_coils_4.stp',
            'efccu_coils_5.stp',
            'efccu_coils_6.stp',
            'antenna.stp',
            'vacvessel.stp',
            'inner_vessel.stp',
        ]
        os.system("rm *.stp")
        my_reactor = paramak.SparcFrom2020PaperDiagram()
        my_reactor.export_stp()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm *.stp")

    def test_make_parametric_sparc_2020_rector(self):
        """Runs the example to check the output files are produced"""
        output_filenames = [
            "plasma.stp",
            "inboard_pf_coils.stp",
            "outboard_pf_coils.stp",
            "div_coils.stp",
            "vs_coils.stp",
            "efccu_coils_1.stp",
            "efccu_coils_2.stp",
            "efccu_coils_3.stp",
            "efccu_coils_4.stp",
            "efccu_coils_5.stp",
            "efccu_coils_6.stp",
            "antenna.stp",
            "tf_coil.stp",
            "vacvessel.stp",
            "inner_vessel.stp",
            "Graveyard.stp",
        ]
        os.system("rm *.stp")
        my_reactor = paramak.SparcFrom2020PaperDiagram(rotation_angle=90)
        my_reactor.export_stp()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm *.stp")
