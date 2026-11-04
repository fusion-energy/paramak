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
    (paramak.LayerType.SOLID, 20),
    (paramak.LayerType.SOLID, 120),
    (paramak.LayerType.SOLID, 10),
]

SPHERICAL_RADIAL_BUILD = [
    (paramak.LayerType.GAP, 10),
    (paramak.LayerType.SOLID, 50),
    (paramak.LayerType.SOLID, 15),
    (paramak.LayerType.GAP, 50),
    (paramak.LayerType.PLASMA, 300),
    (paramak.LayerType.GAP, 60),
    (paramak.LayerType.SOLID, 15),
    (paramak.LayerType.SOLID, 60),
    (paramak.LayerType.SOLID, 10),
]

REACTORS = [
    (paramak.tokamak_from_plasma, TOKAMAK_RADIAL_BUILD),
    (paramak.spherical_tokamak_from_plasma, SPHERICAL_RADIAL_BUILD),
]


def bounding_box(shape):
    if isinstance(shape, cq.Assembly):
        shape = shape.toCompound()
    elif isinstance(shape, cq.Workplane):
        shape = shape.val()
    return shape.BoundingBox()


def volume(shape):
    if isinstance(shape, cq.Workplane):
        return sum(solid.Volume() for solid in shape.vals())
    return shape.toCompound().Volume()


@pytest.mark.parametrize("function, radial_build", REACTORS)
def test_reactor_is_rotated_to_the_start_angle(function, radial_build):
    "a 90 degree reactor starting at 90 degrees fills the -x +y quadrant with unchanged parts"

    unrotated = function(radial_build=radial_build, rotation_angle=90)
    rotated = function(radial_build=radial_build, rotation_angle=90, rotation_start_angle=90)

    assert rotated.names() == unrotated.names()
    for name in unrotated.names()[1:]:
        assert volume(rotated.objects[name].obj) == pytest.approx(volume(unrotated.objects[name].obj), rel=1e-6)

    unrotated_box = bounding_box(unrotated)
    box = bounding_box(rotated)
    assert box.xmax == pytest.approx(0, abs=1e-3)
    assert box.ymin == pytest.approx(0, abs=1e-3)
    assert box.xmin == pytest.approx(-unrotated_box.ymax, rel=1e-6)
    assert box.ymax == pytest.approx(unrotated_box.xmax, rel=1e-6)


@pytest.mark.parametrize("function, radial_build", REACTORS)
def test_extra_cut_shapes_are_not_rotated(function, radial_build):
    "extra shapes are used where they are given, so they only cut the reactor in its rotated position"

    def cutter(x, y):
        return cq.Workplane("XY").box(100, 100, 100).translate((x, y, 0))

    def reactor_volume(cut_shape):
        reactor = function(
            radial_build=radial_build,
            rotation_angle=90,
            rotation_start_angle=180,
            extra_cut_shapes=[cut_shape],
        )
        return sum(volume(reactor.objects[name].obj) for name in reactor.names()[1:] if name.startswith("layer"))

    radius = 10 + 30 + 50 + 10 + 120 + 20 + 60 + 300 + 60 + 70  # inside the outboard layers of either reactor
    if function is paramak.spherical_tokamak_from_plasma:
        radius = 10 + 50 + 15 + 50 + 300 + 60 + 40
    # the reactor covers 180 to 270 degrees, the -x -y quadrant
    assert reactor_volume(cutter(radius, 0.001)) == pytest.approx(reactor_volume(cutter(radius * 10, 0)))
    assert reactor_volume(cutter(-radius * 0.7, -radius * 0.7)) < reactor_volume(cutter(radius * 10, 0))


def test_toroidal_build_starts_at_the_start_angle():
    "toroidal sectors are measured from the rotation_start_angle"

    arc = paramak.toroidal_arc_length(TOKAMAK_RADIAL_BUILD, rotation_angle=90)
    sectors = [(paramak.LayerType.SOLID, arc / 2, "sector")] * 2
    reactor = paramak.tokamak_from_plasma(
        radial_build=TOKAMAK_RADIAL_BUILD,
        rotation_angle=90,
        rotation_start_angle=90,
        toroidal_build=[None, sectors, None, None],
    )
    # the first sector covers 90 to 135 degrees, so it is in -x +y with |x| < y
    box = bounding_box(reactor.objects["layer_3_sector_1"].obj)
    assert box.xmax == pytest.approx(0, abs=1e-3)
    assert box.ymin >= -1e-3
    assert -box.xmin < box.ymax


