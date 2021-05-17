
import os
import unittest
from pathlib import Path

import paramak


class TestITERReactor(unittest.TestCase):

    def test_plasma_construction(self):
        """Creates the plasma part of the ITERTokamak and checks
        the contruction runs"""

        my_reactor = paramak.IterFrom2020PaperDiagram(number_of_tf_coils=1)
        plasma = my_reactor.create_plasma()
        assert plasma[0].volume > 0

    def test_pf_coil_construction(self):
        """Creates the pf coil part of the ITERTokamak and
        checks the contruction runs"""

        my_reactor = paramak.IterFrom2020PaperDiagram(number_of_tf_coils=1)
        pf_coils = my_reactor.create_pf_coils()
        for coil in pf_coils:
            assert coil.volume > 0

    def test_vessel_construction(self):
        """Creates the pf coil part of the ITERTokamak and
        checks the contruction runs"""

        my_reactor = paramak.IterFrom2020PaperDiagram(number_of_tf_coils=1)
        plasma = my_reactor.create_plasma()
        vessel_components = my_reactor.create_vessel_components()
        for component in vessel_components:
            assert component.volume > 0

    def test_make_demo_2015_reactor(self):
        """Creates a ITERTokamak reactor and eports the stp
        files checking that each component results in a stp file"""

        output_filenames = [
            'blanket.stp',
            'divertor.stp',
            'graveyard.stp',
            'outboard_pf_coils.stp',
            'pf_coils_1.stp',
            'pf_coils_2.stp',
            'pf_coils_3.stp',
            'pf_coils_4.stp',
            'pf_coils_5.stp',
            'pf_coils_6.stp',
            'tf_coils.stp',
            'vacvessel.stp',
        ]
        os.system("rm *.stp")
        my_reactor = paramak.IterFrom2020PaperDiagram(number_of_tf_coils=1)
        my_reactor.export_stp()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm *.stp")

    def test_make_parametric_demo_2015_rector(self):
        """Creates a ITERTokamak reactor with a non defulat
        rotation angle and eports the stp files checking that each component
        results in a stp file"""

        output_filenames = [
            'blanket.stp',
            'divertor.stp',
            'graveyard.stp',
            'outboard_pf_coils.stp',
            'pf_coils_1.stp',
            'pf_coils_2.stp',
            'pf_coils_3.stp',
            'pf_coils_4.stp',
            'pf_coils_5.stp',
            'pf_coils_6.stp',
            'tf_coils.stp',
            'vacvessel.stp',
        ]
        os.system("rm *.stp")
        my_reactor = paramak.IterFrom2020PaperDiagram(
            number_of_tf_coils=1, rotation_angle=90)
        my_reactor.export_stp()
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm *.stp")
