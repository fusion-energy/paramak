import importlib
import inspect
import math

import cadquery as cq
from collections import defaultdict
from pathlib import Path

import pytest
from cadquery.occ_impl.assembly import imprint

import paramak

from .test_utils import transport_particles_on_h5m_geometry

PAPER_REACTORS = [
    paramak.sparc_from_2020_paper,
    paramak.iter_from_2020_paper,
    paramak.eu_demo_from_2015_paper,
    paramak.arc_from_2026_paper,
]

# mesh sizes (cm) suited to the size of each reactor
MESH_SIZES = {
    paramak.arc_from_2026_paper: (1, 20),
    paramak.sparc_from_2020_paper: (2, 20),
    paramak.iter_from_2020_paper: (5, 80),
    paramak.eu_demo_from_2015_paper: (5, 100),
}

EXPECTED_PARTS = {
    paramak.arc_from_2026_paper: [
        "plasma",
        "central_solenoid_1",
        "pf_coil_1",
        "pf_coil_case_1",
        "toroidal_field_coil",
        "tungsten_first_wall",
        "inner_vacuum_vessel",
        "outer_vacuum_vessel",
        "neutron_shield",
        "flibe_first_wall",
        "flibe_blanket",
        "outer_blanket_wall",
    ],
    paramak.sparc_from_2020_paper: [
        "plasma",
        "vessel",
        "inner_vessel",
        "antenna",
        "toroidal_field_coil",
        "pf_coil_1",
        "pf_coil_case_1",
    ],
    paramak.iter_from_2020_paper: [
        "plasma",
        "blanket",
        "divertor",
        "vessel",
        "toroidal_field_coil",
        "pf_coil_1",
        "pf_coil_case_1",
    ],
    paramak.eu_demo_from_2015_paper: [
        "plasma",
        "blanket",
        "divertor",
        "vessel",
        "toroidal_field_coil",
        "pf_coil_1",
        "pf_coil_case_1",
    ],
}


def part_volumes(reactor):
    return {name.split("/")[-1]: shape.Volume() for shape, name, _loc, _color in reactor}


@pytest.fixture(scope="module", params=PAPER_REACTORS, ids=lambda f: f.__name__)
def reactor_function_and_180_degree_reactor(request):
    return request.param, request.param(rotation_angle=180)


def test_expected_parts(reactor_function_and_180_degree_reactor):
    reactor_function, reactor = reactor_function_and_180_degree_reactor
    names = reactor.names()
    for name in EXPECTED_PARTS[reactor_function]:
        assert name in names
    assert len(names) == len(set(names))


def test_solids_are_valid_with_positive_volume(reactor_function_and_180_degree_reactor):
    _, reactor = reactor_function_and_180_degree_reactor
    for shape, name, _loc, _color in reactor:
        assert shape.isValid(), name
        assert shape.Volume() > 0, name


def test_plasma_metadata(reactor_function_and_180_degree_reactor):
    _, reactor = reactor_function_and_180_degree_reactor
    assert reactor.major_radius > reactor.minor_radius > 0
    assert reactor.elongation > 1
    assert 0 < reactor.triangularity < 1


def test_plasma_metadata_matches_the_plasma(reactor_function_and_180_degree_reactor):
    """The plasma parameters on the assembly describe the plasma that was built."""
    _, reactor = reactor_function_and_180_degree_reactor
    plasma = reactor.objects["plasma"].obj.val().BoundingBox()
    # the outboard and inboard midplane points of the plasma
    assert plasma.xmax == pytest.approx(reactor.major_radius + reactor.minor_radius, abs=0.1)
    assert plasma.xmin == pytest.approx(-(reactor.major_radius + reactor.minor_radius), abs=0.1)
    height = plasma.zmax - plasma.zmin
    assert height == pytest.approx(2 * reactor.elongation * reactor.minor_radius, rel=1e-3)