WORKPLANES = [
    (paramak.blanket_from_plasma, dict(thickness=20, start_angle=-90, stop_angle=90)),
    (paramak.blanket_constant_thickness_arc_h, dict(inner_mid_point=(100, 0), inner_upper_point=(50, 100), inner_lower_point=(50, -100), thickness=10)),
    (paramak.center_column_shield_cylinder, dict(height=100, inner_radius=10, thickness=10)),
    (paramak.constant_thickness_dome, dict()),
    (paramak.cutting_wedge, dict(height=10, radius=100)),
    (paramak.plasma_simplified, dict()),
    (paramak.poloidal_field_coil, dict(height=10, width=10, center_point=(100, 0))),
    (paramak.poloidal_field_coil_case, dict(coil_height=10, coil_width=10, casing_thickness=2, center_point=(100, 0))),
    (paramak.revolved_shape, dict(points=[(10, 0, "straight"), (20, 0, "straight"), (20, 10, "straight")])),
]


@pytest.mark.parametrize("function, kwargs", WORKPLANES)
def test_workplane_is_rotated_to_the_start_angle(function, kwargs):
    "a 90 degree shape starting at -90 degrees fills the +x -y quadrant"

    unrotated = function(rotation_angle=90, **kwargs)
    rotated = function(rotation_angle=90, rotation_start_angle=-90, **kwargs)

    assert volume(rotated) == pytest.approx(volume(unrotated), rel=1e-6)
    unrotated_box = bounding_box(unrotated)
    box = bounding_box(rotated)
    assert box.ymax == pytest.approx(0, abs=1e-3)
    assert box.ymin == pytest.approx(-unrotated_box.xmax, rel=1e-6)
    assert box.xmax == pytest.approx(unrotated_box.ymax, rel=1e-6)


@pytest.mark.parametrize("function", [paramak.dished_vacuum_vessel, paramak.u_shaped_dome])
def test_parts_of_vessels_are_rotated_to_the_start_angle(function):
    for part in function(rotation_angle=90, rotation_start_angle=180):
        box = bounding_box(part)
        assert box.xmax == pytest.approx(0, abs=1e-3)
        assert box.ymax == pytest.approx(0, abs=1e-3)


@pytest.mark.parametrize(
    "function, kwargs",
    [
        (paramak.toroidal_field_coil_rectangle, dict(horizontal_start_point=(100, 100), vertical_mid_point=(300, 0))),
        (paramak.toroidal_field_coil_princeton_d, dict(r1=100, r2=300)),
    ],
)
def test_toroidal_field_coils_are_kept_in_the_rotated_sector(function, kwargs):
    "coils at negative x and y are kept whole by a wedge starting at 180 degrees"

    angles = [215, 235]
    whole = function(thickness=10, distance=10, azimuthal_placement_angles=angles, **kwargs)
    cut = function(
        thickness=10,
        distance=10,
        azimuthal_placement_angles=angles,
        rotation_angle=90,
        rotation_start_angle=180,
        **kwargs,
    )
    assert volume(cut) == pytest.approx(volume(whole), rel=1e-4)
    box = bounding_box(cut)
    assert box.xmax <= 1e-3
    assert box.ymax <= 1e-3


@pytest.mark.parametrize(
    "function, kwargs",
    [
        (paramak.tokamak_from_plasma, dict(radial_build=TOKAMAK_RADIAL_BUILD)),
        (paramak.spherical_tokamak_from_plasma, dict(radial_build=SPHERICAL_RADIAL_BUILD)),
        (paramak.center_column_shield_cylinder, dict(height=100, inner_radius=10, thickness=10)),
        (paramak.toroidal_field_coil_rectangle, dict()),
    ],
)
@pytest.mark.parametrize("rotation_start_angle", [-361, 360.5])
def test_rotation_start_angle_out_of_range(function, kwargs, rotation_start_angle):
    with pytest.raises(ValueError, match="rotation_start_angle must be between -360 and 360"):
        function(rotation_start_angle=rotation_start_angle, **kwargs)
