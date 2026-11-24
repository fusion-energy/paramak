"""Making the axisymmetric parts of a reactor from one 2D cross section."""

import math

import pytest
from cadquery.occ_impl.assembly import imprint
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

import paramak
from paramak.assemblies.cross_section import profile_face, rectangle_face, revolve_cross_section

from .test_imprint import REACTORS as IMPRINT_REACTORS
from .test_imprint import (
    SPHERICAL_LAYERS,
    SPHERICAL_RADIAL_BUILD,
    TOKAMAK_FROM_PLASMA_RADIAL_BUILD,
    TOKAMAK_RADIAL_BUILD,
)

L = paramak.LayerType
TOKAMAK_VERTICAL_BUILD = [
    (L.SOLID, 15),
    (L.SOLID, 80),
    (L.SOLID, 10),
    (L.GAP, 50),
    (L.PLASMA, 700),
    (L.GAP, 60),
    (L.SOLID, 10),
    (L.SOLID, 40),
    (L.SOLID, 15),
]


def volume(shape):
    """Shape.Volume() can be a few percent out for spline surfaces, an
    adaptive integration is used instead."""
    properties = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, properties, 1e-7, True)
    return properties.Mass()


def pappus(face, rotation_angle):
    "the volume of a face in the XZ plane revolved around the Z axis"
    properties = GProp_GProps()
    BRepGProp.SurfaceProperties_s(face.wrapped, properties, 1e-9, True)
    return properties.Mass() * properties.CentreOfMass().X() * math.radians(rotation_angle)


def share_a_face(first, second):
    "True if the shapes have a face in common, the same face not a copy"
    return any(a.isSame(b) for a in first.Faces() for b in second.Faces())


def parts(assembly):
    return {name.split("/")[-1]: shape.moved(loc) for shape, name, loc, _ in assembly}


@pytest.mark.parametrize("rotation_angle", [63, 180, 360])
def test_touching_profiles_share_a_face(rotation_angle):
    solids = revolve_cross_section(
        {"inner": [rectangle_face(100, 200, -50, 50)], "outer": [rectangle_face(200, 300, -50, 50)]}, rotation_angle
    )
    inner, outer = solids["inner"][0], solids["outer"][0]
    assert share_a_face(inner, outer)
    assert volume(inner) == pytest.approx(pappus(rectangle_face(100, 200, -50, 50), rotation_angle), rel=1e-9)
    assert volume(outer) == pytest.approx(pappus(rectangle_face(200, 300, -50, 50), rotation_angle), rel=1e-9)


def test_overlap_is_kept_by_the_first_part():
    solids = revolve_cross_section(
        {"first": [rectangle_face(100, 220, -50, 50)], "second": [rectangle_face(200, 300, -50, 50)]}, 90
    )
    assert volume(solids["first"][0]) == pytest.approx(pappus(rectangle_face(100, 220, -50, 50), 90), rel=1e-9)
    assert volume(solids["second"][0]) == pytest.approx(pappus(rectangle_face(220, 300, -50, 50), 90), rel=1e-9)
    assert share_a_face(solids["first"][0], solids["second"][0])


def test_profile_inside_an_earlier_profile_raises():
    with pytest.raises(ValueError, match="lies inside"):
        revolve_cross_section(
            {"outer": [rectangle_face(100, 300, -50, 50)], "inner": [rectangle_face(150, 200, -10, 10)]}, 90
        )


@pytest.mark.parametrize("rotation_angle", [45, 360])
def test_closed_outline_is_revolved(rotation_angle):
    "a profile with a single closed edge, like the plasma, inside a ring"
    points = [
        (300 + 50 * math.cos(t), 80 * math.sin(t), "spline") for t in (2 * math.pi * i / 50 for i in range(50))
    ]
    circle = profile_face(points + points[:1])
    ring = rectangle_face(200, 400, -100, 100).cut(circle).Faces()
    solids = revolve_cross_section({"circle": [circle], "ring": ring}, rotation_angle)
    assert solids["circle"][0].isValid() and solids["ring"][0].isValid()
    assert share_a_face(solids["circle"][0], solids["ring"][0])
    assert volume(solids["circle"][0]) == pytest.approx(pappus(circle, rotation_angle), rel=1e-4)