@pytest.mark.parametrize("reactor_function", PAPER_REACTORS, ids=lambda f: f.__name__)
def test_smaller_rotation_angle_gives_smaller_volumes(reactor_function):
    volumes_90 = part_volumes(reactor_function(rotation_angle=90))
    volumes_180 = part_volumes(reactor_function(rotation_angle=180))
    assert volumes_90.keys() == volumes_180.keys()
    # the axisymmetric parts are half the volume, the tolerance allows for the
    # approximate volume calculation of revolved spline surfaces
    vessel_names = [name for name in volumes_90 if "vessel" in name]
    assert vessel_names
    for name in ["plasma", *vessel_names]:
        assert volumes_90[name] == pytest.approx(volumes_180[name] / 2, rel=5e-2)
    assert sum(volumes_90.values()) < sum(volumes_180.values())


@pytest.mark.parametrize("reactor_function", PAPER_REACTORS, ids=lambda f: f.__name__)
def test_colors_override_defaults(reactor_function):
    reactor = reactor_function(rotation_angle=10, colors={"plasma": (0.1, 0.2, 0.3)})
    plasma_color = [color for _shape, name, _loc, color in reactor if name.endswith("/plasma")][0]
    assert plasma_color.toTuple()[:3] == pytest.approx((0.1, 0.2, 0.3))


@pytest.mark.parametrize("reactor_function", PAPER_REACTORS, ids=lambda f: f.__name__)
@pytest.mark.parametrize("rotation_angle", [0, -10, 361])
def test_invalid_rotation_angle(reactor_function, rotation_angle):
    with pytest.raises(ValueError, match="rotation_angle"):
        reactor_function(rotation_angle=rotation_angle)


@pytest.mark.parametrize("reactor_function", PAPER_REACTORS, ids=lambda f: f.__name__)
@pytest.mark.parametrize("number_of_tf_coils", [0, -1, 2.5, True])
def test_invalid_number_of_tf_coils(reactor_function, number_of_tf_coils):
    with pytest.raises(ValueError, match="number_of_tf_coils"):
        reactor_function(number_of_tf_coils=number_of_tf_coils)


def test_pf_coils_have_a_winding_pack_and_case(reactor_function_and_180_degree_reactor):
    """Each poloidal field coil is a winding pack and a case, which together
    fill the outer coil size from the paper."""
    _, reactor = reactor_function_and_180_degree_reactor
    volumes = part_volumes(reactor)
    shapes = {name.split("/")[-1]: shape for shape, name, _loc, _color in reactor}
    pf_coil_numbers = [name.split("_")[-1] for name in volumes if name.startswith("pf_coil_case_")]
    assert pf_coil_numbers
    for number in pf_coil_numbers:
        core, case = shapes[f"pf_coil_{number}"], shapes[f"pf_coil_case_{number}"]
        assert core.Volume() > 0 and case.Volume() > 0
        core_box, case_box = core.BoundingBox(), case.BoundingBox()
        # the case surrounds the winding pack
        assert case_box.zmin < core_box.zmin and case_box.zmax > core_box.zmax
        assert case_box.xmax > core_box.xmax
        # together they make a solid rectangular ring with no gap
        assert core.fuse(case).Volume() == pytest.approx(core.Volume() + case.Volume(), rel=1e-6)


@pytest.mark.parametrize("reactor_function", PAPER_REACTORS, ids=lambda f: f.__name__)
def test_pf_coil_case_thickness_changes_the_split_not_the_coil_size(reactor_function):
    thin = part_volumes(reactor_function(rotation_angle=10, pf_coil_case_thickness=1))
    thick = part_volumes(reactor_function(rotation_angle=10, pf_coil_case_thickness=5))
    assert thick["pf_coil_case_1"] > thin["pf_coil_case_1"]
    if reactor_function is paramak.arc_from_2026_paper:
        # the ARC data gives the winding pack size, the case is added around it
        assert thick["pf_coil_1"] == pytest.approx(thin["pf_coil_1"], rel=1e-6)
        return
    assert thick["pf_coil_1"] < thin["pf_coil_1"]
    assert thick["pf_coil_1"] + thick["pf_coil_case_1"] == pytest.approx(
        thin["pf_coil_1"] + thin["pf_coil_case_1"], rel=1e-6
    )


@pytest.mark.parametrize("reactor_function", PAPER_REACTORS, ids=lambda f: f.__name__)
@pytest.mark.parametrize("pf_coil_case_thickness", [0, -1, float("nan"), float("inf"), 1000])
def test_invalid_pf_coil_case_thickness(reactor_function, pf_coil_case_thickness):
    with pytest.raises(ValueError, match="pf_coil_case_thickness"):
        reactor_function(pf_coil_case_thickness=pf_coil_case_thickness)


