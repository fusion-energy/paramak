import os
import unittest
from pathlib import Path

import paramak


class TestDemo2015Reactor(unittest.TestCase):
    """Tests functionality of the TestDemo2015Reactor class"""

    def test_input_variable_names(self):
        """tests that the number of inputs variables is correct"""

        my_reactor = paramak.EuDemoFrom2015PaperDiagram(number_of_tf_coils=1)
        assert len(my_reactor.input_variables.keys()) == 2
        assert len(my_reactor.input_variable_names) == 2

    def test_plasma_construction(self):
        """Creates the plasma part of the EuDemoFrom2015PaperDiagram and checks
        the contruction runs"""

        my_reactor = paramak.EuDemoFrom2015PaperDiagram(number_of_tf_coils=1)
        plasma = my_reactor.create_plasma()
        assert plasma[0].volume() > 0

    def test_pf_coil_construction(self):
        """Creates the pf coil part of the EuDemoFrom2015PaperDiagram and
        checks the contruction runs"""

        my_reactor = paramak.EuDemoFrom2015PaperDiagram(number_of_tf_coils=1)
        pf_coils = my_reactor.create_pf_coils()
        for coil in pf_coils:
            assert coil.volume() > 0

    def test_vessel_construction(self):
        """Creates the pf coil part of the EuDemoFrom2015PaperDiagram and
        checks the contruction runs"""

        my_reactor = paramak.EuDemoFrom2015PaperDiagram(number_of_tf_coils=1)
        vessel_components = my_reactor.create_vessel_components()
        for component in vessel_components:
            assert component.volume() > 0

    def test_make_demo_2015_reactor(self):
        """Creates a EuDemoFrom2015PaperDiagram reactor and exports the stp
        files checking that each component results in a stp file"""

        output_filenames = [
            "plasma.stp",
            "outboard_pf_coil_1.stp",
            "outboard_pf_coil_2.stp",
            "outboard_pf_coil_3.stp",
            "outboard_pf_coil_4.stp",
            "outboard_pf_coil_5.stp",
            "outboard_pf_coil_6.stp",
            "pf_coils_1.stp",
            "pf_coils_2.stp",
            "pf_coils_3.stp",
            "pf_coils_4.stp",
            "pf_coils_5.stp",
            "divertor.stp",
            "blanket.stp",
            "vessel.stp",
            "tf_coil_casing.stp",
        ]
        os.system("rm *.stp")
        my_reactor = paramak.EuDemoFrom2015PaperDiagram(number_of_tf_coils=1)
        my_reactor.export_stp(filename=output_filenames)
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm *.stp")

    def test_make_parametric_demo_2015_rector(self):
        """Creates a EuDemoFrom2015PaperDiagram reactor with a non default
        rotation angle and exports the stp files checking that each component
        results in a stp file"""

        output_filenames = [
            "plasma.stp",
            "outboard_pf_coil_1.stp",
            "outboard_pf_coil_2.stp",
            "outboard_pf_coil_3.stp",
            "outboard_pf_coil_4.stp",
            "outboard_pf_coil_5.stp",
            "outboard_pf_coil_6.stp",
            "pf_coils_1.stp",
            "pf_coils_2.stp",
            "pf_coils_3.stp",
            "pf_coils_4.stp",
            "pf_coils_5.stp",
            "divertor.stp",
            "blanket.stp",
            "vessel.stp",
            "tf_coil_casing.stp",
        ]

        os.system("rm *.stp")
        my_reactor = paramak.EuDemoFrom2015PaperDiagram(number_of_tf_coils=1, rotation_angle=90)
        my_reactor.export_stp(filename=output_filenames)
        for output_filename in output_filenames:
            assert Path(output_filename).exists() is True
        os.system("rm *.stp")
