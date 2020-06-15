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

__doc__ = "This python script demonstrates the parametric creation of a breeder blanket"

from paramak import RotateMixedShape

height = 700
blanket_rear = 400
blanket_front = 300
blanket_mid_point = 350

blanket = RotateMixedShape(
    points=[
        (blanket_rear, height / 2.0, "straight"),
        (blanket_rear, -height / 2.0, "straight"),
        (blanket_front, -height / 2.0, "spline"),
        (blanket_mid_point, 0, "spline"),
        (blanket_front, height / 2.0, "straight"),
    ]
)

blanket.rotation_angle = 180
blanket.export_stp("blanket_from_parameters.stp")
