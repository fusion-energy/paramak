import math

import cadquery as cq
import pytest

import paramak


def test_colors():
    "passing in the colors dictionary should not raise an error"

    paramak.tokamak_from_plasma(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 30),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 10),
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=180,
        colors={
            "layer_1": (0.4, 0.9, 0.4),
            "layer_2": (0.6, 0.8, 0.6),
            "plasma": (1., 0.7, 0.8, 0.6),
            "layer_3": (0.1, 0.1, 0.9),
            "layer_4": (0.4, 0.4, 0.8),
            "layer_5": (0.5, 0.5, 0.8),
        }
    )


def test_layer_names_are_contiguous_with_interior_gaps():
    "layer names should be sequential layer_1..layer_N even when gaps sit between solid layers"

    my_reactor = paramak.tokamak(
        radial_build=[
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.GAP, 20),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.GAP, 20),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
        ],
        vertical_build=[
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.GAP, 20),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 650),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.GAP, 20),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
        ],
        rotation_angle=180,
    )

    assert my_reactor.names() == ["layer_1", "layer_2", "layer_3", "layer_4", "layer_5", "plasma"]


def test_named_layers_tokamak():
    "layers can be named in the radial_build, or with rename() after building"

    from_radial_build = paramak.tokamak_from_plasma(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 30, "central column"),
            (paramak.LayerType.SOLID, 20, "blanket"),
            (paramak.LayerType.SOLID, 10, "first wall"),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 10),
        ],
        rotation_angle=180,
    )
    assert from_radial_build.names() == ["central column", "first wall", "blanket", "plasma"]

    renamed = (
        paramak.tokamak_from_plasma(
            radial_build=[
                (paramak.LayerType.GAP, 10),
                (paramak.LayerType.SOLID, 30),
                (paramak.LayerType.SOLID, 20),
                (paramak.LayerType.SOLID, 10),
                (paramak.LayerType.GAP, 60),
                (paramak.LayerType.PLASMA, 300),
                (paramak.LayerType.GAP, 60),
                (paramak.LayerType.SOLID, 20),
                (paramak.LayerType.SOLID, 10),
            ],
            rotation_angle=180,
        )
        .rename("layer_1", "central column")
        .rename("layer_2", "first wall")
        .rename("layer_3", "blanket")
    )
    assert renamed.names() == ["central column", "first wall", "blanket", "plasma"]

POLOIDAL_RADIAL_BUILD = [
    (paramak.LayerType.GAP, 10),
    (paramak.LayerType.SOLID, 30),
    (paramak.LayerType.SOLID, 50),
    (paramak.LayerType.SOLID, 10),
    (paramak.LayerType.SOLID, 120),
    (paramak.LayerType.SOLID, 20),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.PLASMA, 300),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.SOLID, 20),
    (paramak.LayerType.SOLID, 120),
    (paramak.LayerType.SOLID, 10),
]


def volumes(assembly):
    return {child.name: child.toCompound().Volume() for child in assembly.children}


def lower_divertor_shape(rotation_angle):
    "a shape overlapping the layers under the plasma, intersected with the layers to make a divertor"
    points = [(300, -700), (300, 0), (400, 0), (400, -700)]
    return cq.Workplane("XZ").polyline(points).close().revolve(rotation_angle)


def equal_segments(arc_length, number_of_segments, gap, name="module"):
    "a poloidal_build entry of equally sized segments separated by gaps"
    segment = (arc_length - number_of_segments * gap) / number_of_segments
    return [(paramak.LayerType.SOLID, segment, name), (paramak.LayerType.GAP, gap)] * number_of_segments


def test_poloidal_arc_length_circular_plasma():
    "a circular plasma has circular offset surfaces, so the arc length is 2 pi r of the plasma facing surface"

    arc_length = paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD, elongation=1.0, triangularity=0.0)

    minor_radius = 150
    gap_to_plasma = 60
    assert arc_length == pytest.approx(2 * math.pi * (minor_radius + gap_to_plasma), rel=1e-6)


