
__doc__ = """This python script demonstrates the creation of 3D volumes
from points to create an example reactor"""

import paramak

plasma = paramak.Plasma()
plasma.major_radius = 250
plasma.minor_radius = 100
plasma.triangularity = 0.5
plasma.elongation = 2.5
plasma.rotation_angle = 180


centre_column = paramak.RotateMixedShape(
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
centre_column.rotation_angle = 180


blanket = paramak.RotateMixedShape(
    points=[
        (325.4886, 300.5, "straight"),
        (538.4886, 300.5, "straight"),
        (538.4886, -300.5, "straight"),
        (325.4528, -300.5, "spline"),
        (389.9263, -138.1335, "spline"),
        (404.5108, 0, "spline"),
        (389.9263, 138.1335, "spline"),
    ]
)
blanket.stp_filename = "blanket.stp"
blanket.rotation_angle = 180


firstwall = paramak.RotateMixedShape(
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
    ]
)
firstwall.stp_filename = "firstwall.stp"
firstwall.rotation_angle = 180


divertor_bottom = paramak.RotateMixedShape(
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
    ]
)
divertor_bottom.stp_filename = "divertor_bottom.stp"
divertor_bottom.rotation_angle = 180


divertor_top = paramak.RotateMixedShape(
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
    ]
)
divertor_top.stp_filename = "divertor_top.stp"
divertor_top.rotation_angle = 180


core = paramak.RotateStraightShape(
    points=[(0, 687.0), (74.6, 687.0), (74.6, -687.0), (0, -687.0)]
)
core.stp_filename = "core.stp"
core.rotation_angle = 180


myreactor = paramak.Reactor()

myreactor.add_shape_or_component(plasma)
myreactor.add_shape_or_component(blanket)
myreactor.add_shape_or_component(core)
myreactor.add_shape_or_component(divertor_top)
myreactor.add_shape_or_component(divertor_bottom)
myreactor.add_shape_or_component(firstwall)
myreactor.add_shape_or_component(centre_column)

myreactor.export_stp(output_folder="can_reactor_from_points")
myreactor.export_html("can_reactor_from_points/reactor.html")
