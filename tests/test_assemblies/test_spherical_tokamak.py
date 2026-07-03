from pathlib import Path

import pytest

import paramak

from .test_utils import transport_particles_on_h5m_geometry

import importlib


@pytest.mark.parametrize("rotation_angle", [30, 180])
@pytest.mark.skipif(not importlib.util.find_spec("cad_to_dagmc"), reason="Skipping transport tests")
def test_transport_with_magnets(rotation_angle):
    from cad_to_dagmc import CadToDagmc

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
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 10),
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=rotation_angle,
        extra_cut_shapes=poloidal_field_coils,
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


@pytest.mark.skipif(not importlib.util.find_spec("cad_to_dagmc"), reason="Skipping transport tests")
def test_transport_without_magnets():
    from cad_to_dagmc import CadToDagmc

    reactor = paramak.spherical_tokamak_from_plasma(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 10),
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

def test_colors():
    "passing in the colors dictionary should not raise an error"
    paramak.spherical_tokamak_from_plasma(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=180,
        colors={
            "layer_1": (0.4, 0.9, 0.4),
            "layer_2": (0.6, 0.8, 0.6),
            "plasma": (1., 0.7, 0.8, 0.6),
            "layer_3": (0.1, 0.1, 0.9),
            "layer_4": (0.4, 0.4, 0.8),
            "layer_5": (0.5, 0.5, 0.8),
        },
    )

def test_attributes():
    "passing in the colors dictionary should not raise an error"
    my_reactor = paramak.spherical_tokamak_from_plasma(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=180,
    )

    assert my_reactor.elongation == 2
    assert my_reactor.triangularity == 0.55
    assert my_reactor.major_radius == 275
    assert my_reactor.minor_radius == 150


def test_named_layers_spherical_tokamak():
    "layers can be named in the radial_build, or with rename() after building"

    from_radial_build = paramak.spherical_tokamak_from_plasma(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 50, "central column"),
            (paramak.LayerType.SOLID, 15, "tf coil"),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10, "first wall"),
            (paramak.LayerType.SOLID, 30, "blanket"),
        ],
        rotation_angle=180,
    )
    assert from_radial_build.names() == ["central column", "tf coil", "first wall", "blanket", "plasma"]

    renamed = (
        paramak.spherical_tokamak_from_plasma(
            radial_build=[
                (paramak.LayerType.GAP, 10),
                (paramak.LayerType.SOLID, 50),
                (paramak.LayerType.SOLID, 15),
                (paramak.LayerType.GAP, 50),
                (paramak.LayerType.PLASMA, 300),
                (paramak.LayerType.GAP, 60),
                (paramak.LayerType.SOLID, 10),
                (paramak.LayerType.SOLID, 30),
            ],
            rotation_angle=180,
        )
        .rename("layer_1", "central column")
        .rename("layer_2", "tf coil")
        .rename("layer_3", "first wall")
        .rename("layer_4", "blanket")
    )
    assert renamed.names() == ["central column", "tf coil", "first wall", "blanket", "plasma"]