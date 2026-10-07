"""Checks the number of solids made by poloidal_build and toroidal_build, so
segments are single solids with no fragments or slivers left over."""

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
    (paramak.LayerType.SOLID, 20),  # first wall, layer_3
    (paramak.LayerType.SOLID, 120),  # blanket, layer_4
    (paramak.LayerType.SOLID, 10),  # rear wall, layer_5
]

SPHERICAL_RADIAL_BUILD = [
    (paramak.LayerType.GAP, 10),
    (paramak.LayerType.SOLID, 50),
    (paramak.LayerType.SOLID, 15),
    (paramak.LayerType.GAP, 50),
    (paramak.LayerType.PLASMA, 300),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.SOLID, 15),  # first wall, layer_3
    (paramak.LayerType.SOLID, 60),  # blanket, layer_4
    (paramak.LayerType.SOLID, 10),  # rear wall, layer_5
]

# parts that are not segmented in these tests: two centre column layers, the
# rear wall and the plasma
UNSEGMENTED_PARTS = ["layer_1", "layer_2", "layer_5", "plasma"]


def segments(arc_length, number_of_segments, gap, name):
    "equally sized solid segments, each followed by a gap"
    length = (arc_length - number_of_segments * gap) / number_of_segments
    return [(paramak.LayerType.SOLID, length, name), (paramak.LayerType.GAP, gap)] * number_of_segments


def solids_per_part(assembly):
    return {child.name: len(child.toCompound().Solids()) for child in assembly.children}


def check_every_part_is_one_valid_solid(assembly):
    for child in assembly.children:
        compound = child.toCompound()
        assert len(compound.Solids()) == 1, f"{child.name} has {len(compound.Solids())} solids"
        assert compound.isValid(), f"{child.name} is not valid"
        assert compound.Volume() > 0, f"{child.name} has no volume"


@pytest.mark.parametrize("reactor", ["tokamak", "spherical_tokamak"])
def test_poloidal_segments_are_single_solids(reactor):
    "each poloidal segment, with gaps between them, is one solid"

    function = getattr(paramak, f"{reactor}_from_plasma")
    radial_build = TOKAMAK_RADIAL_BUILD if reactor == "tokamak" else SPHERICAL_RADIAL_BUILD
    helper = paramak.poloidal_arc_length if reactor == "tokamak" else paramak.spherical_poloidal_arc_length
    number_of_modules = 8
    modules = segments(helper(radial_build), number_of_modules, gap=20, name="module")

    result = function(radial_build=radial_build, rotation_angle=90, poloidal_build=[None, modules, modules, None])

    check_every_part_is_one_valid_solid(result)
    assert len(result.children) == len(UNSEGMENTED_PARTS) + 2 * number_of_modules
    assert len(result.toCompound().Solids()) == len(UNSEGMENTED_PARTS) + 2 * number_of_modules


@pytest.mark.parametrize("reactor", ["tokamak", "spherical_tokamak"])
@pytest.mark.parametrize("rotation_angle", [90, 360])
def test_toroidal_sectors_are_single_solids(reactor, rotation_angle):
    "each toroidal sector, with parallel sided gaps between them, is one solid"

    function = getattr(paramak, f"{reactor}_from_plasma")
    radial_build = TOKAMAK_RADIAL_BUILD if reactor == "tokamak" else SPHERICAL_RADIAL_BUILD
    number_of_sectors = 6
    sectors = segments(
        paramak.toroidal_arc_length(radial_build, rotation_angle=rotation_angle), number_of_sectors, gap=30, name="sector"
    )

    result = function(
        radial_build=radial_build, rotation_angle=rotation_angle, toroidal_build=[None, sectors, sectors, None]
    )

    check_every_part_is_one_valid_solid(result)
    assert len(result.children) == len(UNSEGMENTED_PARTS) + 2 * number_of_sectors


