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


def test_poloidal_arc_lengths_circular_plasma():
    "a circular plasma has circular offset surfaces, so the arc lengths are 2 pi r"

    arc_lengths = paramak.poloidal_arc_lengths(POLOIDAL_RADIAL_BUILD, elongation=1.0, triangularity=0.0)

    minor_radius = 150
    assert arc_lengths[0] is None  # the gap after the plasma
    assert arc_lengths[1] == pytest.approx(2 * math.pi * (minor_radius + 60), rel=1e-6)
    assert arc_lengths[2] == pytest.approx(2 * math.pi * (minor_radius + 80), rel=1e-6)
    assert arc_lengths[3] == pytest.approx(2 * math.pi * (minor_radius + 200), rel=1e-6)


def test_poloidal_arc_lengths_with_vertical_build():
    "the vertical build changes the elongation and so the arc lengths"

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
    from_vertical_build = paramak.poloidal_arc_lengths(
        POLOIDAL_RADIAL_BUILD, triangularity=0.0, vertical_build=vertical_build
    )
    # the vertical build has a plasma height equal to the plasma width so elongation is 1
    from_elongation = paramak.poloidal_arc_lengths(POLOIDAL_RADIAL_BUILD, elongation=1.0, triangularity=0.0)
    assert from_vertical_build[1] == pytest.approx(from_elongation[1])

    with pytest.raises(ValueError, match="elongation can not be set"):
        paramak.poloidal_arc_lengths(POLOIDAL_RADIAL_BUILD, elongation=2.0, vertical_build=vertical_build)


def test_poloidal_build_names_and_volumes():
    "segments without gaps should fill the same volume as the unsegmented layer"

    arc_lengths = paramak.poloidal_arc_lengths(POLOIDAL_RADIAL_BUILD, elongation=2.0, triangularity=0.55)
    arc = arc_lengths[2]

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
            [("outboard", arc * 0.2), ("inboard", arc * 0.6), ("outboard", arc * 0.2)],
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
    assert segment_volume == pytest.approx(unsegmented_volumes["layer_4"], rel=1e-3)
    # the inboard segment is three times the arc length of each outboard segment
    # but is closer to the axis, so it has less than three times the volume
    assert segmented_volumes["layer_4_inboard"] < 3 * segmented_volumes["layer_4_outboard_1"]
    # other layers are unchanged
    for name in ["layer_1", "layer_2", "layer_3", "layer_5", "plasma"]:
        assert segmented_volumes[name] == pytest.approx(unsegmented_volumes[name])


def test_poloidal_build_gaps_remove_volume():
    "gap segments produce no solid so the segments have less volume than the layer"

    arc_lengths = paramak.poloidal_arc_lengths(POLOIDAL_RADIAL_BUILD)
    gap = 50
    number_of_modules = 4
    module = (arc_lengths[1] - number_of_modules * gap) / number_of_modules

    segmented = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        rotation_angle=90,
        poloidal_build=[None, [("module", module), ("gap", gap)] * number_of_modules, None, None],
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
    "a single segment covering the whole loop should match the unsegmented layer"

    arc_lengths = paramak.poloidal_arc_lengths(POLOIDAL_RADIAL_BUILD)
    segmented = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        rotation_angle=90,
        poloidal_build=[None, None, None, [("rear", arc_lengths[3])]],
    )
    unsegmented = paramak.tokamak_from_plasma(radial_build=POLOIDAL_RADIAL_BUILD, rotation_angle=90)
    assert "layer_5_rear" in segmented.names()
    assert volumes(segmented)["layer_5_rear"] == pytest.approx(volumes(unsegmented)["layer_5"], rel=1e-3)


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
    arc_lengths = paramak.poloidal_arc_lengths(radial_build, vertical_build=vertical_build)
    reactor = paramak.tokamak(
        radial_build=radial_build,
        vertical_build=vertical_build,
        rotation_angle=90,
        poloidal_build=[None, [("upper", arc_lengths[1] / 2), ("lower", arc_lengths[1] / 2)]],
    )
    assert reactor.names() == ["layer_1", "blanket_upper", "blanket_lower", "plasma"]