def test_poloidal_arc_length_with_vertical_build():
    "the vertical build sets the elongation"

    vertical_build = [
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.SOLID, 120),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.SOLID, 120),
        (paramak.LayerType.SOLID, 20),
    ]
    # the plasma height equals the plasma width so the elongation is 1
    from_vertical_build = paramak.poloidal_arc_length(
        POLOIDAL_RADIAL_BUILD, triangularity=0.0, vertical_build=vertical_build
    )
    from_elongation = paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD, elongation=1.0, triangularity=0.0)
    assert from_vertical_build == pytest.approx(from_elongation)

    with pytest.raises(ValueError, match="elongation can not be set"):
        paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD, elongation=2.0, vertical_build=vertical_build)


def test_poloidal_build_names_and_volumes():
    "segments without gaps should fill the same volume as the unsegmented layer"

    arc_length = paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD, elongation=2.0, triangularity=0.55)

    unsegmented = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD, elongation=2.0, triangularity=0.55, rotation_angle=90
    )
    segmented = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        elongation=2.0,
        triangularity=0.55,
        rotation_angle=90,
        poloidal_build=[
            None,
            None,
            [
                (paramak.LayerType.SOLID, arc_length * 0.2, "outboard"),
                (paramak.LayerType.SOLID, arc_length * 0.6, "inboard"),
                (paramak.LayerType.SOLID, arc_length * 0.2, "outboard"),
            ],
            None,
        ],
    )

    assert segmented.names() == [
        "layer_1",
        "layer_2",
        "layer_3",
        "layer_4_outboard_1",
        "layer_4_inboard",
        "layer_4_outboard_2",
        "layer_5",
        "plasma",
    ]

    unsegmented_volumes = volumes(unsegmented)
    segmented_volumes = volumes(segmented)
    segment_volume = sum(segmented_volumes[name] for name in segmented_volumes if name.startswith("layer_4_"))
    assert segment_volume == pytest.approx(unsegmented_volumes["layer_4"], rel=1e-6)
    # the inboard segment is three times the arc length of each outboard segment
    # but is closer to the axis, so it has less than three times the volume
    assert segmented_volumes["layer_4_inboard"] < 3 * segmented_volumes["layer_4_outboard_1"]
    # other layers are unchanged
    for name in ["layer_1", "layer_2", "layer_3", "layer_5", "plasma"]:
        assert segmented_volumes[name] == pytest.approx(unsegmented_volumes[name])


def test_poloidal_build_gaps_remove_volume():
    "gap segments produce no solid so the segments have less volume than the layer"

    arc_length = paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD)
    number_of_modules = 4
    module_gap = 50

    segmented = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        rotation_angle=90,
        poloidal_build=[None, equal_segments(arc_length, number_of_modules, module_gap), None, None],
    )
    unsegmented = paramak.tokamak_from_plasma(radial_build=POLOIDAL_RADIAL_BUILD, rotation_angle=90)

    assert segmented.names() == [
        "layer_1",
        "layer_2",
        "layer_3_module_1",
        "layer_3_module_2",
        "layer_3_module_3",
        "layer_3_module_4",
        "layer_4",
        "layer_5",
        "plasma",
    ]
    segmented_volumes = volumes(segmented)
    segment_volume = sum(segmented_volumes[name] for name in segmented_volumes if name.startswith("layer_3_"))
    assert segment_volume < volumes(unsegmented)["layer_3"]


def test_poloidal_build_single_full_segment():
    "a single segment covering the whole loop is the unsegmented layer"

    arc_length = paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD)
    segmented = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        rotation_angle=90,
        poloidal_build=[None, None, None, [(paramak.LayerType.SOLID, arc_length, "rear")]],
    )
    unsegmented = paramak.tokamak_from_plasma(radial_build=POLOIDAL_RADIAL_BUILD, rotation_angle=90)
    assert "layer_5_rear" in segmented.names()
    assert volumes(segmented)["layer_5_rear"] == pytest.approx(volumes(unsegmented)["layer_5"], rel=1e-6)


