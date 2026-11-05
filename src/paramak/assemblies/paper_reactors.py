"""Reactors with fixed geometry taken from figures in published papers.

The coordinates were read off published diagrams, so they are approximate and
the models do not exactly represent the real machines. They are useful as
realistic looking example geometries, for example for neutronics workflows.
"""

from __future__ import annotations

import cadquery as cq
import numpy as np
from OCP.Standard import Standard_ConstructionError, Standard_Failure

from ..utils import create_wire_workplane_from_points, resolve_assembly_color
from ..workplanes.blanket_from_plasma import blanket_from_plasma
from ..workplanes.blanket_from_plasma import find_points as blanket_find_points
from ..workplanes.cutting_wedge import cutting_wedge
from ..workplanes.plasma_simplified import plasma_simplified
from ..workplanes.poloidal_field_coil import poloidal_field_coil
from ..workplanes.revolved_shape import revolved_shape
from ..workplanes.toroidal_field_coil_princeton_d import toroidal_field_coil_princeton_d
from .assembly import Assembly


def _validate(rotation_angle: float, number_of_tf_coils: int | None = None) -> None:
    if not 0 < rotation_angle <= 360:
        msg = f"rotation_angle must be greater than 0 and at most 360, got {rotation_angle}."
        raise ValueError(msg)
    if number_of_tf_coils is not None and (
        isinstance(number_of_tf_coils, bool)
        or not isinstance(number_of_tf_coils, (int, np.integer))
        or number_of_tf_coils < 1
    ):
        msg = f"number_of_tf_coils must be an integer of at least 1, got {number_of_tf_coils}."
        raise ValueError(msg)


def _straight(points):
    return [(r, z, "straight") for r, z in points]


def _spline(points):
    return [(r, z, "spline") for r, z in points]


def _revolve(points, rotation_angle: float) -> cq.Workplane:
    """Revolves a closed profile, see paramak.revolved_shape. A full 360
    degree revolution is made from two 180 degree halves joined together, so
    the surfaces have seam edges. Without these a profile made of a single
    closed spline gives a surface that is periodic in both directions, which
    can not be meshed for neutronics."""
    if rotation_angle < 360:
        return revolved_shape(points, rotation_angle=rotation_angle)
    half = revolved_shape(points, rotation_angle=180)
    return half.union(half.rotate((0, 0, 0), (0, 0, 1), 180))


def _profile_face(points, offset: float = 0.0) -> cq.Face:
    """Makes a planar face in the XZ plane from a closed profile, optionally
    offset outwards in 2D by the given distance."""
    wire = create_wire_workplane_from_points(points=list(points) + [points[0]], plane="XZ")
    if offset:
        wire = wire.offset2D(offset)
    face = cq.Face.makeFromWires(wire.val())
    # profiles drawn clockwise give a face with the opposite normal, all faces
    # are given the same orientation so 2D booleans merge them correctly
    if face.normalAt().y < 0:
        face = cq.Face(face.wrapped.Reversed())
    return face


def _single_face(shape: cq.Shape) -> cq.Face:
    faces = shape.Faces()
    if len(faces) != 1:
        msg = f"Expected the 2D profile operation to give a single face, got {len(faces)}."
        raise RuntimeError(msg)
    return faces[0]


def _revolve_face(face: cq.Face, rotation_angle: float) -> cq.Workplane:
    """Revolves a face in the XZ plane around the Z axis. A full 360 degree
    revolution is made from two halves, see _revolve."""
    axis_start, axis_end = cq.Vector(0, 0, 0), cq.Vector(0, 0, 1)
    if rotation_angle < 360:
        solid = cq.Solid.revolve(face, rotation_angle, axis_start, axis_end)
    else:
        half = cq.Solid.revolve(face, 180, axis_start, axis_end)
        solid = half.fuse(half.rotate(axis_start, axis_end, 180)).clean()
    return cq.Workplane("XZ").add(solid)


def _tf_placement_angles(number_of_tf_coils: int) -> list[float]:
    return np.linspace(0, 360, number_of_tf_coils, endpoint=False).tolist()


def _clip_to_sector(solid: cq.Workplane, rotation_angle: float) -> cq.Workplane:
    """Intersects a solid with a wedge so only the part inside the sector remains."""
    if rotation_angle >= 360:
        return solid
    bb = solid.val().BoundingBox()
    radius = max(abs(bb.xmin), abs(bb.xmax), abs(bb.ymin), abs(bb.ymax)) * 2.1
    height = max(abs(bb.zmin), abs(bb.zmax)) * 2.1
    return solid.intersect(cutting_wedge(height=height, radius=radius, rotation_angle=rotation_angle))