@pytest.mark.parametrize("rotation_angle, rotation_start_angle", [(63, 0), (180, 0), (360, 0), (63, 20)])
def test_tokamak_layers_share_faces(rotation_angle, rotation_start_angle):
    "neighbouring parts share their faces before any imprinting"
    shapes = parts(
        paramak.tokamak_from_plasma(
            radial_build=TOKAMAK_FROM_PLASMA_RADIAL_BUILD,
            elongation=2,
            triangularity=0.55,
            rotation_angle=rotation_angle,
            rotation_start_angle=rotation_start_angle,
        )
    )
    pairs = [
        ("layer_1", "layer_2"),
        ("layer_3", "layer_4"),
        ("layer_4", "layer_5"),
        ("plasma", "vacuum"),
        ("layer_3", "vacuum"),
    ]
    for first, second in pairs:
        assert share_a_face(shapes[first], shapes[second]), f"{first} and {second} share no face"
    assert all(shape.isValid() for shape in shapes.values())


@pytest.mark.parametrize("rotation_angle", [180, 360])
def test_tokamak_centre_column_and_blanket_do_not_overlap(rotation_angle):
    """With no gap in the build the curved blanket touches the straight centre
    column. The blanket's spline crosses the column by a fraction of a micron,
    which is cut from the blanket, so imprinting adds no solids."""
    reactor = paramak.tokamak(
        radial_build=TOKAMAK_RADIAL_BUILD,
        vertical_build=TOKAMAK_VERTICAL_BUILD,
        triangularity=0.55,
        rotation_angle=rotation_angle,
    )
    shapes = parts(reactor)
    shape, origins = imprint(reactor)
    assert len(shape.Solids()) == sum(len(s.Solids()) for s in shapes.values())
    assert [o for o in origins.values() if len(o) > 1] == []
    assert share_a_face(shapes["layer_2"], shapes["layer_5"])


@pytest.mark.parametrize("rotation_angle, rotation_start_angle", [(63, 0), (180, 0), (360, 0), (63, 20)])
def test_spherical_tokamak_layers_share_faces(rotation_angle, rotation_start_angle):
    "the centre column and the layers closed towards it share their faces before any imprinting"
    shapes = parts(
        paramak.spherical_tokamak_from_plasma(
            radial_build=SPHERICAL_RADIAL_BUILD,
            elongation=2,
            triangularity=0.55,
            rotation_angle=rotation_angle,
            rotation_start_angle=rotation_start_angle,
        )
    )
    pairs = [*SPHERICAL_LAYERS, ("plasma", "vacuum"), ("layer_2", "vacuum"), ("layer_3", "vacuum")]
    for first, second in pairs:
        assert share_a_face(shapes[first], shapes[second]), f"{first} and {second} share no face"
    assert all(shape.isValid() for shape in shapes.values())


@pytest.mark.parametrize("rotation_angle", [63, 360])
@pytest.mark.parametrize("reactor", ["sparc", "iter", "eu_demo", "arc"])
def test_paper_reactor_parts_share_faces(reactor, rotation_angle):
    """The neighbouring axisymmetric parts share their faces before any
    imprinting, the same pairs the imprint tests expect to share a face. The
    toroidal field coils are solids made separately, so pairs with them are
    left out."""
    _, expected_pairs = IMPRINT_REACTORS[reactor]
    function = {
        "sparc": paramak.sparc_from_2020_paper,
        "iter": paramak.iter_from_2020_paper,
        "eu_demo": paramak.eu_demo_from_2015_paper,
        "arc": paramak.arc_from_2026_paper,
    }[reactor]
    shapes = parts(function(rotation_angle=rotation_angle))
    pairs = [pair for pair in expected_pairs if "toroidal_field_coil" not in pair]
    assert pairs
    for first, second in pairs:
        assert share_a_face(shapes[first], shapes[second]), f"{first} and {second} share no face"