@pytest.mark.parametrize(
    "poloidal_build, error, match",
    [
        ([None, None], ValueError, "expected 4 entries but got 2"),
        ([[("a", 1)], None, None, None], ValueError, "corresponds to a LayerType.GAP"),
        ([None, [("a", 1)], None, None], ValueError, "Use paramak.poloidal_arc_lengths"),
        ([None, [("gap", 2000)], None, None], ValueError, "at least one segment that is not a gap"),
        ([None, [("a", -1)], None, None], ValueError, "positive arc_length"),
        ([None, [("a", 1000), ("gap", -1)], None, None], ValueError, "0 or more"),
        ([None, [], None, None], TypeError, "non empty list"),
        ([None, [(1, 100)], None, None], TypeError, "string name and a numeric arc_length"),
        ([None, [("a", "100")], None, None], TypeError, "string name and a numeric arc_length"),
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

    arc = paramak.poloidal_arc_lengths(POLOIDAL_RADIAL_BUILD)[1]
    paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        rotation_angle=90,
        poloidal_build=[None, [("a", arc * 0.5), ("b", arc * 0.5005)], None, None],
    )
    with pytest.raises(ValueError, match=f"{arc}"):
        paramak.tokamak_from_plasma(
            radial_build=POLOIDAL_RADIAL_BUILD,
            rotation_angle=90,
            poloidal_build=[None, [("a", arc * 0.5), ("b", arc * 0.51)], None, None],
        )


def test_aligned_poloidal_build_shares_segment_angles():
    "segments made with aligned_poloidal_build start and stop at the same poloidal angles in every layer"

    from paramak.assemblies.tokamak import get_poloidal_build_segment_angles, vertical_build_from_radial_build

    arc_lengths = paramak.poloidal_arc_lengths(POLOIDAL_RADIAL_BUILD)
    gap = 20
    number_of_modules = 8
    module = (arc_lengths[1] - number_of_modules * gap) / number_of_modules

    poloidal_build = paramak.aligned_poloidal_build(
        POLOIDAL_RADIAL_BUILD, [("module", module), ("gap", gap)] * number_of_modules, layers=[1, 2, 3]
    )
    assert poloidal_build[0] is None
    for index in [1, 2, 3]:
        assert sum(length for _, length in poloidal_build[index]) == pytest.approx(arc_lengths[index])
    # the reference layer keeps the requested arc lengths
    assert poloidal_build[1][0][1] == pytest.approx(module)
    assert poloidal_build[1][1][1] == pytest.approx(gap)
    # layers further from the plasma have longer segments and gaps
    assert poloidal_build[1][1][1] < poloidal_build[2][1][1] < poloidal_build[3][1][1]

    segment_angles = get_poloidal_build_segment_angles(
        poloidal_build, POLOIDAL_RADIAL_BUILD, vertical_build_from_radial_build(POLOIDAL_RADIAL_BUILD, 2.0), 0.55
    )
    for first, second, third in zip(segment_angles[1], segment_angles[2], segment_angles[3]):
        assert first[1:] == pytest.approx(second[1:], abs=1e-9)
        assert first[1:] == pytest.approx(third[1:], abs=1e-9)

    reactor = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD, rotation_angle=90, poloidal_build=poloidal_build
    )
    assert len([name for name in reactor.names() if "_module_" in name]) == 3 * number_of_modules


