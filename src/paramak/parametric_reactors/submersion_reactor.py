import warnings
from typing import List, Optional

import cadquery as cq

import paramak


class SubmersionTokamak(paramak.Reactor):
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

    def __init__(
        self,
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

        super().__init__([])

        self.inner_bore_radial_thickness = inner_bore_radial_thickness
        self.inboard_tf_leg_radial_thickness = inboard_tf_leg_radial_thickness
        self.center_column_shield_radial_thickness = center_column_shield_radial_thickness
        self.inboard_blanket_radial_thickness = inboard_blanket_radial_thickness
        self.firstwall_radial_thickness = firstwall_radial_thickness
        self.inner_plasma_gap_radial_thickness = inner_plasma_gap_radial_thickness
        self.plasma_radial_thickness = plasma_radial_thickness
        self.outer_plasma_gap_radial_thickness = outer_plasma_gap_radial_thickness
        self.outboard_blanket_radial_thickness = outboard_blanket_radial_thickness
        self.blanket_rear_wall_radial_thickness = blanket_rear_wall_radial_thickness
        self.pf_coil_radial_thicknesses = pf_coil_radial_thicknesses
        self.outboard_tf_coil_radial_thickness = outboard_tf_coil_radial_thickness
        self.outboard_tf_coil_poloidal_thickness = outboard_tf_coil_poloidal_thickness
        self.divertor_radial_thickness = divertor_radial_thickness
        self.support_radial_thickness = support_radial_thickness
        self.elongation = elongation
        self.triangularity = triangularity
        self.rear_blanket_to_tf_gap = rear_blanket_to_tf_gap
        self.pf_coil_vertical_thicknesses = pf_coil_vertical_thicknesses
        self.pf_coil_case_thicknesses = pf_coil_case_thicknesses
        self.number_of_tf_coils = number_of_tf_coils
        self.rotation_angle = rotation_angle
        self.divertor_position = divertor_position
        self.support_position = support_position
        self.pf_coil_vertical_position = pf_coil_vertical_position
        self.pf_coil_radial_position = pf_coil_radial_position

        # adds self.input_variable_names from the Reactor class
        self.input_variable_names: List[str] = self.input_variable_names + [
            "inner_bore_radial_thickness",
            "inboard_tf_leg_radial_thickness",
            "center_column_shield_radial_thickness",
            "inboard_blanket_radial_thickness",
            "firstwall_radial_thickness",
            "inner_plasma_gap_radial_thickness",
            "plasma_radial_thickness",
            "divertor_radial_thickness",
            "support_radial_thickness",
            "outer_plasma_gap_radial_thickness",
            "outboard_blanket_radial_thickness",
            "blanket_rear_wall_radial_thickness",
            "elongation",
            "triangularity",
            "number_of_tf_coils",
            "rotation_angle",
            "outboard_tf_coil_radial_thickness",
            "rear_blanket_to_tf_gap",
            "outboard_tf_coil_poloidal_thickness",
            "pf_coil_vertical_thicknesses",
            "pf_coil_radial_thicknesses",
            "pf_coil_radial_position",
            "pf_coil_vertical_position",
            "pf_coil_case_thicknesses",
            "divertor_position",
            "support_position",
        ]

        # set by make_plasma
        self.major_radius = None
        self.minor_radius = None

        # set during geometry creation
        self._pf_coils = None
        self._pf_coils_casing = None
        self._divertor_lower = None
        self._divertor_upper = None

    @property
    def pf_coil_radial_position(self):
        return self._pf_coil_radial_position

    @pf_coil_radial_position.setter
    def pf_coil_radial_position(self, value):
        if not isinstance(value, list) and value is not None:
            raise ValueError("pf_coil_radial_position must be a list")
        self._pf_coil_radial_position = value

    @property
    def pf_coil_radial_thicknesses(self):
        return self._pf_coil_radial_thicknesses

    @pf_coil_radial_thicknesses.setter
    def pf_coil_radial_thicknesses(self, value):
        if not isinstance(value, list) and value is not None:
            raise ValueError("pf_coil_radial_thicknesses must be a list")
        self._pf_coil_radial_thicknesses = value

    @property
    def pf_coil_vertical_thicknesses(self):
        return self._pf_coil_vertical_thicknesses

    @pf_coil_vertical_thicknesses.setter
    def pf_coil_vertical_thicknesses(self, value):
        if not isinstance(value, list) and value is not None:
            raise ValueError("pf_coil_vertical_thicknesses must be a list")
        self._pf_coil_vertical_thicknesses = value

    @property
    def divertor_position(self):
        return self._divertor_position

    @divertor_position.setter
    def divertor_position(self, value):
        acceptable_values = ["upper", "lower", "both"]
        if value in acceptable_values:
            self._divertor_position = value
        else:
            msg = "divertor_position must be 'upper', 'lower' or 'both'"
            raise ValueError(msg)

    @property
    def support_position(self):
        return self._support_position

    @support_position.setter
    def support_position(self, value):
        acceptable_values = ["upper", "lower", "both"]
        if value in acceptable_values:
            self._support_position = value
        else:
            msg = "support_position must be 'upper', 'lower' or 'both'"
            raise ValueError(msg)

    def create_solids(self):
        """Creates a list of paramak.Shape for components and saves it in
        self.shapes_and_components
        """

        uncut_shapes = []

        self._rotation_angle_check()
        uncut_shapes.append(self._make_plasma())
        self._make_radial_build()
        self._make_vertical_build()
        uncut_shapes.append(self._make_center_column_shield())
        uncut_shapes.append(self._make_firstwall())
        uncut_shapes.append(self._make_blanket())
        uncut_shapes += self._make_divertor()
        uncut_shapes.append(self._make_supports())
        uncut_shapes.append(self._make_rear_blanket_wall())
        uncut_shapes += self._make_tf_coils()
        pf_coils = self._make_pf_coils()

        if pf_coils is None:
            shapes_and_components = uncut_shapes
        else:
            for shape in uncut_shapes:
                print(shape, shape.name)
                for pf_coil in pf_coils:
                    shape.solid = shape.solid.cut(pf_coil.solid)
            shapes_and_components = pf_coils + uncut_shapes

        self.shapes_and_components = shapes_and_components

    def _rotation_angle_check(self):

        if self.rotation_angle == 360:
            msg = "360 degree rotation may result" + " in a Standard_ConstructionError or AttributeError"
            warnings.warn(msg, UserWarning)

    def _make_radial_build(self):

        # this is the radial build sequence, where one component stops and
        # another starts

        self._inner_bore_start_radius = 0
        self._inner_bore_end_radius = self._inner_bore_start_radius + self.inner_bore_radial_thickness

        self._inboard_tf_coils_start_radius = self._inner_bore_end_radius
        self._inboard_tf_coils_end_radius = self._inboard_tf_coils_start_radius + self.inboard_tf_leg_radial_thickness

        self._center_column_shield_start_radius = self._inboard_tf_coils_end_radius
        self._center_column_shield_end_radius = (
            self._center_column_shield_start_radius + self.center_column_shield_radial_thickness
        )

        self._inboard_blanket_start_radius = self._center_column_shield_end_radius
        self._inboard_blanket_end_radius = self._inboard_blanket_start_radius + self.inboard_blanket_radial_thickness

        self._inboard_firstwall_start_radius = self._inboard_blanket_end_radius
        self._inboard_firstwall_end_radius = self._inboard_firstwall_start_radius + self.firstwall_radial_thickness

        self._inner_plasma_gap_start_radius = self._inboard_firstwall_end_radius
        self._inner_plasma_gap_end_radius = self._inner_plasma_gap_start_radius + self.inner_plasma_gap_radial_thickness

        self._plasma_start_radius = self._inner_plasma_gap_end_radius
        self._plasma_end_radius = self._plasma_start_radius + self.plasma_radial_thickness

        self._outer_plasma_gap_start_radius = self._plasma_end_radius
        self._outer_plasma_gap_end_radius = self._outer_plasma_gap_start_radius + self.outer_plasma_gap_radial_thickness

        self._outboard_firstwall_start_radius = self._outer_plasma_gap_end_radius
        self._outboard_firstwall_end_radius = self._outboard_firstwall_start_radius + self.firstwall_radial_thickness

        self._outboard_blanket_start_radius = self._outboard_firstwall_end_radius
        self._outboard_blanket_end_radius = self._outboard_blanket_start_radius + self.outboard_blanket_radial_thickness

        self._blanket_rear_wall_start_radius = self._outboard_blanket_end_radius
        self._blanket_rear_wall_end_radius = (
            self._blanket_rear_wall_start_radius + self.blanket_rear_wall_radial_thickness
        )

        self._tf_info_provided = False
        if (
            self.outboard_tf_coil_radial_thickness is not None
            and self.rear_blanket_to_tf_gap is not None
            and self.outboard_tf_coil_poloidal_thickness is not None
        ):
            self._tf_info_provided = True
            self._outboard_tf_coil_start_radius = self._blanket_rear_wall_end_radius + self.rear_blanket_to_tf_gap
            self._outboard_tf_coil_end_radius = (
                self._outboard_tf_coil_start_radius + self.outboard_tf_coil_radial_thickness
            )

        self._divertor_start_radius = self._plasma.high_point[0] - 0.5 * self.divertor_radial_thickness
        self._divertor_end_radius = self._plasma.high_point[0] + 0.5 * self.divertor_radial_thickness

        self._support_start_radius = self._plasma.high_point[0] - 0.5 * self.support_radial_thickness
        self._support_end_radius = self._plasma.high_point[0] + 0.5 * self.support_radial_thickness

    def _make_vertical_build(self):

        # this is the vertical build sequence, componets build on each other in
        # a similar manner to the radial build

        self._plasma_start_height = 0
        self._plasma_end_height = self._plasma.high_point[1]

        self._plasma_to_divertor_gap_start_height = self._plasma_end_height
        self._plasma_to_divertor_gap_end_height = (
            self._plasma_to_divertor_gap_start_height + self.outer_plasma_gap_radial_thickness
        )

        # the firstwall is cut by the divertor but uses the same control points
        self._firstwall_start_height = self._plasma_to_divertor_gap_end_height
        self._firstwall_end_height = self._firstwall_start_height + self.firstwall_radial_thickness

        self._blanket_start_height = self._firstwall_end_height
        self._blanket_end_height = self._blanket_start_height + self.outboard_blanket_radial_thickness

        self._blanket_rear_wall_start_height = self._blanket_end_height
        self._blanket_rear_wall_end_height = (
            self._blanket_rear_wall_start_height + self.blanket_rear_wall_radial_thickness
        )

        if self._tf_info_provided:
            self._outboard_tf_coils_vertical_height = self._blanket_rear_wall_end_height * 1.5
            self._outboard_tf_coils_horizontal_length = self._blanket_rear_wall_end_radius * 0.75

    def _make_center_column_shield(self):

        self._center_column_shield = paramak.CenterColumnShieldCylinder(
            height=self._blanket_rear_wall_end_height * 2,
            inner_radius=self._center_column_shield_start_radius,
            outer_radius=self._center_column_shield_end_radius,
            rotation_angle=self.rotation_angle,
            name="center_column_shield",
        )
        return self._center_column_shield

    def _make_plasma(self):

        # sets major radius and minor radius from equatorial_points to allow a
        # radial build this helps avoid the plasma overlapping the center
        # column and other components
        inner_equatorial_point = (
            self.inner_bore_radial_thickness
            + self.inboard_tf_leg_radial_thickness
            + self.center_column_shield_radial_thickness
            + self.inboard_blanket_radial_thickness
            + self.firstwall_radial_thickness
            + self.inner_plasma_gap_radial_thickness
        )
        outer_equatorial_point = inner_equatorial_point + self.plasma_radial_thickness
        self.major_radius = (outer_equatorial_point + inner_equatorial_point) / 2
        self.minor_radius = self.major_radius - inner_equatorial_point

        plasma = paramak.Plasma(
            major_radius=self.major_radius,
            minor_radius=self.minor_radius,
            elongation=self.elongation,
            triangularity=self.triangularity,
            rotation_angle=self.rotation_angle,
        )

        self._plasma = plasma
        return self._plasma

    def _make_firstwall(self):

        # this is used to cut the inboard blanket and then fused / unioned with
        # the firstwall
        self._inboard_firstwall = paramak.BlanketFP(
            plasma=self._plasma,
            offset_from_plasma=self.inner_plasma_gap_radial_thickness,
            start_angle=90,
            stop_angle=270,
            thickness=self.firstwall_radial_thickness,
            rotation_angle=self.rotation_angle,
            color=(0.5, 0.5, 0.5),
        )

        self._firstwall = paramak.BlanketFP(
            plasma=self._plasma,
            offset_from_plasma=self.outer_plasma_gap_radial_thickness,
            start_angle=90,
            stop_angle=-90,
            thickness=self.firstwall_radial_thickness,
            rotation_angle=self.rotation_angle,
            name="outboard_firstwall",
            union=self._inboard_firstwall,
            color=(0.5, 0.5, 0.5),
        )
        return self._firstwall

    def _make_divertor(self):
        fw_envelope_inboard = paramak.BlanketFP(
            plasma=self._plasma,
            offset_from_plasma=self.inner_plasma_gap_radial_thickness,
            start_angle=90,
            stop_angle=270,
            thickness=self.firstwall_radial_thickness,
            rotation_angle=self.rotation_angle,
        )

        fw_envelope = paramak.BlanketFP(
            plasma=self._plasma,
            offset_from_plasma=self.outer_plasma_gap_radial_thickness,
            start_angle=90,
            stop_angle=-90,
            thickness=self.firstwall_radial_thickness,
            rotation_angle=self.rotation_angle,
            name="outboard_firstwall",
            union=fw_envelope_inboard,
        )
        divertor_height = self._blanket_rear_wall_end_height

        divertor_height_top = divertor_height
        divertor_height_bottom = -divertor_height

        if self.divertor_position in ["lower", "both"]:
            self._divertor_lower = paramak.RotateStraightShape(
                points=[
                    (self._divertor_start_radius, divertor_height_bottom),
                    (self._divertor_end_radius, divertor_height_bottom),
                    (self._divertor_end_radius, 0),
                    (self._divertor_start_radius, 0),
                ],
                intersect=fw_envelope,
                name="divertor_lower",
                color=(1.0, 0.667, 0.0),
                rotation_angle=self.rotation_angle,
            )
        if self.divertor_position in ["upper", "both"]:
            self._divertor_upper = paramak.RotateStraightShape(
                points=[
                    (self._divertor_start_radius, 0),
                    (self._divertor_end_radius, 0),
                    (self._divertor_end_radius, divertor_height_top),
                    (self._divertor_start_radius, divertor_height_top),
                ],
                intersect=fw_envelope,
                name="divertor_upper",
                color=(1.0, 0.667, 0.0),
                rotation_angle=self.rotation_angle,
            )

        if self.divertor_position == "upper":
            cut_list = [self._divertor_upper]
        if self.divertor_position == "lower":
            cut_list = [self._divertor_lower]
        if self.divertor_position == "both":
            cut_list = [self._divertor_lower, self._divertor_upper]
        self._firstwall.cut = cut_list
        self._inboard_firstwall.cut = cut_list

        if self.divertor_position == "upper":
            return [self._divertor_upper]
        if self.divertor_position == "lower":
            return [self._divertor_lower]
        if self.divertor_position == "both":
            return [self._divertor_upper, self._divertor_lower]

    def _make_blanket(self):
        self._inboard_blanket = paramak.CenterColumnShieldCylinder(
            height=self._blanket_end_height * 2,
            inner_radius=self._inboard_blanket_start_radius,
            outer_radius=max(self._inboard_firstwall.points)[0],
            rotation_angle=self.rotation_angle,
            cut=self._inboard_firstwall,
        )

        # this takes a single solid from a compound of solids by finding the
        # solid nearest to a point
        # TODO: find alternative
        self._inboard_blanket.solid = self._inboard_blanket.solid.solids(cq.selectors.NearestToPointSelector((0, 0, 0)))

        # this is the outboard fused /unioned with the inboard blanket

        self._blanket = paramak.BlanketFP(
            plasma=self._plasma,
            start_angle=90,
            stop_angle=-90,
            offset_from_plasma=self.outer_plasma_gap_radial_thickness + self.firstwall_radial_thickness,
            thickness=self.outboard_blanket_radial_thickness,
            rotation_angle=self.rotation_angle,
            name="blanket",
            color=(0.0, 1.0, 0.498),
            union=self._inboard_blanket,
        )
        return self._blanket

    def _make_supports(self):
        blanket_envelope = paramak.BlanketFP(
            plasma=self._plasma,
            start_angle=90,
            stop_angle=-90,
            offset_from_plasma=self.outer_plasma_gap_radial_thickness + self.firstwall_radial_thickness,
            thickness=self.outboard_blanket_radial_thickness,
            rotation_angle=self.rotation_angle,
            union=self._inboard_blanket,
        )
        support_height = self._blanket_rear_wall_end_height
        support_height_top = support_height
        support_height_bottom = -support_height

        if self.support_position == "lower":
            support_height_top = 0
        elif self.support_position == "upper":
            support_height_bottom = 0

        self._supports = paramak.RotateStraightShape(
            points=[
                (self._support_start_radius, support_height_bottom),
                (self._support_end_radius, support_height_bottom),
                (self._support_end_radius, support_height_top),
                (self._support_start_radius, support_height_top),
            ],
            rotation_angle=self.rotation_angle,
            name="supports",
            color=(0.0, 0.0, 0.0),
            intersect=blanket_envelope,
        )

        self._blanket.solid = self._blanket.solid.cut(self._supports.solid)

        return self._supports

    def _make_rear_blanket_wall(self):
        self._outboard_rear_blanket_wall_upper = paramak.RotateStraightShape(
            points=[
                (
                    self._center_column_shield_end_radius,
                    self._blanket_rear_wall_start_height,
                ),
                (
                    self._center_column_shield_end_radius,
                    self._blanket_rear_wall_end_height,
                ),
                (
                    max(self._inboard_firstwall.points)[0],
                    self._blanket_rear_wall_end_height,
                ),
                (
                    max(self._inboard_firstwall.points)[0],
                    self._blanket_rear_wall_start_height,
                ),
            ],
            rotation_angle=self.rotation_angle,
        )

        self._outboard_rear_blanket_wall_lower = paramak.RotateStraightShape(
            points=[
                (
                    self._center_column_shield_end_radius,
                    -self._blanket_rear_wall_start_height,
                ),
                (
                    self._center_column_shield_end_radius,
                    -self._blanket_rear_wall_end_height,
                ),
                (
                    max(self._inboard_firstwall.points)[0],
                    -self._blanket_rear_wall_end_height,
                ),
                (
                    max(self._inboard_firstwall.points)[0],
                    -self._blanket_rear_wall_start_height,
                ),
            ],
            rotation_angle=self.rotation_angle,
        )

        self._outboard_rear_blanket_wall = paramak.BlanketFP(
            plasma=self._plasma,
            start_angle=90,
            stop_angle=-90,
            offset_from_plasma=self.outer_plasma_gap_radial_thickness
            + self.firstwall_radial_thickness
            + self.outboard_blanket_radial_thickness,
            thickness=self.blanket_rear_wall_radial_thickness,
            rotation_angle=self.rotation_angle,
            name="outboard_rear_blanket_wall",
            color=(0.0, 1.0, 1.0),
            union=[
                self._outboard_rear_blanket_wall_upper,
                self._outboard_rear_blanket_wall_lower,
            ],
        )

        return self._outboard_rear_blanket_wall

    def _make_pf_coils(self):

        pf_input_lists = [
            self.pf_coil_vertical_thicknesses,
            self.pf_coil_radial_thicknesses,
            self.pf_coil_vertical_position,
            self.pf_coil_radial_position,
        ]

        # checks if lists are all the same length
        if all(len(input_list) == len(pf_input_lists[0]) for input_list in pf_input_lists):
            number_of_pf_coils = len(pf_input_lists[0])
            if number_of_pf_coils == 0:
                return None

            center_points = [(x, y) for x, y in zip(self.pf_coil_radial_position, self.pf_coil_vertical_position)]

            self._pf_coils = []
            for counter, (center_point, pf_coil_vertical_thickness, pf_coil_radial_thickness,) in enumerate(
                zip(
                    center_points,
                    self.pf_coil_vertical_thicknesses,
                    self.pf_coil_radial_thicknesses,
                ),
                1,
            ):
                pf_coil = paramak.PoloidalFieldCoil(
                    height=pf_coil_vertical_thickness,
                    width=pf_coil_radial_thickness,
                    center_point=center_point,
                    rotation_angle=self.rotation_angle,
                    name=f"pf_coil_{counter}",
                )
                self._pf_coils.append(pf_coil)

            if self.pf_coil_case_thicknesses == []:
                return self._pf_coils

            self._pf_coils_casing = []
            if len(self.pf_coil_case_thicknesses) == number_of_pf_coils:
                for counter, (pf_coil_case_thickness, pf_coil) in enumerate(
                    zip(self.pf_coil_case_thicknesses, self._pf_coils), 1
                ):
                    pf_coils_casing = paramak.PoloidalFieldCoilCaseFC(
                        pf_coil=pf_coil,
                        casing_thickness=pf_coil_case_thickness,
                        rotation_angle=self.rotation_angle,
                        name=f"pf_coil_case_{counter}",
                    )
                    self._pf_coils_casing.append(pf_coils_casing)
            else:
                raise ValueError(
                    "pf_coil_case_thicknesses is not the same length as the other "
                    "PF coil inputs (pf_coil_vertical_thicknesses, "
                    "pf_coil_radial_thicknesses, pf_coil_radial_position, "
                    "pf_coil_vertical_position) so can not make pf coils cases"
                )

            return self._pf_coils + self._pf_coils_casing

    def _make_tf_coils(self):
        list_of_components = []

        self._inboard_tf_coils = paramak.CenterColumnShieldCylinder(
            height=self._blanket_rear_wall_end_height * 2,
            inner_radius=self._inboard_tf_coils_start_radius,
            outer_radius=self._inboard_tf_coils_end_radius,
            rotation_angle=self.rotation_angle,
            name="inboard_tf_coils",
            color=(0, 0, 1),
        )
        list_of_components.append(self._inboard_tf_coils)

        if (
            None
            not in [
                self.rear_blanket_to_tf_gap,
                self.outboard_tf_coil_radial_thickness,
                self.outboard_tf_coil_poloidal_thickness,
                self.number_of_tf_coils,
            ]
            and self.number_of_tf_coils > 1
        ):

            if self._tf_info_provided:
                self._tf_coil = paramak.ToroidalFieldCoilCoatHanger(
                    with_inner_leg=False,
                    horizontal_start_point=(
                        self._inboard_tf_coils_start_radius,
                        self._blanket_rear_wall_end_height,
                    ),
                    vertical_mid_point=(self._outboard_tf_coil_start_radius, 0),
                    thickness=self.outboard_tf_coil_radial_thickness,
                    number_of_coils=self.number_of_tf_coils,
                    distance=self.outboard_tf_coil_poloidal_thickness,
                    rotation_angle=self.rotation_angle,
                    horizontal_length=self._outboard_tf_coils_horizontal_length,
                    vertical_length=self._outboard_tf_coils_vertical_height,
                    name="tf_coils",
                )
                list_of_components.append(self._tf_coil)

        return list_of_components
