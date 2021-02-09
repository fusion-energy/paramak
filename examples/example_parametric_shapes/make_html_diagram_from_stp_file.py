"""Creates a stp file and then loads up the stp file and then facets the wires
(edges) of the geometry and plots the faceted eges along with the vertices
within the stp file."""

import paramak


def make_stp_file():
    """Creates an example stp file for plotting html point graphs"""

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

    # this exports the shape as a html image with a few different view planes
    example_shape.export_html("example_shape_RZ.html")
    example_shape.export_html("example_shape_XYZ.html", view_plane='XYZ')
    example_shape.export_html("example_shape_XZ.html", view_plane='XZ')
    
    # This exports the Shape object as an stp file that will be imported later
    example_shape.export_stp("example_shape.stp")


def load_stp_file_and_plot():
    """Loads an stp file and plots html point graphs"""

    # loads the stp file and obtains the solid shape and list of wires / edges
    solid, wires = paramak.utils.load_stp_file(
        filename="example_shape.stp",
    )

    # produces a plot on the R (radius) Z axis and saves the html file
    paramak.utils.export_wire_to_html(
        wires=wires,
        tolerance=0.1,
        view_plane="RZ",
        facet_splines=True,
        facet_circles=True,
        filename="example_shape_from_stp_RZ.html",
    )

    # produces a plot on the XZ axis and saves the html file
    paramak.utils.export_wire_to_html(
        wires=wires,
        tolerance=0.1,
        view_plane="XZ",
        facet_splines=True,
        facet_circles=True,
        filename="example_shape_from_stp_XZ.html",
    )

    # produces a 3D plot with XYZ axis and saves the html file
    paramak.utils.export_wire_to_html(
        wires=wires,
        tolerance=0.1,
        view_plane="XYZ",
        facet_splines=True,
        facet_circles=True,
        filename="example_shape_from_stp_XYZ.html",
    )


if __name__ == "__main__":
    make_stp_file()
    load_stp_file_and_plot()