@pytest.mark.parametrize("reactor", ["tokamak", "spherical_tokamak"])
def test_first_wall_tile_grid_solid_count(reactor):
    "a first wall split both poloidally and toroidally gives rows times columns single solid tiles"

    function = getattr(paramak, f"{reactor}_from_plasma")
    radial_build = TOKAMAK_RADIAL_BUILD if reactor == "tokamak" else SPHERICAL_RADIAL_BUILD
    helper = paramak.poloidal_arc_length if reactor == "tokamak" else paramak.spherical_poloidal_arc_length
    number_of_rows, number_of_columns = 6, 5
    rows = segments(helper(radial_build), number_of_rows, gap=5, name="row")
    columns = segments(paramak.toroidal_arc_length(radial_build, rotation_angle=90), number_of_columns, gap=5, name="column")

    result = function(
        radial_build=radial_build,
        rotation_angle=90,
        poloidal_build=[None, rows, None, None],
        toroidal_build=[None, columns, None, None],
    )

    counts = solids_per_part(result)
    tiles = [name for name in counts if name.startswith("layer_3_")]
    assert len(tiles) == number_of_rows * number_of_columns
    assert tiles[0] == "layer_3_row_1_column_1"
    assert tiles[-1] == f"layer_3_row_{number_of_rows}_column_{number_of_columns}"
    check_every_part_is_one_valid_solid(result)
    # the unsegmented blanket is still there
    assert counts["layer_4"] == 1
    assert len(result.toCompound().Solids()) == len(UNSEGMENTED_PARTS) + 1 + number_of_rows * number_of_columns


def test_split_solids_adds_no_parts_to_segmented_reactor():
    "every segment is one solid, so split_solids keeps the same parts and names"

    modules = segments(paramak.poloidal_arc_length(TOKAMAK_RADIAL_BUILD), 4, gap=20, name="module")
    sectors = segments(paramak.toroidal_arc_length(TOKAMAK_RADIAL_BUILD, rotation_angle=90), 3, gap=20, name="sector")
    result = paramak.tokamak_from_plasma(
        radial_build=TOKAMAK_RADIAL_BUILD,
        rotation_angle=90,
        poloidal_build=[None, modules, None, None],
        toroidal_build=[None, sectors, sectors, None],
    )
    assert result.split_solids().names() == result.names()
    assert len(result.names()) == len(UNSEGMENTED_PARTS) + 4 * 3 + 3


def test_divertor_is_split_into_one_solid_per_overlapped_segment():
    "with segmented layers the divertor has one solid for each segment it cuts out of"

    divertor = cq.Workplane("XZ").polyline([(300, -700), (300, 0), (400, 0), (400, -700)]).close().revolve(90)
    arc_length = paramak.poloidal_arc_length(TOKAMAK_RADIAL_BUILD)
    modules = segments(arc_length, 6, gap=0, name="module")
    poloidal_build = [None, modules, modules, modules]

    without_divertor = paramak.tokamak_from_plasma(
        radial_build=TOKAMAK_RADIAL_BUILD, rotation_angle=90, poloidal_build=poloidal_build
    )
    with_divertor = paramak.tokamak_from_plasma(
        radial_build=TOKAMAK_RADIAL_BUILD,
        rotation_angle=90,
        poloidal_build=poloidal_build,
        extra_intersect_shapes=[divertor],
    )

    volumes_before = {child.name: child.toCompound().Volume() for child in without_divertor.children}
    parts_after = {child.name: child.toCompound() for child in with_divertor.children}
    cut_segments = [
        name
        for name, volume in volumes_before.items()
        if "_module_" in name and parts_after[name].Volume() < volume * (1 - 1e-6)
    ]
    divertor_solids = parts_after["extra_intersect_shapes_1"].Solids()

    assert len(cut_segments) > 0
    assert len(divertor_solids) == len(cut_segments)
    for solid in divertor_solids:
        assert solid.isValid()
