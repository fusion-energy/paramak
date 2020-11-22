"""
This python script demonstrates the creation of 3D volumes from points using
extrude and rotate methods
"""

import paramak


def main():

    # rotate examples

    # this makes a rectangle and rotates it to make a solid
    rotated_straights = paramak.RotateStraightShape(
        rotation_angle=180,
        points=[(400, 100), (400, 200), (600, 200), (600, 100)]
    )
    rotated_straights.export_stp("rotated_straights.stp")
    rotated_straights.export_html("rotated_straights.html")

    # this makes a banana shape and rotates it to make a solid
    rotated_spline = paramak.RotateSplineShape(
        rotation_angle=180,
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
    rotated_spline.export_stp("rotated_spline.stp")
    rotated_spline.export_html("rotated_spline.html")

    # this makes a shape with straight, spline and circular edges and rotates
    # it to make a solid
    rotated_mixed = paramak.RotateMixedShape(
        rotation_angle=180,
        points=[
            (100, 0, "straight"),
            (200, 0, "circle"),
            (250, 50, "circle"),
            (200, 100, "straight"),
            (150, 100, "spline"),
            (140, 75, "spline"),
            (110, 45, "spline"),
        ]
    )
    rotated_mixed.export_stp("rotated_mixed.stp")
    rotated_mixed.export_html("rotated_mixed.html")

    # this makes a circular shape and rotates it to make a solid
    rotated_circle = paramak.RotateCircleShape(
        rotation_angle=180,
        points=[(50, 0)],
        radius=5,
        workplane="XZ"
    )
    rotated_circle.export_stp("rotated_circle.stp")
    rotated_circle.export_html("rotated_circle.html")

    # extrude examples

    # this makes a banana shape with straight edges and rotates it to make a
    # solid
    extruded_straight = paramak.ExtrudeStraightShape(
        distance=200,
        points=[
            (300, -300),
            (400, 0),
            (300, 300),
            (400, 300),
            (500, 0),
            (400, -300),
        ]
    )
    extruded_straight.export_stp("extruded_straight.stp")
    extruded_straight.export_html("extruded_straight.html")

    # this makes a banana shape and rotates it to make a solid
    extruded_spline = paramak.ExtrudeSplineShape(
        distance=200,
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
    extruded_spline.export_stp("extruded_spline.stp")
    extruded_spline.export_html("extruded_spline.html")

    # this makes a banana shape straight top and bottom edges and extrudes it
    # to make a solid
    extruded_mixed = paramak.ExtrudeMixedShape(
        distance=100,
        points=[
            (100, 0, "straight"),
            (200, 0, "circle"),
            (250, 50, "circle"),
            (200, 100, "straight"),
            (150, 100, "spline"),
            (140, 75, "spline"),
            (110, 45, "spline"),
        ],
    )
    extruded_mixed.export_stp("extruded_mixed.stp")
    extruded_mixed.export_html("extruded_mixed.html")

    # this makes a circular shape and extrudes it to make a solid
    extruded_circle = paramak.ExtrudeCircleShape(
        points=[(20, 0)],
        radius=20,
        distance=200
    )
    extruded_circle.export_stp("extruded_circle.stp")
    extruded_circle.export_html("extruded_circle.html")

    # sweep examples

    # this makes a banana shape with straight edges and sweeps it along a
    # spline to make a solid
    sweep_straight = paramak.SweepStraightShape(
        points=[
            (-150, 300),
            (-50, 300),
            (50, 0),
            (-50, -300),
            (-150, -300),
            (-50, 0)
        ],
        path_points=[
            (50, 0),
            (150, 400),
            (400, 500),
            (650, 600),
            (750, 1000)
        ],
        workplane="XY",
        path_workplane="XZ"
    )
    sweep_straight.export_stp("sweep_straight.stp")
    sweep_straight.export_html("sweep_straight.html")

    # this makes a banana shape with spline edges and sweeps it along a spline
    # to make a solid
    sweep_spline = paramak.SweepSplineShape(
        points=[
            (50, 0),
            (50, -20),
            (-50, -300),
            (-150, -300),
            (-50, 0),
            (-150, 300),
            (-50, 300),
            (50, 20)
        ],
        path_points=[
            (50, 0),
            (150, 400),
            (400, 500),
            (650, 600),
            (750, 1000)
        ],
        workplane="XY",
        path_workplane="XZ"
    )
    sweep_spline.export_stp("sweep_spline.stp")
    sweep_spline.export_html("sweep_spline.html")

    # this makes a shape with straight, spline and circular edges and sweeps
    # it along a spline to make a solid
    sweep_mixed = paramak.SweepMixedShape(
        points=[
            (-80, -50, "straight"),
            (20, -50, "circle"),
            (70, 0, "circle"),
            (20, 50, "straight"),
            (-30, 50, "spline"),
            (-40, 25, "spline"),
            (-70, -5, "spline")
        ],
        path_points=[
            (50, 0),
            (150, 400),
            (400, 500),
            (650, 600),
            (750, 1000)
        ],
        workplane="XY",
        path_workplane="XZ"
    )
    sweep_mixed.export_stp("sweep_mixed.stp")
    sweep_mixed.export_html("sweep_mixed.html")

    # this makes a circular shape and sweeps it to make a solid
    sweep_circle = paramak.SweepCircleShape(
        radius=40,
        path_points=[
            (50, 0),
            (150, 400),
            (400, 500),
            (650, 600),
            (750, 1000)
        ],
        workplane="XY",
        path_workplane="XZ"
    )
    sweep_circle.export_stp("sweep_circle.stp")
    sweep_circle.export_html("sweep_circle.html")


if __name__ == "__main__":
    main()