@pytest.mark.parametrize("reactor_function", PAPER_REACTORS, ids=lambda f: f.__name__)
@pytest.mark.parametrize("rotation_angle", [30, 180, 360])
@pytest.mark.skipif(not importlib.util.find_spec("cad_to_dagmc"), reason="Skipping transport tests")
def test_transport(reactor_function, rotation_angle, tmp_path, monkeypatch):
    """Meshes the reactor into a DAGMC geometry and transports neutrons through
    it with OpenMC. This also checks the parts do not overlap, as overlapping
    volumes cause lost particles and OpenMC stops with an error when more than
    a few particles are lost."""
    from cad_to_dagmc import CadToDagmc

    cross_sections_xml = str(Path(__file__).parents[1] / "cross_sections.xml")
    monkeypatch.chdir(tmp_path)

    reactor = reactor_function(rotation_angle=rotation_angle)
    # A named component can contain multiple solids, such as ARC's TF coils.
    material_tags = [f"mat_{name.split('/')[-1]}" for shape, name, _loc, _color in reactor for _solid in shape.Solids()]

    my_model = CadToDagmc()
    my_model.add_cadquery_object(cadquery_object=reactor, material_tags=material_tags)
    min_mesh_size, max_mesh_size = MESH_SIZES[reactor_function]
    my_model.export_dagmc_h5m_file(
        filename="dagmc.h5m",
        min_mesh_size=min_mesh_size,
        max_mesh_size=max_mesh_size,
    )

    flux = transport_particles_on_h5m_geometry(
        h5m_filename="dagmc.h5m",
        material_tags=material_tags,
        nuclides=["H1"] * len(set(material_tags)),
        cross_sections_xml=cross_sections_xml,
    )
    assert flux > 0.0


def test_eu_demo_vessel_sits_against_the_blanket_and_divertor():
    """The vessel is in contact with the blanket and divertor and shares the
    surfaces between them once imprinted, as DAGMC needs."""
    reactor = paramak.eu_demo_from_2015_paper(rotation_angle=180)
    shapes = {name.split("/")[-1]: shape.moved(loc) for shape, name, loc, _color in reactor}
    assert shapes["vessel"].distance(shapes["blanket"]) == pytest.approx(0, abs=1e-6)
    assert shapes["vessel"].distance(shapes["divertor"]) == pytest.approx(0, abs=1e-6)

    _, origins = imprint(reactor)
    parts_on_face = defaultdict(set)
    for solid, solid_origins in origins.items():
        assert len(solid_origins) == 1, f"overlapping parts {solid_origins}"
        for face in solid.Faces():
            parts_on_face[face].add(solid_origins[0].split("/")[-1])
    shared = {tuple(sorted(parts)) for parts in parts_on_face.values() if len(parts) == 2}
    assert {("blanket", "vessel"), ("divertor", "vessel")} <= shared


@pytest.fixture(scope="module")
def arc_reference_reactors():
    return {angle: paramak.arc_from_2026_paper(rotation_angle=angle) for angle in (90, 180, 360)}


def test_arc_public_export():
    assert "arc_from_2026_paper" in paramak.__all__
    assert callable(paramak.arc_from_2026_paper)


