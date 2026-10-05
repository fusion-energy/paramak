import importlib
import math
from pathlib import Path

import cadquery as cq
import pytest

import paramak

from .test_utils import transport_particles_on_h5m_geometry


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
    my_reactor.export(f"spherical_tokamak_with_magnets_{rotation_angle}.step")
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
    reactor.export("spherical_tokamak.step")

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

SPHERICAL_RADIAL_BUILD = [
    (paramak.LayerType.GAP, 10),
    (paramak.LayerType.SOLID, 50),
    (paramak.LayerType.SOLID, 15),
    (paramak.LayerType.GAP, 50),
    (paramak.LayerType.PLASMA, 300),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.SOLID, 15),  # first wall
    (paramak.LayerType.SOLID, 60),  # blanket
    (paramak.LayerType.SOLID, 10),  # rear wall
]


def volumes(assembly):
    return {child.name: child.toCompound().Volume() for child in assembly.children}


def equal_segments(arc_length, number_of_segments, gap, name="module"):
    "a poloidal_build entry of equally sized segments separated by gaps"
    segment = (arc_length - number_of_segments * gap) / number_of_segments
    return [(paramak.LayerType.SOLID, segment, name), (paramak.LayerType.GAP, gap)] * number_of_segments


def test_spherical_poloidal_arc_length_circular_plasma():
    "the path is the bottom of the layer, half a circle around the outboard side and the top of the layer"

    arc_length = paramak.spherical_poloidal_arc_length(SPHERICAL_RADIAL_BUILD, elongation=1.0, triangularity=0.0)

    minor_radius = 150
    major_radius = 10 + 50 + 15 + 50 + minor_radius
    column_radius = 10 + 50 + 15
    gap_to_plasma = 60
    expected = math.pi * (minor_radius + gap_to_plasma) + 2 * (major_radius - column_radius)
    assert arc_length == pytest.approx(expected, rel=1e-6)


def test_spherical_poloidal_arc_length_with_vertical_build():
    "the vertical build sets the elongation"

    vertical_build = [
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 10),
    ]
    # the plasma height equals the plasma width so the elongation is 1
    from_vertical_build = paramak.spherical_poloidal_arc_length(
        SPHERICAL_RADIAL_BUILD, triangularity=0.0, vertical_build=vertical_build
    )
    from_elongation = paramak.spherical_poloidal_arc_length(
        SPHERICAL_RADIAL_BUILD, elongation=1.0, triangularity=0.0
    )
    assert from_vertical_build == pytest.approx(from_elongation)

    with pytest.raises(ValueError, match="elongation can not be set"):
        paramak.spherical_poloidal_arc_length(SPHERICAL_RADIAL_BUILD, elongation=2.0, vertical_build=vertical_build)


def test_spherical_poloidal_build_names_and_volumes():
    "segments without gaps fill the same volume as the unsegmented layers"

    arc_length = paramak.spherical_poloidal_arc_length(SPHERICAL_RADIAL_BUILD)
    number_of_modules = 6
    modules = equal_segments(arc_length, number_of_modules, gap=0)

    unsegmented = paramak.spherical_tokamak_from_plasma(radial_build=SPHERICAL_RADIAL_BUILD, rotation_angle=90)
    segmented = paramak.spherical_tokamak_from_plasma(
        radial_build=SPHERICAL_RADIAL_BUILD, rotation_angle=90, poloidal_build=[None, modules, modules, None]
    )

    assert segmented.names() == [
        "layer_1",
        "layer_2",
        *[f"layer_3_module_{i}" for i in range(1, number_of_modules + 1)],
        *[f"layer_4_module_{i}" for i in range(1, number_of_modules + 1)],
        "layer_5",
        "plasma",
    ]
    unsegmented_volumes = volumes(unsegmented)
    segmented_volumes = volumes(segmented)
    for layer in ["layer_3", "layer_4"]:
        segment_volume = sum(value for name, value in segmented_volumes.items() if name.startswith(f"{layer}_"))
        assert segment_volume == pytest.approx(unsegmented_volumes[layer], rel=1e-6)
    for name in ["layer_1", "layer_2", "layer_5", "plasma"]:
        assert segmented_volumes[name] == pytest.approx(unsegmented_volumes[name])
    for child in segmented.children:
        assert child.toCompound().isValid()


