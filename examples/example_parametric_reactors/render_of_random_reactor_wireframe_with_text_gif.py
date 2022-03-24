# This examples creates Gif animation of 50 reactors by creating individual
# images of reactors and stiching them together using Imagemagick into a Gif
# animation. Two animations are made, of of a 3D render and one of a wireframe
# line drawing.

import os

# to run this example you will need all of the following packages installed
import numpy as np
import paramak

import svgwrite  # required to write text to svg file
import svgutils.transform as sg  # required to merge text svg files with wireframe svg file


def create_reactor_renders(
    render_number,
    inner_blanket_radius,
    blanket_thickness,
    blanket_height,
    lower_blanket_thickness,
    upper_blanket_thickness,
    blanket_vv_gap,
    upper_vv_thickness=10,
    vv_thickness=10,
    lower_vv_thickness=10,
):

    # creates a reactor from the input arguments
    my_reactor = paramak.FlfSystemCodeReactor(
        rotation_angle=180,
        inner_blanket_radius=inner_blanket_radius,
        blanket_thickness=blanket_thickness,
        blanket_height=blanket_height,
        lower_blanket_thickness=lower_blanket_thickness,
        upper_blanket_thickness=upper_blanket_thickness,
        blanket_vv_gap=blanket_vv_gap,
        upper_vv_thickness=upper_vv_thickness,
        vv_thickness=vv_thickness,
        lower_vv_thickness=lower_vv_thickness,
    )

    # exports line drawing of individual reactor
    my_reactor.export_svg(
        f"wireframe_{str(render_number).zfill(3)}.svg",
        projectionDir=[1, -1, -0.1],
        strokeWidth=2,
        width=1000,
        height=800,
    )

    svg_file_object = svgwrite.Drawing(
        filename=f"text_{str(render_number).zfill(3)}.svg",
        size=("1000px", "800px"),
    )

    lines_of_text_to_write = [
        "Parametric reactor inputs",
        f"Inner blanket radius {inner_blanket_radius/100:.1f}m",
        f"Blanket thickness {blanket_thickness/100:.1f}m",
        f"Blanket thickness {blanket_thickness/100:.1f}m",
        f"Blanket height {blanket_height/100:.1f}m",
        f"Lower blanket thickness {lower_blanket_thickness/100:.1f}m",
        f"Upper blanket thickness {upper_blanket_thickness/100:.1f}m",
        f"Blanket vv gap {blanket_vv_gap/100:.1f}m",
        f"Upper vv thickness {upper_vv_thickness/100:.1f}m",
        f"Vv thickness {vv_thickness/100:.1f}m",
        f"Lower vv thickness {lower_vv_thickness/100:.1f}m",
    ]
    y_value = 50
    for line in lines_of_text_to_write:
        y_value = y_value + 40
        svg_file_object.add(svg_file_object.text(line, insert=(555, y_value), font_size=27))
    svg_file_object.save()

    background = sg.fromfile(f"wireframe_{str(render_number).zfill(3)}.svg")
    forground = sg.fromfile(f"text_{str(render_number).zfill(3)}.svg")

    root = forground.getroot()
    background.append([root])

    background.save(f"combined_{str(render_number).zfill(3)}.svg")


# loops through adding a random reactor render to the figure with each iteration
for i in range(50):
    create_reactor_renders(
        render_number=i,
        inner_blanket_radius=np.random.uniform(low=50, high=90),
        blanket_thickness=np.random.uniform(low=50, high=140),
        blanket_height=np.random.uniform(low=400, high=550),
        lower_blanket_thickness=np.random.uniform(low=20, high=70),
        upper_blanket_thickness=np.random.uniform(low=20, high=70),
        blanket_vv_gap=np.random.uniform(low=10, high=90),
    )

# The convert comand requires imagemagick
# saves the line drawing svg files as a gif
os.system("convert -delay 40 -loop 0 combined_*.svg reactors_with_parameters.gif")