def test_arc_defaults():
    # TF default is sourced from Hillesheim p.10; PF case remains provisional.
    parameters = inspect.signature(paramak.arc_from_2026_paper).parameters
    assert parameters["number_of_tf_coils"].default == 18
    assert parameters["rotation_angle"].default == 180.0
    assert parameters["pf_coil_case_thickness"].default == 3.0
    assert parameters["colors"].default is None


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_arc_plasma_geometry_and_metadata(angle, arc_reference_reactors):
    # Reference values measured from the boundary stored in the TokaMaker eqdsk file.
    reactor = arc_reference_reactors[angle]
    assert reactor.names() == (
        ["plasma"]
        + [f"central_solenoid_{i}" for i in range(1, 7)]
        + [name for i in range(1, 11) for name in (f"pf_coil_{i}", f"pf_coil_case_{i}")]
        + [
            "toroidal_field_coil",
            "tungsten_first_wall",
            "inner_vacuum_vessel",
            "flibe_first_wall",
            "outer_vacuum_vessel",
            "neutron_shield",
            "flibe_blanket",
            "outer_blanket_wall",
        ]
    )
    assert reactor.major_radius == pytest.approx(461.7919445, abs=1e-6)
    assert reactor.minor_radius == pytest.approx(116.9309615, abs=1e-6)
    assert reactor.elongation == pytest.approx(1.93261, abs=1e-5)
    assert reactor.triangularity == pytest.approx(0.60799, abs=1e-5)
    shape = reactor.objects["plasma"].obj.val()
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    # full-turn volume of the 800-point boundary polygon is 184.56 m3
    assert shape.Volume() == pytest.approx(184.56e6 * angle / 360, rel=5e-3)
    box = shape.BoundingBox()
    assert box.zmax == pytest.approx(226.034069, abs=0.1)
    assert box.zmin == pytest.approx(-225.929689, abs=0.1)
    assert box.xmax == pytest.approx(578.722906, abs=0.1)
    # the equilibrium boundary sits clear of the first wall
    wall = reactor.objects["tungsten_first_wall"].obj.val()
    assert shape.distance(wall) == pytest.approx(2.86, abs=0.05)


def test_arc_full_turn_is_twice_the_half_turn(arc_reference_reactors):
    half, full = arc_reference_reactors[180], arc_reference_reactors[360]
    assert full.toCompound().Volume() == pytest.approx(2 * half.toCompound().Volume(), rel=1e-3)


def test_arc_colors_override_defaults():
    "one build with a different color for every part checks that each part takes its color"
    names = paramak.arc_from_2026_paper(rotation_angle=10).names()
    colors = {name: (index / len(names), 0.5, 1 - index / len(names)) for index, name in enumerate(names)}
    reactor = paramak.arc_from_2026_paper(rotation_angle=10, colors=colors)
    for name, color in colors.items():
        assert reactor.objects[name].color.toTuple()[:3] == pytest.approx(color), name


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_arc_solenoid_envelopes(angle, arc_reference_reactors):
    # Filament grid extents (centres plus half a grid spacing) of cs1u/l, cs2u/l, cs3u/l.
    reactor = arc_reference_reactors[angle]
    inner_radius, outer_radius = 72, 149
    for index, (centre_z, height) in enumerate(
        [(75, 140), (-75, 140), (190, 70), (-190, 70), (270, 70), (-270, 70)], 1
    ):
        shape = reactor.objects[f"central_solenoid_{index}"].obj.val()
        assert shape.isValid()
        assert len(shape.Solids()) == 1
        box = shape.BoundingBox()
        assert box.zmin == pytest.approx(centre_z - height / 2, abs=1e-5)
        assert box.zmax == pytest.approx(centre_z + height / 2, abs=1e-5)
        assert box.xmax == pytest.approx(outer_radius, abs=1e-5)
        expected_volume = math.pi * (outer_radius**2 - inner_radius**2) * height * angle / 360
        assert shape.Volume() == pytest.approx(expected_volume, rel=1e-6)
    shapes = [child.obj.val() for child in reactor.children]
    for i, first in enumerate(shapes):
        for second in shapes[i + 1 :]:
            assert first.intersect(second).Volume() == pytest.approx(0, abs=1e-5)


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_arc_pf_coil_envelopes_and_cases(angle, arc_reference_reactors):
    # Winding packs are the JSON filament grid extents; an assumed 3 cm case surrounds them.
    reactor = arc_reference_reactors[angle]
    for index in range(1, 11):
        pair = (index - 1) // 2
        centre_r = [140, 190, 620, 620, 695][pair]
        centre_z = [390, 475, 295, 225, 160][pair] * (1 if index % 2 else -1)
        size = [60, 70, 50, 50, 40][pair]
        core = reactor.objects[f"pf_coil_{index}"].obj.val()
        case = reactor.objects[f"pf_coil_case_{index}"].obj.val()
        assert core.isValid() and case.isValid()
        assert core.Volume() > 0 and case.Volume() > 0
        outer = case.BoundingBox()
        inner = core.BoundingBox()
        assert inner.xmax == pytest.approx(centre_r + size / 2, abs=1e-5)
        assert inner.zmin == pytest.approx(centre_z - size / 2, abs=1e-5)
        assert inner.zmax == pytest.approx(centre_z + size / 2, abs=1e-5)
        assert outer.xmax == pytest.approx(inner.xmax + 3, abs=1e-5)
        assert outer.zmin == pytest.approx(inner.zmin - 3, abs=1e-5)
        assert outer.zmax == pytest.approx(inner.zmax + 3, abs=1e-5)
        assert core.intersect(case).Volume() == pytest.approx(0, abs=1e-5)
        assert core.distance(case) == pytest.approx(0, abs=1e-5)
        expected = math.pi * ((centre_r + size / 2) ** 2 - (centre_r - size / 2) ** 2) * size * angle / 360
        assert core.Volume() == pytest.approx(expected, rel=1e-6)
        outer_size = size + 6
        expected = (
            math.pi * ((centre_r + outer_size / 2) ** 2 - (centre_r - outer_size / 2) ** 2) * outer_size * angle / 360
        )
        assert core.fuse(case).Volume() == pytest.approx(expected, rel=1e-6)