def test_spherical_poloidal_build_gaps_and_single_segment():
    "gaps remove volume, and a single segment covering the whole path is the full layer"

    arc_length = paramak.spherical_poloidal_arc_length(SPHERICAL_RADIAL_BUILD)
    segmented = paramak.spherical_tokamak_from_plasma(
        radial_build=SPHERICAL_RADIAL_BUILD,
        rotation_angle=90,
        poloidal_build=[None, equal_segments(arc_length, 4, gap=30), None, [(paramak.LayerType.SOLID, arc_length, "rear")]],
    )
    unsegmented = volumes(paramak.spherical_tokamak_from_plasma(radial_build=SPHERICAL_RADIAL_BUILD, rotation_angle=90))
    segmented_volumes = volumes(segmented)
    segment_volume = sum(value for name, value in segmented_volumes.items() if name.startswith("layer_3_"))
    assert segment_volume < unsegmented["layer_3"]
    assert segmented_volumes["layer_5_rear"] == pytest.approx(unsegmented["layer_5"], rel=1e-6)


def test_spherical_same_segments_line_up():
    "layers given the same segments start and stop at the same positions along the path"

    from paramak.assemblies.spherical_tokamak import (
        get_spherical_poloidal_build_segment_positions,
        spherical_vertical_build_from_radial_build,
    )

    arc_length = paramak.spherical_poloidal_arc_length(SPHERICAL_RADIAL_BUILD)
    modules = equal_segments(arc_length, number_of_segments=8, gap=15)
    positions = get_spherical_poloidal_build_segment_positions(
        [None, modules, modules, modules],
        SPHERICAL_RADIAL_BUILD,
        spherical_vertical_build_from_radial_build(SPHERICAL_RADIAL_BUILD, 2.0),
        0.55,
    )
    assert positions[0] is None
    assert positions[1] == positions[2] == positions[3]
    # the first segment starts at the centre column at the bottom and the last ends at the top
    assert positions[1][0][1] == pytest.approx(0.0)


def test_spherical_poloidal_build_with_named_layer_and_spherical_tokamak():
    "segment names use the layer name from the radial build, and spherical_tokamak() supports poloidal_build"

    radial_build = [
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.GAP, 50),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 60, "blanket"),
    ]
    vertical_build = [
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 700),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 60),
    ]
    arc_length = paramak.spherical_poloidal_arc_length(radial_build, vertical_build=vertical_build)
    reactor = paramak.spherical_tokamak(
        radial_build=radial_build,
        vertical_build=vertical_build,
        rotation_angle=90,
        poloidal_build=[None, [(paramak.LayerType.SOLID, arc_length / 2, "lower"), (paramak.LayerType.SOLID, arc_length / 2, "upper")]],
    )
    assert reactor.names() == ["layer_1", "blanket_lower", "blanket_upper", "plasma"]


@pytest.mark.parametrize(
    "poloidal_build, error, match",
    [
        ([None, None], ValueError, "expected 4 entries but got 2"),
        ([[(paramak.LayerType.SOLID, 1)], None, None, None], ValueError, "corresponds to a LayerType.GAP"),
        ([None, [(paramak.LayerType.SOLID, 1)], None, None], ValueError, "Use paramak.spherical_poloidal_arc_length"),
        ([None, [(paramak.LayerType.SOLID, -1)], None, None], ValueError, "positive arc_length"),
        ("not a list", TypeError, "must be a list"),
    ],
)
def test_spherical_poloidal_build_validation(poloidal_build, error, match):
    with pytest.raises(error, match=match):
        paramak.spherical_tokamak_from_plasma(
            radial_build=SPHERICAL_RADIAL_BUILD, rotation_angle=90, poloidal_build=poloidal_build
        )


def test_spherical_poloidal_build_with_divertor():
    "the divertor is the same with and without segmentation and is cut out of the segments"

    divertor = cq.Workplane("XZ").polyline([(200, -700), (200, 0), (300, 0), (300, -700)]).close().revolve(90)
    arc_length = paramak.spherical_poloidal_arc_length(SPHERICAL_RADIAL_BUILD)
    modules = equal_segments(arc_length, number_of_segments=6, gap=0)

    unsegmented = volumes(
        paramak.spherical_tokamak_from_plasma(
            radial_build=SPHERICAL_RADIAL_BUILD, rotation_angle=90, extra_intersect_shapes=[divertor]
        )
    )
    segmented = paramak.spherical_tokamak_from_plasma(
        radial_build=SPHERICAL_RADIAL_BUILD,
        rotation_angle=90,
        extra_intersect_shapes=[divertor],
        poloidal_build=[None, modules, modules, None],
    )
    segmented_volumes = volumes(segmented)
    assert segmented_volumes["extra_intersect_shapes_1"] == pytest.approx(
        unsegmented["extra_intersect_shapes_1"], rel=1e-3
    )
    assert segmented_volumes["extra_intersect_shapes_1"] > 0

    def total(volume_dict):
        return sum(value for name, value in volume_dict.items() if name != "plasma")

    assert total(segmented_volumes) == pytest.approx(total(unsegmented), rel=1e-3)
    for child in segmented.children:
        assert child.toCompound().isValid()
