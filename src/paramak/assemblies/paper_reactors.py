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
from ..workplanes.poloidal_field_coil_case import poloidal_field_coil_case
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


PF_COIL_CASE_COLOR = (0.9, 0.4, 0.4)


def _pf_coils_with_cases(center_points, widths, heights, case_thickness: float, rotation_angle: float):
    """Makes each poloidal field coil as a winding pack inside a case of
    constant thickness. The widths and heights are the outer size of each
    coil (including the case), as read off the paper figures.

    Returns:
        a list of (name, solid) tuples, a pf_coil_N winding pack and a
        pf_coil_case_N case for each coil.
    """
    if (
        isinstance(case_thickness, bool)
        or not isinstance(case_thickness, (int, float, np.integer, np.floating))
        or not np.isfinite(case_thickness)
        or case_thickness <= 0
    ):
        msg = f"pf_coil_case_thickness must be a positive number, got {case_thickness}."
        raise ValueError(msg)
    smallest_size = min(min(widths), min(heights))
    if 2 * case_thickness >= smallest_size:
        msg = (
            f"pf_coil_case_thickness must be less than half the size of the smallest poloidal field coil "
            f"({smallest_size / 2} cm) so there is room for the winding pack, got {case_thickness}."
        )
        raise ValueError(msg)
    parts = []
    for counter, (center_point, width, height) in enumerate(zip(center_points, widths, heights), 1):
        core_width, core_height = width - 2 * case_thickness, height - 2 * case_thickness
        parts.append(
            (
                f"pf_coil_{counter}",
                poloidal_field_coil(
                    height=core_height, width=core_width, center_point=center_point, rotation_angle=rotation_angle
                ),
            )
        )
        parts.append(
            (
                f"pf_coil_case_{counter}",
                poloidal_field_coil_case(
                    coil_height=core_height,
                    coil_width=core_width,
                    casing_thickness=case_thickness,
                    center_point=center_point,
                    rotation_angle=rotation_angle,
                ),
            )
        )
    return parts


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
        default_color = default_colors.get(name)
        if default_color is None and name.startswith("pf_coil_case"):
            default_color = PF_COIL_CASE_COLOR
        color = (colors or {}).get(name, default_color) or resolve_assembly_color(name)
        assembly.add(solid, name=name, color=cq.Color(*color))
    for key, value in plasma_parameters.items():
        setattr(assembly, key, value)
    return assembly


def sparc_from_2020_paper(
    rotation_angle: float = 180.0,
    number_of_tf_coils: int = 18,
    pf_coil_case_thickness: float = 3.0,
    colors: dict | None = None,
) -> Assembly:
    """Creates a simplified SPARC reactor from a figure in a published paper.

    The geometry is based on Figure 4 of A. J. Creely et al., "Overview of the
    SPARC tokamak", Journal of Plasma Physics, 86(5), 865860502 (2020),
    `doi:10.1017/S0022377820001257
    <https://doi.org/10.1017/S0022377820001257>`_. The coordinates were read
    off the figure, so they are approximate and the model does not exactly
    match the reactor.

    The assembly contains the plasma, the central solenoid, the poloidal field
    coils (each a winding pack inside a case), the divertor and vertical
    stability coils, the ICRF antenna, the vacuum vessel, the inner vessel
    components and the toroidal field coils.

    Args:
        rotation_angle: the angle in degrees of the sector to build, between
            0 (exclusive) and 360.
        number_of_tf_coils: the number of toroidal field coils, equally spaced
            around 360 degrees. Only the coils inside the sector are kept.
        pf_coil_case_thickness: the thickness (cm) of the case around each
            poloidal field coil winding pack. The outer size of each coil (with
            its case) is taken from the paper figure.
        colors: optional dictionary of RGB(A) colors keyed by part name, used
            in place of the default colors.

    Returns:
        A paramak Assembly with a named part for each component.
    """
    _validate(rotation_angle, number_of_tf_coils)

    major_radius, elongation, triangularity = 185.0, 1.97, 0.31
    # the paper gives a minor radius of 57 cm, the plasma is made slightly
    # smaller so that it does not touch the inner vessel components. The
    # modelled value is used for the plasma and reported on the assembly.
    paper_minor_radius = 57.0
    minor_radius = paper_minor_radius - 6

    plasma = plasma_simplified(
        major_radius=major_radius,
        minor_radius=minor_radius,
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
    pf_coils = _pf_coils_with_cases(
        [(86, 230), (86, -230), (164, 241), (164, -241), (263, 222), (263, -222), (373, 131), (373, -131)],
        [32, 32, 50, 50, 43, 43, 48, 48],
        [40, 40, 30, 30, 28, 28, 37, 37],
        pf_coil_case_thickness,
        rotation_angle,
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
    pf_coil_case_thickness: float = 10.0,
    colors: dict | None = None,
) -> Assembly:
    """Creates a simplified ITER reactor from a figure in a published paper.

    The geometry is based on the diagram in "ITER Project: International
    Cooperation and Energy Investment" (2020),
    `doi:10.1007/978-3-030-42913-3_26
    <https://doi.org/10.1007/978-3-030-42913-3_26>`_. Several parts use
    paramak parametric shapes, so the model does not exactly match the
    diagram or the reactor.

    The assembly contains the plasma, a blanket that follows the plasma, a
    single null divertor, the vacuum vessel, the central solenoid, the
    poloidal field coils (each a winding pack inside a case) and the toroidal
    field coils.

    Args:
        rotation_angle: the angle in degrees of the sector to build, between
            0 (exclusive) and 360.
        number_of_tf_coils: the number of toroidal field coils, equally spaced
            around 360 degrees. Only the coils inside the sector are kept.
        pf_coil_case_thickness: the thickness (cm) of the case around each
            poloidal field coil winding pack. The outer size of each coil (with
            its case) is taken from the paper figure.
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
    pf_coils = _pf_coils_with_cases(
        [((lower[0] + upper[0]) / 2, (lower[1] + upper[1]) / 2) for lower, upper in pf_coil_corners],
        [upper[0] - lower[0] for lower, upper in pf_coil_corners],
        [upper[1] - lower[1] for lower, upper in pf_coil_corners],
        pf_coil_case_thickness,
        rotation_angle,
    )

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
    pf_coil_case_thickness: float = 10.0,
    colors: dict | None = None,
) -> Assembly:
    """Creates a simplified EU DEMO reactor from a figure in a published paper.

    The geometry is based on Figure 2 of R. Kemp et al., "Definition of the
    basic DEMO tokamak geometry based on systems code studies", Fusion
    Engineering and Design (2015), `doi:10.1016/j.fusengdes.2015.06.097
    <https://doi.org/10.1016/j.fusengdes.2015.06.097>`_. The coordinates were
    read off the figure, so they are approximate and the model does not
    exactly match the reactor.

    The assembly contains the plasma, the blanket, a single null divertor,
    the vacuum vessel, the central solenoid, the poloidal field coils (each a
    winding pack inside a case) and the toroidal field coil casings.

    Args:
        rotation_angle: the angle in degrees of the sector to build, between
            0 (exclusive) and 360.
        number_of_tf_coils: the number of toroidal field coils, equally spaced
            around 360 degrees. Only the coils inside the sector are kept.
        pf_coil_case_thickness: the thickness (cm) of the case around each
            poloidal field coil winding pack. The outer size of each coil (with
            its case) is taken from the paper figure.
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
    # the vessel sits directly against the blanket and divertor, so the space
    # inside it is the outline of the two (their fused face with the hole for
    # the plasma filled in). The vessel then shares its inner surfaces with
    # them and imprints onto them. The vessel profile is made with 2D booleans
    # and then revolved, which is more robust than 3D booleans on the
    # revolved shapes.
    blanket_and_divertor = _single_face(_profile_face(blanket_points).fuse(_profile_face(divertor_points)).clean())
    cavity_face = cq.Face.makeFromWires(blanket_and_divertor.outerWire())
    vessel_face = _single_face(_profile_face(vessel_outer_points).cut(cavity_face).clean())
    vessel = _revolve_face(vessel_face, rotation_angle)

    pf_coil_sizes = [204, 141, 102, 95, 79, 121]
    pf_coils = _pf_coils_with_cases(
        [(689, -985), (1421, -689), (1580, -252), (1550, 293), (1400, 598), (621, 811)],
        pf_coil_sizes,
        pf_coil_sizes,
        pf_coil_case_thickness,
        rotation_angle,
    )

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
        {"toroidal_field_coil": ["pf_coil_6", "pf_coil_case_6"]},
        colors,
        default_colors,
        {
            "major_radius": major_radius,
            "minor_radius": minor_radius,
            "elongation": elongation,
            "triangularity": triangularity,
        },
    )


