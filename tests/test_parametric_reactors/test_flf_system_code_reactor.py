import math
import os
import unittest
from pathlib import Path
from cadquery.occ_impl.shapes import Shape
import pytest

import paramak


class TestFlfSystemCodeReactor(unittest.TestCase):
    """Tests the FlfSystemCodeReactor functionality"""

    def setUp(self):
        self.test_reactor = paramak.FlfSystemCodeReactor(
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

        assert len(self.test_reactor.input_variables.keys()) == 10
        assert len(self.test_reactor.input_variable_names) == 10

    def test_stp_file_creation(self):
        """Exports a step file and checks that it was saved successfully"""

        os.system("rm *.stp")
        self.test_reactor.export_stp(filename="cylinder.stp")
        assert Path("cylinder.stp").is_file()

    def test_multiple_stp_file_creation(self):
        """Exports the reactor as separate step files and checks
        that they are saved successfully"""

        os.system("rm *.stp")
        self.test_reactor.export_stp()
        assert Path("lower_vessel.stp").is_file()
        assert Path("lower_blanket.stp").is_file()
        assert Path("blanket.stp").is_file()
        assert Path("upper_blanket.stp").is_file()
        assert Path("upper_vessel.stp").is_file()
        assert Path("vessel.stp").is_file()

    def test_graveyard_volume_in_brep_export(self):
        """Exports the reactor as a brep file and checks the number of volumes
        with and without the optional graveyard"""

        my_reactor = paramak.FlfSystemCodeReactor()

        my_reactor.export_brep(filename="without_graveyard.brep", include_graveyard=None)
        brep_shapes = Shape.importBrep("without_graveyard.brep").Solids()
        assert len(brep_shapes) == 6

        my_reactor.export_brep(filename="with_graveyard.brep", include_graveyard={"size": 2000})
        brep_shapes = Shape.importBrep("with_graveyard.brep").Solids()
        assert len(brep_shapes) == 7

        # TODO uncomment if ability to not merge surfaces is brought back
        # my_reactor.export_brep(filename="without_graveyard.brep", include_graveyard=False, merge=False)
        # brep_shapes = Shape.importBrep("without_graveyard.brep").Solids()
        # assert len(brep_shapes) == 6

        # my_reactor.export_brep(filename="with_graveyard.brep", include_graveyard=True, merge=False)
        # brep_shapes = Shape.importBrep("with_graveyard.brep").Solids()
        # assert len(brep_shapes) == 7

    def test_order_of_names_in_reactor(self):
        """tests the order of Shapes in the reactor is as expected"""

        assert self.test_reactor.name == [
            "blanket",
            "vessel",
            "upper_blanket",
            "lower_blanket",
            "lower_vessel",
            "upper_vessel",
        ]

    def test_blanket_volume_against_analytical_volume(self):
        """Checks the volume of the blanket is approximately equal
        to the analytical volume of the half cylinder"""

        outer_volume = (
            math.pi
            * math.pow(
                self.test_reactor.inner_blanket_radius + self.test_reactor.blanket_thickness,
                2,
            )
            * self.test_reactor.blanket_height
        )
        inner_volume = math.pi * math.pow(self.test_reactor.inner_blanket_radius, 2) * self.test_reactor.blanket_height
        sector_fraction = 360.0 / self.test_reactor.rotation_angle
        blanket_volume = (outer_volume - inner_volume) / sector_fraction

        assert pytest.approx(self.test_reactor.volume()[0]) == blanket_volume

    def test_upper_blanket_volume_against_analytical_volume(self):
        """Checks the volume of the upper_blanket is approximately equal
        to the analytical volume of the half cylinder"""

        full_rotation_volume = (
            math.pi
            * math.pow(
                self.test_reactor.inner_blanket_radius
                + self.test_reactor.blanket_thickness
                + self.test_reactor.blanket_vv_gap,
                2,
            )
            * self.test_reactor.upper_blanket_thickness
        )
        sector_fraction = 360.0 / self.test_reactor.rotation_angle
        blanket_volume = full_rotation_volume / sector_fraction

        assert pytest.approx(self.test_reactor.volume()[2]) == blanket_volume