def test_aligned_poloidal_build_reference_layer():
    "the segment arc lengths can be measured on a layer other than the first"

    arc_lengths = paramak.poloidal_arc_lengths(POLOIDAL_RADIAL_BUILD)
    poloidal_build = paramak.aligned_poloidal_build(
        POLOIDAL_RADIAL_BUILD,
        [("upper", arc_lengths[3] / 2), ("lower", arc_lengths[3] / 2)],
        layers=[1, 2],
        reference_layer=3,
    )
    assert poloidal_build[3] is None
    # the boundary at half the loop is the inboard midplane in every layer
    assert poloidal_build[1][0][1] == pytest.approx(arc_lengths[1] / 2, rel=1e-3)
    assert poloidal_build[2][0][1] == pytest.approx(arc_lengths[2] / 2, rel=1e-3)


@pytest.mark.parametrize(
    "kwargs, error, match",
    [
        ({"layers": []}, ValueError, "at least one"),
        ({"layers": [0]}, ValueError, "LayerType.GAP"),
        ({"layers": [9]}, ValueError, "out of range"),
        ({"layers": [1.0]}, TypeError, "must be integers"),
        ({"layers": [1], "segments": [("a", 1)]}, ValueError, "Use paramak.poloidal_arc_lengths"),
        ({"layers": [1], "segments": [("a", -1)]}, ValueError, "positive arc_length"),
    ],
)
def test_aligned_poloidal_build_validation(kwargs, error, match):
    arc = paramak.poloidal_arc_lengths(POLOIDAL_RADIAL_BUILD)[1]
    kwargs = {"segments": [("a", arc)], **kwargs}
    with pytest.raises(error, match=match):
        paramak.aligned_poloidal_build(POLOIDAL_RADIAL_BUILD, **kwargs)


def lower_divertor_shape(rotation_angle):
    "a shape overlapping the layers under the plasma, intersected with the layers to make a divertor"
    points = [(300, -700), (300, 0), (400, 0), (400, -700)]
    return cq.Workplane("XZ").polyline(points).close().revolve(rotation_angle)


def test_poloidal_build_with_divertor_conserves_volume():
    "the divertor is cut out of the segments, and segments plus divertor fill the same volume as without segments"

    arc_lengths = paramak.poloidal_arc_lengths(POLOIDAL_RADIAL_BUILD)
    number_of_modules = 6
    poloidal_build = paramak.aligned_poloidal_build(
        POLOIDAL_RADIAL_BUILD,
        [("module", arc_lengths[1] / number_of_modules)] * number_of_modules,
        layers=[1, 2, 3],
    )

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
    removed = sum(no_divertor_volumes[name] - segmented_volumes[name] for name in no_divertor_volumes if "_module_" in name)
    removed_from_layers = sum(
        no_divertor_volumes[name] - segmented_volumes[name] for name in ["layer_1", "layer_2"]
    )
    assert removed + removed_from_layers == pytest.approx(segmented_volumes["extra_intersect_shapes_1"], rel=1e-3)

    # total volume of layers and divertor matches the unsegmented reactor
    def total(volume_dict):
        return sum(value for name, value in volume_dict.items() if name != "plasma")

    assert total(segmented_volumes) == pytest.approx(total(unsegmented_volumes), rel=1e-3)


def test_poloidal_build_with_divertor_and_gaps():
    "gaps between segments are not filled by the divertor"

    arc_lengths = paramak.poloidal_arc_lengths(POLOIDAL_RADIAL_BUILD)
    arc = arc_lengths[1]
    # the gap runs from 70 to 80 percent of the way around the loop, which is
    # under the plasma where the divertor is
    poloidal_build = paramak.aligned_poloidal_build(
        POLOIDAL_RADIAL_BUILD,
        [("upper", arc * 0.7), ("gap", arc * 0.1), ("lower", arc * 0.2)],
        layers=[1, 2, 3],
    )

    with_gaps = paramak.tokamak_from_plasma(
        radial_build=POLOIDAL_RADIAL_BUILD,
        rotation_angle=90,
        extra_intersect_shapes=[lower_divertor_shape(90)],
        poloidal_build=poloidal_build,
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