# ARC V3A plasma boundary, (R, Z) in metres. These are the 800 boundary points
# stored in ARC_V3A_kinetic_tokamaker_800res.eqdsk, the TokaMaker kinetic
# equilibrium supplied with the paper (Appendix A), unchanged and in file
# order. The last point repeats the first to close the loop and is left out.
# fmt: off
_ARC_PLASMA_BOUNDARY_M = (
    (5.78722906, -4.90995092e-07), (5.78718948, 0.00880821049), (5.78707123, 0.0176161416), (5.78687668, 0.0264225863),
    (5.78660488, 0.0352268219), (5.7862525, 0.0440279618), (5.78582335, 0.0528253838), (5.7853179, 0.0616183765),
    (5.78473663, 0.0704062581), (5.78407717, 0.0791881606), (5.78334045, 0.0879634023), (5.78252602, 0.0967312232),
    (5.78163624, 0.105491035), (5.78067064, 0.114242107), (5.77962971, 0.122983783), (5.77851343, 0.131715342),
    (5.77732182, 0.140436158), (5.77605629, 0.149145544), (5.77471685, 0.157842994), (5.77330351, 0.166527718),
    (5.77181816, 0.175199315), (5.77025843, 0.183856785), (5.76862812, 0.192500114), (5.76692581, 0.201128379),
    (5.76515484, 0.209741548), (5.76331139, 0.218338341), (5.76139975, 0.226918891), (5.75941706, 0.235482067),
    (5.75736618, 0.244027838), (5.75524902, 0.252556026), (5.75306273, 0.261065364), (5.7508111, 0.269556314),
    (5.74849415, 0.27802825), (5.7461133, 0.286481053), (5.74366379, 0.294912934), (5.74115181, 0.303324848),
    (5.73857737, 0.311716527), (5.73594046, 0.320087403), (5.73324251, 0.328437328), (5.73048353, 0.336766034),
    (5.72766495, 0.345073462), (5.72478771, 0.353359431), (5.72184801, 0.361622125), (5.71885252, 0.369863659),
    (5.71579838, 0.378082484), (5.71268797, 0.386279166), (5.70952225, 0.394453496), (5.70630074, 0.402605087),
    (5.70302582, 0.410734564), (5.69969654, 0.418841213), (5.69631481, 0.426925302), (5.69287968, 0.434986353),
    (5.68939447, 0.44302541), (5.68585634, 0.451041162), (5.68226814, 0.459034383), (5.67863083, 0.467005342),
    (5.67494345, 0.474953294), (5.6712079, 0.482879072), (5.66742516, 0.490782887), (5.66359472, 0.498664141),
    (5.65971756, 0.50652355), (5.65579462, 0.514361203), (5.6518259, 0.522177041), (5.64781141, 0.529971004),
    (5.64375353, 0.537744164), (5.63965178, 0.545496047), (5.63550615, 0.553226829), (5.63131809, 0.560937166),
    (5.62708759, 0.568627238), (5.62281561, 0.576297164), (5.61850214, 0.583947361), (5.61414814, 0.591578424),
    (5.60975266, 0.59918946), (5.60531712, 0.606781662), (5.60084343, 0.614356041), (5.59633017, 0.621912062),
    (5.5917778, 0.629450381), (5.58718634, 0.63697058), (5.5825572, 0.64447397), (5.5778904, 0.651960611),
    (5.57318592, 0.65943104), (5.56844473, 0.666885495), (5.56366634, 0.674324572), (5.55885172, 0.681748569),
    (5.55400085, 0.68915832), (5.54911327, 0.69655323), (5.54419041, 0.703934968), (5.5392313, 0.711302996),
    (5.53423738, 0.718658864), (5.52920818, 0.726002455), (5.5241437, 0.733334184), (5.5190444, 0.740654528),
    (5.51390982, 0.747964084), (5.5087409, 0.755263388), (5.50353718, 0.762553036), (5.4982996, 0.769834042),
    (5.49302721, 0.777106225), (5.48772001, 0.784370303), (5.48237801, 0.791626036), (5.47700262, 0.798876286),
    (5.47159243, 0.806119502), (5.46614838, 0.813357234), (5.46066952, 0.820590198), (5.4551568, 0.827818871),
    (5.4496088, 0.835042894), (5.44402647, 0.842264056), (5.43840981, 0.849482715), (5.43275785, 0.856699109),
    (5.42707157, 0.863915384), (5.42134905, 0.871129394), (5.41559219, 0.878344417), (5.40980053, 0.885560691),
    (5.40397215, 0.892777681), (5.39810801, 0.899997056), (5.39220858, 0.907219768), (5.38627243, 0.914445996),
    (5.38030005, 0.921676397), (5.37428999, 0.928911746), (5.36824369, 0.936153769), (5.36216021, 0.943402708),
    (5.35603857, 0.950659215), (5.34987926, 0.957924485), (5.34368134, 0.965198517), (5.33744431, 0.972482443),
    (5.33116722, 0.97977674), (5.32485104, 0.987083137), (5.31849432, 0.994401753), (5.31209707, 1.00173366),
    (5.30565834, 1.00908017), (5.2991786, 1.01644278), (5.29265547, 1.02382004), (5.28609037, 1.03121519),
    (5.27948189, 1.03862846), (5.27282906, 1.04606068), (5.2661314, 1.05351293), (5.2593894, 1.06098711),
    (5.25260067, 1.068483), (5.24576521, 1.07600129), (5.23888302, 1.08354509), (5.23195219, 1.09111333),
    (5.22497225, 1.09870744), (5.21794271, 1.10632992), (5.21086311, 1.11398149), (5.20373201, 1.1216625),
    (5.19654846, 1.1293757), (5.1893115, 1.13712013), (5.18202066, 1.14489877), (5.17467499, 1.15271246),
    (5.16727304, 1.16056299), (5.15981388, 1.16845047), (5.15229702, 1.17637813), (5.14472008, 1.18434548),
    (5.13708305, 1.19235456), (5.12938404, 1.20040655), (5.12162209, 1.2085036), (5.11379623, 1.21664715),
    (5.10590458, 1.22483838), (5.09794664, 1.23308015), (5.08991957, 1.24137187), (5.08182335, 1.24971676),
    (5.07365608, 1.25811636), (5.06541634, 1.26657164), (5.05710173, 1.27508533), (5.04871178, 1.28365862),
    (5.0402441, 1.29229414), (5.03169727, 1.30099332), (5.0230689, 1.30975723), (5.01435757, 1.31858873),
    (5.00556183, 1.32749128), (4.99667931, 1.33646441), (4.98770809, 1.34551406), (4.9786458, 1.3546381),
    (4.96949053, 1.36384261), (4.96024036, 1.37312782), (4.95089245, 1.3824985), (4.94144392, 1.39195228),
    (4.93189383, 1.40149701), (4.92223835, 1.41113365), (4.91247559, 1.42086458), (4.9026022, 1.43069339),
    (4.8926158, 1.44062257), (4.88251352, 1.45065427), (4.87229156, 1.46079206), (4.86194801, 1.47104025),
    (4.85147905, 1.48140109), (4.84088087, 1.49187982), (4.83015108, 1.50247777), (4.81928539, 1.51319969),
    (4.80827999, 1.52404928), (4.79713106, 1.53502977), (4.78583527, 1.54614544), (4.77438736, 1.55740142),
    (4.762784, 1.56879973), (4.75102091, 1.58034706), (4.73909235, 1.59204721), (4.72699451, 1.60390365),
    (4.71472216, 1.61592162), (4.70227003, 1.62810624), (4.68963289, 1.64046264), (4.67680502, 1.6529938),
    (4.66378117, 1.66570556), (4.65055513, 1.67860341), (4.63712072, 1.69169116), (4.62347174, 1.70497513),
    (4.6096015, 1.7184571), (4.59550381, 1.73214316), (4.58117104, 1.74603653), (4.56659651, 1.76014042),
    (4.55177355, 1.77445757), (4.53669453, 1.78898728), (4.52135229, 1.80373025), (4.50573921, 1.8186866),
    (4.48984957, 1.83384931), (4.47367525, 1.84921741), (4.45721149, 1.86477482), (4.44045115, 1.88051534),
    (4.42339039, 1.89642072), (4.40602493, 1.9124701), (4.38835192, 1.92863846), (4.37037086, 1.94489479),
    (4.35208273, 1.9612031), (4.33348942, 1.97752202), (4.31459618, 1.9938041), (4.29540968, 2.00999928),
    (4.27593994, 2.02605271), (4.25619841, 2.0419066), (4.23619843, 2.05750322), (4.21595478, 2.07278514),
    (4.19548559, 2.08769536), (4.17480707, 2.10218334), (4.15393782, 2.11620092), (4.1328969, 2.12970591),
    (4.11170197, 2.14266205), (4.09037161, 2.15503907), (4.06892204, 2.16681314), (4.04737043, 2.17796803),
    (4.02573109, 2.18849063), (4.00401831, 2.19837666), (3.98224306, 2.20762801), (3.96041727, 2.21624684),
    (3.93856096, 2.22420788), (3.90699363, 2.26034069), (3.89357185, 2.24174619), (3.88887405, 2.19911957),
    (3.88012028, 2.16945696), (3.87190795, 2.1394608), (3.86419559, 2.10926771), (3.8569541, 2.07897019),
    (3.85014653, 2.04867148), (3.84372878, 2.01848412), (3.83765101, 1.9885242), (3.83186102, 1.9589045),
    (3.82630777, 1.92972493), (3.82094216, 1.90107238), (3.81572151, 1.87301338), (3.81060863, 1.8455956),
    (3.8055737, 1.81884766), (3.80059385, 1.79278195), (3.79565191, 1.76739657), (3.79073644, 1.74267983),
    (3.78583932, 1.71861172), (3.78095627, 1.69516802), (3.77608538, 1.67232108), (3.77122617, 1.65004134),
    (3.76637983, 1.62829936), (3.76154804, 1.60706627), (3.75673294, 1.58631349), (3.75193691, 1.56601417),
    (3.74716282, 1.54614305), (3.74241281, 1.52667642), (3.7376895, 1.50759161), (3.73299503, 1.48886836),
    (3.72833157, 1.470487), (3.72370124, 1.45242989), (3.71910524, 1.43468046), (3.71454573, 1.41722322),
    (3.71002388, 1.40004385), (3.70554066, 1.38312924), (3.70109725, 1.36646688), (3.69669437, 1.35004544),
    (3.69233322, 1.33385432), (3.68801427, 1.31788325), (3.68373775, 1.30212307), (3.67950463, 1.28656495),
    (3.67531466, 1.2712009), (3.67116833, 1.25602317), (3.66706634, 1.24102426), (3.66300821, 1.22619772),
    (3.6589942, 1.211537), (3.65502429, 1.19703603), (3.65109873, 1.18268895), (3.64721704, 1.16849053),
    (3.64337969, 1.15443552), (3.63958621, 1.1405189), (3.63583636, 1.12673628), (3.63213015, 1.11308312),
    (3.62846732, 1.09955513), (3.62484765, 1.0861485), (3.62127113, 1.07285905), (3.61773753, 1.05968344),
    (3.61424637, 1.04661798), (3.61079741, 1.03365934), (3.60739064, 1.02080429), (3.6040256, 1.00804961),
    (3.60070205, 0.995392561), (3.59741998, 0.982830048), (3.59417892, 0.970359445), (3.59097838, 0.957978129),
    (3.58781862, 0.945683479), (3.58469892, 0.933472991), (3.5816195, 0.92134434), (3.57857943, 0.909295321),
    (3.57557893, 0.897323549), (3.57261777, 0.885426998), (3.56969547, 0.873603582), (3.5668118, 0.861851335),
    (3.56396675, 0.850168288), (3.56115985, 0.838552475), (3.55839086, 0.827002108), (3.55565977, 0.815515518),
    (3.55296636, 0.804090917), (3.55031013, 0.792726576), (3.54769111, 0.781420946), (3.5451088, 0.770172536),
    (3.54256344, 0.758979678), (3.54005456, 0.747840941), (3.53758192, 0.736754954), (3.53514552, 0.725720167),
    (3.53274512, 0.714735329), (3.53038049, 0.703799069), (3.52805161, 0.692910135), (3.52575803, 0.682067156),
    (3.52349997, 0.671269059), (3.52127695, 0.660514534), (3.51908898, 0.649802387), (3.51693606, 0.639131606),
    (3.51481771, 0.628500938), (3.51273417, 0.617909431), (3.51068497, 0.607355952), (3.50867033, 0.596839428),
    (3.50668979, 0.586358905), (3.50474381, 0.57591331), (3.5028317, 0.56550175), (3.50095367, 0.555123329),
    (3.49910951, 0.544777095), (3.49729919, 0.534462094), (3.49552274, 0.524177492), (3.4937799, 0.513922453),
    (3.49207044, 0.503696144), (3.49039435, 0.493497699), (3.48875189, 0.483326286), (3.48714304, 0.473181129),
    (3.48556733, 0.463061482), (3.48402476, 0.45296663), (3.48251557, 0.44289571), (3.48103952, 0.432848096),
    (3.47959661, 0.422823042), (3.47818661, 0.412819862), (3.47680974, 0.402837873), (3.47546601, 0.392876357),
    (3.47415543, 0.382934719), (3.4728775, 0.373012275), (3.47163248, 0.363108456), (3.4704206, 0.353222549),
    (3.46924138, 0.343354017), (3.46809506, 0.333502233), (3.46698165, 0.323666602), (3.46590066, 0.313846588),
    (3.46485257, 0.304041624), (3.46383762, 0.294251025), (3.46285534, 0.284474373), (3.46190572, 0.274711102),
    (3.460989, 0.264960617), (3.46010494, 0.25522247), (3.45925355, 0.245496124), (3.45843506, 0.235781074),
    (3.45764899, 0.226076812), (3.45689607, 0.216382846), (3.45617557, 0.206698686), (3.45548773, 0.197023854),
    (3.45483279, 0.187357873), (3.45421076, 0.177700266), (3.45362115, 0.168050587), (3.45306444, 0.158408374),
    (3.4525404, 0.148773164), (3.45204926, 0.13914454), (3.45159078, 0.129522011), (3.45116496, 0.119905166),
    (3.45077181, 0.110293575), (3.45041132, 0.100686789), (3.45008397, 0.091084376), (3.44978905, 0.0814859271),
    (3.44952703, 0.0718910098), (3.4492979, 0.0622992031), (3.44910121, 0.0527100861), (3.44893742, 0.043123249),
    (3.44880629, 0.0335382745), (3.44870806, 0.0239547379), (3.44864249, 0.0143722333), (3.44860983, 0.00479034847),
    (3.44860983, -0.00479133008), (3.44864273, -0.014373214), (3.4487083, -0.0239557177), (3.44880652, -0.0335392542),
    (3.44893742, -0.0431242287), (3.44910121, -0.0527110696), (3.4492979, -0.0623001829), (3.44952703, -0.0718919933),
    (3.44978905, -0.0814869106), (3.45008397, -0.0910853595), (3.45041156, -0.100687772), (3.45077181, -0.110294543),
    (3.45116496, -0.119906127), (3.45159101, -0.129522964), (3.45204949, -0.139145479), (3.45254064, -0.148774117),
    (3.45306492, -0.158409312), (3.45362163, -0.168051526), (3.454211, -0.17770119), (3.45483327, -0.187358782),
    (3.4554882, -0.197024748), (3.45617604, -0.206699595), (3.45689631, -0.216383755), (3.45764947, -0.226077721),
    (3.4584353, -0.235781983), (3.45925403, -0.245497033), (3.46010518, -0.255223364), (3.46098948, -0.264961511),
    (3.46190619, -0.274711937), (3.46285582, -0.284475207), (3.46383834, -0.294251829), (3.46485353, -0.304042399),
    (3.46590137, -0.313847423), (3.46698213, -0.323667437), (3.46809554, -0.333503067), (3.46924186, -0.343354881),
    (3.47042108, -0.353223383), (3.4716332, -0.363109261), (3.47287798, -0.373013139), (3.4741559, -0.382935494),
    (3.47546673, -0.392877132), (3.47681046, -0.402838618), (3.47818732, -0.412820637), (3.47959709, -0.422823846),
    (3.48104, -0.432848901), (3.48251605, -0.442896485), (3.48402524, -0.452967376), (3.48556781, -0.463062286),
    (3.48714352, -0.473181903), (3.4887526, -0.483327061), (3.49039483, -0.493498474), (3.49207067, -0.503697038),
    (3.4937799, -0.513923407), (3.49552274, -0.524178445), (3.49729943, -0.534463048), (3.49910975, -0.544778049),
    (3.50095391, -0.555124283), (3.5028317, -0.565502763), (3.50474381, -0.575914264), (3.50669003, -0.586359799),
    (3.50867033, -0.596840382), (3.51068497, -0.607356966), (3.5127337, -0.617910564), (3.51481724, -0.628502131),
    (3.51693559, -0.639132798), (3.51908851, -0.649803638), (3.52127647, -0.660515785), (3.52349949, -0.671270311),
    (3.52575755, -0.682068408), (3.52805114, -0.692911327), (3.53038001, -0.703800321), (3.53274465, -0.71473664),
    (3.53514504, -0.725721478), (3.53758144, -0.736756206), (3.54005408, -0.747842252), (3.54256296, -0.75898093),
    (3.54510832, -0.770173788), (3.54769063, -0.781422257), (3.55030966, -0.792727888), (3.55296588, -0.804092228),
    (3.55565929, -0.815516889), (3.55839038, -0.827003479), (3.56115937, -0.838553846), (3.56396627, -0.850169659),
    (3.56681132, -0.861852765), (3.56969476, -0.873605072), (3.57261705, -0.885428488), (3.57557845, -0.897325099),
    (3.57857895, -0.909296691), (3.58161879, -0.921345949), (3.58469844, -0.933474541), (3.58781815, -0.94568491),
    (3.59097791, -0.95797956), (3.59417844, -0.970360816), (3.5974195, -0.982831419), (3.60070181, -0.995393932),
    (3.60402513, -1.00805092), (3.6073904, -1.02080536), (3.61079717, -1.03366053), (3.61424613, -1.04661906),
    (3.61773729, -1.05968451), (3.62127113, -1.07286012), (3.62484765, -1.08614945), (3.62846732, -1.09955609),
    (3.63213015, -1.11308396), (3.6358366, -1.126737), (3.63958645, -1.14051938), (3.64338017, -1.15443587),
    (3.64721775, -1.16849089), (3.65109944, -1.18268919), (3.65502501, -1.19703603), (3.65899491, -1.211537),
    (3.66300917, -1.2261976), (3.66706729, -1.24102402), (3.67116976, -1.25602269), (3.67531586, -1.27120042),
    (3.67950583, -1.28656423), (3.68373942, -1.302122), (3.68801594, -1.31788182), (3.69233513, -1.33385277),
    (3.69669652, -1.35004365), (3.70109916, -1.36646485), (3.70554304, -1.38312674), (3.71002626, -1.4000411),
    (3.71454859, -1.41722012), (3.71910834, -1.43467689), (3.72370434, -1.45242608), (3.7283349, -1.47048295),
    (3.73299837, -1.48886395), (3.73769307, -1.50758696), (3.74241638, -1.52667129), (3.7471664, -1.54613781),
    (3.75194073, -1.56600893), (3.75673652, -1.58630824), (3.76155114, -1.60706151), (3.76638269, -1.62829518),
    (3.77122855, -1.650038), (3.77608705, -1.6723187), (3.78095722, -1.6951673), (3.78583908, -1.71861291),
    (3.79073501, -1.74268329), (3.79564929, -1.76740289), (3.80058956, -1.79279172), (3.80556774, -1.81886148),
    (3.81060028, -1.84561419), (3.81571102, -1.87303722), (3.82092905, -1.90110278), (3.82629156, -1.92976296),
    (3.83184123, -1.95895183), (3.83762646, -1.98858392), (3.8436985, -2.01855922), (3.8501091, -2.04876637),
    (3.85690689, -2.0790925), (3.86413503, -2.10942793), (3.87182665, -2.13968086), (3.88000107, -2.16978669),
    (3.88866186, -2.19972038), (3.89437842, -2.23940921), (3.90734482, -2.25929689), (3.93840694, -2.22467971),
    (3.96032, -2.21655273), (3.98217249, -2.20785594), (4.00396395, -2.19855785), (4.02568769, -2.18864059),
    (4.04733419, -2.17809558), (4.068892, -2.166924), (4.09034586, -2.15513515), (4.11168051, -2.14274621),
    (4.1328783, -2.12978029), (4.15392208, -2.11626673), (4.17479372, -2.10224152), (4.19547415, -2.08774614),
    (4.21594572, -2.07282925), (4.23619032, -2.05754161), (4.25619221, -2.0419395), (4.2759347, -2.02608061),
    (4.29540586, -2.01002336), (4.31459284, -1.99382412), (4.33348656, -1.97753859), (4.35208035, -1.9612174),
    (4.37036943, -1.94490719), (4.38835049, -1.92864871), (4.4060235, -1.91247904), (4.42338943, -1.89642835),
    (4.44045067, -1.88052201), (4.45721054, -1.86478078), (4.47367525, -1.84922063), (4.48984909, -1.8338542),
    (4.50573921, -1.81869066), (4.52135181, -1.80373299), (4.53669453, -1.78898823), (4.55177355, -1.77445757),
    (4.56659651, -1.76014102), (4.58117104, -1.74603689), (4.59550381, -1.73214221), (4.6096015, -1.71845472),
    (4.62347174, -1.70497179), (4.63712072, -1.69168711), (4.65055513, -1.67859817), (4.66378117, -1.66569996),
    (4.67680502, -1.65298665), (4.68963242, -1.64045382), (4.70226955, -1.62809813), (4.71472168, -1.61591375),
    (4.72699404, -1.60389543), (4.73909187, -1.59203911), (4.75102043, -1.58033919), (4.76278353, -1.56879246),
    (4.77438688, -1.55739331), (4.78583431, -1.54613805), (4.79713058, -1.53502202), (4.80827904, -1.52404201),
    (4.81928444, -1.51319265), (4.83015013, -1.50247097), (4.84087992, -1.49187267), (4.8514781, -1.48139441),
    (4.86194706, -1.47103357), (4.87229061, -1.46078622), (4.88251209, -1.45064747), (4.89261484, -1.44061577),
    (4.90260124, -1.43068755), (4.91247463, -1.42085946), (4.9222374, -1.41112888), (4.93189287, -1.40149343),
    (4.94144344, -1.39194894), (4.95089149, -1.38249445), (4.96023941, -1.37312436), (4.96948957, -1.36383951),
    (4.97864532, -1.35463607), (4.98770761, -1.34551156), (4.99667835, -1.33646262), (5.00556087, -1.32748842),
    (5.01435709, -1.31858718), (5.02306795, -1.30975473), (5.03169584, -1.3009901), (5.04024315, -1.29229176),
    (5.04871082, -1.2836566), (5.05710125, -1.27508354), (5.06541538, -1.26656997), (5.07365561, -1.25811493),
    (5.08182287, -1.2497164), (5.08991957, -1.24137175), (5.09794617, -1.23308027), (5.10590458, -1.22483957),
    (5.11379623, -1.2166487), (5.12162256, -1.20850587), (5.12938499, -1.20041025), (5.13708353, -1.19235706),
    (5.14472103, -1.18434858), (5.1522975, -1.17638063), (5.15981483, -1.16845405), (5.16727448, -1.16056669),
    (5.17467642, -1.15271676), (5.18202257, -1.14490318), (5.18931341, -1.13712478), (5.19654989, -1.12937987),
    (5.20373297, -1.12166607), (5.21086407, -1.11398458), (5.21794415, -1.10633326), (5.2249732, -1.09871054),
    (5.23195314, -1.09111559), (5.23888397, -1.08354723), (5.24576616, -1.07600379), (5.25260115, -1.06848478),
    (5.25938988, -1.0609889), (5.26613235, -1.05351567), (5.27283001, -1.04606366), (5.27948332, -1.03863239),
    (5.28609228, -1.03121912), (5.29265738, -1.0238235), (5.29917955, -1.01644564), (5.30566025, -1.00908434),
    (5.3120985, -1.00173676), (5.31849575, -0.994404793), (5.32485199, -0.987085402), (5.33116817, -0.979779124),
    (5.33744526, -0.972485006), (5.34368229, -0.965201259), (5.3498807, -0.957927048), (5.35604048, -0.950662613),
    (5.36216211, -0.943406343), (5.36824608, -0.936157584), (5.37429285, -0.928916335), (5.38030195, -0.921679735),
    (5.38627386, -0.914448738), (5.39221001, -0.90722245), (5.39810944, -0.899999559), (5.40397358, -0.892780483),
    (5.40980148, -0.885562837), (5.41559362, -0.87834686), (5.42135, -0.871131361), (5.42707157, -0.863916278),
    (5.43275785, -0.85670054), (5.43840933, -0.84948349), (5.44402647, -0.84226501), (5.44960928, -0.835044265),
    (5.4551568, -0.827819645), (5.46067047, -0.820591986), (5.46615076, -0.813360929), (5.47159481, -0.80612272),
    (5.47700405, -0.79887861), (5.48237991, -0.791629136), (5.48772144, -0.78437227), (5.49302816, -0.777108073),
    (5.49830103, -0.769836366), (5.50353956, -0.762556016), (5.50874233, -0.755265832), (5.51391172, -0.747966588),
    (5.51904631, -0.740657151), (5.52414656, -0.733337283), (5.52921104, -0.726005614), (5.53423882, -0.718661249),
    (5.53923321, -0.711305678), (5.54419279, -0.703937769), (5.54911518, -0.696555674), (5.55400276, -0.689160705),
    (5.55885363, -0.681751251), (5.56366777, -0.674326718), (5.56844664, -0.666888058), (5.57318735, -0.659432828),
    (5.5778923, -0.651962817), (5.58255911, -0.644476235), (5.58718777, -0.636972547), (5.59177971, -0.629452407),
    (5.59633255, -0.621914923), (5.60084629, -0.614358783), (5.60531998, -0.606784523), (5.60975504, -0.599191844),
    (5.61415005, -0.591580629), (5.61850452, -0.583949924), (5.62281799, -0.576299608), (5.62709045, -0.56862998),
    (5.63132048, -0.56093955), (5.63550901, -0.553229392), (5.63965321, -0.545497835), (5.64375496, -0.537745893),
    (5.64781332, -0.52997303), (5.65182734, -0.52217871), (5.65579748, -0.514363766), (5.65971899, -0.506525397),
    (5.66359568, -0.498665631), (5.66742611, -0.490784228), (5.67120934, -0.482880622), (5.67494583, -0.474955291),
    (5.67863131, -0.467006445), (5.68226862, -0.459035516), (5.68585777, -0.451042712), (5.68939304, -0.443025798),
    (5.69287872, -0.434986889), (5.69631243, -0.426925421), (5.69969416, -0.418841243), (5.70302343, -0.410734534),
    (5.70629883, -0.402605474), (5.70951891, -0.394453228), (5.71268415, -0.386278659), (5.71579409, -0.378081948),
    (5.71884632, -0.369862527), (5.72184134, -0.361620843), (5.72477818, -0.353357196), (5.72765779, -0.345072061),
    (5.7304759, -0.336764634), (5.73323441, -0.328435868), (5.73593283, -0.320086062), (5.73856926, -0.311715096),
    (5.74114227, -0.303323179), (5.74365377, -0.294911176), (5.74610043, -0.286478668), (5.74848461, -0.278026789),
    (5.75080109, -0.269554913), (5.75305319, -0.261064142), (5.75523901, -0.252554655), (5.75735664, -0.244026735),
    (5.75940847, -0.235481188), (5.76139116, -0.226918146), (5.76330376, -0.218337879), (5.76514769, -0.209741235),
    (5.76692152, -0.201128572), (5.76862478, -0.192500517), (5.77025509, -0.183857232), (5.77181387, -0.175199628),
    (5.77330017, -0.166528165), (5.77471352, -0.1578435), (5.77605343, -0.149146169), (5.77731991, -0.140436873),
    (5.77851248, -0.131716236), (5.77962971, -0.122984774), (5.7806716, -0.114243202), (5.78163767, -0.105492122),
    (5.78252697, -0.0967322662), (5.78334045, -0.087964423), (5.78407764, -0.0791891813), (5.78473759, -0.0704073161),
    (5.78532076, -0.0616195165), (5.78582621, -0.052826494), (5.78625536, -0.0440290496), (5.78660631, -0.0352278501),
    (5.78687811, -0.0264236089), (5.78707314, -0.0176171549), (5.78719091, -0.00880920514),
)
# fmt: on

