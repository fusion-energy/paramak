"""
This python script demonstrates the creation of plasmas
"""

import math

import numpy as np

import paramak
import plotly.graph_objects as go


def plot_plasma(plasma, name=""):
    """Extract points that make up the plasma and creates a plotly trace"""

    if name.endswith("plasmaboundaries"):
        major_radius = plasma.major_radius
        low_point = plasma.low_point
        high_point = plasma.high_point
        inner_equatorial_point = plasma.inner_equatorial_point
        outer_equatorial_point = plasma.outer_equatorial_point
        x_points = [row[0] for row in plasma.points]
        y_points = [row[1] for row in plasma.points]

    else:
        major_radius = plasma.major_radius * -1
        low_point = (plasma.low_point[0] * -1, plasma.low_point[1])
        high_point = (plasma.high_point[0] * -1, plasma.high_point[1])
        inner_equatorial_point = (
            plasma.inner_equatorial_point[0] * -1,
            plasma.inner_equatorial_point[1])
        outer_equatorial_point = (
            plasma.outer_equatorial_point[0] * -1,
            plasma.outer_equatorial_point[1])
        x_points = [row[0] * -1 for row in plasma.points]
        y_points = [row[1] for row in plasma.points]

    traces = []

    traces.append(
        go.Scatter(
            x=[major_radius],
            y=[0],
            mode="markers",
            name="major_radius",
            marker={"color": plasma.color},
        )
    )

    traces.append(
        go.Scatter(
            x=x_points,
            y=y_points,
            mode="markers",
            name="points",
            marker={"color": plasma.color},
        )
    )

    traces.append(
        go.Scatter(
            x=[low_point[0]],
            y=[low_point[1]],
            mode="markers",
            name="low_point",
            marker={"color": plasma.color},
        )
    )

    traces.append(
        go.Scatter(
            x=[high_point[0]],
            y=[high_point[1]],
            mode="markers",
            name="high_point",
            marker={"color": plasma.color},
        )
    )

    traces.append(
        go.Scatter(
            x=[inner_equatorial_point[0]],
            y=[inner_equatorial_point[1]],
            mode="markers",
            name="inner_equatorial_point",
            marker={"color": plasma.color},
        )
    )

    traces.append(
        go.Scatter(
            x=[outer_equatorial_point[0]],
            y=[outer_equatorial_point[1]],
            mode="markers",
            name="outer_equatorial_point",
            marker={"color": plasma.color},
        )
    )

    return traces


def make_plasma(
        major_radius,
        minor_radius,
        triangularity,
        elongation,
        name,
        color):
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

    NSTX_double_null_plasma_plasmaboundaries = make_plasma_plasmaboundaries(
        name="NSTX_double_null_plasma_plasmaboundaries",
        A=0,
        major_radius=850,
        minor_radius=680,
        triangularity=0.35,
        elongation=2,
        color="yellow",
        config="double-null"
    )

    NSTX_single_null_plasma_plasmaboundaries = make_plasma_plasmaboundaries(
        name="NSTX_single_null_plasma_plasmaboundaries",
        A=-0.05,
        major_radius=850,
        minor_radius=680,
        triangularity=0.35,
        elongation=2,
        color="purple",
        config="single-null"
    )

    fig = go.Figure()
    fig.add_traces(plot_plasma(plasma=ITER_plasma, name="ITER_plasma"))
    fig.add_traces(
        plot_plasma(
            plasma=ITER_plasma_plasmaboundaries,
            name="ITER_plasma_plasmaboundaries"))
    fig.add_traces(plot_plasma(plasma=EU_DEMO_plasma, name="EU_DEMO_plasma"))
    fig.add_traces(plot_plasma(plasma=ST_plasma, name="ST_plasma"))
    fig.add_traces(plot_plasma(plasma=AST_plasma, name="AST_plasma"))
    fig.add_traces(
        plot_plasma(
            plasma=NSTX_double_null_plasma_plasmaboundaries,
            name="NSTX_double_null_plasma_plasmaboundaries"))
    fig.add_traces(
        plot_plasma(
            plasma=NSTX_single_null_plasma_plasmaboundaries,
            name="NSTX_single_null_plasma_plasmaboundaries"))
    fig.show()
    fig.write_html("all_plasma_and_points.html")


if __name__ == "__main__":
    main()
