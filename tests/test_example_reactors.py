
import os
import sys
import unittest
from pathlib import Path

from examples.example_parametric_reactors import (
    ball_reactor, ball_reactor_single_null, submersion_reactor_single_null,
    htc_reactor)

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'examples'))


class TestExampleReactors(unittest.TestCase):
    def test_make_parametric_htc_rector(self):
        """Runs the example to check the output files are produced"""
        output_filenames = [
            "plasma.stp",
            "inboard_pf_coils.stp",
            "outboard_pf_coils.stp",
            "div_coils.stp",
            "vs_coils.stp",
            "EFCCu_coils_1.stp",
            "EFCCu_coils_2.stp",
            "EFCCu_coils_3.stp",
            "EFCCu_coils_4.stp",
            "EFCCu_coils_5.stp",
            "EFCCu_coils_6.stp",
            "antenna.stp",
            "tf_coil.stp",
            "vacvessel.stp",
            "inner_vessel.stp",
            "Graveyard.stp",
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        htc_reactor.main(90)
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_parametric_ball_rector(self):
        """Runs the example and checks the output files are produced"""
        output_filenames = [
            "plasma.stp",
            "inboard_tf_coils.stp",
            "center_column_shield.stp",
            "divertor.stp",
            "firstwall.stp",
            "blanket.stp",
            "blanket_rear_wall.stp",
            "Graveyard.stp",
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        ball_reactor.make_ball_reactor(output_folder='')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_parametric_single_null_ball_reactor(self):
        """Runs the example and checks the output files are produced"""
        output_filenames = [
            "blanket_rear_wall.stp",
            "blanket.stp",
            "center_column_shield.stp",
            "divertor.stp",
            "firstwall.stp",
            "Graveyard.stp",
            "inboard_tf_coils.stp",
            "pf_coils.stp",
            "plasma.stp",
            "tf_coil.stp"
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        ball_reactor_single_null.make_ball_reactor_sn(output_folder='')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_parametric_single_null_submersion_reactor(self):
        """Runs the example and checks the output files are produced"""
        output_filenames = [
            'inboard_tf_coils.stp',
            'center_column_shield.stp',
            'plasma.stp',
            'divertor.stp',
            'supports.stp',
            'outboard_firstwall.stp',
            'blanket.stp',
            'outboard_rear_blanket_wall.stp',
            'outboard_tf_coil.stp',
            'pf_coils.stp',
            'Graveyard.stp'
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        submersion_reactor_single_null.make_submersion_sn(output_folder='')
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_htc_reactor(self):
        output_filenames = [
            'inboard_pf_coils.stp',
            'outboard_pf_coils.stp',
            'div_coils.stp',
            'vs_coils.stp',
            'EFCCu_coils_1.stp',
            'EFCCu_coils_2.stp',
            'EFCCu_coils_3.stp',
            'EFCCu_coils_4.stp',
            'EFCCu_coils_5.stp',
            'EFCCu_coils_6.stp',
            'antenna.stp',
            'vacvessel.stp',
            'inner_vessel.stp',
            'htc_reactor.svg',
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        htc_reactor.main()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)


if __name__ == "__main__":
    unittest.main()