def test_arc_pf_case_thickness_keeps_the_winding_pack():
    # The assumed case is added around the winding pack, which keeps its size.
    thin = paramak.arc_from_2026_paper(rotation_angle=30, pf_coil_case_thickness=1)
    thick = paramak.arc_from_2026_paper(rotation_angle=30, pf_coil_case_thickness=5)
    for index in range(1, 11):
        core, case = f"pf_coil_{index}", f"pf_coil_case_{index}"

        def volume(assembly, name):
            return assembly.objects[name].obj.val().Volume()

        assert volume(thick, core) == pytest.approx(volume(thin, core), rel=1e-6)
        assert volume(thick, case) > volume(thin, case)


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_arc_tf_profile_extrusion(angle, arc_reference_reactors):
    # [Spline interpolation should stay close to the supplied polygon envelope
    # and area (cm2); extrusion assumption is 40 cm.
    reactor = arc_reference_reactors[angle]
    tf = reactor.objects["toroidal_field_coil"].obj.val()
    assert tf.isValid()
    assert tf.Volume() == pytest.approx(282664.2849663841 * 40 * 18 * angle / 360, rel=0.01)
    edge_types = {edge.geomType() for edge in tf.Edges()}
    assert {"BSPLINE", "LINE"} <= edge_types
    box = tf.BoundingBox()
    assert box.xmax == pytest.approx(889.6142109267835, abs=2)
    assert box.zmin == pytest.approx(-567.4071533810901, abs=2)
    assert box.zmax == pytest.approx(570.0708867122844, abs=2)
    if angle < 360:
        assert box.ymin >= -1e-5
    if angle == 90:
        assert box.xmin >= -1e-5
    if angle == 360:
        solids = tf.Solids()
        assert len(solids) == 18
        for first, second in zip(solids, solids[1:] + solids[:1]):
            assert first.intersect(second).Volume() == pytest.approx(0, abs=1e-5)