# Thicker cases would reach the toroidal field coils.
_ARC_MAX_PF_COIL_CASE_THICKNESS = 6.0


def arc_from_2026_paper(
    rotation_angle: float = 180.0,
    number_of_tf_coils: int = 18,
    pf_coil_case_thickness: float = 3.0,
    colors: dict | None = None,
) -> Assembly:
    """Creates a simplified ARC V3A reactor from a published paper and its data.

    The geometry is based on J. C. Hillesheim et al., "Overview of the physics
    basis for the ARC fusion power plant", Journal of Plasma Physics, 92, E69
    (2026), `doi:10.1017/S0022377826101706
    <https://doi.org/10.1017/S0022377826101706>`_. The inner and outer toroidal
    field coil profiles were read off Figure 2. The plasma boundary is taken
    from the accompanying TokaMaker equilibrium file and the other component
    profiles and coil locations from the accompanying device_V3A.json file,
    both described in Appendix A. The model is approximate and does not exactly
    represent the reactor or a final engineering design.

    The assembly contains the plasma, six central solenoid modules, ten poloidal
    field coils (each a winding pack inside a case), the toroidal field coils,
    the tungsten first wall, the inner and outer vacuum vessel walls, the FLiBe
    first-wall cooling region, the bulk FLiBe blanket, the neutron shield and
    the outer blanket wall (the roughly 2 cm thick wall of the blanket tank that
    holds the FLiBe, the JSON entry named Blanket).

    The plasma is the 800-point boundary stored in
    ARC_V3A_kinetic_tokamaker_800res.eqdsk, with its two X-points kept as
    corners. The assembly major radius, minor radius, elongation and
    triangularity are measured from that boundary, and they do not all match
    the separatrix values in Table 2 (page 10) of the paper. The major radius
    (461.8 cm against 462 cm) and minor radius (116.9 cm against 118 cm)
    agree to within 1%, but the boundary is more elongated (1.93 against
    1.8) and less triangular (0.61 against 0.65), and the plasma volume is
    184.6 m3 against 189 m3.
    Solenoid module and poloidal field coil winding pack cross-sections are
    the extents of the JSON filament grids (outermost filament centres plus
    half a grid spacing). The JSON has no coil cases, so an assumed case is
    added around each poloidal field coil winding pack. The toroidal field
    coil profiles are extruded to an assumed total thickness of 40 cm, with
    the outer inboard leg made vertical at 150.7 cm. Physical material
    compositions and densities are not assigned.

    Args:
        rotation_angle: the angle in degrees of the sector to build, between
            0 (exclusive) and 360.
        number_of_tf_coils: the number of toroidal field coils, equally spaced
            around 360 degrees. Only the portions inside the sector are kept.
            The default of 18 is the paper's ARC V3A baseline. Other counts
            require checking coil packing with the fixed extrusion thickness.
        pf_coil_case_thickness: the thickness (cm) of the case around each
            poloidal field coil winding pack, at most 6 cm. The default of
            3 cm is assumed, not specified by the ARC data. The case is added
            outside the winding pack, so changing the thickness changes the
            outer coil size and leaves the winding pack unchanged.
        colors: optional dictionary of RGB(A) colors keyed by part name, used
            in place of the default colors.

    Returns:
        A paramak Assembly with a named part for each component.
    """
    _validate(rotation_angle, number_of_tf_coils)

    # Plasma: the equilibrium boundary, converted to cm. The shape parameters
    # are measured from the same points so the metadata matches the solid.
    plasma_boundary = [(100 * r, 100 * z) for r, z in _ARC_PLASMA_BOUNDARY_M]
    plasma_radii = [r for r, _ in plasma_boundary]
    plasma_heights = [z for _, z in plasma_boundary]
    major_radius = (max(plasma_radii) + min(plasma_radii)) / 2
    minor_radius = (max(plasma_radii) - min(plasma_radii)) / 2
    elongation = (max(plasma_heights) - min(plasma_heights)) / (2 * minor_radius)
    # The highest and lowest points are the X-points of the double null.
    upper_x_point = plasma_heights.index(max(plasma_heights))
    lower_x_point = plasma_heights.index(min(plasma_heights))
    triangularity = (major_radius - plasma_radii[upper_x_point]) / minor_radius
    # One spline for each side, joined at the X-points so they stay sharp corners.
    inboard_side = plasma_boundary[upper_x_point : lower_x_point + 1]
    outboard_side = plasma_boundary[lower_x_point:] + plasma_boundary[: upper_x_point + 1]
    plasma_face = cq.Face.makeFromWires(
        cq.Wire.assembleEdges(
            [cq.Edge.makeSpline([cq.Vector(r, 0, z) for r, z in side]) for side in (outboard_side, inboard_side)]
        )
    )
    if plasma_face.normalAt().y < 0:
        plasma_face = cq.Face(plasma_face.wrapped.Reversed())
    plasma = _revolve_face(plasma_face, rotation_angle)

    # Coil cross-sections from the device_V3A.json filament grids, in cm. Each
    # filament stands for one cell of the grid, so a coil edge is half a grid
    # spacing beyond its outermost filament centres. This gives round sizes.
    solenoid_bounds = [
        (72.0, 149.0, 5.0, 145.0),  # CS1U
        (72.0, 149.0, -145.0, -5.0),  # CS1L
        (72.0, 149.0, 155.0, 225.0),  # CS2U
        (72.0, 149.0, -225.0, -155.0),  # CS2L
        (72.0, 149.0, 235.0, 305.0),  # CS3U
        (72.0, 149.0, -305.0, -235.0),  # CS3L
    ]
    central_solenoid = [
        (
            f"central_solenoid_{index}",
            poloidal_field_coil(
                height=zmax - zmin,
                width=rmax - rmin,
                center_point=((rmin + rmax) / 2, (zmin + zmax) / 2),
                rotation_angle=rotation_angle,
            ),
        )
        for index, (rmin, rmax, zmin, zmax) in enumerate(solenoid_bounds, 1)
    ]

    # PF winding packs, from the filament grids in the same way. The data has
    # no case, so the assumed case is added around the winding pack.
    pf_winding_bounds = [
        (110.0, 170.0, 360.0, 420.0),  # PF1U
        (110.0, 170.0, -420.0, -360.0),  # PF1L
        (155.0, 225.0, 440.0, 510.0),  # PF2U
        (155.0, 225.0, -510.0, -440.0),  # PF2L
        (595.0, 645.0, 270.0, 320.0),  # PF3U
        (595.0, 645.0, -320.0, -270.0),  # PF3L
        (595.0, 645.0, 200.0, 250.0),  # PF4U
        (595.0, 645.0, -250.0, -200.0),  # PF4L
        (675.0, 715.0, 140.0, 180.0),  # PF5U
        (675.0, 715.0, -180.0, -140.0),  # PF5L
    ]
    if (
        isinstance(pf_coil_case_thickness, (int, float, np.integer, np.floating))
        and np.isfinite(pf_coil_case_thickness)
        and pf_coil_case_thickness > _ARC_MAX_PF_COIL_CASE_THICKNESS
    ):
        msg = (
            f"pf_coil_case_thickness must be at most {_ARC_MAX_PF_COIL_CASE_THICKNESS} cm so the cases "
            f"stay clear of the toroidal field coils and each other, got {pf_coil_case_thickness}."
        )
        raise ValueError(msg)
    # _pf_coils_with_cases takes the outer (case-inclusive) coil sizes.
    pf_coils = _pf_coils_with_cases(
        [((rmin + rmax) / 2, (zmin + zmax) / 2) for rmin, rmax, zmin, zmax in pf_winding_bounds],
        [rmax - rmin + 2 * pf_coil_case_thickness for rmin, rmax, _, _ in pf_winding_bounds],
        [zmax - zmin + 2 * pf_coil_case_thickness for _, _, zmin, zmax in pf_winding_bounds],
        pf_coil_case_thickness,
        rotation_angle,
    )

    # Tungsten first wall: device_V3A.json wall.description_2d[1].vessel.unit[0].
    # Use both supplied contours, not a new offset; source coordinates are metres.
    first_wall_inner_m = [
        (3.42, 0.0),
        (3.42, 0.85),
        (3.68, 2.1),
        (3.46, 2.3),
        (3.46, 2.33),
        (3.76, 2.48),
        (4.36, 3.48),
        (4.77, 4.09),
        (5.31, 4.09),
        (5.31, 3.35),
        (4.94, 3.52),
        (4.18, 2.35),
        (4.77, 1.84),
        (5.23, 1.3),
        (5.67, 0.75),
        (5.82, 0.3),
        (5.82, 0.0),
        (5.82, -0.3),
        (5.67, -0.75),
        (5.23, -1.3),
        (4.77, -1.84),
        (4.18, -2.35),
        (4.94, -3.52),
        (5.31, -3.35),
        (5.31, -4.09),
        (4.77, -4.09),
        (4.36, -3.48),
        (3.76, -2.48),
        (3.46, -2.33),
        (3.46, -2.3),
        (3.68, -2.1),
        (3.42, -0.85),
    ]
    first_wall_outer_m = [
        (3.415, 0.0),
        (3.415, -0.8505145),
        (3.674523, -2.098222),
        (3.455, -2.297788),
        (3.455, -2.33309),
        (3.756462, -2.483821),
        (4.355779, -3.482683),
        (4.767336, -4.095),
        (5.315, -4.095),
        (5.315, -3.3422),
        (4.941839, -3.513653),
        (4.186568, -2.350932),
        (4.773559, -1.843533),
        (5.233856, -1.303184),
        (5.674461, -0.7524271),
        (5.825, -0.3008114),
        (5.825, 0.0),
        (5.825, 0.3008114),
        (5.674461, 0.7524271),
        (5.233856, 1.303184),
        (4.773559, 1.843533),
        (4.186568, 2.350932),
        (4.941839, 3.513653),
        (5.315, 3.3422),
        (5.315, 4.095),
        (4.767336, 4.095),
        (4.355779, 3.482683),
        (3.756462, 2.483821),
        (3.455, 2.33309),
        (3.455, 2.297788),
        (3.674523, 2.098222),
        (3.415, 0.8505145),
    ]
    first_wall_outer_face = _profile_face(_straight([(100 * r, 100 * z) for r, z in first_wall_outer_m]))
    first_wall_inner_face = _profile_face(_straight([(100 * r, 100 * z) for r, z in first_wall_inner_m]))
    first_wall_section = _single_face(first_wall_outer_face.cut(first_wall_inner_face).clean())
    tungsten_first_wall = _revolve_face(first_wall_section, rotation_angle)

    # Inner/outer vessel walls: device_V3A.json wall.description_2d[1].vessel.unit[1:3].
    # Preserve supplied contours; coordinates below are metres, converted to cm.
    # The inner wall's inner contour is exactly the first wall's outer contour.
    inner_vessel_outer_m = [
        (3.405, 0.0),
        (3.405, -0.8515435),
        (3.663569, -2.094665),
        (3.445, -2.293364),
        (3.445, -2.339271),
        (3.749385, -2.491463),
        (4.347336, -3.488048),
        (4.762009, -4.105),
        (5.325, -4.105),
        (5.325, -3.326601),
        (4.945517, -3.500958),
        (4.199703, -2.352796),
        (4.780676, -1.850599),
        (5.241569, -1.309551),
        (5.683384, -0.7572814),
        (5.835, -0.3024342),
        (5.835, 0.0),
        (5.835, 0.3024342),
        (5.683384, 0.7572814),
        (5.241569, 1.309551),
        (4.780676, 1.850599),
        (4.199703, 2.352796),
        (4.945517, 3.500958),
        (5.325, 3.326601),
        (5.325, 4.105),
        (4.762009, 4.105),
        (4.347336, 3.488048),
        (3.749385, 2.491463),
        (3.445, 2.339271),
        (3.445, 2.293364),
        (3.663569, 2.094665),
        (3.405, 0.8515435),
    ]
    inner_vessel_outer_face = _profile_face(_straight([(100 * r, 100 * z) for r, z in inner_vessel_outer_m]))
    inner_vessel_section = _single_face(inner_vessel_outer_face.cut(first_wall_outer_face).clean())
    inner_vacuum_vessel = _revolve_face(inner_vessel_section, rotation_angle)

    outer_vessel_inner_m = [
        (3.36, 0.0),
        (3.36, -0.8561739),
        (3.614277, -2.07866),
        (3.4, -2.273458),
        (3.4, -2.367082),
        (3.71754, -2.525852),
        (4.309343, -3.512191),
        (4.738034, -4.15),
        (5.37, -4.15),
        (5.37, -3.256402),
        (4.962069, -3.44383),
        (4.258812, -2.361184),
        (4.812703, -1.882396),
        (5.276274, -1.338204),
        (5.723537, -0.7791256),
        (5.88, -0.3097367),
        (5.88, 0.0),
        (5.88, 0.3097367),
        (5.723537, 0.7791256),
        (5.276274, 1.338204),
        (4.812703, 1.882396),
        (4.258812, 2.361184),
        (4.962069, 3.44383),
        (5.37, 3.256402),
        (5.37, 4.15),
        (4.738034, 4.15),
        (4.309343, 3.512191),
        (3.71754, 2.525852),
        (3.4, 2.367082),
        (3.4, 2.273458),
        (3.614277, 2.07866),
        (3.36, 0.8561739),
    ]
    outer_vessel_outer_m = [
        (3.33, 0.0),
        (3.33, -0.8592609),
        (3.581416, -2.067991),
        (3.37, -2.260187),
        (3.37, -2.385623),
        (3.69631, -2.548778),
        (4.284015, -3.528287),
        (4.722052, -4.18),
        (5.4, -4.18),
        (5.4, -3.209604),
        (4.973104, -3.405745),
        (4.298218, -2.366775),
        (4.834055, -1.903594),
        (5.299412, -1.357306),
        (5.750306, -0.7936884),
        (5.91, -0.314605),
        (5.91, 0.0),
        (5.91, 0.314605),
        (5.750306, 0.7936884),
        (5.299412, 1.357306),
        (4.834055, 1.903594),
        (4.298218, 2.366775),
        (4.973104, 3.405745),
        (5.4, 3.209604),
        (5.4, 4.18),
        (4.722052, 4.18),
        (4.284015, 3.528287),
        (3.69631, 2.548778),
        (3.37, 2.385623),
        (3.37, 2.260187),
        (3.581416, 2.067991),
        (3.33, 0.8592609),
    ]
    outer_vessel_inner_face = _profile_face(_straight([(100 * r, 100 * z) for r, z in outer_vessel_inner_m]))
    outer_vessel_outer_face = _profile_face(_straight([(100 * r, 100 * z) for r, z in outer_vessel_outer_m]))
    outer_vessel_section = _single_face(outer_vessel_outer_face.cut(outer_vessel_inner_face).clean())
    outer_vacuum_vessel = _revolve_face(outer_vessel_section, rotation_angle)
    flibe_first_wall_section = _single_face(outer_vessel_inner_face.cut(inner_vessel_outer_face).clean())
    flibe_first_wall = _revolve_face(flibe_first_wall_section, rotation_angle)

    # Neutron shield: device_V3A.json wall.description_2d[3].vessel.unit[0].element[0].
    neutron_shield_m = [
        (2.48, 0.0),
        (2.48, 1.35),
        (2.61, 2.37),
        (2.92, 3.12),
        (3.51, 3.95),
        (4.11, 4.37),
        (3.22, 3.3),
        (2.77, 2.35),
        (3.12, 0.75),
        (3.12, 0.0),
        (3.12, -0.75),
        (2.77, -2.35),
        (3.22, -3.3),
        (4.11, -4.37),
        (3.51, -3.95),
        (2.92, -3.12),
        (2.61, -2.37),
        (2.48, -1.35),
    ]
    neutron_shield_face = _profile_face(_straight([(100 * r, 100 * z) for r, z in neutron_shield_m]))
    neutron_shield = _revolve_face(neutron_shield_face, rotation_angle)

    # Bulk FLiBe: tank interior from wall.description_2d[2].vessel.unit[0].
    blanket_tank_inner_m = [
        (2.48, 0.0),
        (2.48, 1.35),
        (2.61, 2.37),
        (2.92, 3.12),
        (3.51, 3.95),
        (4.11, 4.37),
        (5.05, 4.68),
        (5.65, 4.62),
        (5.65, 2.5),
        (5.65, 1.8),
        (6.45, 1.1),
        (7.2, 1.1),
        (7.2, 0.0),
        (7.2, -1.1),
        (6.45, -1.1),
        (5.65, -1.8),
        (5.65, -2.5),
        (5.65, -4.62),
        (5.05, -4.68),
        (4.11, -4.37),
        (3.51, -3.95),
        (2.92, -3.12),
        (2.61, -2.37),
        (2.48, -1.35),
    ]
    blanket_tank_inner_face = _profile_face(_straight([(100 * r, 100 * z) for r, z in blanket_tank_inner_m]))
    flibe_blanket_section = _single_face(
        blanket_tank_inner_face.cut(outer_vessel_outer_face).cut(neutron_shield_face).clean()
    )
    flibe_blanket = _revolve_face(flibe_blanket_section, rotation_angle)

    # Blanket tank wall: the shell between the two contours of
    # wall.description_2d[2].vessel.unit[0], about 2 cm thick.
    blanket_tank_outer_m = [
        (2.46, 0.0),
        (2.46, -1.351269),
        (2.590498, -2.375175),
        (2.902384, -3.129738),
        (3.4957, -3.964403),
        (4.100941, -4.388072),
        (5.047767, -4.700323),
        (5.67, -4.6381),
        (5.67, -2.5),
        (5.67, -1.809075),
        (6.457515, -1.12),
        (7.22, -1.12),
        (7.22, 0.0),
        (7.22, 1.12),
        (6.457515, 1.12),
        (5.67, 1.809075),
        (5.67, 2.5),
        (5.67, 4.6381),
        (5.047767, 4.700323),
        (4.100941, 4.388072),
        (3.4957, 3.964403),
        (2.902384, 3.129738),
        (2.590498, 2.375175),
        (2.46, 1.351269),
    ]
    blanket_tank_outer_face = _profile_face(_straight([(100 * r, 100 * z) for r, z in blanket_tank_outer_m]))
    outer_blanket_wall_section = _single_face(blanket_tank_outer_face.cut(blanket_tank_inner_face).clean())
    outer_blanket_wall = _revolve_face(outer_blanket_wall_section, rotation_angle)

    # Toroidal field coils: the region between an outer and an inner
    # perimeter read off Figure 2, in metres, where each connection describes
    # the outgoing edge.
    # The inboard legs and outer horizontal shoulders are straight and the
    # remaining arcs are splines. The outer inboard leg is made vertical at its
    # most common digitized radius (digitized spread 2 cm), which keeps it clear
    # of the central solenoid.
    tf_outer_points_m = [
        (1.5074554987568587, 3.3923282715247196, "straight"),
        (1.7586289812671465, 3.3923282715247196, "spline"),
        (1.9574746549211248, 3.799689553100859, "spline"),
        (2.365631564000343, 4.384618572799932, "spline"),
        (2.7947195966220852, 4.802425015442126, "spline"),
        (3.3493943704989713, 5.199341135952211, "spline"),
        (4.102914818029836, 5.544031451132021, "spline"),
        (4.96109088327332, 5.700708867122844, "spline"),
        (5.777404701431756, 5.638037900726515, "spline"),
        (6.405338407707476, 5.4082443572733085, "spline"),
        (6.980944305126887, 5.0217733978292785, "spline"),
        (7.451894584833677, 4.5308508277247, "spline"),
        (7.8495859321416335, 3.9981476133559015, "spline"),
        (8.132156099965709, 3.507225043251323, "spline"),
        (8.45658851487483, 2.7551734464953728, "spline"),
        (8.66589975030007, 2.024012171871533, "spline"),
        (8.791486491555212, 1.3346315415119108, "spline"),
        (8.87521098572531, 0.530354139425687, "spline"),
        (8.896142109267835, -0.25303294052842773, "spline"),
        (8.791486491555212, -1.391555496728408, "spline"),
        (8.603106379672496, -2.195832898814631, "spline"),
        (8.310070650077162, -3.0627812672971864, "spline"),
        (8.037966044024351, -3.6581554480623133, "spline"),
        (7.723999190886491, -4.149078018166891, "spline"),
        (7.493756831918726, -4.4519876890824825, "spline"),
        (7.137927731695817, -4.838458648526512, "spline"),
        (6.8239608785579575, -5.120477997309994, "spline"),
        (6.478597340106311, -5.329381218631092, "spline"),
        (6.028578183942044, -5.5382844399521876, "spline"),
        (5.547162342463992, -5.653181211678792, "spline"),
        (5.212264365783608, -5.674071533810901, "spline"),
        (4.866900827331962, -5.663626372744847, "spline"),
        (4.375019424082648, -5.6009554063485165, "spline"),
        (3.8726724590620716, -5.433832829291639, "spline"),
        (3.3912566175840198, -5.224929607970543, "spline"),
        (2.8889096525634432, -4.890684453856787, "spline"),
        (2.5016838670267494, -4.525103816544865, "spline"),
        (2.051664710862483, -3.950619957911851, "spline"),
        (1.8214223518947183, -3.5119231931375445, "spline"),
        (1.7690945430384089, -3.4074715824769957, "straight"),
        (1.5074554987568587, -3.4074715824769957, "straight"),
        (1.5074554987568587, -1.8824780668329861, "straight"),
        (1.5074554987568587, -0.5246071282458544, "straight"),
        (1.5074554987568587, 0.7497025218128393, "straight"),
        (1.5074554987568587, 1.8986702390788741, "straight"),
        (1.5074554987568587, 2.8491798960898667, "straight"),
    ]
    tf_outer_points = [
        (100 * r, 100 * z, connection) for r, z, connection in tf_outer_points_m + [tf_outer_points_m[0]]
    ]
    # The inner perimeter bounds the TF opening, not the vessel or plasma.
    tf_inner_points_m = [
        (2.397028249314129, 0.2274444685100958, "straight"),
        (2.407493811085391, 0.9272702599357725, "straight"),
        (2.4179593728566533, 1.6479863734935574, "spline"),
        (2.5435461141117974, 2.4000379702495076, "spline"),
        (2.8365818437071333, 3.1834250502036223, "spline"),
        (3.2866009998714, 3.8414701973650787, "spline"),
        (3.7889479648919755, 4.321947606403603, "spline"),
        (4.375019424082648, 4.635302438385248, "spline"),
        (4.971556445044582, 4.781534693310016, "spline"),
        (5.348316668810014, 4.791979854376072, "spline"),
        (5.798335824974281, 4.656192760517358, "spline"),
        (6.227423857596023, 4.3637282506678226, "spline"),
        (6.6355807666752415, 3.9250314858935176, "spline"),
        (6.918150934499315, 3.4758895600531585, "spline"),
        (7.273980034722224, 2.671612157966934, "spline"),
        (7.5251535172325115, 1.7733283062862162, "spline"),
        (7.661205820258918, 0.7601476828788947, "spline"),
        (7.703068067343966, -0.16947165199998881, "spline"),
        (7.650740258487656, -0.8901877655577737, "spline"),
        (7.5565502025462985, -1.6109038791155594, "spline"),
        (7.368170090663582, -2.373400636937566, "spline"),
        (7.127462169924555, -3.0418909451650773, "spline"),
        (6.803029755015433, -3.6581554480623133, "spline"),
        (6.426269531250001, -4.159523179232947, "spline"),
        (6.0076470603995205, -4.535548977610921, "spline"),
        (5.463437848293896, -4.744452198932018, "spline"),
        (5.128539871613512, -4.765342521064127, "spline"),
        (4.80410745670439, -4.744452198932018, "spline"),
        (4.040121447402264, -4.472878011214593, "spline"),
        (3.474981111754116, -4.034181246440289, "spline"),
        (3.014496393818587, -3.4701425488733264, "spline"),
        (2.763322911308299, -3.031445784099022, "spline"),
        (2.574942799425583, -2.5196328918623347, "spline"),
        (2.4598216199417013, -2.028710321757753, "spline"),
        (2.407493811085391, -1.2871038860678592, "straight"),
        (2.407493811085391, -0.5872780946421834, "straight"),
    ]
    tf_inner_points = [
        (100 * r, 100 * z, connection) for r, z, connection in tf_inner_points_m + [tf_inner_points_m[0]]
    ]
    tf_thickness = 40.0
    outer_wire = create_wire_workplane_from_points(points=tf_outer_points, plane="XZ")
    inner_wire = create_wire_workplane_from_points(points=tf_inner_points, plane="XZ")
    single_tf_coil = (
        outer_wire.extrude(tf_thickness / 2, both=True).cut(inner_wire.extrude(tf_thickness / 2, both=True)).val()
    )
    # Interpolate the supplied contours; no Princeton-D fit or automatic PF cuts.
    placed_tf_coils = [
        single_tf_coil.rotate((0, 0, 0), (0, 0, 1), angle) for angle in _tf_placement_angles(number_of_tf_coils)
    ]
    tf_coils = _clip_to_sector(cq.Workplane("XZ").add(cq.Compound.makeCompound(placed_tf_coils)), rotation_angle)

    return _build_assembly(
        [("plasma", plasma)]
        + central_solenoid
        + pf_coils
        + [
            ("toroidal_field_coil", tf_coils),
            ("tungsten_first_wall", tungsten_first_wall),
            ("inner_vacuum_vessel", inner_vacuum_vessel),
            ("flibe_first_wall", flibe_first_wall),
            ("outer_vacuum_vessel", outer_vacuum_vessel),
            ("neutron_shield", neutron_shield),
            ("flibe_blanket", flibe_blanket),
            ("outer_blanket_wall", outer_blanket_wall),
        ],
        {},
        colors,
        {
            "tungsten_first_wall": (0.7, 0.7, 0.7),
            "inner_vacuum_vessel": (0.0, 0.8, 0.8),
            "outer_vacuum_vessel": (0.0, 0.5, 0.7),
            "flibe_first_wall": (0.5, 0.9, 0.5),
            "neutron_shield": (0.0, 0.5, 0.2),
            "flibe_blanket": (0.6, 0.85, 0.35),
            "outer_blanket_wall": (0.45, 0.45, 0.5),
        },
        dict(
            major_radius=major_radius,
            minor_radius=minor_radius,
            elongation=elongation,
            triangularity=triangularity,
        ),
    )
