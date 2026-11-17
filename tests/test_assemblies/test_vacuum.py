"""The vacuum part that fills the gap between the plasma and the first wall."""

import importlib
import math
from pathlib import Path

import cadquery as cq
import numpy as np
import pytest
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

import paramak
from paramak.utils import DEFAULT_VACUUM_COLOR, sum_up_to_gap_before_plasma
from paramak.workplanes.blanket_from_plasma import offset_curve_coordinates

from .test_imprint import SPHERICAL_RADIAL_BUILD, TOKAMAK_FROM_PLASMA_RADIAL_BUILD
from .test_utils import transport_particles_on_h5m_geometry

L = paramak.LayerType
TRIANGULARITY = 0.55
ELONGATION = 2.0
# the first solid layer after the plasma
FIRST_WALL = {"tokamak_from_plasma": "layer_3", "spherical_tokamak_from_plasma": "layer_3"}


def build(reactor, **kwargs):
    radial_build = TOKAMAK_FROM_PLASMA_RADIAL_BUILD if reactor == "tokamak_from_plasma" else SPHERICAL_RADIAL_BUILD
    kwargs.setdefault("rotation_angle", 90)
    return getattr(paramak, reactor)(
        radial_build=radial_build, elongation=ELONGATION, triangularity=TRIANGULARITY, **kwargs
    )


def parts(assembly):
    return {name.split("/")[-1]: shape.moved(loc) for shape, name, loc, _color in assembly}


def volume(shape):
    """Shape.Volume() can be a few percent out for these spline surfaces, an
    adaptive integration is used instead."""
    properties = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, properties, 1e-7, True)
    return properties.Mass()


def revolved_volume(r, z, rotation_angle):
    """Volume of a closed (R, Z) polygon revolved by rotation_angle degrees,
    from Pappus's theorem written as a contour integral of R^2 / 2 dZ."""
    r, z = np.append(r, r[0]), np.append(z, z[0])
    r_squared = (r[:-1] ** 2 + r[:-1] * r[1:] + r[1:] ** 2) / 3
    return abs(np.sum(r_squared / 2 * np.diff(z))) * math.radians(rotation_angle)


def expected_volume(reactor, assembly, rotation_angle):
    """The volume between the plasma and the inner surface of the first wall,
    worked out from the parametric curves rather than the CAD."""
    a, major_radius = assembly.minor_radius, assembly.major_radius
    thetas = np.linspace(0, 360, 20001)[:-1]
    plasma = revolved_volume(
        *offset_curve_coordinates(major_radius, a, TRIANGULARITY, ELONGATION, 0, thetas, 0), rotation_angle
    )
    if reactor == "tokamak_from_plasma":
        # the first wall is 60 cm from the plasma all the way around
        return (
            revolved_volume(
                *offset_curve_coordinates(major_radius, a, TRIANGULARITY, ELONGATION, 0, thetas, 60), rotation_angle
            )
            - plasma
        )
    # the spherical first wall is 60 cm from the plasma, flat at the top and
    # bottom and closed by the centre column
    column = sum_up_to_gap_before_plasma(SPHERICAL_RADIAL_BUILD)
    r, z = offset_curve_coordinates(major_radius, a, TRIANGULARITY, ELONGATION, 0, thetas[:10001] - 90, 60)
    r, z = np.concatenate([[column], r, [column]]), np.concatenate([[z[0]], z, [z[-1]]])
    return revolved_volume(r, z, rotation_angle) - plasma


@pytest.mark.parametrize("rotation_angle", [90, 360])
@pytest.mark.parametrize("reactor", list(FIRST_WALL))
def test_vacuum_fills_the_gap(reactor, rotation_angle):
    assembly = build(reactor, rotation_angle=rotation_angle)
    shapes = parts(assembly)
    vacuum = shapes.pop("vacuum")

    assert assembly.names()[-1] == "vacuum"
    assert len(vacuum.Solids()) == 1
    assert vacuum.isValid()
    assert volume(vacuum) == pytest.approx(expected_volume(reactor, assembly, rotation_angle), rel=1e-4)
    for name in ("plasma", FIRST_WALL[reactor]):
        assert vacuum.distance(shapes[name]) == pytest.approx(0, abs=1e-6)
    for name, shape in shapes.items():
        assert volume(vacuum.intersect(shape)) < 1e-6 * volume(vacuum), f"vacuum overlaps {name}"


@pytest.mark.parametrize("reactor", list(FIRST_WALL))
def test_vacuum_can_be_removed(reactor):
    assembly = build(reactor)
    names, solid_count = assembly.names(), len(assembly.toCompound().Solids())
    assert assembly.remove("vacuum") is assembly
    assert assembly.names() == names[:-1]
    assert len(assembly.toCompound().Solids()) == solid_count - 1


