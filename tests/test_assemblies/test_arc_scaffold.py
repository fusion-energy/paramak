import inspect
import math

import cadquery as cq
import pytest
from cadquery.occ_impl.assembly import imprint

import paramak


def test_public_export():
    assert "arc_from_2026_paper" in paramak.__all__
    assert callable(paramak.arc_from_2026_paper)


def test_defaults():
    #ARC TF default is sourced from Hillesheim p.10; PF case remains provisional.
    parameters = inspect.signature(paramak.arc_from_2026_paper).parameters
    assert parameters["number_of_tf_coils"].default == 18
    assert parameters["rotation_angle"].default == 180.0
    assert parameters["pf_coil_case_thickness"].default == 3.0
    assert parameters["colors"].default is None


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_plasma_geometry_and_metadata(angle):
    #ARC Validate the smooth approximation; full equilibrium geometry is pending.
    reactor = paramak.arc_from_2026_paper(rotation_angle=angle)
    assert reactor.names() == (
        ["plasma"] + [f"central_solenoid_{i}" for i in range(1, 7)]
        + [name for i in range(1, 11) for name in (f"pf_coil_{i}", f"pf_coil_case_{i}")]
        + ["toroidal_field_coil", "first_wall", "inner_vessel", "flibe_first_wall", "outer_vessel", "neutron_shield", "flibe_blanket"]
    )
    assert reactor.major_radius == 462.0
    assert reactor.minor_radius == 118.0
    assert reactor.elongation == 1.8
    assert math.sin(reactor.triangularity) == pytest.approx(0.65)
    shape = reactor.objects["plasma"].obj.val()
    assert shape.isValid()
    assert shape.Volume() > 0
    box = shape.BoundingBox()
    assert box.zmax == pytest.approx(118 * 1.8, abs=0.1)
    assert box.zmin == pytest.approx(-118 * 1.8, abs=0.1)
    assert box.xmax == pytest.approx(462 + 118, abs=0.1)


def test_plasma_sector_volume_and_color():
    #ARC Keep metadata consistent while checking full-turn construction and overrides.
    half = paramak.arc_from_2026_paper(colors={"plasma": (0.1, 0.2, 0.3)})
    full = paramak.arc_from_2026_paper(rotation_angle=360)
    assert full.toCompound().Volume() == pytest.approx(2 * half.toCompound().Volume(), rel=1e-3)
    color = next(iter(half))[3]
    assert color.toTuple()[:3] == pytest.approx((0.1, 0.2, 0.3))


@pytest.mark.parametrize("angle", [0, -10, 361])
def test_invalid_rotation_angle(angle):
    with pytest.raises(ValueError, match="rotation_angle"):
        paramak.arc_from_2026_paper(rotation_angle=angle)


@pytest.mark.parametrize("count", [0, -1, 2.5, True])
def test_invalid_tf_coil_count(count):
    with pytest.raises(ValueError, match="number_of_tf_coils"):
        paramak.arc_from_2026_paper(number_of_tf_coils=count)


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_solenoid_envelopes(angle):
    #ARC Independent reference expectations from cs1u/l, cs2u/l, cs3u/l elements.
    reactor = paramak.arc_from_2026_paper(rotation_angle=angle)
    inner_radius, outer_radius = 72.69, 148.31
    for index, (centre_z, height) in enumerate(
        [(75, 138.6565217391304), (-75, 138.6565217391304),
         (190, 68.6565217391304), (-190, 68.6565217391304),
         (270, 68.6565217391304), (-270, 68.6565217391304)], 1
    ):
        shape = reactor.objects[f"central_solenoid_{index}"].obj.val()
        assert shape.isValid()
        assert len(shape.Solids()) == 1
        box = shape.BoundingBox()
        assert box.zmin == pytest.approx(centre_z - height / 2, abs=1e-5)
        assert box.zmax == pytest.approx(centre_z + height / 2, abs=1e-5)
        assert box.xmax == pytest.approx(outer_radius, abs=1e-5)
        expected_volume = math.pi * (outer_radius**2 - inner_radius**2) * height * angle / 360
        assert shape.Volume() == pytest.approx(expected_volume, rel=1e-6)
    shapes = [child.obj.val() for child in reactor.children]
    for i, first in enumerate(shapes):
        for second in shapes[i + 1:]:
            assert first.intersect(second).Volume() == pytest.approx(0, abs=1e-5)