def test_poloidal_build_with_named_layer_and_tokamak():
    "segment names use the layer name from the radial build, and tokamak() supports poloidal_build"

    radial_build = [
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 30),
        (paramak.LayerType.SOLID, 20, "blanket"),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 20),
    ]
    vertical_build = [
        (paramak.LayerType.SOLID, 30),
        (paramak.LayerType.GAP, 50),
        (paramak.LayerType.PLASMA, 700),
        (paramak.LayerType.GAP, 50),
        (paramak.LayerType.SOLID, 30),
    ]
    arc_length = paramak.poloidal_arc_length(radial_build, vertical_build=vertical_build)
    reactor = paramak.tokamak(
        radial_build=radial_build,
        vertical_build=vertical_build,
        rotation_angle=90,
        poloidal_build=[None, [(paramak.LayerType.SOLID, arc_length / 2, "upper"), (paramak.LayerType.SOLID, arc_length / 2, "lower")]],
    )
    assert reactor.names() == ["layer_1", "blanket_upper", "blanket_lower", "plasma"]


def test_same_segments_line_up_through_layers():
    "layers given the same segments start and stop at the same poloidal angles"

    from paramak.assemblies.tokamak import get_poloidal_build_segment_angles, vertical_build_from_radial_build

    arc_length = paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD)
    modules = equal_segments(arc_length, number_of_segments=8, gap=20)
    poloidal_build = [None, modules, modules, modules]

    segment_angles = get_poloidal_build_segment_angles(
        poloidal_build, POLOIDAL_RADIAL_BUILD, vertical_build_from_radial_build(POLOIDAL_RADIAL_BUILD, 2.0), 0.55
    )
    assert segment_angles[0] is None
    assert segment_angles[1] == segment_angles[2] == segment_angles[3]

    reactor = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD, rotation_angle=90, poloidal_build=poloidal_build
    )
    assert len([name for name in reactor.names() if "_module_" in name]) == 3 * 8


def test_different_segments_per_layer():
    "each layer can have its own segments, and boundaries at the same arc length line up"

    from paramak.assemblies.tokamak import get_poloidal_build_segment_angles, vertical_build_from_radial_build

    arc_length = paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD)
    poloidal_build = [
        None,
        equal_segments(arc_length, number_of_segments=4, gap=0, name="tile"),
        equal_segments(arc_length, number_of_segments=2, gap=0),
        None,
    ]
    segment_angles = get_poloidal_build_segment_angles(
        poloidal_build, POLOIDAL_RADIAL_BUILD, vertical_build_from_radial_build(POLOIDAL_RADIAL_BUILD, 2.0), 0.55
    )
    tiles, modules = segment_angles[1], segment_angles[2]
    # the boundary between the two modules is the boundary between the second and third tile
    assert modules[0][2] == pytest.approx(tiles[1][2])
    assert modules[1][1] == pytest.approx(tiles[2][1])

    reactor = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD, rotation_angle=90, poloidal_build=poloidal_build
    )
    assert [name for name in reactor.names() if "_tile_" in name or "_module_" in name] == [
        "layer_3_tile_1",
        "layer_3_tile_2",
        "layer_3_tile_3",
        "layer_3_tile_4",
        "layer_4_module_1",
        "layer_4_module_2",
    ]


def test_unnamed_segments():
    "solid segments without a name are called segment"

    arc_length = paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD)
    reactor = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        rotation_angle=90,
        poloidal_build=[
            None,
            [(paramak.LayerType.SOLID, arc_length / 2), (paramak.LayerType.SOLID, arc_length / 2)],
            [(paramak.LayerType.SOLID, arc_length)],
            None,
        ],
    )
    assert reactor.names() == [
        "layer_1",
        "layer_2",
        "layer_3_segment_1",
        "layer_3_segment_2",
        "layer_4_segment",
        "layer_5",
        "plasma",
    ]