def test_arc_tf_custom_count():
    reactor = paramak.arc_from_2026_paper(rotation_angle=360, number_of_tf_coils=6)
    tf = reactor.objects["toroidal_field_coil"]
    assert len(tf.obj.val().Solids()) == 6
    assert tf.obj.val().Volume() == pytest.approx(282664.2849663841 * 40 * 6, rel=0.01)


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_arc_tungsten_first_wall_geometry(angle, arc_reference_reactors):
    # Independent full-turn volume from the JSON polygon moments; cm3.
    reactor = arc_reference_reactors[angle]
    wall = reactor.objects["tungsten_first_wall"].obj.val()
    assert wall.isValid()
    assert len(wall.Solids()) == 1
    assert wall.Volume() == pytest.approx(3041653.552999719 * angle / 360, rel=1e-6)
    box = wall.BoundingBox()
    assert box.xmax == pytest.approx(582.5, abs=1e-5)
    assert box.zmax == pytest.approx(409.5, abs=1e-5)
    assert box.zmin == pytest.approx(-409.5, abs=1e-5)
    if angle < 360:
        assert box.ymin >= -1e-5
    if angle == 90:
        assert box.xmin >= -1e-5
    other_parts = (child for child in reactor.children if child.name != "tungsten_first_wall")
    for part in other_parts:
        assert wall.intersect(part.obj.val()).Volume() == pytest.approx(0, abs=1e-4), part.name


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_arc_vessel_walls_and_neutron_shield(angle, arc_reference_reactors):
    # Independent polygon-moment volumes from the supplied JSON, in cm3.
    reactor = arc_reference_reactors[angle]
    expected = {
        "inner_vacuum_vessel": (6105123.0299052, 583.5, 410.50000000000006),
        "outer_vacuum_vessel": (18883600.83873242, 591.0, 418.0),
        "neutron_shield": (55362184.56153011, 411.0, 437.0),
    }
    for name, (full_volume, rmax, zmax) in expected.items():
        shape = reactor.objects[name].obj.val()
        assert shape.isValid()
        assert len(shape.Solids()) == 1
        assert shape.Volume() == pytest.approx(full_volume * angle / 360, rel=1e-6)
        box = shape.BoundingBox()
        assert box.xmax == pytest.approx(rmax, abs=1e-5)
        assert box.zmax == pytest.approx(zmax, abs=1e-5)
        assert box.zmin == pytest.approx(-zmax, abs=1e-5)
        if angle < 360:
            assert box.ymin >= -1e-5
        if angle == 90:
            assert box.xmin >= -1e-5
        for child in reactor.children:
            if child.name != name:
                assert shape.intersect(child.obj.val()).Volume() == pytest.approx(0, abs=1e-4), (name, child.name)
    first = reactor.objects["tungsten_first_wall"].obj.val()
    inner = reactor.objects["inner_vacuum_vessel"].obj.val()
    outer = reactor.objects["outer_vacuum_vessel"].obj.val()
    assert first.distance(inner) == pytest.approx(0, abs=1e-5)
    assert inner.distance(outer) > 0


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_arc_flibe_first_wall_geometry(angle, arc_reference_reactors):
    # Volume is the difference of independently integrated JSON vessel boundary polygons.
    reactor = arc_reference_reactors[angle]
    flibe = reactor.objects["flibe_first_wall"].obj.val()
    assert flibe.isValid()
    assert len(flibe.Solids()) == 1
    assert flibe.Volume() == pytest.approx(27833226.82232392 * angle / 360, rel=1e-6)
    box = flibe.BoundingBox()
    assert box.xmax == pytest.approx(588, abs=1e-5)
    assert box.zmin == pytest.approx(-415, abs=1e-5)
    assert box.zmax == pytest.approx(415, abs=1e-5)
    if angle < 360:
        assert box.ymin >= -1e-5
    if angle == 90:
        assert box.xmin >= -1e-5
    for name in ("inner_vacuum_vessel", "outer_vacuum_vessel"):
        vessel = reactor.objects[name].obj.val()
        assert flibe.distance(vessel) == pytest.approx(0, abs=1e-5)
        assert flibe.intersect(vessel).Volume() == pytest.approx(0, abs=1e-4)


def test_arc_flibe_first_wall_interfaces_imprint(arc_reference_reactors):
    # Verify shared faces on both sides of the filled cooling region.
    reactor = arc_reference_reactors[180]
    assembly = cq.Assembly()
    for name in ("inner_vacuum_vessel", "flibe_first_wall", "outer_vacuum_vessel"):
        assembly.add(reactor.objects[name].obj, name=name)
    _, origins = imprint(assembly)
    faces = {}
    for solid, names in origins.items():
        assert len(names) == 1
        for face in solid.Faces():
            faces.setdefault(face, set()).add(names[0].split("/")[-1])
    pairs = {frozenset(names) for names in faces.values() if len(names) == 2}
    assert frozenset(("inner_vacuum_vessel", "flibe_first_wall")) in pairs
    assert frozenset(("outer_vacuum_vessel", "flibe_first_wall")) in pairs


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_arc_flibe_blanket_geometry(angle, arc_reference_reactors):
    # Independent polygon-moment volume: tank cavity minus vessel envelope and shield.
    reactor = arc_reference_reactors[angle]
    blanket = reactor.objects["flibe_blanket"].obj.val()
    assert blanket.isValid()
    assert len(blanket.Solids()) == 1
    assert blanket.Volume() == pytest.approx(431989820.1713178 * angle / 360, rel=1e-6)
    box = blanket.BoundingBox()
    assert box.xmax == pytest.approx(720, abs=1e-5)
    assert box.zmax == pytest.approx(468, abs=1e-5)
    assert box.zmin == pytest.approx(-468, abs=1e-5)
    if angle < 360:
        assert box.ymin >= -1e-5
    if angle == 90:
        assert box.xmin >= -1e-5
    for child in reactor.children:
        if child.name != "flibe_blanket":
            assert blanket.intersect(child.obj.val()).Volume() == pytest.approx(0, abs=1e-4), child.name
    for name in ("outer_vacuum_vessel", "neutron_shield"):
        assert blanket.distance(reactor.objects[name].obj.val()) == pytest.approx(0, abs=1e-5)