def test_solenoid_color_override():
    reactor = paramak.arc_from_2026_paper(colors={"central_solenoid_1": (0.2, 0.4, 0.6)})
    assert reactor.objects["central_solenoid_1"].color.toTuple()[:3] == pytest.approx((0.2, 0.4, 0.6))


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_pf_coil_envelopes_and_cases(angle):
    #ARC Independent envelope expectations from JSON; 3 cm casing is assumed.
    reactor = paramak.arc_from_2026_paper(rotation_angle=angle)
    for index in range(1, 11):
        pair = (index - 1) // 2
        centre_r = [140, 190, 620, 620, 695][pair]
        centre_z = [390, 475, 295, 225, 160][pair] * (1 if index % 2 else -1)
        size = [59, 68.9565217391304, 48.875, 48.875, 38.9230769230769][pair]
        core = reactor.objects[f"pf_coil_{index}"].obj.val()
        case = reactor.objects[f"pf_coil_case_{index}"].obj.val()
        assert core.isValid() and case.isValid()
        assert core.Volume() > 0 and case.Volume() > 0
        outer = case.BoundingBox()
        inner = core.BoundingBox()
        assert outer.xmax == pytest.approx(centre_r + size / 2, abs=1e-5)
        assert outer.zmin == pytest.approx(centre_z - size / 2, abs=1e-5)
        assert outer.zmax == pytest.approx(centre_z + size / 2, abs=1e-5)
        assert inner.zmin == pytest.approx(outer.zmin + 3, abs=1e-5)
        assert inner.zmax == pytest.approx(outer.zmax - 3, abs=1e-5)
        assert core.intersect(case).Volume() == pytest.approx(0, abs=1e-5)
        assert core.distance(case) == pytest.approx(0, abs=1e-5)
        expected = math.pi * ((centre_r + size / 2)**2 - (centre_r - size / 2)**2) * size * angle / 360
        assert core.fuse(case).Volume() == pytest.approx(expected, rel=1e-6)


def test_pf_case_thickness_and_colors():
    #ARC Hypothesized thickness changes the split while preserving the outer envelope.
    thin = paramak.arc_from_2026_paper(rotation_angle=30, pf_coil_case_thickness=1)
    thick = paramak.arc_from_2026_paper(
        rotation_angle=30, pf_coil_case_thickness=5,
        colors={"pf_coil_1": (0.1, 0.2, 0.3), "pf_coil_case_1": (0.4, 0.5, 0.6)},
    )
    for index in range(1, 11):
        core, case = f"pf_coil_{index}", f"pf_coil_case_{index}"
        def volume(assembly, name):
            return assembly.objects[name].obj.val().Volume()
        assert volume(thick, core) < volume(thin, core)
        assert volume(thick, case) > volume(thin, case)
        assert volume(thick, core) + volume(thick, case) == pytest.approx(
            volume(thin, core) + volume(thin, case), rel=1e-6,
        )
    assert thick.objects["pf_coil_1"].color.toTuple()[:3] == pytest.approx((0.1, 0.2, 0.3))
    assert thick.objects["pf_coil_case_1"].color.toTuple()[:3] == pytest.approx((0.4, 0.5, 0.6))


@pytest.mark.parametrize("thickness", [0, -1, float("nan"), float("inf"), 1000, 20])
def test_invalid_pf_case_thickness(thickness):
    with pytest.raises(ValueError, match="pf_coil_case_thickness"):
        paramak.arc_from_2026_paper(pf_coil_case_thickness=thickness)


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_tf_profile_extrusion(angle):
    #ARC Reference polygon area from the user profiles, cm2; extrusion assumption is 40 cm.
    reactor = paramak.arc_from_2026_paper(rotation_angle=angle)
    tf = reactor.objects["toroidal_field_coil"].obj.val()
    assert tf.isValid()
    assert tf.Volume() == pytest.approx(283368.27020694205 * 40 * 18 * angle / 360, rel=1e-6)
    box = tf.BoundingBox()
    assert box.xmax == pytest.approx(889.6142109267835, abs=1e-5)
    assert box.zmin == pytest.approx(-567.4071533810901, abs=1e-5)
    assert box.zmax == pytest.approx(570.0708867122844, abs=1e-5)
    if angle < 360:
        assert box.ymin >= -1e-5
    if angle == 90:
        assert box.xmin >= -1e-5
    if angle == 360:
        solids = tf.Solids()
        assert len(solids) == 18
        for first, second in zip(solids, solids[1:] + solids[:1]):
            assert first.intersect(second).Volume() == pytest.approx(0, abs=1e-5)


