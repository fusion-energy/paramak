"""Imprints each reactor builder as cad_to_dagmc does before meshing.

DAGMC needs neighbouring volumes to share the surface between them, which is
what imprinting makes. These tests check two things on the imprinted geometry:

- no parts overlap: imprinting overlapping parts splits off the shared region
  as an extra solid, so the solid count would grow
- neighbouring parts share faces: a layer that is meant to sit against another
  but is left a sliver away, or meets it on surfaces that are only nearly
  coincident, does not imprint and would leave a gap in the DAGMC geometry

Parts that only touch along a line share no face and are hard to mesh, so the
builds avoid them. The blanket made by tokamak_from_plasma is curved on the
inboard side and would meet the centre column along a circle at the midplane,
so its build has a 2 cm gap between the two, taken off the plasma.
"""

import importlib
from collections import defaultdict
from pathlib import Path

import cadquery as cq
import pytest
from cadquery.occ_impl.assembly import imprint

import paramak

from .test_utils import transport_particles_on_h5m_geometry

L = paramak.LayerType

TOKAMAK_RADIAL_BUILD = [
    (L.GAP, 10),
    (L.SOLID, 30),
    (L.SOLID, 50),
    (L.SOLID, 10),
    (L.SOLID, 120),
    (L.SOLID, 20),
    (L.GAP, 60),
    (L.PLASMA, 300),
    (L.GAP, 60),
    (L.SOLID, 20),
    (L.SOLID, 120),
    (L.SOLID, 10),
]

# the same overall size as TOKAMAK_RADIAL_BUILD with a 2 cm gap between the
# centre column and the blanket, so the curved blanket does not touch the
# centre column along a line
TOKAMAK_FROM_PLASMA_RADIAL_BUILD = [
    *TOKAMAK_RADIAL_BUILD[:3],
    (L.GAP, 2),
    *TOKAMAK_RADIAL_BUILD[3:7],
    (L.PLASMA, 298),
    *TOKAMAK_RADIAL_BUILD[8:],
]

SPHERICAL_RADIAL_BUILD = [
    (L.GAP, 10),
    (L.SOLID, 50),
    (L.SOLID, 15),
    (L.GAP, 50),
    (L.PLASMA, 300),
    (L.GAP, 60),
    (L.SOLID, 15),
    (L.SOLID, 60),
    (L.SOLID, 10),
]

TOKAMAK_LAYERS = {("layer_1", "layer_2"), ("layer_3", "layer_4"), ("layer_4", "layer_5")}

SPHERICAL_LAYERS = {
    ("layer_1", "layer_2"),
    ("layer_2", "layer_3"),
    ("layer_2", "layer_4"),
    ("layer_2", "layer_5"),
    ("layer_3", "layer_4"),
    ("layer_4", "layer_5"),
}


def segments(arc_length, number_of_segments, gap, name):
    "equally sized solid segments, each followed by a gap"
    length = (arc_length - number_of_segments * gap) / number_of_segments
    return [(L.SOLID, length, name), (L.GAP, gap)] * number_of_segments


def tokamak_from_plasma(**kwargs):
    return paramak.tokamak_from_plasma(
        radial_build=TOKAMAK_FROM_PLASMA_RADIAL_BUILD, elongation=2, triangularity=0.55, **kwargs
    )


def spherical_tokamak_from_plasma(**kwargs):
    kwargs.setdefault("radial_build", SPHERICAL_RADIAL_BUILD)
    kwargs.setdefault("elongation", 2)
    return paramak.spherical_tokamak_from_plasma(triangularity=0.55, **kwargs)


def tokamak():
    return paramak.tokamak(
        radial_build=TOKAMAK_RADIAL_BUILD,
        vertical_build=[
            (L.SOLID, 15),
            (L.SOLID, 80),
            (L.SOLID, 10),
            (L.GAP, 50),
            (L.PLASMA, 700),
            (L.GAP, 60),
            (L.SOLID, 10),
            (L.SOLID, 40),
            (L.SOLID, 15),
        ],
        triangularity=0.55,
        rotation_angle=180,
    )


def with_divertor():
    divertor = cq.Workplane("XZ").polyline([(300, -700), (300, 0), (400, 0), (400, -700)]).close().revolve(180)
    return tokamak_from_plasma(rotation_angle=180, extra_intersect_shapes=[divertor])


def with_poloidal_segments():
    arc = paramak.poloidal_arc_length(TOKAMAK_FROM_PLASMA_RADIAL_BUILD, elongation=2, triangularity=0.55)
    return tokamak_from_plasma(rotation_angle=180, poloidal_build=[None, segments(arc, 6, 5, "row"), None, None])