def test_arc_flibe_blanket_interfaces_imprint(arc_reference_reactors):
    # Both excluded solids must meet the bulk liquid on shared imprinted faces.
    reactor = arc_reference_reactors[180]
    assembly = cq.Assembly()
    for name in ("outer_vacuum_vessel", "neutron_shield", "flibe_blanket"):
        assembly.add(reactor.objects[name].obj, name=name)
    _, origins = imprint(assembly)
    faces = {}
    for solid, names in origins.items():
        assert len(names) == 1
        for face in solid.Faces():
            faces.setdefault(face, set()).add(names[0].split("/")[-1])
    pairs = {frozenset(names) for names in faces.values() if len(names) == 2}
    assert frozenset(("outer_vacuum_vessel", "flibe_blanket")) in pairs
    assert frozenset(("neutron_shield", "flibe_blanket")) in pairs


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_arc_outer_blanket_wall_geometry(angle, arc_reference_reactors):
    # Independent polygon-moment volume between the two JSON Blanket contours, in cm3.
    reactor = arc_reference_reactors[angle]
    wall = reactor.objects["outer_blanket_wall"].obj.val()
    assert wall.isValid()
    assert len(wall.Solids()) == 1
    assert wall.Volume() == pytest.approx(14487629.277982116 * angle / 360, rel=1e-6)
    box = wall.BoundingBox()
    assert box.xmax == pytest.approx(722, abs=1e-5)
    assert box.zmax == pytest.approx(470.0323, abs=1e-5)
    assert box.zmin == pytest.approx(-470.0323, abs=1e-5)
    if angle < 360:
        assert box.ymin >= -1e-5
    if angle == 90:
        assert box.xmin >= -1e-5
    for child in reactor.children:
        if child.name != "outer_blanket_wall":
            assert wall.intersect(child.obj.val()).Volume() == pytest.approx(0, abs=1e-4), child.name
    for name in ("flibe_blanket", "neutron_shield"):
        assert wall.distance(reactor.objects[name].obj.val()) == pytest.approx(0, abs=1e-5)
    # the wall is clear of the toroidal field coils
    assert wall.distance(reactor.objects["toroidal_field_coil"].obj.val()) > 3


def test_arc_outer_blanket_wall_interfaces_imprint(arc_reference_reactors):
    # The wall must meet the bulk liquid and the shield on shared imprinted faces.
    reactor = arc_reference_reactors[180]
    assembly = cq.Assembly()
    for name in ("neutron_shield", "flibe_blanket", "outer_blanket_wall"):
        assembly.add(reactor.objects[name].obj, name=name)
    _, origins = imprint(assembly)
    faces = {}
    for solid, names in origins.items():
        assert len(names) == 1
        for face in solid.Faces():
            faces.setdefault(face, set()).add(names[0].split("/")[-1])
    pairs = {frozenset(names) for names in faces.values() if len(names) == 2}
    assert frozenset(("flibe_blanket", "outer_blanket_wall")) in pairs
    assert frozenset(("neutron_shield", "outer_blanket_wall")) in pairs


@pytest.mark.parametrize("thickness", [20])
def test_arc_case_too_thick_to_clear_the_tf_coils(thickness):
    with pytest.raises(ValueError, match="pf_coil_case_thickness"):
        paramak.arc_from_2026_paper(pf_coil_case_thickness=thickness)