def test_tf_custom_count_and_color():
    reactor = paramak.arc_from_2026_paper(
        rotation_angle=360, number_of_tf_coils=6,
        colors={"toroidal_field_coil": (0.2, 0.3, 0.4)},
    )
    tf = reactor.objects["toroidal_field_coil"]
    assert len(tf.obj.val().Solids()) == 6
    assert tf.obj.val().Volume() == pytest.approx(283368.27020694205 * 40 * 6, rel=1e-6)
    assert tf.color.toTuple()[:3] == pytest.approx((0.2, 0.3, 0.4))


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_first_wall_geometry(angle):
    #ARC Independent full-turn volume from the JSON polygon moments; cm3.
    reactor = paramak.arc_from_2026_paper(rotation_angle=angle)
    wall = reactor.objects["first_wall"].obj.val()
    assert wall.isValid()
    assert len(wall.Solids()) == 1
    assert wall.Volume() == pytest.approx(3041653.552999719 * angle / 360, rel=1e-6)
    box = wall.BoundingBox()
    assert box.xmax == pytest.approx(582.5, abs=1e-5)
    assert box.zmax == pytest.approx(409.5, abs=1e-5)
    assert box.zmin == pytest.approx(-409.5, abs=1e-5)
    if angle < 360:
        assert box.ymin >= -1e-5
    if angle == 90:
        assert box.xmin >= -1e-5
    for child in reactor.children:
        if child.name != "first_wall":
            assert wall.intersect(child.obj.val()).Volume() == pytest.approx(0, abs=1e-4)


def test_first_wall_color_override():
    reactor = paramak.arc_from_2026_paper(colors={"first_wall": (0.3, 0.4, 0.5)})
    assert reactor.objects["first_wall"].color.toTuple()[:3] == pytest.approx((0.3, 0.4, 0.5))


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_vessel_walls_and_neutron_shield(angle):
    #ARC Independent polygon-moment volumes from the supplied JSON, in cm3.
    reactor = paramak.arc_from_2026_paper(rotation_angle=angle)
    expected = {
        "inner_vessel": (6105123.0299052, 583.5, 410.50000000000006),
        "outer_vessel": (18883600.83873242, 591.0, 418.0),
        "neutron_shield": (55362184.56153011, 411.0, 437.0),
    }
    for name, (full_volume, rmax, zmax) in expected.items():
        shape = reactor.objects[name].obj.val()
        assert shape.isValid()
        assert len(shape.Solids()) == 1
        assert shape.Volume() == pytest.approx(full_volume * angle / 360, rel=1e-6)
        box = shape.BoundingBox()
        assert box.xmax == pytest.approx(rmax, abs=1e-5)
        assert box.zmax == pytest.approx(zmax, abs=1e-5)
        assert box.zmin == pytest.approx(-zmax, abs=1e-5)
        if angle < 360:
            assert box.ymin >= -1e-5
        if angle == 90:
            assert box.xmin >= -1e-5
        for child in reactor.children:
            if child.name != name:
                assert shape.intersect(child.obj.val()).Volume() == pytest.approx(0, abs=1e-4), (name, child.name)
    first = reactor.objects["first_wall"].obj.val()
    inner = reactor.objects["inner_vessel"].obj.val()
    outer = reactor.objects["outer_vessel"].obj.val()
    assert first.distance(inner) == pytest.approx(0, abs=1e-5)
    assert inner.distance(outer) > 0


