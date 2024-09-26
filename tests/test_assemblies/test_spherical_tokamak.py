from pathlib import Path

import pytest
from cad_to_dagmc import CadToDagmc

import paramak

from .test_utils import transport_particles_on_h5m_geometry


@pytest.mark.parametrize("rotation_angle", [30, 360])
def test_transport_with_magnets(rotation_angle):
    poloidal_field_coils = []
    for case_thickness, height, width, center_point in zip(
        [10, 15],
        [20, 50],
        [20, 50],
        [(500, 300), (590, 100)],
    ):
        poloidal_field_coils.append(
            paramak.poloidal_field_coil(
                height=height, width=width, center_point=center_point, rotation_angle=rotation_angle
            )
        )
        poloidal_field_coils.append(
            paramak.poloidal_field_coil_case(
                coil_height=height,
                coil_width=width,
                casing_thickness=case_thickness,
                rotation_angle=rotation_angle,
                center_point=center_point,
            )
        )

    my_reactor = paramak.spherical_tokamak_from_plasma(
        radial_builds=[
            ("gap", 10),
            ("layer", 50),
            ("layer", 15),
            ("gap", 50),
            ("plasma", 300),
            ("gap", 60),
            ("layer", 15),
            ("layer", 60),
            ("layer", 10),
            ("gap", 10),
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=rotation_angle,
        add_extra_cut_shapes=poloidal_field_coils,
    )
    my_reactor.save(f"spherical_tokamak_with_magnets_{rotation_angle}.step")
    assert Path(f"spherical_tokamak_with_magnets_{rotation_angle}.step").exists()

    my_model = CadToDagmc()
    material_tags = ["mat1"] * 11  # rear wall is being split into 2 parts by the magnet that is cut out
    my_model.add_cadquery_object(cadquery_object=my_reactor, material_tags=material_tags)
    my_model.export_dagmc_h5m_file(min_mesh_size=2, max_mesh_size=30.0)

    h5m_filename = "dagmc.h5m"
    flux = transport_particles_on_h5m_geometry(
        h5m_filename=h5m_filename,
        material_tags=material_tags,
        nuclides=["H1"] * len(material_tags),
        cross_sections_xml="tests/cross_sections.xml",
    )
    assert flux > 0.0


def test_transport_without_magnets():
    reactor = paramak.spherical_tokamak_from_plasma(
        radial_builds=[
            ("gap", 10),
            ("layer", 50),
            ("layer", 15),
            ("gap", 50),
            ("plasma", 300),
            ("gap", 60),
            ("layer", 15),
            ("layer", 60),
            ("layer", 10),
            ("gap", 10),
        ],
        elongation=2,
        triangularity=0.55,
    )
    reactor.save("spherical_tokamak.step")

    my_model = CadToDagmc()
    material_tags = ["mat1"] * 6
    my_model.add_cadquery_object(cadquery_object=reactor, material_tags=material_tags)

    my_model.export_dagmc_h5m_file(filename="dagmc.h5m", min_mesh_size=10.0, max_mesh_size=100.0)

    flux = transport_particles_on_h5m_geometry(
        h5m_filename="dagmc.h5m",
        material_tags=material_tags,
        nuclides=["H1"] * len(material_tags),
        cross_sections_xml="tests/cross_sections.xml",
    )
    assert flux > 0.0