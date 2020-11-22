"""
This script creates a can shaped reactor with plasma, center column, blanket, firstwall, divertor and core
"""

import paramak


def main():

    outer_most_x = 900
    blanket_height = 300

    plasma = paramak.Plasma(
        major_radius=250,
        minor_radius=100,
        triangularity=0.5,
        elongation=2.5,
        rotation_angle=180
    )

    centre_column = paramak.RotateMixedShape(
        rotation_angle=180,
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
        ]
    )
    centre_column.stp_filename = "centre_column.stp"
    centre_column.stl_filename = "centre_column.stl"

    blanket = paramak.RotateMixedShape(
        rotation_angle=180,
        points=[
            (325.4528, blanket_height, "straight"),
            (outer_most_x, blanket_height, "straight"),
            (outer_most_x, -blanket_height, "straight"),
            (325.4528, -blanket_height, "spline"),
            (389.9263, -138.1335, "spline"),
            (404.5108, 0, "spline"),
            (389.9263, 138.1335, "spline"),
        ]
    )
    blanket.stp_filename = "blanket.stp"
    blanket.stl_filename = "blanket.stl"

    firstwall = paramak.RotateMixedShape(
        rotation_angle=180,
        points=[
            (322.9528, blanket_height, "straight"),
            (325.4528, blanket_height, "spline"),
            (389.9263, 138.1335, "spline"),
            (404.5108, 0, "spline"),
            (389.9263, -138.1335, "spline"),
            (325.4528, -blanket_height, "straight"),
            (322.9528, -blanket_height, "spline"),
            (387.4263, -138.1335, "spline"),
            (402.0108, 0, "spline"),
            (387.4263, 138.1335, "spline"),
        ]
    )
    firstwall.stp_filename = "firstwall.stp"
    firstwall.stl_filename = "firstwall.stl"

    divertor_bottom = paramak.RotateMixedShape(
        rotation_angle=180,
        points=[
            (192.4782, -447.204, "spline"),
            (272.4957, -370.5, "spline"),
            (322.9528, -blanket_height, "straight"),
            (outer_most_x, -blanket_height, "straight"),
            (outer_most_x, -687.0, "straight"),
            (171.0, -687.0, "straight"),
            (171.0, -459.9232, "spline"),
            (218.8746, -513.3484, "spline"),
            (362.4986, -602.3905, "straight"),
            (372.5012, -580.5742, "spline"),
            (237.48395, -497.21782, "spline"),
        ]
    )
    divertor_bottom.stp_filename = "divertor_bottom.stp"
    divertor_bottom.stl_filename = "divertor_bottom.stl"

    divertor_top = paramak.RotateMixedShape(
        rotation_angle=180,
        points=[
            (192.4782, 447.204, "spline"),
            (272.4957, 370.5, "spline"),
            (322.9528, blanket_height, "straight"),
            (outer_most_x, blanket_height, "straight"),
            (outer_most_x, 687.0, "straight"),
            (171.0, 687.0, "straight"),
            (171.0, 459.9232, "spline"),
            (218.8746, 513.3484, "spline"),
            (362.4986, 602.3905, "straight"),
            (372.5012, 580.5742, "spline"),
            (237.48395, 497.21782, "spline"),
        ]
    )
    divertor_top.stp_filename = "divertor_top.stp"
    divertor_top.stl_filename = "divertor_top.stl"

    core = paramak.RotateStraightShape(
        rotation_angle=180,
        points=[
            (0, 687.0),
            (74.6, 687.0),
            (74.6, -687.0),
            (0, -687.0)]
    )
    core.stp_filename = "core.stp"
    core.stl_filename = "core.stl"

    # initiates a reactor object
    myreactor = paramak.Reactor([plasma,
                                 blanket,
                                 core,
                                 divertor_top,
                                 divertor_bottom,
                                 firstwall,
                                 centre_column])

    myreactor.export_stp(output_folder="can_reactor_from_parameters")
    myreactor.export_stl(output_folder="can_reactor_from_parameters")
    myreactor.export_html(filename="can_reactor_from_parameters/reactor.html")


if __name__ == "__main__":
    main()
