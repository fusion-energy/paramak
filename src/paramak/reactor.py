from pathlib import Path
from typing import List, Optional, Tuple, Union

import cadquery as cq
import matplotlib.pyplot as plt
from cadquery import exporters

import paramak
from paramak.utils import (
    _replace,
    export_solids_to_brep,
    export_solids_to_dagmc_h5m,
)

import typing
from cadquery.occ_impl.geom import Location
from cadquery.occ_impl.assembly import Color


def export_dagmc_h5m(
    self,
    filename: str = "dagmc.h5m",
    min_mesh_size: float = 5,
    max_mesh_size: float = 20,
    verbose: bool = False,
    volume_atol: float = 0.000001,
    center_atol: float = 0.000001,
    bounding_box_atol: float = 0.000001,
    tags: typing.Optional[typing.Iterable[str]] = None,
) -> str:
    """Export a DAGMC compatible h5m file for use in neutronics simulations.
    This method makes use of Gmsh to create a surface mesh of the geometry.
    MOAB is used to convert the meshed geometry into a h5m with parts tagged by
    using the reactor.shape_and_components.name properties. You will need
    Gmsh installed and MOAB installed to use this function. Acceptable
    tolerances may need increasing to match reactor parts with the parts
    in the intermediate Brep file produced during the process

    Args:
        filename: the filename of the DAGMC h5m file to write
        min_mesh_size: the minimum mesh element size to use in Gmsh. Passed
            into gmsh.option.setNumber("Mesh.MeshSizeMin", min_mesh_size)
        max_mesh_size: the maximum mesh element size to use in Gmsh. Passed
            into gmsh.option.setNumber("Mesh.MeshSizeMax", max_mesh_size)
        volume_atol: the absolute volume tolerance to allow when matching
            parts in the intermediate brep file with the cadquery parts
        center_atol: the absolute center coordinates tolerance to allow
            when matching parts in the intermediate brep file with the
            cadquery parts
        bounding_box_atol: the absolute volume tolerance to allow when
            matching parts in the intermediate brep file with the cadquery
            parts
        tags: the dagmc tag to use in when naming the shape in the h5m file.
            If left as None then the Shape.name will be used. This allows
            the DAGMC geometry created to be compatible with a wider range
            of neutronics codes that have specific DAGMC tag requirements.
    """

    output_filename = export_solids_to_dagmc_h5m(
        solids=self,
        filename=filename,
        min_mesh_size=min_mesh_size,
        max_mesh_size=max_mesh_size,
        verbose=verbose,
        volume_atol=volume_atol,
        center_atol=center_atol,
        bounding_box_atol=bounding_box_atol,
        tags=[child.name for child in self.children],
    )

    return output_filename


# patches cadquery assembly to have this addtional function
cq.assembly.Assembly.export_dagmc_h5m = export_dagmc_h5m