def with_toroidal_sectors():
    arc = paramak.toroidal_arc_length(TOKAMAK_FROM_PLASMA_RADIAL_BUILD, rotation_angle=90)
    sectors = segments(arc, 4, 20, "sector")
    return tokamak_from_plasma(rotation_angle=90, toroidal_build=[None, sectors, sectors, None])


def with_pf_coils():
    coils = []
    for case_thickness, size, center_point in zip(
        [10, 15, 15, 10], [20, 50, 50, 20], [(500, 300), (560, 100), (560, -100), (500, -300)]
    ):
        coils.append(
            paramak.poloidal_field_coil(height=size, width=size, center_point=center_point, rotation_angle=180)
        )
        coils.append(
            paramak.poloidal_field_coil_case(
                coil_height=size,
                coil_width=size,
                casing_thickness=case_thickness,
                center_point=center_point,
                rotation_angle=180,
            )
        )
    return spherical_tokamak_from_plasma(rotation_angle=180, extra_cut_shapes=coils)


def with_tf_coils():
    coils = paramak.toroidal_field_coil_rectangle(
        horizontal_start_point=(10, 520),
        vertical_mid_point=(600, 0),
        thickness=50,
        distance=40,
        with_inner_leg=True,
        azimuthal_placement_angles=[0, 30, 60, 90],
        rotation_angle=90,
    )
    radial_build = [(L.GAP, 70), (L.SOLID, 10), (L.SOLID, 10)] + SPHERICAL_RADIAL_BUILD[3:]
    return spherical_tokamak_from_plasma(
        radial_build=radial_build, elongation=2.5, rotation_angle=90, extra_cut_shapes=[coils]
    )


def pf_coils_in_cases(count):
    return {(f"pf_coil_{i}", f"pf_coil_case_{i}") for i in range(1, count + 1)}


# (builder, pairs of parts that must share faces once imprinted)
REACTORS = {
    "tokamak_from_plasma": (lambda: tokamak_from_plasma(rotation_angle=180), TOKAMAK_LAYERS),
    # the vertical build gives the centre column and the inner blanket leg a
    # straight face in common
    "tokamak": (tokamak, TOKAMAK_LAYERS | {("layer_2", "layer_5")}),
    "divertor": (
        with_divertor,
        TOKAMAK_LAYERS | {("extra_intersect_shapes_1", layer) for layer in ("layer_3", "layer_4", "layer_5")},
    ),
    "poloidal_segments": (
        with_poloidal_segments,
        {("layer_1", "layer_2"), ("layer_4", "layer_5")} | {(f"layer_3_row_{i}", "layer_4") for i in range(1, 7)},
    ),
    "toroidal_sectors": (
        with_toroidal_sectors,
        {("layer_1", "layer_2")}
        | {(f"layer_3_sector_{i}", f"layer_4_sector_{i}") for i in range(1, 5)}
        | {(f"layer_4_sector_{i}", "layer_5") for i in range(1, 5)},
    ),
    "spherical_tokamak_from_plasma": (lambda: spherical_tokamak_from_plasma(rotation_angle=180), SPHERICAL_LAYERS),
    "spherical_pf_coils": (
        with_pf_coils,
        SPHERICAL_LAYERS
        | {(f"poloidal_field_coil_{i}", f"poloidal_field_coil_case_{i + 1}") for i in (1, 3, 5, 7)}
        | {(layer, f"poloidal_field_coil_case_{i}") for layer in ("layer_4", "layer_5") for i in (4, 6)},
    ),
    # the coils sit clear of the blanket so they only need not to overlap
    "spherical_tf_coils": (with_tf_coils, SPHERICAL_LAYERS),
    "sparc": (
        lambda: paramak.sparc_from_2020_paper(rotation_angle=180),
        pf_coils_in_cases(8)
        | {
            ("antenna", "inner_vessel"),
            ("inner_vessel", "vessel"),
            ("inner_vessel", "vs_coil_1"),
            ("inner_vessel", "vs_coil_2"),
        },
    ),
    "iter": (
        lambda: paramak.iter_from_2020_paper(rotation_angle=180),
        pf_coils_in_cases(6)
        | {("blanket", "divertor"), ("blanket", "vessel"), ("divertor", "vessel")}
        | {(f"central_solenoid_{i}", f"central_solenoid_{i + 1}") for i in range(1, 6)},
    ),
    "eu_demo": (
        lambda: paramak.eu_demo_from_2015_paper(rotation_angle=180),
        pf_coils_in_cases(6) | {("blanket", "divertor"), ("pf_coil_case_6", "toroidal_field_coil")},
    ),
    "arc": (
        lambda: paramak.arc_from_2026_paper(rotation_angle=180),
        pf_coils_in_cases(10)
        | {
            ("inner_vacuum_vessel", "tungsten_first_wall"),
            ("flibe_first_wall", "inner_vacuum_vessel"),
            ("flibe_first_wall", "outer_vacuum_vessel"),
            ("flibe_blanket", "outer_vacuum_vessel"),
            ("flibe_blanket", "neutron_shield"),
            ("flibe_blanket", "outer_blanket_wall"),
            ("neutron_shield", "outer_blanket_wall"),
        },
    ),
}


