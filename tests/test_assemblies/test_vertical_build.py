import pytest

import paramak

L = paramak.LayerType

TOKAMAK_RADIAL_BUILD = [(L.GAP, 10), (L.SOLID, 30), (L.SOLID, 50), (L.GAP, 60), (L.PLASMA, 300), (L.GAP, 60), (L.SOLID, 20)]
SPHERICAL_RADIAL_BUILD = [(L.GAP, 10), (L.SOLID, 50), (L.GAP, 50), (L.PLASMA, 300), (L.GAP, 60), (L.SOLID, 20)]
# a thick layer at the top and a thin one at the bottom
VERTICAL_BUILD = [(L.SOLID, 100), (L.GAP, 10), (L.PLASMA, 600), (L.GAP, 10), (L.SOLID, 20)]

REACTORS = [
    (paramak.tokamak, TOKAMAK_RADIAL_BUILD, "tokamak()"),
    (paramak.spherical_tokamak, SPHERICAL_RADIAL_BUILD, "spherical_tokamak()"),
]


def z_range(reactor, name):
    bb = reactor.objects[name].obj.val().BoundingBox()
    return bb.zmin, bb.zmax


@pytest.mark.parametrize("function, radial_build, _", REACTORS)
def test_vertical_build_is_ordered_from_the_top(function, radial_build, _):
    "both reactors put the entries before the plasma above it"

    reactor = function(radial_build=radial_build, vertical_build=VERTICAL_BUILD, rotation_angle=90)
    blanket = reactor.names()[-2]
    zmin, zmax = z_range(reactor, blanket)
    assert zmax == pytest.approx(300 + 10 + 100, abs=1)
    assert zmin == pytest.approx(-(300 + 10 + 20), abs=1)


@pytest.mark.parametrize("function, radial_build, reactor_name", REACTORS)
@pytest.mark.parametrize(
    "vertical_build",
    [
        [(L.GAP, 10), (L.PLASMA, 600), (L.GAP, 10), (L.SOLID, 20)],  # too few above
        [(L.SOLID, 100), (L.GAP, 10), (L.PLASMA, 600), (L.GAP, 10)],  # too few below
    ],
)
def test_vertical_build_too_short(function, radial_build, reactor_name, vertical_build):
    with pytest.raises(ValueError, match=rf"The vertical_build for {reactor_name.replace('(', '[(]').replace(')', '[)]')} needs at least 2 entries"):
        function(radial_build=radial_build, vertical_build=vertical_build, rotation_angle=90)


def test_tokamak_needs_an_inboard_entry_for_each_outboard_entry():
    radial_build = [(L.GAP, 50), (L.PLASMA, 300), (L.GAP, 10), (L.SOLID, 20)]
    with pytest.raises(ValueError, match="has 2 entries after the plasma but only 1 before it"):
        paramak.tokamak_from_plasma(radial_build=radial_build, rotation_angle=90)


@pytest.mark.parametrize("function, radial_build, _", REACTORS)
def test_centre_column_lines_up_with_the_blanket(function, radial_build, _):
    "the centre column covers the same heights as the blanket for an asymmetric vertical_build"

    reactor = function(radial_build=radial_build, vertical_build=VERTICAL_BUILD, rotation_angle=90)
    centre_column, blanket = reactor.names()[0], reactor.names()[-2]
    assert z_range(reactor, centre_column) == pytest.approx(z_range(reactor, blanket), abs=1)