@pytest.mark.parametrize(
    "poloidal_build, error, match",
    [
        ([None, None], ValueError, "expected 4 entries but got 2"),
        ([[(paramak.LayerType.SOLID, 1)], None, None, None], ValueError, "corresponds to a LayerType.GAP"),
        ([None, [(paramak.LayerType.SOLID, 1)], None, None], ValueError, "Use paramak.poloidal_arc_length"),
        ([None, [(paramak.LayerType.GAP, 2000)], None, None], ValueError, "at least one LayerType.SOLID segment"),
        ([None, [(paramak.LayerType.SOLID, -1)], None, None], ValueError, "positive arc_length"),
        ([None, [(paramak.LayerType.SOLID, 1000), (paramak.LayerType.GAP, -1)], None, None], ValueError, "0 or more"),
        ([None, [(paramak.LayerType.SOLID, 1000), (paramak.LayerType.GAP, 10, "named")], None, None], ValueError, "can not be named"),
        ([None, [(paramak.LayerType.PLASMA, 1000)], None, None], ValueError, "must be LayerType.SOLID or"),
        ([None, [], None, None], TypeError, "non empty list"),
        ([None, [("tile", 100)], None, None], TypeError, "paramak.LayerType, arc_length"),
        ([None, [(paramak.LayerType.SOLID, "100")], None, None], TypeError, "numeric arc_length"),
        ([None, [(paramak.LayerType.SOLID, 100, 5)], None, None], TypeError, "string"),
        ("not a list", TypeError, "must be a list"),
    ],
)
def test_poloidal_build_validation(poloidal_build, error, match):
    with pytest.raises(error, match=match):
        paramak.tokamak_from_plasma(
            radial_build=POLOIDAL_RADIAL_BUILD, rotation_angle=90, poloidal_build=poloidal_build
        )


def test_poloidal_build_sum_tolerance():
    "arc lengths slightly off the total are accepted, larger differences are not"

    arc_length = paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD)
    paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        rotation_angle=90,
        poloidal_build=[None, [(paramak.LayerType.SOLID, arc_length * 0.5), (paramak.LayerType.SOLID, arc_length * 0.5005)], None, None],
    )
    with pytest.raises(ValueError, match=f"{arc_length}"):
        paramak.tokamak_from_plasma(
            radial_build=POLOIDAL_RADIAL_BUILD,
            rotation_angle=90,
            poloidal_build=[None, [(paramak.LayerType.SOLID, arc_length * 0.5), (paramak.LayerType.SOLID, arc_length * 0.51)], None, None],
        )


def test_poloidal_build_with_divertor_conserves_volume():
    "the divertor is cut out of the segments, and segments plus divertor fill the same volume as without segments"

    arc_length = paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD)
    number_of_modules = 6
    modules = equal_segments(arc_length, number_of_modules, gap=0)
    poloidal_build = [None, modules, modules, modules]

    unsegmented = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        rotation_angle=90,
        extra_intersect_shapes=[lower_divertor_shape(90)],
    )
    segmented = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        rotation_angle=90,
        extra_intersect_shapes=[lower_divertor_shape(90)],
        poloidal_build=poloidal_build,
    )
    segmented_no_divertor = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD, rotation_angle=90, poloidal_build=poloidal_build
    )

    assert "extra_intersect_shapes_1" in segmented.names()
    assert len([name for name in segmented.names() if "_module_" in name]) == 3 * number_of_modules

    unsegmented_volumes = volumes(unsegmented)
    segmented_volumes = volumes(segmented)
    no_divertor_volumes = volumes(segmented_no_divertor)

    # the divertor is the same shape whether or not the layers are segmented
    assert segmented_volumes["extra_intersect_shapes_1"] == pytest.approx(
        unsegmented_volumes["extra_intersect_shapes_1"], rel=1e-3
    )
    assert segmented_volumes["extra_intersect_shapes_1"] > 0

    # the divertor volume is removed from the segments it overlaps and no others
    reduced = [
        name
        for name in no_divertor_volumes
        if "_module_" in name and segmented_volumes[name] < no_divertor_volumes[name] * (1 - 1e-6)
    ]
    assert 0 < len(reduced) < 3 * number_of_modules
    removed = sum(
        no_divertor_volumes[name] - segmented_volumes[name] for name in no_divertor_volumes if name != "plasma"
    )
    assert removed == pytest.approx(segmented_volumes["extra_intersect_shapes_1"], rel=1e-3)

    # total volume of layers and divertor matches the unsegmented reactor
    def total(volume_dict):
        return sum(value for name, value in volume_dict.items() if name != "plasma")

    assert total(segmented_volumes) == pytest.approx(total(unsegmented_volumes), rel=1e-3)