def test_vessel_and_shield_colors():
    colors = {name: (0.2, 0.4, 0.6) for name in ("inner_vessel", "outer_vessel", "neutron_shield")}
    reactor = paramak.arc_from_2026_paper(colors=colors)
    for name, color in colors.items():
        assert reactor.objects[name].color.toTuple()[:3] == pytest.approx(color)


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_flibe_first_wall_geometry(angle):
    #ARC Volume is the difference of independently integrated JSON vessel boundary polygons.
    reactor = paramak.arc_from_2026_paper(rotation_angle=angle)
    flibe = reactor.objects["flibe_first_wall"].obj.val()
    assert flibe.isValid()
    assert len(flibe.Solids()) == 1
    assert flibe.Volume() == pytest.approx(27833226.82232392 * angle / 360, rel=1e-6)
    box = flibe.BoundingBox()
    assert box.xmax == pytest.approx(588, abs=1e-5)
    assert box.zmin == pytest.approx(-415, abs=1e-5)
    assert box.zmax == pytest.approx(415, abs=1e-5)
    if angle < 360:
        assert box.ymin >= -1e-5
    if angle == 90:
        assert box.xmin >= -1e-5
    for name in ("inner_vessel", "outer_vessel"):
        vessel = reactor.objects[name].obj.val()
        assert flibe.distance(vessel) == pytest.approx(0, abs=1e-5)
        assert flibe.intersect(vessel).Volume() == pytest.approx(0, abs=1e-4)


def test_flibe_first_wall_interfaces_imprint():
    #ARC Verify shared faces on both sides of the filled cooling region.
    reactor = paramak.arc_from_2026_paper()
    assembly = cq.Assembly()
    for name in ("inner_vessel", "flibe_first_wall", "outer_vessel"):
        assembly.add(reactor.objects[name].obj, name=name)
    _, origins = imprint(assembly)
    faces = {}
    for solid, names in origins.items():
        assert len(names) == 1
        for face in solid.Faces():
            faces.setdefault(face, set()).add(names[0].split("/")[-1])
    pairs = {frozenset(names) for names in faces.values() if len(names) == 2}
    assert frozenset(("inner_vessel", "flibe_first_wall")) in pairs
    assert frozenset(("outer_vessel", "flibe_first_wall")) in pairs


def test_flibe_first_wall_color():
    reactor = paramak.arc_from_2026_paper(colors={"flibe_first_wall": (0.2, 0.5, 0.8)})
    assert reactor.objects["flibe_first_wall"].color.toTuple()[:3] == pytest.approx((0.2, 0.5, 0.8))


@pytest.mark.parametrize("angle", [90, 180, 360])
def test_flibe_blanket_geometry(angle):
    #ARC Independent polygon-moment volume: tank cavity minus vessel envelope and shield.
    reactor = paramak.arc_from_2026_paper(rotation_angle=angle)
    blanket = reactor.objects["flibe_blanket"].obj.val()
    assert blanket.isValid()
    assert len(blanket.Solids()) == 1
    assert blanket.Volume() == pytest.approx(431989820.1713178 * angle / 360, rel=1e-6)
    box = blanket.BoundingBox()
    assert box.xmax == pytest.approx(720, abs=1e-5)
    assert box.zmax == pytest.approx(468, abs=1e-5)
    assert box.zmin == pytest.approx(-468, abs=1e-5)
    if angle < 360:
        assert box.ymin >= -1e-5
    if angle == 90:
        assert box.xmin >= -1e-5
    for child in reactor.children:
        if child.name != "flibe_blanket":
            assert blanket.intersect(child.obj.val()).Volume() == pytest.approx(0, abs=1e-4), child.name
    for name in ("outer_vessel", "neutron_shield"):
        assert blanket.distance(reactor.objects[name].obj.val()) == pytest.approx(0, abs=1e-5)


def test_flibe_blanket_interfaces_imprint():
    #ARC Both excluded solids must meet the bulk liquid on shared imprinted faces.
    reactor = paramak.arc_from_2026_paper()
    assembly = cq.Assembly()
    for name in ("outer_vessel", "neutron_shield", "flibe_blanket"):
        assembly.add(reactor.objects[name].obj, name=name)
    _, origins = imprint(assembly)
    faces = {}
    for solid, names in origins.items():
        assert len(names) == 1
        for face in solid.Faces():
            faces.setdefault(face, set()).add(names[0].split("/")[-1])
    pairs = {frozenset(names) for names in faces.values() if len(names) == 2}
    assert frozenset(("outer_vessel", "flibe_blanket")) in pairs
    assert frozenset(("neutron_shield", "flibe_blanket")) in pairs


def test_flibe_blanket_color():
    reactor = paramak.arc_from_2026_paper(colors={"flibe_blanket": (0.2, 0.7, 0.3)})
    assert reactor.objects["flibe_blanket"].color.toTuple()[:3] == pytest.approx((0.2, 0.7, 0.3))
