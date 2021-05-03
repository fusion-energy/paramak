
import os
import unittest
from pathlib import Path

import paramak


class TestSparc2020Reactor(unittest.TestCase):

    def setUp(self):
        self.test_reactor = paramak.BallReactor(
            inner_bore_radial_thickness=50,
            inboard_tf_leg_radial_thickness=200,
            center_column_shield_radial_thickness=50,
            divertor_radial_thickness=100,
            inner_plasma_gap_radial_thickness=150,
            plasma_radial_thickness=100,
            outer_plasma_gap_radial_thickness=50,
            firstwall_radial_thickness=50,
            blanket_radial_thickness=100,
            blanket_rear_wall_radial_thickness=10,
            elongation=2,
            triangularity=0.55,
            number_of_tf_coils=16,
            rotation_angle=180,
        )

        self.output_filenames = [
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
            "vacuum_vessel.stp",
            "vacuum_vessel_inner.stp",
            "graveyard.stp",
        ]

    def test_make_sparc_2020_reactor(self):
        """Runs the example to check the output files are produced"""
        os.system("rm *.stp")
        my_reactor = paramak.SparcFrom2020PaperDiagram()
        my_reactor.export_stp()
        for output_filename in self.output_filenames:
            assert Path(output_filename).exists() is True

    def test_make_parametric_sparc_2020_rector(self):
        """Runs the example to check the output files are produced for sector
        model"""

        os.system("rm *.stp")
        my_reactor = paramak.SparcFrom2020PaperDiagram(rotation_angle=90)
        my_reactor.export_stp()
        for output_filename in self.output_filenames:
            assert Path(output_filename).exists() is True
