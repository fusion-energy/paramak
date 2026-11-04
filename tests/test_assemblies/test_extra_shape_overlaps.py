import cadquery as cq
import pytest

import paramak

L = paramak.LayerType

REACTORS = [
    (
        paramak.tokamak_from_plasma,
        [(L.GAP, 10), (L.SOLID, 30), (L.SOLID, 50), (L.SOLID, 50), (L.GAP, 60), (L.PLASMA, 300), (L.GAP, 60), (L.SOLID, 20), (L.SOLID, 100)],
    ),
    (
        paramak.spherical_tokamak_from_plasma,
        [(L.GAP, 10), (L.SOLID, 50), (L.GAP, 50), (L.PLASMA, 300), (L.GAP, 60), (L.SOLID, 20), (L.SOLID, 100)],
    ),
]


def box(x, z, size=100):
    return cq.Workplane("XY").box(size, size, size).translate((x, 50, z))


def volume(shape):
    return sum(solid.Volume() for solid in shape.Solids())


def overlap_volume(a, b):
    return volume(a.toCompound().intersect(b.toCompound()))


@pytest.mark.parametrize("function, radial_build", REACTORS)
@pytest.mark.parametrize("poloidal", [False, True])
def test_no_parts_overlap(function, radial_build, poloidal):
    "intersect parts do not overlap the cut shapes or each other"

    arc_length_function = paramak.poloidal_arc_length if function is paramak.tokamak_from_plasma else paramak.spherical_poloidal_arc_length
    kwargs = {}
    if poloidal:
        arc = arc_length_function(radial_build)
        kwargs["poloidal_build"] = [None, [(L.SOLID, arc / 2)] * 2, None]

    # boxes on the outboard blanket at the midplane that overlap each other
    radius = sum(item[1] for item in radial_build) - 60
    intersect_1 = box(radius, 0)
    intersect_2 = box(radius + 30, 40)
    cutter = box(radius - 30, -40)
    reactor = function(
        radial_build=radial_build,
        rotation_angle=90,
        extra_intersect_shapes=[intersect_1, intersect_2],
        extra_cut_shapes=[cutter],
        **kwargs,
    )
    parts = {child.name: child for child in reactor.children}
    names = list(parts)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            assert overlap_volume(parts[a], parts[b]) == pytest.approx(0, abs=1e-3), (a, b)
    # the intersect parts are not empty
    assert volume(parts["extra_intersect_shapes_1"].toCompound()) > 0
    assert volume(parts["extra_intersect_shapes_2"].toCompound()) > 0