def test_poloidal_build_with_divertor_and_gaps():
    "gaps between segments are not filled by the divertor"

    arc_length = paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD)
    # the gap runs from 70 to 80 percent of the way around the loop, which is
    # under the plasma where the divertor is
    segments = [
        (paramak.LayerType.SOLID, arc_length * 0.7, "upper"),
        (paramak.LayerType.GAP, arc_length * 0.1),
        (paramak.LayerType.SOLID, arc_length * 0.2, "lower"),
    ]

    with_gaps = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        rotation_angle=90,
        extra_intersect_shapes=[lower_divertor_shape(90)],
        poloidal_build=[None, segments, segments, segments],
    )
    without_segments = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        rotation_angle=90,
        extra_intersect_shapes=[lower_divertor_shape(90)],
    )
    divertor_with_gaps = volumes(with_gaps)["extra_intersect_shapes_1"]
    divertor_without_segments = volumes(without_segments)["extra_intersect_shapes_1"]
    assert 0 < divertor_with_gaps < divertor_without_segments * 0.99
    for child in with_gaps.children:
        assert child.toCompound().isValid()


@pytest.mark.parametrize(
    "segmented_layers, number_of_modules",
    [
        ([1], 16),  # first wall tiles next to an unsegmented blanket
        ([2], 3),  # blanket modules between an unsegmented first wall and rear wall
        ([1, 2], 3),  # first wall and blanket next to an unsegmented rear wall
    ],
)
def test_poloidal_build_next_to_unsegmented_layers_with_divertor(segmented_layers, number_of_modules):
    "segmented layers next to unsegmented layers share faces exactly, so the divertor can be made"

    arc_length = paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD)
    modules = equal_segments(arc_length, number_of_modules, gap=15)
    poloidal_build = [modules if index in segmented_layers else None for index in range(4)]
    reactor = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        rotation_angle=90,
        extra_intersect_shapes=[lower_divertor_shape(90)],
        poloidal_build=poloidal_build,
    )
    assert volumes(reactor)["extra_intersect_shapes_1"] > 0
    for child in reactor.children:
        assert child.toCompound().isValid()


def test_segment_names_that_clash_after_suffixes():
    "a name given directly that matches a suffixed repeated name raises a clear error"

    arc_length = paramak.poloidal_arc_length(POLOIDAL_RADIAL_BUILD)
    with pytest.raises(ValueError, match="tile_1"):
        paramak.tokamak_from_plasma(
            radial_build=POLOIDAL_RADIAL_BUILD,
            rotation_angle=90,
            poloidal_build=[
                None,
                [
                    (paramak.LayerType.SOLID, arc_length / 3, "tile"),
                    (paramak.LayerType.SOLID, arc_length / 3, "tile"),
                    (paramak.LayerType.SOLID, arc_length / 3, "tile_1"),
                ],
                None,
                None,
            ],
        )