@pytest.fixture(scope="module", params=list(REACTORS))
def imprinted(request):
    "(part names, solid count, imprinted solid origins, pairs of parts sharing a face)"
    build, expected_pairs = REACTORS[request.param]
    reactor = build()

    names = [name.split("/")[-1] for _, name, _, _ in reactor]
    solid_count = sum(len(obj.moved(loc).Solids()) for obj, _, loc, _ in reactor)

    shape, origins = imprint(reactor)

    parts_on_face = defaultdict(set)
    for solid, solid_origins in origins.items():
        for face in solid.Faces():
            parts_on_face[face].update(origin.split("/")[-1] for origin in solid_origins)
    shared = {tuple(sorted(parts)) for parts in parts_on_face.values() if len(parts) == 2}

    return names, solid_count, shape, origins, shared, expected_pairs


def test_imprinting_adds_no_solids(imprinted):
    "overlapping parts would gain a solid for the region they share"
    _names, solid_count, shape, origins, _shared, _expected = imprinted
    assert len(shape.Solids()) == solid_count
    overlaps = [solid_origins for solid_origins in origins.values() if len(solid_origins) > 1]
    assert overlaps == []


def test_neighbouring_parts_share_faces(imprinted):
    names, _solid_count, _shape, _origins, shared, expected_pairs = imprinted
    # the expected pairs name real parts, so a renamed part fails here rather
    # than passing without checking anything
    assert {name for pair in expected_pairs for name in pair} <= set(names)
    missing = {tuple(sorted(pair)) for pair in expected_pairs} - shared
    assert missing == set(), f"parts that should touch but share no face: {sorted(missing)}"


def test_tokamak_from_plasma_blanket_clears_centre_column():
    "the 2 cm gap in the build keeps the curved blanket off the centre column"
    reactor = tokamak_from_plasma(rotation_angle=180)
    parts = {name.split("/")[-1]: obj.moved(loc) for obj, name, loc, _ in reactor}
    assert parts["layer_2"].distance(parts["layer_5"]) == pytest.approx(2, abs=1e-6)


# mesh sizes (cm) for reactors with parts too thin for the default (5, 50),
# such as the 0.5 cm tungsten first wall of ARC
MESH_SIZES = {"arc": (1, 20)}


@pytest.mark.parametrize("reactor", list(REACTORS))
@pytest.mark.skipif(not importlib.util.find_spec("cad_to_dagmc"), reason="Skipping transport tests")
def test_transport(reactor, tmp_path, monkeypatch):
    """Meshes the reactor into a DAGMC geometry and transports neutrons through
    it with OpenMC. Overlapping or badly imprinted volumes lose particles, and
    OpenMC stops with an error when more than a few are lost."""
    from cad_to_dagmc import CadToDagmc

    cross_sections_xml = str(Path(__file__).parents[1] / "cross_sections.xml")
    monkeypatch.chdir(tmp_path)

    build, _expected_pairs = REACTORS[reactor]
    assembly = build()
    # one tag per solid, as a part can be several solids (the PF coils cut the
    # outer layer of the spherical tokamak in three). Tags are numbered by part
    # to keep them short, as the 28 character mat_extra_intersect_shapes_1
    # comes back from the h5m file as mat_extra_intersect_shapes_10.
    material_tags = [f"mat_{index}" for index, (obj, *_) in enumerate(assembly) for _ in obj.Solids()]

    my_model = CadToDagmc()
    my_model.add_cadquery_object(cadquery_object=assembly, material_tags=material_tags)
    min_mesh_size, max_mesh_size = MESH_SIZES.get(reactor, (5, 50))
    my_model.export_dagmc_h5m_file(filename="dagmc.h5m", min_mesh_size=min_mesh_size, max_mesh_size=max_mesh_size)

    flux = transport_particles_on_h5m_geometry(
        h5m_filename="dagmc.h5m",
        material_tags=material_tags,
        nuclides=["H1"] * len(set(material_tags)),
        cross_sections_xml=cross_sections_xml,
    )
    assert flux > 0.0
