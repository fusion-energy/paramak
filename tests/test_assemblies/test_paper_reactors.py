import importlib
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
]

# mesh sizes (cm) suited to the size of each reactor
MESH_SIZES = {
    paramak.sparc_from_2020_paper: (2, 20),
    paramak.iter_from_2020_paper: (5, 80),
    paramak.eu_demo_from_2015_paper: (5, 100),
}

EXPECTED_PARTS = {
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
    for name in ["plasma", "vessel"]:
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
@pytest.mark.parametrize("number_of_tf_coils", [0, -1, 2.5])
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
    assert thick["pf_coil_1"] < thin["pf_coil_1"]
    assert thick["pf_coil_1"] + thick["pf_coil_case_1"] == pytest.approx(
        thin["pf_coil_1"] + thin["pf_coil_case_1"], rel=1e-6
    )


@pytest.mark.parametrize("reactor_function", PAPER_REACTORS, ids=lambda f: f.__name__)
@pytest.mark.parametrize("pf_coil_case_thickness", [0, -1, float("nan"), 1000])
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
    material_tags = [f"mat_{name.split('/')[-1]}" for _shape, name, _loc, _color in reactor]

    my_model = CadToDagmc()
    my_model.add_cadquery_object(cadquery_object=reactor, material_tags=material_tags)
    min_mesh_size, max_mesh_size = MESH_SIZES[reactor_function]
    my_model.export_dagmc_h5m_file(filename="dagmc.h5m", min_mesh_size=min_mesh_size, max_mesh_size=max_mesh_size)

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
