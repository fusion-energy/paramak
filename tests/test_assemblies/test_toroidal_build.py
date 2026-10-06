import math

import cadquery as cq
import pytest

import paramak

TOKAMAK_RADIAL_BUILD = [
    (paramak.LayerType.GAP, 10),
    (paramak.LayerType.SOLID, 30),
    (paramak.LayerType.SOLID, 50),
    (paramak.LayerType.SOLID, 10),
    (paramak.LayerType.SOLID, 120),
    (paramak.LayerType.SOLID, 20),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.PLASMA, 300),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.SOLID, 20),  # first wall
    (paramak.LayerType.SOLID, 120),  # blanket
    (paramak.LayerType.SOLID, 10),  # rear wall
]

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


def equal_sectors(arc_length, number_of_sectors, gap, name="sector"):
    "a toroidal_build entry of equally sized sectors, each followed by a gap"
    sector = (arc_length - number_of_sectors * gap) / number_of_sectors
    return [(paramak.LayerType.SOLID, sector, name), (paramak.LayerType.GAP, gap)] * number_of_sectors


def test_toroidal_arc_length():
    "the arc length is measured at the plasma facing surface at the outboard midplane"

    plasma_facing_radius = 10 + 30 + 50 + 10 + 120 + 20 + 60 + 300 + 60
    for rotation_angle in [90, 180, 360]:
        assert paramak.toroidal_arc_length(TOKAMAK_RADIAL_BUILD, rotation_angle=rotation_angle) == pytest.approx(
            plasma_facing_radius * math.radians(rotation_angle)
        )


@pytest.mark.parametrize("reactor", ["tokamak", "spherical_tokamak"])
def test_sectors_without_gaps_fill_the_layer(reactor):
    "sectors without gaps fill the layer exactly and have equal volumes"

    function = getattr(paramak, f"{reactor}_from_plasma")
    radial_build = TOKAMAK_RADIAL_BUILD if reactor == "tokamak" else SPHERICAL_RADIAL_BUILD
    arc_length = paramak.toroidal_arc_length(radial_build, rotation_angle=90)
    sectors = equal_sectors(arc_length, number_of_sectors=3, gap=0)

    unsegmented = volumes(function(radial_build=radial_build, rotation_angle=90))
    segmented_reactor = function(radial_build=radial_build, rotation_angle=90, toroidal_build=[None, None, sectors, None])
    segmented = volumes(segmented_reactor)

    sector_names = ["layer_4_sector_1", "layer_4_sector_2", "layer_4_sector_3"]
    assert [name for name in segmented_reactor.names() if "_sector_" in name] == sector_names
    assert sum(segmented[name] for name in sector_names) == pytest.approx(unsegmented["layer_4"], rel=1e-6)
    for name in sector_names:
        assert segmented[name] == pytest.approx(unsegmented["layer_4"] / 3, rel=1e-6)
    for name in ["layer_1", "layer_2", "layer_3", "layer_5", "plasma"]:
        assert segmented[name] == pytest.approx(unsegmented[name])


def test_gaps_have_parallel_sides():
    "a gap has the same width at every radius"

    arc_length = paramak.toroidal_arc_length(TOKAMAK_RADIAL_BUILD, rotation_angle=90)
    gap = 50
    sector = (arc_length - 2 * gap) / 3
    toroidal_build = [
        None,
        None,
        [
            (paramak.LayerType.SOLID, sector, "sector"),
            (paramak.LayerType.GAP, gap),
            (paramak.LayerType.SOLID, sector, "sector"),
            (paramak.LayerType.GAP, gap),
            (paramak.LayerType.SOLID, sector, "sector"),
        ],
        None,
    ]
    reactor = paramak.tokamak_from_plasma(
        radial_build=TOKAMAK_RADIAL_BUILD, rotation_angle=90, toroidal_build=toroidal_build
    )
    parts = {child.name: child.toCompound() for child in reactor.children}

    # measures the gap between the first two sectors on the inboard and outboard sides
    for radius in [150, 700]:
        ring = cq.Solid.makeCylinder(radius + 1, 2, cq.Vector(0, 0, -1)).cut(
            cq.Solid.makeCylinder(radius - 1, 2, cq.Vector(0, 0, -1))
        )
        first = parts["layer_4_sector_1"].intersect(ring)
        second = parts["layer_4_sector_2"].intersect(ring)
        assert first.distance(second) == pytest.approx(gap, abs=0.5)


