"""
This python script demonstrates the creation of all parametric shapes available
in the paramak tool
"""

import os
import paramak
from make_all_parametric_reactors import main
from cadquery import exporters


def export_images():

    all_reactors = main()

    for reactor in all_reactors:
        with open(reactor.name + ".svg", "w") as f:
            exporters.exportShape(reactor.solid, "SVG", f)

        reactor.export_stp(output_folder=reactor.name)


if __name__ == "__main__":
    export_images()