def _build_assembly(parts, cuts, colors, default_colors, plasma_parameters) -> Assembly:
    """Adds the named parts to an Assembly.

    Args:
        parts: a list of (name, solid) tuples.
        cuts: a dictionary mapping a part name to the names of the parts that
            are cut from it, used where the outlines from the figures overlap.
            The overlaps are listed explicitly because automatic detection
            with boolean operations is not reliable for the nearly touching
            spline surfaces in these models.
        colors: user colors keyed by part name.
        default_colors: colors keyed by part name used when no user color is
            given, other parts get a color based on their name.
        plasma_parameters: plasma shape attributes to set on the assembly.
    """
    solids = dict(parts)
    assembly = Assembly()
    for name, solid in parts:
        for cutter_name in cuts.get(name, []):
            # boolean operations can change the tolerances of their arguments
            # in place, so a copy of the cutting part is used
            cutter = solids[cutter_name].val().copy()
            try:
                solid = solid.cut(cutter)
            except (Standard_Failure, Standard_ConstructionError):
                # merging the faces of the result can fail for some spline
                # surfaces, the cut is still valid without it
                solid = solid.cut(cutter, clean=False)
        solids[name] = solid
        color = (colors or {}).get(name, default_colors.get(name)) or resolve_assembly_color(name)
        assembly.add(solid, name=name, color=cq.Color(*color))
    for key, value in plasma_parameters.items():
        setattr(assembly, key, value)
    return assembly


