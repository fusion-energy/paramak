"""
This python script demonstrates the creation of plasmas
"""

import math

import numpy as np

import paramak
import plotly.graph_objects as go

def plot_plasma(plasma, name=""):
    """Extract points that make up the plasma and creates a plotly trace"""

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=[plasma.x_position_for_outside_arc],
            y=[0],
            mode="markers",
            name="x_position_for_outside_arc",
            marker={"color": plasma.color},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[plasma.x_position_for_inside_arc],
            y=[0],
            mode="markers",
            name="x_position_for_inside_arc",
            marker={"color": plasma.color},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[plasma.major_radius],
            y=[0],
            mode="markers",
            name="major_radius",
            marker={"color": plasma.color},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[row[0] for row in plasma.points],
            y=[row[1] for row in plasma.points],
            mode="markers",
            name="points",
            marker={"color": plasma.color},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=plasma.xs_inner_arc,
            y=plasma.zs_inner_arc,
            mode="markers",
            name="inner arc points",
            marker={"color": plasma.color},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=plasma.xs_outer_arc,
            y=plasma.zs_outer_arc,
            mode="markers",
            name="outer arc points",
            marker={"color": plasma.color},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[plasma.x_point],
            y=[plasma.z_point],
            mode="markers",
            name="x and z points",
            marker={"color": plasma.color},
        )
    )


def make_plasma(major_radius, minor_radius, triangularity, elongation, name, color):
    """Creates a plasma object from argument inputs"""

    plasma = paramak.Plasma()
    plasma.name = "plasma"
    plasma.stp_filename = name + ".stp"
    plasma.major_radius = major_radius
    plasma.minor_radius = minor_radius
    plasma.triangularity = triangularity
    plasma.elongation = elongation
    plasma.single_null = True
    plasma.color = color
    plasma.rotation_angle = 180
    plasma.find_points()
    plasma.export_2d_image(name + ".png")
    plasma.export_html(name + ".html")
    plasma.export_stp(name + ".stp")

    return plasma


def main():

    ITER_plasma = make_plasma(
        name="ITER_plasma",
        major_radius=620,
        minor_radius=210,
        triangularity=0.33,
        elongation=1.85,
        color="blue",
    )

    EU_DEMO_plasma = make_plasma(
        name="EU_DEMO_plasma",
        major_radius=910,
        minor_radius=290,
        triangularity=0.33,
        elongation=1.59,
        color="red",
    )

    ST_plasma = make_plasma(
        name="ST_plasma",
        major_radius=170,
        minor_radius=129,
        triangularity=0.55,
        elongation=2.3,
        color="green",
    )

    AST_plasma = make_plasma(
        name="AST_plasma",
        major_radius=170,
        minor_radius=129,
        triangularity=-0.55,
        elongation=2.3,
        color="black",
    )

    fig = go.Figure()
    plot_plasma(plasma=ITER_plasma)
    plot_plasma(plasma=EU_DEMO_plasma)
    plot_plasma(plasma=ST_plasma)
    plot_plasma(plasma=AST_plasma)
    fig.show()
    fig.write_html("all_plasma_and_points.html")


if __name__ == "__main__":
    main()
