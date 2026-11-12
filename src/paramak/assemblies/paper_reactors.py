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


def arc_from_2026_paper(
    rotation_angle: float = 180.0,
    number_of_tf_coils: int = 18,
    pf_coil_case_thickness: float = 3.0,  # Borrowed SPARC default in cm
    colors: dict | None = None,
) -> Assembly:
    """Creates a simplified ARC V3A reactor from a published paper and its data.

    The geometry is based on J. C. Hillesheim et al., "Overview of the physics
    basis for the ARC fusion power plant", Journal of Plasma Physics, 92, E69
    (2026), `doi:10.1017/S0022377826101706
    <https://doi.org/10.1017/S0022377826101706>`_. The inner and outer toroidal
    field coil profiles were read off Figure 2. The other component profiles
    and coil locations are taken from the accompanying device_V3A.json file
    described in Appendix A. The model is approximate and does not exactly
    represent the reactor or a final engineering design.

    The assembly contains the plasma, six central solenoid modules, ten poloidal
    field coils (each a winding pack inside a case), the toroidal field coils,
    the tungsten first wall, the inner and outer vacuum vessel walls, the FLiBe
    first-wall cooling region, the bulk FLiBe blanket and the neutron shield.

    The plasma is a smooth approximation clipped to the first-wall cavity.
    Solenoid and poloidal field coil dimensions approximate the JSON element
    envelopes, with the latter assumed to include their cases. The toroidal
    field coil profiles use straight segments and an assumed total extrusion
    thickness of 40 cm. Physical material compositions and densities are not
    assigned. Assembly triangularity metadata records the plasma primitive's
    angular shaping coefficient, arcsin(0.65), rather than geometric triangularity.

    Args:
        rotation_angle: the angle in degrees of the sector to build, between
            0 (exclusive) and 360.
        number_of_tf_coils: the number of toroidal field coils, equally spaced
            around 360 degrees. Only the portions inside the sector are kept.
            The default of 18 is the paper's ARC V3A baseline. Other counts
            require checking coil packing with the fixed extrusion thickness.
        pf_coil_case_thickness: the thickness (cm) of the case around each
            poloidal field coil winding pack. The default of 3 cm is assumed,
            not specified by the ARC data. Changing the thickness preserves
            the case-inclusive outer dimensions derived from the JSON envelopes.
        colors: optional dictionary of RGB(A) colors keyed by part name, used
            in place of the default colors.

    Returns:
        A paramak Assembly with a named part for each component.
    """
    _validate(rotation_angle, number_of_tf_coils)

    major_radius = 462.0
    minor_radius = 118.0
    elongation = 1.8

    # Geometric triangularity target 0.65; primitive coefficient is asin(delta).
    triangularity = float(np.arcsin(0.65))

    # Smooth boundary; replace with equilibrium data for double-null geometry.
    plasma = plasma_simplified(
        major_radius=major_radius,
        minor_radius=minor_radius,
        elongation=elongation,
        triangularity=triangularity,
        rotation_angle=rotation_angle,
    )

    solenoid_bounds = [
        (72.690000000000, 148.310000000000, 5.671739130435, 144.328260869565),  #ARC CS1U
        (72.690000000000, 148.310000000000, -144.328260869565, -5.671739130435),  #ARC CS1L
        (72.690000000000, 148.310000000000, 155.671739130435, 224.328260869565),  #ARC CS2U
        (72.690000000000, 148.310000000000, -224.328260869565, -155.671739130435),  #ARC CS2L
        (72.690000000000, 148.310000000000, 235.671739130435, 304.328260869565),  #ARC CS3U
        (72.690000000000, 148.310000000000, -304.328260869565, -235.671739130435),  #ARC CS3L
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

    # PF bounds from device_V3A.json annular-element extents, converted to cm.
    # Assume envelopes include cases; 
    pf_bounds = [
        (110.500000000000, 169.500000000000, 360.500000000000, 419.500000000000),  #ARC PF1U
        (110.500000000000, 169.500000000000, -419.500000000000, -360.500000000000),  #ARC PF1L
        (155.521739130435, 224.478260869565, 440.521739130435, 509.478260869565),  #ARC PF2U
        (155.521739130435, 224.478260869565, -509.478260869565, -440.521739130435),  #ARC PF2L
        (595.562500000000, 644.437500000000, 270.562500000000, 319.437500000000),  #ARC PF3U
        (595.562500000000, 644.437500000000, -319.437500000000, -270.562500000000),  #ARC PF3L
        (595.562500000000, 644.437500000000, 200.562500000000, 249.437500000000),  #ARC PF4U
        (595.562500000000, 644.437500000000, -249.437500000000, -200.562500000000),  #ARC PF4L
        (675.538461538462, 714.461538461538, 140.538461538462, 179.461538461538),  #ARC PF5U
        (675.538461538462, 714.461538461538, -179.461538461538, -140.538461538462),  #ARC PF5L
    ]
    pf_coils = _pf_coils_with_cases(
        [((rmin + rmax) / 2, (zmin + zmax) / 2) for rmin, rmax, zmin, zmax in pf_bounds],
        [rmax - rmin for rmin, rmax, _, _ in pf_bounds],
        [zmax - zmin for _, _, zmin, zmax in pf_bounds],
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
    first_wall = _revolve_face(first_wall_section, rotation_angle)
    plasma = plasma.intersect(_revolve_face(first_wall_inner_face, rotation_angle), clean=False)

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
    inner_vessel = _revolve_face(inner_vessel_section, rotation_angle)

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
    outer_vessel = _revolve_face(outer_vessel_section, rotation_angle)
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

    # 6. TF profiles: fill BOTH closed perimeters in R/Z coordinates, in cm.
    # Each point is (R, Z, "straight") or (R, Z, "spline").
    _tf_outer_points_m = [
        (1.5074554987568587, 3.3923282715247196),
        (1.7586289812671465, 3.3923282715247196),
        (1.9574746549211248, 3.799689553100859),
        (2.365631564000343, 4.384618572799932),
        (2.7947195966220852, 4.802425015442126),
        (3.3493943704989713, 5.199341135952211),
        (4.102914818029836, 5.544031451132021),
        (4.96109088327332, 5.700708867122844),
        (5.777404701431756, 5.638037900726515),
        (6.405338407707476, 5.4082443572733085),
        (6.980944305126887, 5.0217733978292785),
        (7.451894584833677, 4.5308508277247),
        (7.8495859321416335, 3.9981476133559015),
        (8.132156099965709, 3.507225043251323),
        (8.45658851487483, 2.7551734464953728),
        (8.66589975030007, 2.024012171871533),
        (8.791486491555212, 1.3346315415119108),
        (8.87521098572531, 0.530354139425687),
        (8.896142109267835, -0.25303294052842773),
        (8.791486491555212, -1.391555496728408),
        (8.603106379672496, -2.195832898814631),
        (8.310070650077162, -3.0627812672971864),
        (8.037966044024351, -3.6581554480623133),
        (7.723999190886491, -4.149078018166891),
        (7.493756831918726, -4.4519876890824825),
        (7.137927731695817, -4.838458648526512),
        (6.8239608785579575, -5.120477997309994),
        (6.478597340106311, -5.329381218631092),
        (6.028578183942044, -5.5382844399521876),
        (5.547162342463992, -5.653181211678792),
        (5.212264365783608, -5.674071533810901),
        (4.866900827331962, -5.663626372744847),
        (4.375019424082648, -5.6009554063485165),
        (3.8726724590620716, -5.433832829291639),
        (3.3912566175840198, -5.224929607970543),
        (2.8889096525634432, -4.890684453856787),
        (2.5016838670267494, -4.525103816544865),
        (2.051664710862483, -3.950619957911851),
        (1.8214223518947183, -3.5119231931375445),
        (1.7690945430384089, -3.4074715824769957),
        (1.5074554987568587, -3.4074715824769957),
        (1.486524375214335, -1.8824780668329861),
        (1.486524375214335, -0.5246071282458544),
        (1.4969899369855963, 0.7497025218128393),
        (1.5074554987568587, 1.8986702390788741),
        (1.5074554987568587, 2.8491798960898667),
    ]
    _tf_outer_points = [
        (100 * r, 100 * z, "straight")
        for r, z in _tf_outer_points_m + [_tf_outer_points_m[0]]
    ]
    # The inner perimeter bounds the TF opening, not the vessel or plasma.
    _tf_inner_points_m = [
        (2.397028249314129, 0.2274444685100958),
        (2.407493811085391, 0.9272702599357725),
        (2.4179593728566533, 1.6479863734935574),
        (2.5435461141117974, 2.4000379702495076),
        (2.8365818437071333, 3.1834250502036223),
        (3.2866009998714, 3.8414701973650787),
        (3.7889479648919755, 4.321947606403603),
        (4.375019424082648, 4.635302438385248),
        (4.971556445044582, 4.781534693310016),
        (5.348316668810014, 4.791979854376072),
        (5.798335824974281, 4.656192760517358),
        (6.227423857596023, 4.3637282506678226),
        (6.6355807666752415, 3.9250314858935176),
        (6.918150934499315, 3.4758895600531585),
        (7.273980034722224, 2.671612157966934),
        (7.5251535172325115, 1.7733283062862162),
        (7.661205820258918, 0.7601476828788947),
        (7.703068067343966, -0.16947165199998881),
        (7.650740258487656, -0.8901877655577737),
        (7.5565502025462985, -1.6109038791155594),
        (7.368170090663582, -2.373400636937566),
        (7.127462169924555, -3.0418909451650773),
        (6.803029755015433, -3.6581554480623133),
        (6.426269531250001, -4.159523179232947),
        (6.0076470603995205, -4.535548977610921),
        (5.463437848293896, -4.744452198932018),
        (5.128539871613512, -4.765342521064127),
        (4.80410745670439, -4.744452198932018),
        (4.040121447402264, -4.472878011214593),
        (3.474981111754116, -4.034181246440289),
        (3.014496393818587, -3.4701425488733264),
        (2.763322911308299, -3.031445784099022),
        (2.574942799425583, -2.5196328918623347),
        (2.4598216199417013, -2.028710321757753),
        (2.407493811085391, -1.2871038860678592),
        (2.407493811085391, -0.5872780946421834),
    ]
    _tf_inner_points = [
        (100 * r, 100 * z, "straight")
        for r, z in _tf_inner_points_m + [_tf_inner_points_m[0]]
    ]
    _tf_distance = 40.0
    outer_wire = create_wire_workplane_from_points(points=_tf_outer_points, plane="XZ")
    inner_wire = create_wire_workplane_from_points(points=_tf_inner_points, plane="XZ")
    single_tf_coil = outer_wire.extrude(_tf_distance / 2, both=True).cut(
        inner_wire.extrude(_tf_distance / 2, both=True)
    ).val()
    #Preserve the supplied profiles; no Princeton-D fit or automatic PF cuts.
    placed_tf_coils = [
        single_tf_coil.rotate((0, 0, 0), (0, 0, 1), angle)
        for angle in _tf_placement_angles(number_of_tf_coils)
    ]
    tf_coils = _clip_to_sector(
        cq.Workplane("XZ").add(cq.Compound.makeCompound(placed_tf_coils)), rotation_angle
    )

    return _build_assembly(
        [("plasma", plasma)] + central_solenoid + pf_coils + [
            ("toroidal_field_coil", tf_coils),
            ("first_wall", first_wall),
            ("inner_vessel", inner_vessel),
            ("flibe_first_wall", flibe_first_wall),
            ("outer_vessel", outer_vessel),
            ("neutron_shield", neutron_shield),
            ("flibe_blanket", flibe_blanket),
        ],
        {},
        colors,
        {
            "first_wall": (0.7, 0.7, 0.7),
            "inner_vessel": (0.0, 0.8, 0.8),
            "outer_vessel": (0.0, 0.5, 0.7),
            "flibe_first_wall": (0.5, 0.9, 0.5),
            "neutron_shield": (0.0, 0.5, 0.2),
            "flibe_blanket": (0.6, 0.85, 0.35),
        },
        dict(
            major_radius=major_radius,
            minor_radius=minor_radius,
            elongation=elongation,
            triangularity=triangularity,
        ),
    )
