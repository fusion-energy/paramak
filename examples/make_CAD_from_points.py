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

__doc__ = """"This python script demonstrates the creation of 3D volumes
              from points using extrude and rotate methods"""


from paramak import (
    RotateStraightShape,
    RotateSplineShape,
    RotateMixedShape,
    RotateCircleShape,
)
from paramak import (
    ExtrudeSplineShape,
    ExtrudeStraightShape,
    ExtrudeMixedShape,
    ExtrudeCircleShape,
)

# rotate examples

# this makes a rectangle and rotates it to make a solid
rotated_straights = RotateStraightShape(
    points=[(400, 100), (400, 200), (600, 200), (600, 100)]
)
rotated_straights.rotation_angle = 180
rotated_straights.export_stp("rotated_straights.stp")
rotated_straights.export_html("rotated_straights.html")


# this makes a banana shape and rotates it to make a solid
rotated_spline = RotateSplineShape(
    points=[
        (500, 0),
        (500, -20),
        (400, -300),
        (300, -300),
        (400, 0),
        (300, 300),
        (400, 300),
        (500, 20),
    ]
)
rotated_spline.rotation_angle = 180
rotated_spline.export_stp("rotated_spline.stp")
rotated_spline.export_html("rotated_spline.html")


# this makes a banana shape with straight top and bottom edges and rotates it to make a solid
rotated_mixed = RotateMixedShape(
    points=[
        (300, -300, "spline"),
        (400, 0, "spline"),
        (300, 300, "circle"),
        (350, 350, "circle"),
        (400, 300, "spline"),
        (500, 0, "spline"),
        (400, -300, "straight"),
    ]
)
rotated_mixed.rotation_angle = 180
rotated_mixed.export_stp("rotated_mixed.stp")
rotated_mixed.export_html("rotated_mixed.html")


# this makes a circular shape and rotates it to make a solid
rotated_circle = RotateCircleShape(points=[(50, 0)], radius=5, workplane="XZ")
rotated_circle.rotation_angle = 180
rotated_circle.export_stp("rotated_circle.stp")
rotated_circle.export_html("rotated_circle.html")


# extrude examples

# this makes a banana shape with straight edges and rotates it to make a solid
extruded_straight = ExtrudeStraightShape(
    points=[
        (300, -300),
        (400, 0),
        (300, 300),
        (400, 300),
        (500, 0),
        (400, -300),
    ],
    distance=200,
)
extruded_straight.export_stp("extruded_straight.stp")
extruded_straight.export_html("extruded_straight.html")

# this makes a banana shape and rotates it to make a solid
extruded_spline = ExtrudeSplineShape(
    points=[
        (500, 0),
        (500, -20),
        (400, -300),
        (300, -300),
        (400, 0),
        (300, 300),
        (400, 300),
        (500, 20),
    ],
    distance=200,
)
extruded_spline.export_stp("extruded_spline.stp")
extruded_spline.export_html("extruded_spline.html")


# this makes a banana shape straight top and bottom edges and extrudes it to make a solid
extruded_mixed = ExtrudeMixedShape(
    points=[
        (300, -300, "spline"),
        (400, 0, "spline"),
        (300, 300, "circle"),
        (350, 350, "circle"),
        (400, 300, "spline"),
        (500, 0, "spline"),
        (400, -300, "straight"),
    ],
    distance=200,
)
extruded_mixed.export_stp("extruded_mixed.stp")
extruded_mixed.export_html("extruded_mixed.html")


# this makes a circular shape and extrudes it to make a solid
extruded_circle = ExtrudeCircleShape(points=[(20, 0)], radius=20, distance=200)
extruded_circle.export_stp("extruded_circle.stp")
extruded_circle.export_html("extruded_circle.html")
