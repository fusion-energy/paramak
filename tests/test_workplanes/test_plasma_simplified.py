from pathlib import Path

import cadquery as cq
import pytest
from cad_to_dagmc import CadToDagmc

import paramak

from .utils import transport_particles_on_h5m_geometry


@pytest.mark.parametrize("rotation_angle", [30, 90, 180, 360])
def test_creation_different_angles(rotation_angle):
    test_shape = paramak.plasma_simplified(rotation_angle=rotation_angle)

    cq.exporters.export(test_shape, f"plasma_simplified_{rotation_angle}.step")

    assert Path(f"plasma_simplified_{rotation_angle}.step").exists()


@pytest.mark.parametrize("rotation_angle", [60, 360])
def test_transport_different_angles(rotation_angle):
    test_shape = paramak.plasma_simplified(rotation_angle=rotation_angle)

    my_model = CadToDagmc()
    material_tags = ["mat1"]
    my_model.add_cadquery_object(
        cadquery_object=test_shape,
        material_tags=material_tags,
    )

    h5m_filename = "dagmc.h5m"
    my_model.export_dagmc_h5m_file(
        filename=h5m_filename,
        min_mesh_size=10,
        max_mesh_size=200,
    )

    flux = transport_particles_on_h5m_geometry(
        h5m_filename=h5m_filename,
        material_tags=material_tags,
        nuclides=["H1"],
        cross_sections_xml="tests/cross_sections.xml",
    )
    assert flux > 0.0