def sparc_from_2020_paper(
    rotation_angle: float = 180.0,
    number_of_tf_coils: int = 18,
    colors: dict | None = None,
) -> Assembly:
    """Creates a simplified SPARC reactor from a figure in a published paper.

    The geometry is based on Figure 4 of A. J. Creely et al., "Overview of the
    SPARC tokamak", Journal of Plasma Physics, 86(5), 865860502 (2020),
    doi:10.1017/S0022377820001257. The coordinates were read off the figure,
    so they are approximate and the model does not exactly match the
    reactor.

    The assembly contains the plasma, the central solenoid and poloidal field
    coils, the divertor and vertical stability coils, the ICRF antenna, the
    vacuum vessel, the inner vessel components and the toroidal field coils.

    Args:
        rotation_angle: the angle in degrees of the sector to build, between
            0 (exclusive) and 360.
        number_of_tf_coils: the number of toroidal field coils, equally spaced
            around 360 degrees. Only the coils inside the sector are kept.
        colors: optional dictionary of RGB(A) colors keyed by part name, used
            in place of the default colors.

    Returns:
        A paramak Assembly with a named part for each component.
    """
    _validate(rotation_angle, number_of_tf_coils)

    major_radius, minor_radius, elongation, triangularity = 185.0, 57.0, 1.97, 0.31

    # the paper gives a minor radius of 57 cm, the plasma is made slightly
    # smaller so that it does not touch the inner vessel components
    plasma = plasma_simplified(
        major_radius=major_radius,
        minor_radius=minor_radius - 6,
        elongation=elongation,
        triangularity=triangularity,
        rotation_angle=rotation_angle,
    )

    def rectangular_coils(prefix, center_points, widths, heights):
        return [
            (
                f"{prefix}_{counter}",
                poloidal_field_coil(
                    height=height, width=width, center_point=center_point, rotation_angle=rotation_angle
                ),
            )
            for counter, (center_point, width, height) in enumerate(zip(center_points, widths, heights), 1)
        ]

    vs_coils = rectangular_coils("vs_coil", [(240, 70), (240, -70)], [10, 10], [10, 10])
    central_solenoid = rectangular_coils(
        "central_solenoid",
        [(53.5, -169.58), (53.5, -118.43), (53.5, -46.54), (53.5, 46.54), (53.5, 118.43), (53.5, 169.58)],
        [27.7] * 6,
        [41.5, 40.5, 82.95, 82.95, 40.5, 41.5],
    )
    pf_coils = rectangular_coils(
        "pf_coil",
        [(86, 230), (86, -230), (164, 241), (164, -241), (263, 222), (263, -222), (373, 131), (373, -131)],
        [32, 32, 50, 50, 43, 43, 48, 48],
        [40, 40, 30, 30, 28, 28, 37, 37],
    )
    divertor_coils = rectangular_coils(
        "divertor_coil", [(207, 144), (207, 125), (207, -144), (207, -125)], [15] * 4, [15] * 4
    )

    efccu_lower = [
        [(235.57, -127.65), (240.18, -121.20), (246.65, -125.81), (242.03, -132.26)],
        [(262.36, -90.78), (266.97, -84.33), (273.44, -88.94), (268.82, -94.47)],
        [(281.76, -71.43), (289.15, -71.43), (289.15, -78.80), (281.76, -78.80)],
    ]
    # the upper coils are a mirror of the lower coils, reversed so the
    # profile keeps the same winding direction
    efccu_upper = [[(r, -z) for r, z in reversed(coil)] for coil in efccu_lower]
    efccu_coils = [
        (f"efccu_coil_{counter}", _revolve(_straight(points), rotation_angle=rotation_angle))
        for counter, points in enumerate(efccu_lower + efccu_upper, 1)
    ]

    antenna = _revolve(
        [
            (263.28, 46.54, "straight"),
            (263.28, -46.54, "straight"),
            (231.87, -46.54, "spline"),
            (243.88, 0.0, "spline"),
            (231.87, 46.54, "straight"),
        ],
        rotation_angle=rotation_angle,
    )

    # the vacuum vessel is a shell between an outer and an inner wall
    vessel_outer_wall = _revolve(
        _straight(
            [
                (117.32, 126.73),
                (163.51, 170.05),
                (181.99, 171.89),
                (196.77, 169.12),
                (196.77, 115.67),
                (236.49, 114.75),
                (273.44, 65.90),
                (272.52, -65.90),
                (236.49, -115.67),
                (196.77, -115.67),
                (196.77, -169.12),
                (181.99, -172.81),
                (163.51, -170.05),
                (117.32, -126.73),
            ]
        ),
        rotation_angle=rotation_angle,
    )
    vessel_inner_wall = _revolve(
        _straight(
            [
                (123.79, 123.04),
                (123.79, -123.96),
                (165.36, -162.67),
                (181.99, -164.52),
                (190.30, -162.67),
                (190.30, -112.90),
                (194.00, -109.22),
                (232.79, -109.22),
                (266.97, -63.13),
                (266.05, 62.21),
                (232.79, 109.22),
                (194.00, 109.22),
                (190.30, 111.98),
                (190.30, 162.67),
                (181.99, 164.52),
                (165.36, 162.67),
            ]
        ),
        rotation_angle=rotation_angle,
    )
    vessel = vessel_outer_wall.cut(vessel_inner_wall)

    inner_vessel = _revolve(
        [
            (269.75, -46.54, "straight"),
            (231.87, -46.54, "spline"),
            (223.56, -62.21, "spline"),
            (207.85, -80.65, "spline"),
            (166.28, -115.67, "spline"),
            (164.43, -119.35, "spline"),
            (164.43, -122.12, "straight"),
            (173.67, -140.55, "straight"),
            (184.76, -140.55, "straight"),
            (184.76, -158.99, "straight"),
            (181.99, -159.91, "straight"),
            (147.81, -118.43, "straight"),
            (129.33, -123.04, "straight"),
            (145.96, -111.06, "straight"),
            (126.56, -50.23, "straight"),
            (127.48, 50.23, "straight"),
            (145.96, 110.14, "straight"),
            (128.41, 123.04, "straight"),
            (147.81, 117.51, "straight"),
            (181.99, 159.91, "straight"),
            (185.68, 158.99, "straight"),
            (184.76, 140.55, "straight"),
            (172.75, 140.55, "spline"),
            (164.43, 121.20, "spline"),
            (164.43, 118.43, "spline"),
            (165.36, 115.67, "spline"),
            (173.67, 111.06, "spline"),
            (207.85, 80.65, "spline"),
            (220.79, 66.82, "spline"),
            (231.87, 46.54, "spline"),
            (268.82, 46.54, "straight"),
            (268.82, 63.13, "straight"),
            (233.72, 111.98, "straight"),
            (194.00, 112.90, "straight"),
            (192.15, 164.52, "straight"),
            (163.51, 166.36, "straight"),
            (121.94, 123.96, "straight"),
            (121.02, -125.81, "straight"),
            (163.51, -166.36, "straight"),
            (192.15, -166.36, "straight"),
            (194.00, -112.90, "straight"),
            (234.64, -111.98, "straight"),
            (269.75, -63.13, "straight"),
        ],
        rotation_angle=rotation_angle,
    )

    tf_coils = toroidal_field_coil_princeton_d(
        r1=72,
        r2=339,
        thickness=33,
        distance=33,
        azimuthal_placement_angles=_tf_placement_angles(number_of_tf_coils),
        rotation_angle=rotation_angle,
    )

    parts = (
        [("plasma", plasma)]
        + vs_coils
        + [("antenna", antenna), ("vessel", vessel), ("inner_vessel", inner_vessel)]
        + central_solenoid
        + pf_coils
        + divertor_coils
        + efccu_coils
        + [("toroidal_field_coil", tf_coils)]
    )
    default_colors = {
        "vessel": (0.0, 1.0, 1.0),
        "inner_vessel": (0.0, 1.0, 0.5),
        "antenna": (0.9, 0.6, 0.1),
    }
    return _build_assembly(
        parts,
        {"inner_vessel": ["vessel", "antenna", "vs_coil_1", "vs_coil_2"]},
        colors,
        default_colors,
        {
            "major_radius": major_radius,
            "minor_radius": minor_radius,
            "elongation": elongation,
            "triangularity": triangularity,
        },
    )