def test_vacuum_color():
    color = dict((name.split("/")[-1], c.toTuple()) for _s, name, _l, c in build("tokamak_from_plasma"))["vacuum"]
    assert color == pytest.approx(DEFAULT_VACUUM_COLOR)
    assembly = build("tokamak_from_plasma", colors={"vacuum": (0, 0, 1, 0.5)})
    color = dict((name.split("/")[-1], c.toTuple()) for _s, name, _l, c in assembly)["vacuum"]
    assert color == pytest.approx((0, 0, 1, 0.5))


@pytest.mark.parametrize("reactor", list(FIRST_WALL))
def test_vacuum_is_cut_by_extra_cut_shapes(reactor):
    """A divertor that reaches through the first wall into the gap takes its
    share of the vacuum, so the two do not overlap and share faces."""
    reference = build(reactor)
    bottom = -reference.elongation * reference.minor_radius
    r = reference.major_radius
    # reaches from the plasma side of the gap through the first wall
    divertor = (
        cq.Workplane("XZ")
        .polyline([(r - 40, bottom - 30), (r + 40, bottom - 30), (r + 40, bottom - 150), (r - 40, bottom - 150)])
        .close()
        .revolve(90)
    )
    shapes = parts(build(reactor, extra_cut_shapes=[divertor]))
    vacuum = shapes["vacuum"]
    assert volume(vacuum.intersect(shapes["add_extra_cut_shape_1"])) < 1e-6 * volume(vacuum)
    assert vacuum.distance(shapes["add_extra_cut_shape_1"]) == pytest.approx(0, abs=1e-6)
    reference_vacuum = parts(reference)["vacuum"]
    removed = volume(reference_vacuum) - volume(vacuum)
    assert removed == pytest.approx(volume(reference_vacuum.intersect(divertor.val())), rel=1e-4)


def test_vacuum_name_must_be_unique():
    radial_build = [*TOKAMAK_FROM_PLASMA_RADIAL_BUILD[:-1], (L.SOLID, 10, "vacuum")]
    with pytest.raises(ValueError, match="vacuum"):
        paramak.tokamak_from_plasma(radial_build=radial_build, rotation_angle=90)


@pytest.mark.parametrize(
    "reactor_function",
    [
        paramak.sparc_from_2020_paper,
        paramak.iter_from_2020_paper,
        paramak.eu_demo_from_2015_paper,
        paramak.arc_from_2026_paper,
    ],
    ids=lambda f: f.__name__,
)
def test_paper_reactor_vacuum_is_enclosed(reactor_function):
    """The vacuum is enclosed by the plasma facing components, so it stays
    well inside the reactor and touches the plasma."""
    assembly = reactor_function(rotation_angle=90)
    shapes = parts(assembly)
    vacuum = shapes.pop("vacuum")
    assert vacuum.isValid()
    assert vacuum.distance(shapes["plasma"]) == pytest.approx(0, abs=1e-6)
    box, reactor_box = vacuum.BoundingBox(), cq.Compound.makeCompound(list(shapes.values())).BoundingBox()
    assert reactor_box.zmin < box.zmin and box.zmax < reactor_box.zmax
    assert assembly.names()[-1] == "vacuum"


@pytest.mark.skipif(not importlib.util.find_spec("cad_to_dagmc"), reason="Skipping transport tests")
def test_transport_with_and_without_vacuum(tmp_path, monkeypatch):
    """The vacuum is void, so filling the gap with it gives the same flux as
    leaving the gap to the implicit complement."""
    from cad_to_dagmc import CadToDagmc

    cross_sections_xml = str(Path(__file__).parents[1] / "cross_sections.xml")
    monkeypatch.chdir(tmp_path)

    fluxes = []
    for include_vacuum in (False, True):
        assembly = build("tokamak_from_plasma", rotation_angle=30)
        if not include_vacuum:
            assembly.remove("vacuum")
        material_tags = [
            "vacuum" if name.split("/")[-1] in ("plasma", "vacuum") else f"mat_{index}"
            for index, (shape, name, _loc, _color) in enumerate(assembly)
            for _solid in shape.Solids()
        ]
        my_model = CadToDagmc()
        my_model.add_cadquery_object(cadquery_object=assembly, material_tags=material_tags)
        my_model.export_dagmc_h5m_file(filename=f"dagmc_{include_vacuum}.h5m", min_mesh_size=5, max_mesh_size=50)
        fluxes.append(
            transport_particles_on_h5m_geometry(
                h5m_filename=f"dagmc_{include_vacuum}.h5m",
                material_tags=[tag for tag in material_tags if tag != "vacuum"],
                nuclides=["H1"] * len(set(material_tags)),
                cross_sections_xml=cross_sections_xml,
            )
        )
    assert fluxes[1] == pytest.approx(fluxes[0], rel=0.02)
