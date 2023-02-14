import warnings
from typing import List, Optional

import cadquery as cq

import paramak


def SubmersionTokamak(
    inner_bore_radial_thickness: float = 30.0,
    inboard_tf_leg_radial_thickness: float = 30,
    center_column_shield_radial_thickness: float = 30,
    inboard_blanket_radial_thickness: float = 80,
    firstwall_radial_thickness: float = 20,
    inner_plasma_gap_radial_thickness: float = 50,
    plasma_radial_thickness: float = 200,
    divertor_radial_thickness: float = 80,
    support_radial_thickness: float = 90,
    outer_plasma_gap_radial_thickness: float = 50,
    outboard_blanket_radial_thickness: float = 30,
    blanket_rear_wall_radial_thickness: float = 30,
    elongation: float = 2.0,
    triangularity: float = 0.5,
    number_of_tf_coils: int = 16,
    rotation_angle: float = 180.0,
    outboard_tf_coil_radial_thickness: Optional[float] = None,
    rear_blanket_to_tf_gap: Optional[float] = None,
    outboard_tf_coil_poloidal_thickness: Optional[float] = None,
    pf_coil_radial_thicknesses: List[float] = [],
    pf_coil_vertical_thicknesses: List[float] = [],
    pf_coil_radial_position: List[float] = [],
    pf_coil_vertical_position: List[float] = [],
    pf_coil_case_thicknesses: List[float] = [],
    divertor_position: Optional[str] = "both",
    support_position: Optional[str] = "both",
):
    """Creates geometry for a simple submersion reactor including a plasma,
    cylindrical center column shielding, inboard and outboard breeder blanket,
    divertor (upper and lower), support legs. Optional coat hanger shaped
    toroidal field coils and pf coils.

    Arguments:
        inner_bore_radial_thickness: the radial thickness of the inner bore
            (cm)
        inboard_tf_leg_radial_thickness: the radial thickness of the inner leg
            of the toroidal field coils (cm)
        center_column_shield_radial_thickness: the radial thickness of the
            center column shield (cm)
        inboard_blanket_radial_thickness: the radial thickness of the inboard
            blanket (cm)
        firstwall_radial_thickness: the radial thickness of the first wall (cm)
        inner_plasma_gap_radial_thickness: the radial thickness of the inboard
            gap between the plasma and the center column shield (cm)
        plasma_radial_thickness: the radial thickness of the plasma (cm)
        divertor_radial_thickness: the radial thickness of the divertors (cm)
        support_radial_thickness: the radial thickness of the upper and lower
            supports (cm)
        outer_plasma_gap_radial_thickness: the radial thickness of the outboard
            gap between the plasma and the first wall (cm)
        outboard_blanket_radial_thickness: the radial thickness of the blanket
            (cm)
        blanket_rear_wall_radial_thickness: the radial thickness of the rear
            wall of the blanket (cm)
        elongation: the elongation of the plasma
        triangularity: the triangularity of the plasma
        number_of_tf_coils: the number of tf coils.
        rotation_angle: the angle of the sector that is desired.
        outboard_tf_coil_radial_thickness: the radial thickness of the toroidal
            field coil.
        rear_blanket_to_tf_gap: the radial distance between the rear of the
            blanket and the toroidal field coil.
        outboard_tf_coil_poloidal_thickness: the vertical thickness of each
            poloidal field coil.
        pf_coil_vertical_thicknesses: the vertical thickness of each poloidal
            field coil.
        pf_coil_radial_thicknesses: the radial thickness of  each poloidal
            field coil.
        divertor_position: the position of the divertor, "upper", "lower" or
            "both". Defaults to "both".
        support_position: the position of the supports, "upper", "lower" or
            "both". Defaults to "both".
    """

    def _rotation_angle_check():

        if rotation_angle == 360:
            msg = "360 degree rotation may result" + " in a Standard_ConstructionError or AttributeError"
            warnings.warn(msg, UserWarning)

    def _make_center_column_shield():

        _center_column_shield = paramak.CenterColumnShieldCylinder(
            height=_blanket_rear_wall_end_height * 2,
            inner_radius=_center_column_shield_start_radius,
            outer_radius=_center_column_shield_end_radius,
            rotation_angle=rotation_angle,
            name="center_column_shield",
        )
        return _center_column_shield

    def _make_plasma():

        # sets major radius and minor radius from equatorial_points to allow a
        # radial build this helps avoid the plasma overlapping the center
        # column and other components
        inner_equatorial_point = (
            inner_bore_radial_thickness
            + inboard_tf_leg_radial_thickness
            + center_column_shield_radial_thickness
            + inboard_blanket_radial_thickness
            + firstwall_radial_thickness
            + inner_plasma_gap_radial_thickness
        )
        outer_equatorial_point = inner_equatorial_point + plasma_radial_thickness
        major_radius = (outer_equatorial_point + inner_equatorial_point) / 2
        minor_radius = major_radius - inner_equatorial_point

        plasma = paramak.Plasma(
            major_radius=major_radius,
            minor_radius=minor_radius,
            elongation=elongation,
            triangularity=triangularity,
            rotation_angle=rotation_angle,
        )

        _plasma = plasma
        return _plasma

    def _make_firstwall():

        # this is used to cut the inboard blanket and then fused / unioned with
        # the firstwall
        _inboard_firstwall = paramak.BlanketFP(
            plasma=_plasma,
            offset_from_plasma=inner_plasma_gap_radial_thickness,
            start_angle=90,
            stop_angle=270,
            thickness=firstwall_radial_thickness,
            rotation_angle=rotation_angle,
            color=(0.5, 0.5, 0.5),
        )

        _firstwall = paramak.BlanketFP(
            plasma=_plasma,
            offset_from_plasma=outer_plasma_gap_radial_thickness,
            start_angle=90,
            stop_angle=-90,
            thickness=firstwall_radial_thickness,
            rotation_angle=rotation_angle,
            name="outboard_firstwall",
            union=_inboard_firstwall,
            color=(0.5, 0.5, 0.5),
        )
        return _firstwall

    def _make_divertor():
        fw_envelope_inboard = paramak.BlanketFP(
            plasma=_plasma,
            offset_from_plasma=inner_plasma_gap_radial_thickness,
            start_angle=90,
            stop_angle=270,
            thickness=firstwall_radial_thickness,
            rotation_angle=rotation_angle,
        )

        fw_envelope = paramak.BlanketFP(
            plasma=_plasma,
            offset_from_plasma=outer_plasma_gap_radial_thickness,
            start_angle=90,
            stop_angle=-90,
            thickness=firstwall_radial_thickness,
            rotation_angle=rotation_angle,
            name="outboard_firstwall",
            union=fw_envelope_inboard,
        )
        divertor_height = _blanket_rear_wall_end_height

        divertor_height_top = divertor_height
        divertor_height_bottom = -divertor_height

        if divertor_position in ["lower", "both"]:
            _divertor_lower = paramak.RotateStraightShape(
                points=[
                    (_divertor_start_radius, divertor_height_bottom),
                    (_divertor_end_radius, divertor_height_bottom),
                    (_divertor_end_radius, 0),
                    (_divertor_start_radius, 0),
                ],
                intersect=fw_envelope,
                name="divertor_lower",
                color=(1.0, 0.667, 0.0),
                rotation_angle=rotation_angle,
            )
        if divertor_position in ["upper", "both"]:
            _divertor_upper = paramak.RotateStraightShape(
                points=[
                    (_divertor_start_radius, 0),
                    (_divertor_end_radius, 0),
                    (_divertor_end_radius, divertor_height_top),
                    (_divertor_start_radius, divertor_height_top),
                ],
                intersect=fw_envelope,
                name="divertor_upper",
                color=(1.0, 0.667, 0.0),
                rotation_angle=rotation_angle,
            )

        if divertor_position == "upper":
            cut_list = [_divertor_upper]
        if divertor_position == "lower":
            cut_list = [_divertor_lower]
        if divertor_position == "both":
            cut_list = [_divertor_lower, _divertor_upper]
        _firstwall.cut = cut_list
        _inboard_firstwall.cut = cut_list

        if divertor_position == "upper":
            return [_divertor_upper]
        if divertor_position == "lower":
            return [_divertor_lower]
        if divertor_position == "both":
            return [_divertor_upper, _divertor_lower]

    def _make_blanket():
        _inboard_blanket = paramak.CenterColumnShieldCylinder(
            height=_blanket_end_height * 2,
            inner_radius=_inboard_blanket_start_radius,
            outer_radius=max(_inboard_firstwall.points)[0],
            rotation_angle=rotation_angle,
            cut=_inboard_firstwall,
        )

        # this takes a single solid from a compound of solids by finding the
        # solid nearest to a point
        # TODO: find alternative
        _inboard_blanket.solid = _inboard_blanket.solid.solids(cq.selectors.NearestToPointSelector((0, 0, 0)))

        # this is the outboard fused /unioned with the inboard blanket

        _blanket = paramak.BlanketFP(
            plasma=_plasma,
            start_angle=90,
            stop_angle=-90,
            offset_from_plasma=outer_plasma_gap_radial_thickness + firstwall_radial_thickness,
            thickness=outboard_blanket_radial_thickness,
            rotation_angle=rotation_angle,
            name="blanket",
            color=(0.0, 1.0, 0.498),
            union=_inboard_blanket,
        )
        return _blanket

    def _make_supports():
        blanket_envelope = paramak.BlanketFP(
            plasma=_plasma,
            start_angle=90,
            stop_angle=-90,
            offset_from_plasma=outer_plasma_gap_radial_thickness + firstwall_radial_thickness,
            thickness=outboard_blanket_radial_thickness,
            rotation_angle=rotation_angle,
            union=_inboard_blanket,
        )
        support_height = _blanket_rear_wall_end_height
        support_height_top = support_height
        support_height_bottom = -support_height

        if support_position == "lower":
            support_height_top = 0
        elif support_position == "upper":
            support_height_bottom = 0

        _supports = paramak.RotateStraightShape(
            points=[
                (_support_start_radius, support_height_bottom),
                (_support_end_radius, support_height_bottom),
                (_support_end_radius, support_height_top),
                (_support_start_radius, support_height_top),
            ],
            rotation_angle=rotation_angle,
            name="supports",
            color=(0.0, 0.0, 0.0),
            intersect=blanket_envelope,
        )

        _blanket.solid = _blanket.solid.cut(_supports.solid)

        return _supports

    def _make_rear_blanket_wall():
        _outboard_rear_blanket_wall_upper = paramak.RotateStraightShape(
            points=[
                (
                    _center_column_shield_end_radius,
                    _blanket_rear_wall_start_height,
                ),
                (
                    _center_column_shield_end_radius,
                    _blanket_rear_wall_end_height,
                ),
                (
                    max(_inboard_firstwall.points)[0],
                    _blanket_rear_wall_end_height,
                ),
                (
                    max(_inboard_firstwall.points)[0],
                    _blanket_rear_wall_start_height,
                ),
            ],
            rotation_angle=rotation_angle,
        )

        _outboard_rear_blanket_wall_lower = paramak.RotateStraightShape(
            points=[
                (
                    _center_column_shield_end_radius,
                    -_blanket_rear_wall_start_height,
                ),
                (
                    _center_column_shield_end_radius,
                    -_blanket_rear_wall_end_height,
                ),
                (
                    max(_inboard_firstwall.points)[0],
                    -_blanket_rear_wall_end_height,
                ),
                (
                    max(_inboard_firstwall.points)[0],
                    -_blanket_rear_wall_start_height,
                ),
            ],
            rotation_angle=rotation_angle,
        )

        _outboard_rear_blanket_wall = paramak.BlanketFP(
            plasma=_plasma,
            start_angle=90,
            stop_angle=-90,
            offset_from_plasma=outer_plasma_gap_radial_thickness
            + firstwall_radial_thickness
            + outboard_blanket_radial_thickness,
            thickness=blanket_rear_wall_radial_thickness,
            rotation_angle=rotation_angle,
            name="outboard_rear_blanket_wall",
            color=(0.0, 1.0, 1.0),
            union=[
                _outboard_rear_blanket_wall_upper,
                _outboard_rear_blanket_wall_lower,
            ],
        )

        return _outboard_rear_blanket_wall

    def _make_pf_coils():

        pf_input_lists = [
            pf_coil_vertical_thicknesses,
            pf_coil_radial_thicknesses,
            pf_coil_vertical_position,
            pf_coil_radial_position,
        ]

        # checks if lists are all the same length
        if all(len(input_list) == len(pf_input_lists[0]) for input_list in pf_input_lists):
            number_of_pf_coils = len(pf_input_lists[0])
            if number_of_pf_coils == 0:
                return None

            center_points = [(x, y) for x, y in zip(pf_coil_radial_position, pf_coil_vertical_position)]

            _pf_coils = []
            for counter, (center_point, pf_coil_vertical_thickness, pf_coil_radial_thickness,) in enumerate(
                zip(
                    center_points,
                    pf_coil_vertical_thicknesses,
                    pf_coil_radial_thicknesses,
                ),
                1,
            ):
                pf_coil = paramak.PoloidalFieldCoil(
                    height=pf_coil_vertical_thickness,
                    width=pf_coil_radial_thickness,
                    center_point=center_point,
                    rotation_angle=rotation_angle,
                    name=f"pf_coil_{counter}",
                )
                _pf_coils.append(pf_coil)

            if pf_coil_case_thicknesses == []:
                return _pf_coils

            _pf_coils_casing = []
            if len(pf_coil_case_thicknesses) == number_of_pf_coils:
                for counter, (pf_coil_case_thickness, pf_coil) in enumerate(
                    zip(pf_coil_case_thicknesses, _pf_coils), 1
                ):
                    pf_coils_casing = paramak.PoloidalFieldCoilCaseFC(
                        pf_coil=pf_coil,
                        casing_thickness=pf_coil_case_thickness,
                        rotation_angle=rotation_angle,
                        name=f"pf_coil_case_{counter}",
                    )
                    _pf_coils_casing.append(pf_coils_casing)
            else:
                raise ValueError(
                    "pf_coil_case_thicknesses is not the same length as the other "
                    "PF coil inputs (pf_coil_vertical_thicknesses, "
                    "pf_coil_radial_thicknesses, pf_coil_radial_position, "
                    "pf_coil_vertical_position) so can not make pf coils cases"
                )

            return _pf_coils + _pf_coils_casing

    def _make_tf_coils():
        list_of_components = []

        _inboard_tf_coils = paramak.CenterColumnShieldCylinder(
            height=_blanket_rear_wall_end_height * 2,
            inner_radius=_inboard_tf_coils_start_radius,
            outer_radius=_inboard_tf_coils_end_radius,
            rotation_angle=rotation_angle,
            name="inboard_tf_coils",
            color=(0, 0, 1),
        )
        list_of_components.append(_inboard_tf_coils)

        if (
            None
            not in [
                rear_blanket_to_tf_gap,
                outboard_tf_coil_radial_thickness,
                outboard_tf_coil_poloidal_thickness,
                number_of_tf_coils,
            ]
            and number_of_tf_coils > 1
        ):

            if _tf_info_provided:
                _tf_coil = paramak.ToroidalFieldCoilCoatHanger(
                    with_inner_leg=False,
                    horizontal_start_point=(
                        _inboard_tf_coils_start_radius,
                        _blanket_rear_wall_end_height,
                    ),
                    vertical_mid_point=(_outboard_tf_coil_start_radius, 0),
                    thickness=outboard_tf_coil_radial_thickness,
                    number_of_coils=number_of_tf_coils,
                    distance=outboard_tf_coil_poloidal_thickness,
                    rotation_angle=rotation_angle,
                    horizontal_length=_outboard_tf_coils_horizontal_length,
                    vertical_length=_outboard_tf_coils_vertical_height,
                    name="tf_coils",
                )
                list_of_components.append(_tf_coil)

        return list_of_components

    uncut_shapes = []

    _rotation_angle_check()
    _plasma = uncut_shapes.append(_make_plasma())

    # this is the radial build sequence, where one component stops and
    # another starts

    _inner_bore_start_radius = 0
    _inner_bore_end_radius = _inner_bore_start_radius + inner_bore_radial_thickness

    _inboard_tf_coils_start_radius = _inner_bore_end_radius
    _inboard_tf_coils_end_radius = _inboard_tf_coils_start_radius + inboard_tf_leg_radial_thickness

    _center_column_shield_start_radius = _inboard_tf_coils_end_radius
    _center_column_shield_end_radius = _center_column_shield_start_radius + center_column_shield_radial_thickness

    _inboard_blanket_start_radius = _center_column_shield_end_radius
    _inboard_blanket_end_radius = _inboard_blanket_start_radius + inboard_blanket_radial_thickness

    _inboard_firstwall_start_radius = _inboard_blanket_end_radius
    _inboard_firstwall_end_radius = _inboard_firstwall_start_radius + firstwall_radial_thickness

    _inner_plasma_gap_start_radius = _inboard_firstwall_end_radius
    _inner_plasma_gap_end_radius = _inner_plasma_gap_start_radius + inner_plasma_gap_radial_thickness

    _plasma_start_radius = _inner_plasma_gap_end_radius
    _plasma_end_radius = _plasma_start_radius + plasma_radial_thickness

    _outer_plasma_gap_start_radius = _plasma_end_radius
    _outer_plasma_gap_end_radius = _outer_plasma_gap_start_radius + outer_plasma_gap_radial_thickness

    _outboard_firstwall_start_radius = _outer_plasma_gap_end_radius
    _outboard_firstwall_end_radius = _outboard_firstwall_start_radius + firstwall_radial_thickness

    _outboard_blanket_start_radius = _outboard_firstwall_end_radius
    _outboard_blanket_end_radius = _outboard_blanket_start_radius + outboard_blanket_radial_thickness

    _blanket_rear_wall_start_radius = _outboard_blanket_end_radius
    _blanket_rear_wall_end_radius = _blanket_rear_wall_start_radius + blanket_rear_wall_radial_thickness

    _tf_info_provided = False
    if (
        outboard_tf_coil_radial_thickness is not None
        and rear_blanket_to_tf_gap is not None
        and outboard_tf_coil_poloidal_thickness is not None
    ):
        _tf_info_provided = True
        _outboard_tf_coil_start_radius = _blanket_rear_wall_end_radius + rear_blanket_to_tf_gap
        _outboard_tf_coil_end_radius = _outboard_tf_coil_start_radius + outboard_tf_coil_radial_thickness

    _divertor_start_radius = _plasma.high_point[0] - 0.5 * divertor_radial_thickness
    _divertor_end_radius = _plasma.high_point[0] + 0.5 * divertor_radial_thickness

    _support_start_radius = _plasma.high_point[0] - 0.5 * support_radial_thickness
    _support_end_radius = _plasma.high_point[0] + 0.5 * support_radial_thickness

    # this is the vertical build sequence, componets build on each other in
    # a similar manner to the radial build

    # _plasma_start_height = 0
    _plasma_end_height = _plasma.high_point[1]

    _plasma_to_divertor_gap_start_height = _plasma_end_height
    _plasma_to_divertor_gap_end_height = _plasma_to_divertor_gap_start_height + outer_plasma_gap_radial_thickness

    # the firstwall is cut by the divertor but uses the same control points
    _firstwall_start_height = _plasma_to_divertor_gap_end_height
    _firstwall_end_height = _firstwall_start_height + firstwall_radial_thickness

    _blanket_start_height = _firstwall_end_height
    _blanket_end_height = _blanket_start_height + outboard_blanket_radial_thickness

    _blanket_rear_wall_start_height = _blanket_end_height
    _blanket_rear_wall_end_height = _blanket_rear_wall_start_height + blanket_rear_wall_radial_thickness

    if _tf_info_provided:
        _outboard_tf_coils_vertical_height = _blanket_rear_wall_end_height * 1.5
        _outboard_tf_coils_horizontal_length = _blanket_rear_wall_end_radius * 0.75

    uncut_shapes.append(_make_center_column_shield())
    uncut_shapes.append(_make_firstwall())
    uncut_shapes.append(_make_blanket())
    uncut_shapes += _make_divertor()
    uncut_shapes.append(_make_supports())
    uncut_shapes.append(_make_rear_blanket_wall())
    uncut_shapes += _make_tf_coils()
    pf_coils = _make_pf_coils()

    if pf_coils is None:
        shapes_and_components = uncut_shapes
    else:
        for shape in uncut_shapes:
            print(shape, shape.name)
            for pf_coil in pf_coils:
                shape.solid = shape.solid.cut(pf_coil.solid)
        shapes_and_components = pf_coils + uncut_shapes

    shapes_and_components = shapes_and_components
