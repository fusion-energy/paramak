
import json
import os
import unittest
from pathlib import Path

import paramak
import pytest

cwd = os.getcwd()

"These tests require a visual front end which is not well suported on docker based CI systems"


class TestLocalExamples(unittest.TestCase):
    def test_make_collarge(self):
        """ Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples"))
        output_filenames = [
            "output_collarge/1.png",
            "output_collarge/2.png",
            "output_collarge/3.png",
            "output_collarge/4.png",
            "output_collarge/5.png",
            "output_collarge/6.png",
            "output_collarge/7.png",
            "output_collarge/8.png",
            "output_collarge/9.png",
            "output_collarge/combine_images1.sh",
            "output_collarge/combine_images2.sh",
            "output_collarge/paramak_array1.svg",
            "output_collarge/paramak_array2.svg",
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python make_collarge.py")
        for output_filename in output_filenames:
            assert Path(output_filename).exists()
            os.system("rm " + output_filename)

    def test_make_paramak_animation(self):
        """ Runs the example and checks the output files are produced"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples"))
        output_filenames = [
            "output_for_animation_2d/0.png",
            "output_for_animation_2d/1.png",
            "output_for_animation_2d/2.png",
            "output_for_animation_3d/0.png",
            "output_for_animation_3d/1.png",
            "output_for_animation_3d/2.png",
            "2d.gif",
            "3d.gif",
        ]
        for output_filename in output_filenames:
            os.system("rm " + output_filename)
        os.system("python make_animation.py -n 3")
        for output_filename in output_filenames:
            assert Path(output_filename).exists()
            os.system("rm " + output_filename)

    def test_export_3d_image(self):
        """checks that export_3d_image() exports png files with the correct suffix"""

        test_shape = paramak.RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0)]
        )
        test_shape.rotation_angle = 360
        os.system("rm filename.png")
        test_shape.export_3d_image("filename")
        assert Path("filename.png").exists() is True
        os.system("rm filename.png")
        test_shape.export_3d_image("filename.png")
        assert Path("filename.png").exists() is True
        os.system("rm filename.png")

    def test_neutronics_cell_tally(self):
        """ Runs the neutronics example and checks the TBR"""
        os.chdir(Path(cwd))
        os.chdir(Path("examples/neutronics"))
        output_filename = "simulation_result.json"
        os.system("rm " + output_filename)
        os.system("python make_simple_neutronics_model.py")
        with open(output_filename) as json_file:
            data = json.load(json_file)
        assert data["TBR"] == pytest.approx(0.456, abs=0.01)
        os.system("rm " + output_filename)


if __name__ == "__main__":
    unittest.main()
