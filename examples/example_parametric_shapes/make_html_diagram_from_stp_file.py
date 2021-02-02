"""Creates a stp file and then loads up the stp file and then facets the wires
(edges) of the geometry and plots the faceted eges along with the vertices
within the stp file."""

import paramak


def main():
    # this creates a Shape object
    example_shape = paramak.ExtrudeMixedShape(
        distance=1,
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
    # This exports the Shape object as an stp file that will be imported later
    example_shape.export_stp("example_shape.stp")

    # this exports the shape as a html image
    fig = example_shape.export_html("example_shape_from_solid.html")

    # shows the html image resulting from the solid shape directly
    fig.show()

    # loads the stp file and obtains the solid 3d shape and list of wires
    # (edges)
    solid, wires = paramak.utils.load_stp_file(
        filename="example_shape.stp",
    )

    # produces a plot on the R (radius) Z axis and saves the html file
    fig = paramak.utils.export_wire_to_html(
        wires=wires,
        tolerance=0.1,
        view_plane="XZ",
        facet_splines=True,
        facet_circles=True,
        filename="example_shape_from_stp.html",
    )

    # shows the html image resulting from the stp file load
    fig.show()


if __name__ == "__main__":
    main()
