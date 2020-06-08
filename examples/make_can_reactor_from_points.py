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

__doc__ = """This python script demonstrates the creation of 3D volumes
from points to create an example reactor"""

from paramak import RotateMixedShape, RotateStraightShape, Reactor
from paramak.parametric_shapes import PlasmaShape


plasma = PlasmaShape()
plasma.major_radius = 250
plasma.minor_radius = 100
plasma.triangularity = 0.5
plasma.elongation = 2.5
plasma.rotation_angle = 180


centre_column = RotateMixedShape(
    points=[
        (74.6, 687.0, "straight"),
        (171.0, 687.0, "straight"),
        (171.0, 459.9232, "spline"),
        (108.001, 249.9402, "spline"),
        (92.8995, 0, "spline"),
        (108.001, -249.9402, "spline"),
        (171.0, -459.9232, "straight"),
        (171.0, -687.0, "straight"),
        (74.6, -687.0, "straight"),
        (74.6, 687.0),
    ]
)
centre_column.stp_filename = "centre_column.stp"
centre_column.rotation_angle = 180


blanket = RotateMixedShape(
    points=[
        (325.4886, 300.5, "straight"),
        (538.4886, 300.5, "straight"),
        (538.4886, -300.5, "straight"),
        (325.4528, -300.5, "spline"),
        (389.9263, -138.1335, "spline"),
        (404.5108, 0, "spline"),
        (389.9263, 138.1335, "spline"),
        (325.4886, 300.5),
    ]
)
blanket.stp_filename = "blanket.stp"
blanket.rotation_angle = 180


firstwall = RotateMixedShape(
    points=[
        (322.9528, 300.5, "straight"),
        (325.4528, 300.5, "spline"),
        (389.9263, 138.1335, "spline"),
        (404.5108, 0, "spline"),
        (389.9263, -138.1335, "spline"),
        (325.4528, -300.5, "straight"),
        (322.9528, -300.5, "spline"),
        (387.4263, -138.1335, "spline"),
        (402.0108, 0, "spline"),
        (387.4263, 138.1335, "spline"),
        (322.9528, 300.5),
    ]
)
firstwall.stp_filename = "firstwall.stp"
firstwall.rotation_angle = 180


divertor_bottom = RotateMixedShape(
    points=[
        (192.4782, -447.204, "spline"),
        (272.4957, -370.5, "spline"),
        (322.9528, -300.5, "straight"),
        (538.4886, -300.5, "straight"),
        (538.4886, -687.0, "straight"),
        (171.0, -687.0, "straight"),
        (171.0, -459.9232, "spline"),
        (218.8746, -513.3484, "spline"),
        (362.4986, -602.3905, "straight"),
        (372.5012, -580.5742, "spline"),
        (237.48395, -497.21782, "spline"),
        (192.4782, -447.204),
    ]
)
divertor_bottom.stp_filename = "divertor_bottom.stp"
divertor_bottom.rotation_angle = 180


divertor_top = RotateMixedShape(
    points=[
        (192.4782, 447.204, "spline"),
        (272.4957, 370.5, "spline"),
        (322.9528, 300.5, "straight"),
        (538.4886, 300.5, "straight"),
        (538.4886, 687.0, "straight"),
        (171.0, 687.0, "straight"),
        (171.0, 459.9232, "spline"),
        (218.8746, 513.3484, "spline"),
        (362.4986, 602.3905, "straight"),
        (372.5012, 580.5742, "spline"),
        (237.48395, 497.21782, "spline"),
        (192.4782, 447.204),
    ]
)
divertor_top.stp_filename = "divertor_top.stp"
divertor_top.rotation_angle = 180


core = RotateStraightShape(
    points=[(0, 687.0), (74.6, 687.0), (74.6, -687.0), (0, -687.0), (0, 687.0)]
)
core.stp_filename = "core.stp"
core.rotation_angle = 180


myreactor = Reactor()

myreactor.add_shape(plasma)
myreactor.add_shape(blanket)
myreactor.add_shape(core)
myreactor.add_shape(divertor_top)
myreactor.add_shape(divertor_bottom)
myreactor.add_shape(firstwall)
myreactor.add_shape(centre_column)

myreactor.export_stp(output_folder="can_reactor_from_points")
myreactor.export_html("can_reactor_from_points/reactor.html")
