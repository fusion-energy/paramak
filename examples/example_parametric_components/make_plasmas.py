"""
This python script demonstrates the creation of plasmas
"""

import math

import numpy as np

import paramak
import plotly.graph_objects as go


def plot_plasma(plasma, name=""):
    """Extract points that make up the plasma and creates a plotly trace"""

    traces = []

    traces.append(
        go.Scatter(
            x=[plasma.major_radius],
            y=[0],
            mode="markers",
            name="major_radius",
            marker={"color": plasma.color},
        )
    )

    traces.append(
        go.Scatter(
            x=[row[0] for row in plasma.points],
            y=[row[1] for row in plasma.points],
            mode="markers",
            name="points",
            marker={"color": plasma.color},
        )
    )

    traces.append(
        go.Scatter(
            x=[plasma.low_point[0]],
            y=[plasma.low_point[1]],
            mode="markers",
            name="low_point",
            marker={"color": plasma.color},
        )
    )

    traces.append(
        go.Scatter(
            x=[plasma.high_point[0]],
            y=[plasma.high_point[1]],
            mode="markers",
            name="high_point",
            marker={"color": plasma.color},
        )
    )

    traces.append(
        go.Scatter(
            x=[plasma.inner_equatorial_point[0]],
            y=[plasma.inner_equatorial_point[1]],
            mode="markers",
            name="inner_equatorial_point",
            marker={"color": plasma.color},
        )
    )

    traces.append(
        go.Scatter(
            x=[plasma.outer_equatorial_point[0]],
            y=[plasma.outer_equatorial_point[1]],
            mode="markers",
            name="outer_equatorial_point",
            marker={"color": plasma.color},
        )
    )

    return traces


def make_plasma(major_radius, minor_radius, triangularity, elongation, name, color):
    """Creates a plasma object from argument inputs"""

    plasma = paramak.Plasma(
        major_radius=major_radius,
        minor_radius=minor_radius,
        triangularity=triangularity,
        elongation=elongation,
    )
    plasma.name = "plasma"
    plasma.stp_filename = name + ".stp"
    plasma.single_null = True
    plasma.color = color
    plasma.rotation_angle = 180
    plasma.find_points()
    plasma.export_2d_image(name + ".png")
    plasma.export_html(name + ".html")
    plasma.export_stp(name + ".stp")
    plasma.create_solid()

    return plasma


def make_plasma_plasmaboundaries(
    A,
    major_radius,
    minor_radius,
    triangularity,
    elongation,
    name,
    color,
    config="single-null",
):
    """Creates a plasma object from argument inputs"""

    plasma = paramak.PlasmaBoundaries(
        A=A,
        major_radius=major_radius,
        minor_radius=minor_radius,
        triangularity=triangularity,
        elongation=elongation,
        configuration=config,
    )
    plasma.name = "plasma"
    plasma.export_2d_image(name + ".png")
    plasma.export_html(name + ".html")
    plasma.export_stp(name + ".stp")
    plasma.create_solid()

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

    ITER_plasma_plasmaboundaries = make_plasma_plasmaboundaries(
        name="ITER_plasma_plasmaboundaries",
        A=-0.155,
        major_radius=620,
        minor_radius=210,
        triangularity=0.33,
        elongation=1.85,
        color="orange",
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
    fig.add_traces(plot_plasma(plasma=ITER_plasma))
    fig.add_traces(plot_plasma(plasma=ITER_plasma_plasmaboundaries))
    fig.add_traces(plot_plasma(plasma=EU_DEMO_plasma))
    fig.add_traces(plot_plasma(plasma=ST_plasma))
    fig.add_traces(plot_plasma(plasma=AST_plasma))
    fig.show()
    fig.write_html("all_plasma_and_points.html")


if __name__ == "__main__":
    main()
