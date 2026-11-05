import importlib
from pathlib import Path

import pytest

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
    paramak.sparc_from_2020_paper: ["plasma", "vessel", "inner_vessel", "antenna", "toroidal_field_coil", "pf_coil_1"],
    paramak.iter_from_2020_paper: ["plasma", "blanket", "divertor", "vessel", "toroidal_field_coil", "pf_coil_1"],
    paramak.eu_demo_from_2015_paper: ["plasma", "blanket", "divertor", "vessel", "toroidal_field_coil", "pf_coil_1"],
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
