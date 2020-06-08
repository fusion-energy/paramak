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

__doc__ = "This python script demonstrates the creation of a center column shield using plasma parameters"

from paramak.parametric_shapes import CenterColumnShieldPlasmaHyperbola

# Default shield parameters

# height = None
# inner_radius = None
# mid_offset = None
# edge_offset = None


# Default plasma parameters

# major_radius = 450
# minor_radius = 150
# triangularity = 0.55
# elongation = 2.0

# these parameters can also be specified as part of the CenterColumnShieldPlasmaHyperbola class


# using default plasma parameters

test_shape_1 = CenterColumnShieldPlasmaHyperbola(
    inner_radius=150, height=800, mid_offset=10, edge_offset=15
)
test_shape_1.export_stp("test_shape_1.stp")


# specifying plasma parameters

test_shape_2 = CenterColumnShieldPlasmaHyperbola(
    # plasma parameters
    major_radius=600,
    minor_radius=200,
    triangularity=0.7,
    elongation=1.5,
    # shield parameters
    inner_radius=50,
    height=1000,
    mid_offset=30,
    edge_offset=10,
)
test_shape_2.export_stp("test_shape_2.stp")
