"""
This python script demonstrates the creation of all parametric shapes available
in the paramak tool
"""

from make_all_parametric_components import main


def export_images():

    all_componets = main()

    for componet in all_componets:
        componet.workplane = "XY"
        componet.export_svg(componet.stp_filename[:-3] + "svg")


if __name__ == "__main__":
    export_images()
