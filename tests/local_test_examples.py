"""
This file is part of PARAMAK which is a design tool capable 
of creating 3D CAD models compatible with automated neutronics 
analysis.

PARAMAK is released under GNU General Public License v3.0. 
Go to https://github.com/Shimwell/paramak/blob/master/LICENSE 
for full license details.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Copyright (C) 2019  UKAEA

THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
"""

import os
import unittest
from pathlib import Path

from paramak import RotateStraightShape

cwd = os.getcwd()

"These tests require a visual front end which is not well suported on docker based CI systems"


class test_object_properties(unittest.TestCase):
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
            assert Path(output_filename).exists() == True
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
            assert Path(output_filename).exists() == True
            os.system("rm " + output_filename)

    def test_RotateStraightShape_export_3d_image(self):
        """checks that export_3d_image() exports png files with the correct suffix"""

        test_shape = RotateStraightShape(
            points=[(0, 0), (0, 20), (20, 20), (20, 0), (0, 0)]
        )
        test_shape.rotation_angle = 360
        os.system("rm filename.png")
        test_shape.export_3d_image("filename")
        assert Path("filename.png").exists() is True
        os.system("rm filename.png")
        test_shape.export_3d_image("filename.png")
        assert Path("filename.png").exists() is True
        os.system("rm filename.png")


if __name__ == "__main__":
    unittest.main()
