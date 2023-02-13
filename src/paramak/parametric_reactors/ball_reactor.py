from typing import List, Optional

import paramak
import cadquery as cq


def BallReactor(
    inner_bore_radial_thickness: float = 10.0,
    inboard_tf_leg_radial_thickness: float = 30.0,
    center_column_shield_radial_thickness: float = 60.0,
    divertor_radial_thickness: float = 150.0,
    inner_plasma_gap_radial_thickness: float = 30.0,
    plasma_radial_thickness: float = 300.0,
    outer_plasma_gap_radial_thickness: float = 30.0,
    firstwall_radial_thickness: float = 30.0,
    blanket_radial_thickness: float = 50.0,
    blanket_rear_wall_radial_thickness: float = 30.0,
    elongation: float = 2.0,
    triangularity: float = 0.55,
    plasma_gap_vertical_thickness: float = 50.0,
    divertor_to_tf_gap_vertical_thickness: Optional[float] = 0.0,
    number_of_tf_coils: Optional[int] = 12,
    rear_blanket_to_tf_gap: Optional[float] = None,
    pf_coil_radial_thicknesses: List[float] = [],
    pf_coil_vertical_thicknesses: List[float] = [],
    pf_coil_radial_position: List[float] = [],
    pf_coil_vertical_position: List[float] = [],
    pf_coil_case_thicknesses: List[float] = [],
    outboard_tf_coil_radial_thickness: float = None,
    outboard_tf_coil_poloidal_thickness: float = None,
    divertor_position: Optional[str] = "both",
    rotation_angle: Optional[str] = 180.0,
):
    """Creates geometry for a simple ball reactor including a plasma,
    cylindrical center column shielding, square toroidal field coils.
    There is no inboard breeder blanket on this ball reactor like
    most spherical reactors.

    Arguments:
        inner_bore_radial_thickness: the radial thickness of the inner bore
            (cm)
        inboard_tf_leg_radial_thickness: the radial thickness of the inner leg
            of the toroidal field coils (cm)
        center_column_shield_radial_thickness: the radial thickness of the
            center column shield (cm)
        divertor_radial_thickness: the radial thickness of the divertor
            (cm), this fills the gap between the center column shield and
            blanket
        inner_plasma_gap_radial_thickness: the radial thickness of the
            inboard gap between the plasma and the center column shield (cm)
        plasma_radial_thickness: the radial thickness of the plasma
        outer_plasma_gap_radial_thickness: the radial thickness of the
            outboard gap between the plasma and firstwall (cm)
        firstwall_radial_thickness: the radial thickness of the first wall (cm)
        blanket_radial_thickness: the radial thickness of the blanket (cm)
        blanket_rear_wall_radial_thickness: the radial thickness of the rear
            wall of the blanket (cm)
        elongation: the elongation of the plasma
        triangularity: the triangularity of the plasma
        plasma_gap_vertical_thickness: the vertical thickness of the gap
            between the plasma and firstwall (cm).
        divertor_to_tf_gap_vertical_thickness: the vertical thickness of the
            gap between the divertor and the TF coils.
        number_of_tf_coils: the number of tf coils
        rear_blanket_to_tf_gap: the radial distance between the back of the
            blankets and the start of the TF coils.
        pf_coil_radial_thicknesses: the radial
            thickness of each poloidal field coil.
        pf_coil_vertical_thicknesses: the vertical
            thickness of each poloidal field coil.
        pf_coil_radial_position: The radial (x) position(s) of the centers of
            the poloidal field coils.
        pf_coil_vertical_position: The vertical (z) position(s) of the centers
            of the poloidal field coils.
        pf_coil_case_thicknesses: the thickness(s) to use in both the radial
            and vertical direction for the casing around the pf coils. Each
            float value in the list will be applied to the pf coils one by one.
            To have no casing set each entry to 0 or leave as an empty list.
        outboard_tf_coil_radial_thickness: the radial thickness of the toroidal
            field coil.
        outboard_tf_coil_poloidal_thickness: the poloidal thickness of the
            toroidal field coil.
        divertor_position: the position of the divertor, "upper", "lower" or
            "both".
        rotation_angle: the angle of the sector that is desired.
    """

    def _make_inboard_tf_coils():

        _inboard_tf_coils = paramak.CenterColumnShieldCylinder(
            height=_tf_coil_start_height * 2,
            inner_radius=_inboard_tf_coils_start_radius,
            outer_radius=_inboard_tf_coils_end_radius,
            rotation_angle=rotation_angle,
            name="inboard_tf_coils",
            color=(0, 0, 1),
        )
        return _inboard_tf_coils

    def _make_center_column_shield():

        _center_column_shield = paramak.CenterColumnShieldCylinder(
            height=_center_column_shield_height,
            inner_radius=_center_column_shield_start_radius,
            outer_radius=_center_column_shield_end_radius,
            rotation_angle=rotation_angle,
            color=(0.0, 0.333, 0.0),
            name="center_column_shield",
        )
        return _center_column_shield

    def _make_blankets_layers():

        offset_from_plasma = [
            major_radius - minor_radius,
            plasma_gap_vertical_thickness,
            outer_plasma_gap_radial_thickness,
            plasma_gap_vertical_thickness,
            major_radius - minor_radius,
        ]

        _center_column_cutter = paramak.CenterColumnShieldCylinder(
            # extra 0.5 to ensure overlap,
            height=_center_column_shield_height * 1.5,
            inner_radius=0,
            outer_radius=_center_column_shield_end_radius,
            rotation_angle=360,
            color=(0.0, 0.0, 1.0),
        )

        _firstwall = paramak.BlanketFP(
            plasma=plasma,
            thickness=firstwall_radial_thickness,
            offset_from_plasma=offset_from_plasma,
            start_angle=-180,
            stop_angle=180,
            rotation_angle=rotation_angle,
            color=(0.5, 0.5, 0.5),
            name="firstwall",
            cut=[_center_column_cutter],
            allow_overlapping_shape=True,
        )

        _blanket = paramak.BlanketFP(
            plasma=plasma,
            thickness=blanket_radial_thickness,
            offset_from_plasma=[e + firstwall_radial_thickness for e in offset_from_plasma],
            start_angle=-180,
            stop_angle=180,
            rotation_angle=rotation_angle,
            color=(0.0, 1.0, 0.498),
            name="blanket",
            cut=[_center_column_cutter],
            allow_overlapping_shape=True,
        )

        _blanket_rear_wall = paramak.BlanketFP(
            plasma=plasma,
            thickness=blanket_rear_wall_radial_thickness,
            offset_from_plasma=[e + firstwall_radial_thickness + blanket_radial_thickness for e in offset_from_plasma],
            start_angle=-180,
            stop_angle=180,
            rotation_angle=rotation_angle,
            color=(0.0, 1.0, 1.0),
            name="blanket_rear_wall",
            cut=[_center_column_cutter],
            allow_overlapping_shape=True,
        )

        return _firstwall, _blanket, _blanket_rear_wall

    def _make_divertor():

        offset_from_plasma = [
            major_radius - minor_radius,
            plasma_gap_vertical_thickness,
            outer_plasma_gap_radial_thickness,
            plasma_gap_vertical_thickness,
            major_radius - minor_radius,
        ]

        # used as an intersect when making the divertor
        _blanket_fw_rear_wall_envelope = paramak.BlanketFP(
            plasma=plasma,
            thickness=firstwall_radial_thickness + blanket_radial_thickness + blanket_rear_wall_radial_thickness,
            offset_from_plasma=offset_from_plasma,
            start_angle=-180,
            stop_angle=180,
            rotation_angle=rotation_angle,
            allow_overlapping_shape=True,
        )

        divertor_height = _blanket_rear_wall_end_height * 2

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
                intersect=_blanket_fw_rear_wall_envelope,
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
                intersect=_blanket_fw_rear_wall_envelope,
                name="divertor_upper",
                color=(1.0, 0.667, 0.0),
                rotation_angle=rotation_angle,
            )

        if divertor_position == "upper":
            return [(_divertor_upper, "divertor_upper")]
        if divertor_position == "lower":
            return [(_divertor_lower, "divertor_lower")]
        if divertor_position == "both":
            return [(_divertor_lower, "divertor_lower"), (_divertor_upper, "divertor_upper")]

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
                _pf_coils.append((pf_coil, "pf_coils"))

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
                    _pf_coils_casing.append((pf_coils_casing, "pf_coils_casing"))
            else:
                raise ValueError(
                    "pf_coil_case_thicknesses is not the same length as the other "
                    "PF coil inputs (pf_coil_vertical_thicknesses, "
                    "pf_coil_radial_thicknesses, pf_coil_radial_position, "
                    "pf_coil_vertical_position) so can not make pf coils cases"
                )

            return _pf_coils + _pf_coils_casing

        raise ValueError(
            "pf_coil_vertical_thicknesses, pf_coil_radial_thicknesses, "
            "pf_coil_radial_position, pf_coil_vertical_position are not "
            "the same length so can not make PF coils"
        )

    def _make_tf_coils():
        comp = None
        # checks that all the required information has been input by the user
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

            _tf_coil = paramak.ToroidalFieldCoilRectangle(
                with_inner_leg=False,
                horizontal_start_point=(
                    _inboard_tf_coils_start_radius,
                    _tf_coil_start_height,
                ),
                vertical_mid_point=(_tf_coil_start_radius, 0),
                thickness=outboard_tf_coil_radial_thickness,
                number_of_coils=number_of_tf_coils,
                distance=outboard_tf_coil_poloidal_thickness,
                name="tf_coil",
                rotation_angle=rotation_angle,
            )
            comp = (_tf_coil, "tf_coil")
        return comp

    uncut_shapes = []

    inner_equatorial_point = (
        inner_bore_radial_thickness
        + inboard_tf_leg_radial_thickness
        + center_column_shield_radial_thickness
        + inner_plasma_gap_radial_thickness
    )
    outer_equatorial_point = inner_equatorial_point + plasma_radial_thickness

    # sets major radius and minor radius from equatorial_points to allow a
    # radial build. This helps avoid the plasma overlapping the center
    # column and other components
    major_radius = (outer_equatorial_point + inner_equatorial_point) / 2
    minor_radius = major_radius - inner_equatorial_point

    plasma = paramak.Plasma(
        major_radius=major_radius,
        minor_radius=minor_radius,
        elongation=elongation,
        triangularity=triangularity,
        rotation_angle=rotation_angle,
    )

    uncut_shapes.append((plasma, "plasma"))

    # this is the radial build sequence, where one component stops and
    # another starts

    _inner_bore_start_radius = 0
    _inner_bore_end_radius = _inner_bore_start_radius + inner_bore_radial_thickness

    _inboard_tf_coils_start_radius = _inner_bore_end_radius
    _inboard_tf_coils_end_radius = _inboard_tf_coils_start_radius + inboard_tf_leg_radial_thickness

    _center_column_shield_start_radius = _inboard_tf_coils_end_radius
    _center_column_shield_end_radius = _center_column_shield_start_radius + center_column_shield_radial_thickness

    _divertor_start_radius = _center_column_shield_end_radius
    _divertor_end_radius = _center_column_shield_end_radius + divertor_radial_thickness

    _firstwall_start_radius = (
        _center_column_shield_end_radius
        + inner_plasma_gap_radial_thickness
        + plasma_radial_thickness
        + outer_plasma_gap_radial_thickness
    )
    _firstwall_end_radius = _firstwall_start_radius + firstwall_radial_thickness

    _blanket_start_radius = _firstwall_end_radius
    _blanket_end_radius = _blanket_start_radius + blanket_radial_thickness

    _blanket_rear_wall_start_radius = _blanket_end_radius
    _blanket_rear_wall_end_radius = _blanket_rear_wall_start_radius + blanket_rear_wall_radial_thickness

    # this is the vertical build sequence, components build on each other
    # in a similar manner to the radial build

    _firstwall_start_height = plasma.high_point[1] + plasma_gap_vertical_thickness
    _firstwall_end_height = _firstwall_start_height + firstwall_radial_thickness

    _blanket_start_height = _firstwall_end_height
    _blanket_end_height = _blanket_start_height + blanket_radial_thickness

    _blanket_rear_wall_start_height = _blanket_end_height
    _blanket_rear_wall_end_height = _blanket_rear_wall_start_height + blanket_rear_wall_radial_thickness

    _tf_coil_start_height = _blanket_rear_wall_end_height + divertor_to_tf_gap_vertical_thickness

    _center_column_shield_height = _blanket_rear_wall_end_height * 2

    if rear_blanket_to_tf_gap is not None:
        _tf_coil_start_radius = _blanket_rear_wall_end_radius + rear_blanket_to_tf_gap
        _tf_coil_end_radius = _tf_coil_start_radius + outboard_tf_coil_radial_thickness

    inboard_tf_coils = _make_inboard_tf_coils()
    uncut_shapes.append((inboard_tf_coils, "inboard_tf_coils"))
    center_column_shield = _make_center_column_shield()
    firstwall, blanket, blanket_rear_wall = _make_blankets_layers()
    divertors = _make_divertor()

    for (divertor, name) in divertors:
        for component in [firstwall, blanket, blanket_rear_wall]:
            component.solid.cut(divertor.solid)

        uncut_shapes.append((divertor, name))

    uncut_shapes.append((firstwall, "firstwall"))
    uncut_shapes.append((blanket, "blanket"))
    uncut_shapes.append((blanket_rear_wall, "blanket_rear_wall"))

    tf_coils = _make_tf_coils()
    if tf_coils:
        uncut_shapes.append((tf_coils, "tf_coils"))

    pf_coils = _make_pf_coils()

    if pf_coils is None:
        shapes_and_components = uncut_shapes
    else:
        for (shape, name) in uncut_shapes:
            for pf_coil in pf_coils:
                shape.solid = shape.solid.cut(pf_coil.solid)
        shapes_and_components = uncut_shapes + pf_coils

    colors = [(0.5, 0.5, 0.5)]

    assembly = cq.Assembly(name="BallReactor")

    for (shape, name) in shapes_and_components:
        assembly.add(shape.solid, name=name)

    return assembly