def iter_from_2020_paper(
    rotation_angle: float = 180.0,
    number_of_tf_coils: int = 18,
    colors: dict | None = None,
) -> Assembly:
    """Creates a simplified ITER reactor from a figure in a published paper.

    The geometry is based on the diagram in "ITER Project: International
    Cooperation and Energy Investment" (2020),
    https://link.springer.com/chapter/10.1007/978-3-030-42913-3_26 . Several
    parts use paramak parametric shapes, so the model does not exactly match
    the diagram or the reactor.

    The assembly contains the plasma, a blanket that follows the plasma, a
    single null divertor, the vacuum vessel, the central solenoid, the
    poloidal field coils and the toroidal field coils.

    Args:
        rotation_angle: the angle in degrees of the sector to build, between
            0 (exclusive) and 360.
        number_of_tf_coils: the number of toroidal field coils, equally spaced
            around 360 degrees. Only the coils inside the sector are kept.
        colors: optional dictionary of RGB(A) colors keyed by part name, used
            in place of the default colors.

    Returns:
        A paramak Assembly with a named part for each component.
    """
    _validate(rotation_angle, number_of_tf_coils)

    major_radius, minor_radius, elongation, triangularity = 620.0, 200.0, 1.7, 0.33
    vertical_displacement = 57.0

    plasma = plasma_simplified(
        major_radius=major_radius,
        minor_radius=minor_radius,
        elongation=elongation,
        triangularity=triangularity,
        vertical_displacement=vertical_displacement,
        rotation_angle=rotation_angle,
    )

    blanket_parameters = {
        "thickness": 54.0,
        "start_angle": -70,
        "stop_angle": 230,
        "offset_from_plasma": [[-70, 0, 90, 180, 230], [50, 20, 59, 16, 50]],
        "major_radius": major_radius,
        "minor_radius": minor_radius,
        "elongation": elongation,
        "triangularity": triangularity,
        "vertical_displacement": vertical_displacement,
        "num_points": 50,
    }
    blanket = blanket_from_plasma(rotation_angle=rotation_angle, **blanket_parameters)

    # outline of an ITER like divertor with inner and outer vertical targets
    # and a dome, generated with the ITERtypeDivertor class from earlier
    # paramak versions
    divertor = _revolve(
        [
            (392.71, -230.32, "circle"),
            (437.93, -269.98, "circle"),
            (434.00, -330.00, "straight"),
            (411.50, -368.97, "straight"),
            (470.20, -349.67, "circle"),
            (503.97, -356.64, "circle"),
            (528.19, -381.19, "straight"),
            (558.62, -448.95, "straight"),
            (556.00, -374.00, "circle"),
            (588.95, -315.16, "circle"),
            (656.36, -317.22, "straight"),
            (573.33, -456.95, "straight"),
            (559.14, -463.95, "straight"),
            (407.00, -376.77, "straight"),
            (396.79, -360.97, "straight"),
        ],
        rotation_angle=rotation_angle,
    )

    # the inside of the vacuum vessel follows the outer surface of the blanket
    # and the underside of the divertor
    blanket_points = blanket_find_points(connect_to_center=False, allow_overlapping_shape=False, **blanket_parameters)
    blanket_outer_points = [tuple(p) for p in blanket_points[len(blanket_points) // 2 :]]
    divertor_casing_points = [
        (573.33, -456.95, "straight"),
        (559.14, -463.95, "straight"),
        (407.00, -376.77, "straight"),
        (396.79, -360.97, "straight"),
    ]
    vessel_cavity = _revolve(blanket_outer_points + divertor_casing_points, rotation_angle=rotation_angle)

    vessel = _revolve(
        _spline(
            [
                (327.77, 36.5),
                (327.77, 73.38),
                (327.77, 108.31),
                (327.77, 143.25),
                (327.77, 178.18),
                (327.77, 213.11),
                (327.77, 248.05),
                (327.77, 282.98),
                (327.77, 317.92),
                (328.61, 368.24),
                (336.18, 422.43),
                (350.48, 457.54),
                (371.96, 492.47),
                (404.32, 522.02),
                (439.65, 544.46),
                (474.98, 556.36),
                (510.22, 564.09),
                (545.64, 565.12),
                (565.83, 563.19),
                (580.97, 559.44),
                (616.31, 548.41),
                (651.64, 533.22),
                (686.97, 515.3),
                (722.3, 492.24),
                (757.63, 466.87),
                (792.96, 437.11),
                (825.77, 403.72),
                (853.53, 369.42),
                (877.92, 333.91),
                (898.95, 300.52),
                (916.62, 265.24),
                (932.6, 230.72),
                (946.06, 193.11),
                (956.15, 156.88),
                (962.88, 118.11),
                (967.93, 80.39),
                (968.77, 38.25),
                (968.77, 25.77),
                (964.57, -1.67),
                (956.99, -29.94),
                (956.15, -34.6),
                (946.06, -71.15),
                (931.76, -104.26),
                (914.93, -139.91),
                (898.95, -174.48),
                (883.81, -213.64),
                (867.83, -248.22),
                (851.0, -284.21),
                (834.18, -319.95),
                (818.2, -359.1),
                (800.53, -391.23),
                (776.13, -427.87),
                (744.17, -460.46),
                (708.84, -490.03),
                (673.51, -512.7),
                (638.18, -528.37),
                (602.85, -539.05),
                (567.52, -546.12),
                (532.18, -548.96),
                (496.85, -547.75),
                (461.52, -541.4),
                (426.19, -527.6),
                (390.86, -501.28),
                (360.58, -468.05),
                (340.39, -431.44),
                (329.87, -399.07),
                (327.77, -357.48),
                (327.77, -311.73),
                (327.77, -276.8),
                (327.77, -241.86),
                (327.77, -206.93),
                (327.77, -172.0),
                (327.77, -137.06),
                (327.77, -102.13),
                (327.77, -67.19),
            ]
        ),
        rotation_angle=rotation_angle,
    ).cut(vessel_cavity)

    # outboard coils, given by their lower left and upper right corners
    pf_coil_corners = [
        ((345.54, -788.05), (511.99, -690.40)),
        ((800.65, -703.37), (880.71, -611.83)),
        ((1160.94, -272.69), (1222.04, -162.38)),
        ((1158.83, 268.98), (1230.47, 379.28)),
        ((798.54, 621.64), (861.75, 681.95)),
        ((345.54, 707.78), (446.68, 803.45)),
    ]
    pf_coils = [
        (
            f"pf_coil_{counter}",
            poloidal_field_coil(
                height=upper[1] - lower[1],
                width=upper[0] - lower[0],
                center_point=((lower[0] + upper[0]) / 2, (lower[1] + upper[1]) / 2),
                rotation_angle=rotation_angle,
            ),
        )
        for counter, (lower, upper) in enumerate(pf_coil_corners, 1)
    ]

    # the central solenoid is made of 6 stacked modules
    cs_inner, cs_outer = 132.74, 202.27
    central_solenoid = [
        (
            f"central_solenoid_{counter}",
            poloidal_field_coil(
                height=200,
                width=cs_outer - cs_inner,
                center_point=((cs_inner + cs_outer) / 2, z_bottom + 100),
                rotation_angle=rotation_angle,
            ),
        )
        for counter, z_bottom in enumerate(range(-600, 600, 200), 1)
    ]

    r1 = 219
    coil_thickness = r1 - 130
    tf_coils = toroidal_field_coil_princeton_d(
        r1=r1,
        r2=1056,
        thickness=coil_thickness,
        distance=coil_thickness,
        azimuthal_placement_angles=_tf_placement_angles(number_of_tf_coils),
        rotation_angle=rotation_angle,
    )

    parts = (
        [("plasma", plasma), ("blanket", blanket), ("divertor", divertor), ("vessel", vessel)]
        + central_solenoid
        + pf_coils
        + [("toroidal_field_coil", tf_coils)]
    )
    default_colors = {
        "blanket": (0.0, 1.0, 0.5),
        "vessel": (0.0, 1.0, 1.0),
    }
    return _build_assembly(
        parts,
        {"divertor": ["blanket"]},
        colors,
        default_colors,
        {
            "major_radius": major_radius,
            "minor_radius": minor_radius,
            "elongation": elongation,
            "triangularity": triangularity,
        },
    )


def eu_demo_from_2015_paper(
    rotation_angle: float = 180.0,
    number_of_tf_coils: int = 16,
    colors: dict | None = None,
) -> Assembly:
    """Creates a simplified EU DEMO reactor from a figure in a published paper.

    The geometry is based on Figure 2 of R. Kemp et al., "Definition of the
    basic DEMO tokamak geometry based on systems code studies", Fusion
    Engineering and Design (2015), doi:10.1016/j.fusengdes.2015.06.097 . The
    coordinates were read off the figure, so they are approximate and the
    model does not exactly match the reactor.

    The assembly contains the plasma, the blanket, a single null divertor,
    the vacuum vessel, the central solenoid, the poloidal field coils and the
    toroidal field coil casings.

    Args:
        rotation_angle: the angle in degrees of the sector to build, between
            0 (exclusive) and 360.
        number_of_tf_coils: the number of toroidal field coils, equally spaced
            around 360 degrees. Only the coils inside the sector are kept.
        colors: optional dictionary of RGB(A) colors keyed by part name, used
            in place of the default colors.

    Returns:
        A paramak Assembly with a named part for each component.
    """
    _validate(rotation_angle, number_of_tf_coils)

    # plasma shape from the inner and outer equatorial points and the high point
    inner_equatorial_r, outer_equatorial_r, high_point = 677.0, 1118.0, (853.0, 368.0)
    minor_radius = (outer_equatorial_r - inner_equatorial_r) / 2
    major_radius = inner_equatorial_r + minor_radius
    elongation = high_point[1] / minor_radius
    triangularity = (major_radius - high_point[0]) / minor_radius

    plasma = plasma_simplified(
        major_radius=major_radius,
        minor_radius=minor_radius,
        elongation=elongation,
        triangularity=triangularity,
        rotation_angle=rotation_angle,
    )

    blanket_points = [
        (1028.51, -506.44, "spline"),
        (1192.28, -281.28, "spline"),
        (1257.92, -56.44, "spline"),
        (1244.83, 216.29, "spline"),
        (1153.67, 400.52, "spline"),
        (988.24, 520.33, "spline"),
        (807.6, 539.8, "spline"),
        (670.53, 475.18, "spline"),
        (584.85, 334.51, "spline"),
        (574.29, 81.77, "spline"),
        (579.38, -158.89, "spline"),
        (580.36, -363.47, "straight"),
        (686.3, -355.11, "spline"),
        (657.99, -182.71, "straight"),
        (657.41, -62.37, "straight"),
        (656.68, 90.05, "straight"),
        (671.4, 294.68, "spline"),
        (725.94, 379.09, "spline"),
        (804.25, 419.45, "spline"),
        (1036.13, 356.02, "spline"),
        (1095.49, 255.92, "spline"),
        (1127.49, 131.68, "spline"),
        (1128.41, -60.86, "spline"),
        (1082.09, -221.46, "spline"),
        (945.66, -418.46, "straight"),
    ]
    blanket = _revolve(blanket_points, rotation_angle=rotation_angle)

    divertor_points = _straight(
        [
            (580.36, -363.47),
            (678.5, -367.16),
            (698.21, -383.15),
            (706.21, -415.21),
            (698.5, -443.32),
            (694.74, -479.43),
            (690.88, -491.48),
            (726.22, -495.37),
            (745.69, -463.22),
            (769.22, -459.13),
            (788.89, -467.09),
            (808.57, -479.06),
            (863.87, -551.09),
            (891.4, -563.04),
            (895.17, -530.93),
            (883.26, -502.89),
            (886.99, -462.77),
            (945.66, -418.46),
            (1028.51, -506.44),
            (985.89, -622.9),
            (946.75, -647.1),
            (801.53, -647.56),
            (675.58, -575.76),
            (612.38, -491.73),
            (584.53, -415.6),
        ]
    )
    divertor = _revolve(divertor_points, rotation_angle=rotation_angle)

    # the space inside the vacuum vessel, which the blanket and divertor sit in
    vessel_cavity_points = _spline(
        [
            (574.13, 101.11),
            (574.69, 165.88),
            (576.22, 183.81),
            (578.25, 276.25),
            (592.98, 356.14),
            (618.39, 410.17),
            (660.06, 462.71),
            (711.89, 503.99),
            (763.71, 528.24),
            (800.81, 535.07),
            (957.82, 529.16),
            (1009.65, 511.73),
            (1061.48, 484.36),
            (1113.31, 445.67),
            (1160.05, 396.81),
            (1196.13, 343.45),
            (1221.54, 290.07),
            (1239.32, 234.98),
            (1251.52, 177.4),
            (1259.9, 119.15),
            (1262.9, 91.48),
            (1257.76, -69.66),
            (1248.47, -117.97),
            (1236.27, -162.39),
            (1219.5, -215.31),
            (1198.16, -267.66),
            (1171.74, -320.87),
            (1140.74, -372.28),
            (1102.63, -425.0),
            (1058.94, -476.29),
            (1022.86, -523.16),
            (998.47, -582.32),
            (961.88, -633.83),
            (788.1, -641.84),
            (746.44, -626.41),
            (694.61, -595.17),
            (646.34, -549.17),
            (610.77, -496.43),
            (588.92, -442.35),
            (578.15, -383.5),
            (577.7, -343.84),
            (576.22, -254.97),
            (576.22, -201.97),
            (576.22, -148.97),
            (576.22, -95.98),
        ]
    )

    vessel_outer_points = _spline(
        [
            (515.49, 96.83),
            (515.49, 142.76),
            (515.82, 194.68),
            (518.01, 287.54),
            (532.01, 362.38),
            (553.35, 416.55),
            (586.38, 470.35),
            (631.6, 520.05),
            (683.43, 557.88),
            (735.26, 582.92),
            (785.06, 596.53),
            (975.1, 588.58),
            (1026.92, 570.66),
            (1078.75, 545.28),
            (1130.58, 510.38),
            (1181.92, 463.91),
            (1225.57, 410.04),
            (1258.12, 357.04),
            (1283.02, 304.73),
            (1302.33, 252.01),
            (1316.56, 198.48),
            (1326.96, 139.4),
            (1333.09, 100.85),
            (1343.49, -64.8),
            (1336.09, -109.34),
            (1327.34, -183.2),
            (1318.02, -232.48),
            (1302.84, -287.56),
            (1285.56, -341.5),
            (1263.71, -396.83),
            (1237.29, -451.74),
            (1207.31, -505.04),
            (1172.76, -556.01),
            (1128.04, -612.4),
            (1076.72, -658.26),
            (1024.89, -689.93),
            (973.06, -711.78),
            (799.79, -721.93),
            (771.84, -713.39),
            (720.02, -692.62),
            (668.67, -662.28),
            (617.9, -618.11),
            (575.71, -565.77),
            (546.74, -511.79),
            (524.95, -451.31),
            (516.75, -393.53),
            (516.75, -334.63),
            (516.75, -281.64),
            (516.75, -228.64),
            (516.75, -175.65),
            (516.75, -107.41),
        ]
    )
    # the blanket and divertor outlines from the figure poke slightly outside
    # the cavity in places and nearly touch it elsewhere. Adding them, with a
    # 1 cm gap, to the cavity stops the vessel overlapping or touching them,
    # as nearly coincident spline surfaces do not imprint reliably for
    # neutronics. The vessel profile is made with 2D booleans and then
    # revolved, which is more robust than 3D booleans on the revolved shapes.
    cavity_face = _profile_face(vessel_cavity_points).fuse(
        _profile_face(blanket_points, offset=1.0), _profile_face(divertor_points, offset=1.0)
    )
    vessel_face = _single_face(_profile_face(vessel_outer_points).cut(_single_face(cavity_face.clean())).clean())
    vessel = _revolve_face(vessel_face, rotation_angle)

    pf_coils = [
        (
            f"pf_coil_{counter}",
            poloidal_field_coil(height=size, width=size, center_point=center_point, rotation_angle=rotation_angle),
        )
        for counter, (center_point, size) in enumerate(
            zip(
                [(689, -985), (1421, -689), (1580, -252), (1550, 293), (1400, 598), (621, 811)],
                [204, 141, 102, 95, 79, 121],
            ),
            1,
        )
    ]

    central_solenoid_corners = [
        ((263.61, -881.62), (363.05, -609.17)),
        ((266.2, -600.85), (357.77, -332.38)),
        ((263.56, -316.04), (360.33, 217.16)),
        ((262.23, 229.49), (357.7, 493.93)),
        ((261.01, 510.28), (356.35, 746.64)),
    ]
    central_solenoid = [
        (
            f"central_solenoid_{counter}",
            _revolve(
                _straight([(r0, z0), (r1, z0), (r1, z1), (r0, z1)]),
                rotation_angle=rotation_angle,
            ),
        )
        for counter, ((r0, z0), (r1, z1)) in enumerate(central_solenoid_corners, 1)
    ]

    # the toroidal field coil casing is not a Princeton-D, it follows the
    # outline in the paper diagram and is extruded either side of each
    # placement plane
    tf_profile = create_wire_workplane_from_points(
        points=[
            (805.58, 755, "spline"),
            (956.8, 744.12, "spline"),
            (1019.81, 731.22, "spline"),
            (1082.82, 710.39, "spline"),
            (1145.83, 680.4, "spline"),
            (1208.83, 642.52, "spline"),
            (1271.84, 593.95, "spline"),
            (1332.82, 533.19, "spline"),
            (1382.61, 468.42, "spline"),
            (1420.21, 405.19, "spline"),
            (1450.19, 339.5, "spline"),
            (1472.04, 273.44, "spline"),
            (1486.78, 209.79, "spline"),
            (1498.17, 130.93, "spline"),
            (1507.0, -64.36, "spline"),
            (1499.48, -158.26, "spline"),
            (1489.83, -227.51, "spline"),
            (1473.57, -301.27, "spline"),
            (1453.75, -371.55, "spline"),
            (1429.36, -437.88, "spline"),
            (1402.43, -500.68, "spline"),
            (1367.37, -566.76, "spline"),
            (1327.18, -631.0, "spline"),
            (1276.52, -694.44, "spline"),
            (1214.93, -753.16, "spline"),
            (1151.92, -796.94, "spline"),
            (1088.92, -828.82, "spline"),
            (1025.91, -851.72, "spline"),
            (962.9, -866.36, "spline"),
            (805.58, -875.0, "straight"),
            (377.7, -875.0, "straight"),
            (375.45, 755, "straight"),
            (805.58, 755, "straight"),
        ],
        plane="XZ",
    )
    single_tf_coil = tf_profile.extrude(100, both=True).val()
    # neighbouring casings would overlap on the inboard side, so each casing is
    # trimmed to its own wedge of 360 / number_of_tf_coils degrees. The casings
    # then meet on shared flat faces and can be glued into one solid that
    # imprints and meshes cleanly.
    spacing = 360.0 / number_of_tf_coils
    placed_coils = []
    for angle in _tf_placement_angles(number_of_tf_coils):
        wedge = cutting_wedge(height=4000, radius=4000, rotation_angle=spacing).val()
        wedge = wedge.rotate((0, 0, 0), (0, 0, 1), angle - spacing / 2)
        placed_coils.append(single_tf_coil.rotate((0, 0, 0), (0, 0, 1), angle).intersect(wedge))
    if len(placed_coils) == 1:
        tf_coils = cq.Workplane("XZ").add(placed_coils[0])
    else:
        tf_coils = cq.Workplane("XZ").add(placed_coils[0].fuse(*placed_coils[1:], glue=True).clean())
    # the casing profile is a filled D, the region inside the outer wall of
    # the vessel (plus a 1 cm gap) is removed to leave the casing around the
    # vessel. The gap avoids the casing and vessel sharing spline surfaces,
    # which do not imprint reliably for neutronics. The cutter is a full 360
    # degree shape made from two halves, rotated by half a coil spacing so its
    # seams are away from the middle of a casing.
    tf_cutter = _revolve_face(_profile_face(vessel_outer_points, offset=1.0), 360)
    tf_cutter = tf_cutter.rotate((0, 0, 0), (0, 0, 1), 180.0 / number_of_tf_coils)
    tf_coils = _clip_to_sector(tf_coils.cut(tf_cutter), rotation_angle)

    parts = (
        [("plasma", plasma), ("blanket", blanket), ("divertor", divertor), ("vessel", vessel)]
        + central_solenoid
        + pf_coils
        + [("toroidal_field_coil", tf_coils)]
    )
    default_colors = {
        "blanket": (0.0, 1.0, 0.5),
        "divertor": (1.0, 0.67, 0.0),
        "vessel": (0.0, 1.0, 1.0),
        "toroidal_field_coil": (1.0, 1.0, 0.5),
    }
    return _build_assembly(
        parts,
        {"toroidal_field_coil": ["pf_coil_6"]},
        colors,
        default_colors,
        {
            "major_radius": major_radius,
            "minor_radius": minor_radius,
            "elongation": elongation,
            "triangularity": triangularity,
        },
    )