def test_toroidal_and_poloidal_build_together():
    "each poloidal segment is split into the toroidal sectors"

    poloidal_arc = paramak.poloidal_arc_length(TOKAMAK_RADIAL_BUILD)
    toroidal_arc = paramak.toroidal_arc_length(TOKAMAK_RADIAL_BUILD, rotation_angle=90)
    tiles = [(paramak.LayerType.SOLID, poloidal_arc / 2, "tile")] * 2
    sectors = [(paramak.LayerType.SOLID, toroidal_arc / 2, "sector")] * 2

    reactor = paramak.tokamak_from_plasma(
        radial_build=TOKAMAK_RADIAL_BUILD,
        rotation_angle=90,
        poloidal_build=[None, tiles, None, None],
        toroidal_build=[None, sectors, None, None],
    )
    assert [name for name in reactor.names() if name.startswith("layer_3")] == [
        "layer_3_tile_1_sector_1",
        "layer_3_tile_1_sector_2",
        "layer_3_tile_2_sector_1",
        "layer_3_tile_2_sector_2",
    ]
    unsegmented = volumes(paramak.tokamak_from_plasma(radial_build=TOKAMAK_RADIAL_BUILD, rotation_angle=90))
    segmented = volumes(reactor)
    assert sum(value for name, value in segmented.items() if name.startswith("layer_3")) == pytest.approx(
        unsegmented["layer_3"], rel=1e-5
    )


def test_full_rotation_and_single_sector():
    "a full torus can be split into sectors, and a single sector covering the rotation is the full layer"

    arc_length = paramak.toroidal_arc_length(SPHERICAL_RADIAL_BUILD, rotation_angle=360)
    number_of_sectors = 6
    reactor = paramak.spherical_tokamak_from_plasma(
        radial_build=SPHERICAL_RADIAL_BUILD,
        rotation_angle=360,
        toroidal_build=[
            None,
            [(paramak.LayerType.SOLID, arc_length)],
            equal_sectors(arc_length, number_of_sectors, gap=30),
            None,
        ],
    )
    names = reactor.names()
    assert "layer_3_segment" in names
    assert len([name for name in names if name.startswith("layer_4_sector_")]) == number_of_sectors
    unsegmented = volumes(paramak.spherical_tokamak_from_plasma(radial_build=SPHERICAL_RADIAL_BUILD, rotation_angle=360))
    segmented = volumes(reactor)
    assert segmented["layer_3_segment"] == pytest.approx(unsegmented["layer_3"], rel=1e-6)
    assert sum(value for name, value in segmented.items() if name.startswith("layer_4_")) < unsegmented["layer_4"]
    for child in reactor.children:
        assert child.toCompound().isValid()


def test_tokamak_with_vertical_build_and_divertor():
    "tokamak() supports toroidal_build, and the divertor is cut out of the sectors"

    vertical_build = [
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.SOLID, 80),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.GAP, 50),
        (paramak.LayerType.PLASMA, 700),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 40),
        (paramak.LayerType.SOLID, 15),
    ]
    divertor = cq.Workplane("XZ").polyline([(300, -700), (300, 0), (400, 0), (400, -700)]).close().revolve(90)
    arc_length = paramak.toroidal_arc_length(TOKAMAK_RADIAL_BUILD, rotation_angle=90)
    sectors = equal_sectors(arc_length, number_of_sectors=2, gap=0)

    unsegmented = volumes(
        paramak.tokamak(
            radial_build=TOKAMAK_RADIAL_BUILD,
            vertical_build=vertical_build,
            rotation_angle=90,
            extra_intersect_shapes=[divertor],
        )
    )
    reactor = paramak.tokamak(
        radial_build=TOKAMAK_RADIAL_BUILD,
        vertical_build=vertical_build,
        rotation_angle=90,
        extra_intersect_shapes=[divertor],
        toroidal_build=[None, sectors, sectors, sectors],
    )
    segmented = volumes(reactor)
    assert segmented["extra_intersect_shapes_1"] == pytest.approx(unsegmented["extra_intersect_shapes_1"], rel=1e-3)

    def total(volume_dict):
        return sum(value for name, value in volume_dict.items() if name != "plasma")

    assert total(segmented) == pytest.approx(total(unsegmented), rel=1e-3)
    for child in reactor.children:
        assert child.toCompound().isValid()


@pytest.mark.parametrize(
    "toroidal_build, error, match",
    [
        ([None, None], ValueError, "toroidal_build must have one entry"),
        ([[(paramak.LayerType.SOLID, 1)], None, None, None], ValueError, "toroidal_build entry 0 corresponds"),
        ([None, [(paramak.LayerType.SOLID, 1)], None, None], ValueError, "Use paramak.toroidal_arc_length"),
        ([None, [(paramak.LayerType.GAP, 100)], None, None], ValueError, "at least one LayerType.SOLID"),
        ([None, [("sector", 100)], None, None], TypeError, "paramak.LayerType, arc_length"),
        ("not a list", TypeError, "toroidal_build must be a list"),
    ],
)
def test_toroidal_build_validation(toroidal_build, error, match):
    with pytest.raises(error, match=match):
        paramak.tokamak_from_plasma(
            radial_build=TOKAMAK_RADIAL_BUILD, rotation_angle=90, toroidal_build=toroidal_build
        )
