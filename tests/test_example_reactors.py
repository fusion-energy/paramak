
import os
import unittest
from pathlib import Path

cwd = os.getcwd()


class test_object_properties(unittest.TestCase):
    def test_make_parametric_ball_rector(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_reactors"))
        output_filenames = [
            "BallReactor/plasma.stp",
            "BallReactor/inboard_tf_coils.stp",
            "BallReactor/center_column_shield.stp",
            "BallReactor/divertor.stp",
            "BallReactor/firstwall.stp",
            "BallReactor/blanket.stp",
            "BallReactor/blanket_rear_wall.stp",
            "BallReactor/Graveyard.stp",
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python ball_reactor.py")
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_parametric_single_null_ball_reactor(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_reactors"))
        output_filenames = [
            "BallReactor_sn/blanket_rear_wall.stp",
            "BallReactor_sn/blanket.stp",
            "BallReactor_sn/center_column_shield.stp",
            "BallReactor_sn/divertor.stp",
            "BallReactor_sn/firstwall.stp",
            "BallReactor_sn/Graveyard.stp",
            "BallReactor_sn/inboard_tf_coils.stp",
            "BallReactor_sn/pf_coils.stp",
            "BallReactor_sn/plasma.stp",
            "BallReactor_sn/tf_coil.stp"
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python ball_reactor_single_null.py")
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)

    def test_make_parametric_single_null_submersion_reactor(self):
        """Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/example_parametric_reactors"))
        output_filenames = [
            'SubmersionTokamak_sn/inboard_tf_coils.stp',
            'SubmersionTokamak_sn/center_column_shield.stp',
            'SubmersionTokamak_sn/plasma.stp',
            'SubmersionTokamak_sn/divertor.stp',
            'SubmersionTokamak_sn/supports.stp',
            'SubmersionTokamak_sn/outboard_firstwall.stp',
            'SubmersionTokamak_sn/blanket.stp',
            'SubmersionTokamak_sn/outboard_rear_blanket_wall.stp',
            'SubmersionTokamak_sn/outboard_tf_coil.stp',
            'SubmersionTokamak_sn/pf_coils.stp',
            'SubmersionTokamak_sn/Graveyard.stp'
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python submersion_reactor_single_null.py")
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
            os.system("rm " + output_filename)


if __name__ == "__main__":
    unittest.main()
