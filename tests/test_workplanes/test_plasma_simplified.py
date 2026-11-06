import importlib
from pathlib import Path

import cadquery as cq
import pytest

import paramak

from .utils import transport_particles_on_h5m_geometry


@pytest.mark.parametrize("rotation_angle", [30, 90, 180, 360])
def test_creation_different_angles(rotation_angle):
    test_shape = paramak.plasma_simplified(rotation_angle=rotation_angle)

    cq.exporters.export(test_shape, f"plasma_simplified_{rotation_angle}.step")

    assert Path(f"plasma_simplified_{rotation_angle}.step").exists()


@pytest.mark.parametrize("rotation_angle", [60, 360])
@pytest.mark.skipif(
    not (importlib.util.find_spec("cad_to_dagmc") and importlib.util.find_spec("openmc")),
    reason="transport tests need cad_to_dagmc and openmc, install them with the transport extra",
)
def test_transport_different_angles(rotation_angle):
    from cad_to_dagmc import CadToDagmc

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


def test_full_rotation_is_centred_on_the_z_axis():
    full = paramak.plasma_simplified(major_radius=450, minor_radius=150, rotation_angle=360)
    half = paramak.plasma_simplified(major_radius=450, minor_radius=150, rotation_angle=180)
    bb = full.val().BoundingBox()
    assert bb.xmin == pytest.approx(-600, abs=1e-3)
    assert bb.xmax == pytest.approx(600, abs=1e-3)
    assert bb.ymin == pytest.approx(-600, abs=1e-3)
    assert bb.ymax == pytest.approx(600, abs=1e-3)
    assert full.val().Volume() == pytest.approx(2 * half.val().Volume(), rel=1e-6)
