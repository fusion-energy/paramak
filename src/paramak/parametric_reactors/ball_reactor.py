import warnings
from typing import List, Optional

import paramak


class BallReactor(paramak.Reactor):
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
        pf_coil_radial_thicknesses: the radial
            thickness of each poloidal field coil.
        pf_coil_vertical_thicknesses: the vertical
            thickness of each poloidal field coil.
        pf_coil_to_tf_coil_radial_gap: the radial distance
            between the rear of the poloidal field coil and the toroidal field
            coil.
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

    def __init__(
        self,
        inner_bore_radial_thickness: float = 10.0,
        inboard_tf_leg_radial_thickness: float = 30.0,
        center_column_shield_radial_thickness: float = 60.0,
        divertor_radial_thickness: float = 150.0,
        inner_plasma_gap_radial_thickness: float = 30.0,
        plasma_radial_thickness: float = 300.0,
        outer_plasma_gap_radial_thickness: float = 30.0,
        plasma_gap_vertical_thickness: float = 50.0,
        firstwall_radial_thickness: float = 30.0,
        blanket_radial_thickness: float = 50.0,
        blanket_rear_wall_radial_thickness: float = 30.0,
        elongation: float = 2.0,
        triangularity: float = 0.55,
        divertor_to_tf_gap_vertical_thickness: Optional[float] = 0,
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

        super().__init__([])

        self.inner_bore_radial_thickness = inner_bore_radial_thickness
        self.inboard_tf_leg_radial_thickness = inboard_tf_leg_radial_thickness
        self.center_column_shield_radial_thickness = center_column_shield_radial_thickness
        self.divertor_radial_thickness = divertor_radial_thickness
        self.inner_plasma_gap_radial_thickness = inner_plasma_gap_radial_thickness
        self.plasma_radial_thickness = plasma_radial_thickness
        self.outer_plasma_gap_radial_thickness = outer_plasma_gap_radial_thickness
        self.firstwall_radial_thickness = firstwall_radial_thickness
        self.blanket_radial_thickness = blanket_radial_thickness
        self.blanket_rear_wall_radial_thickness = blanket_rear_wall_radial_thickness

        self.pf_coil_vertical_position = pf_coil_vertical_position
        self.pf_coil_radial_position = pf_coil_radial_position
        self.pf_coil_radial_thicknesses = pf_coil_radial_thicknesses
        self.pf_coil_vertical_thicknesses = pf_coil_vertical_thicknesses
        self.rear_blanket_to_tf_gap = rear_blanket_to_tf_gap

        self.pf_coil_case_thicknesses = pf_coil_case_thicknesses
        self.outboard_tf_coil_radial_thickness = outboard_tf_coil_radial_thickness
        self.outboard_tf_coil_poloidal_thickness = outboard_tf_coil_poloidal_thickness
        self.divertor_position = divertor_position
        self.rotation_angle = rotation_angle

        self.plasma_gap_vertical_thickness = plasma_gap_vertical_thickness
        self.divertor_to_tf_gap_vertical_thickness = divertor_to_tf_gap_vertical_thickness

        self.elongation = elongation
        self.triangularity = triangularity

        self.number_of_tf_coils = number_of_tf_coils
        self.rotation_angle = rotation_angle

        # adds self.input_variable_names from the Reactor class
        self.input_variable_names: List[str] = self.input_variable_names + [
            "inner_bore_radial_thickness",
            "inboard_tf_leg_radial_thickness",
            "center_column_shield_radial_thickness",
            "divertor_radial_thickness",
            "inner_plasma_gap_radial_thickness",
            "plasma_radial_thickness",
            "outer_plasma_gap_radial_thickness",
            "firstwall_radial_thickness",
            "blanket_radial_thickness",
            "blanket_rear_wall_radial_thickness",
            "elongation",
            "triangularity",
            "plasma_gap_vertical_thickness",
            "divertor_to_tf_gap_vertical_thickness",
            "number_of_tf_coils",
            "rear_blanket_to_tf_gap",
            "pf_coil_radial_thicknesses",
            "pf_coil_vertical_thicknesses",
            "pf_coil_radial_position",
            "pf_coil_vertical_position",
            "pf_coil_case_thicknesses",
            "outboard_tf_coil_radial_thickness",
            "outboard_tf_coil_poloidal_thickness",
            "divertor_position",
            "rotation_angle",
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
    def rotation_angle(self):
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        if value == 360:
            msg = "360 degree rotation may result in a " "Standard_ConstructionError or AttributeError"
            warnings.warn(msg, UserWarning)
        elif value > 360:
            raise ValueError("rotation_angle can not be larger than 360")
        self._rotation_angle = value

    @property
    def pf_coil_vertical_position(self):
        return self._pf_coil_vertical_position

    @pf_coil_vertical_position.setter
    def pf_coil_vertical_position(self, value):
        if not isinstance(value, list):
            raise ValueError("pf_coil_vertical_position must be a list")
        self._pf_coil_vertical_position = value

    @property
    def pf_coil_radial_position(self):
        return self._pf_coil_radial_position

    @pf_coil_radial_position.setter
    def pf_coil_radial_position(self, value):
        if not isinstance(value, list):
            raise ValueError("pf_coil_radial_position must be a list")
        self._pf_coil_radial_position = value

    @property
    def pf_coil_radial_thicknesses(self):
        return self._pf_coil_radial_thicknesses

    @pf_coil_radial_thicknesses.setter
    def pf_coil_radial_thicknesses(self, value):
        if not isinstance(value, list):
            raise ValueError("pf_coil_radial_thicknesses must be a list")
        self._pf_coil_radial_thicknesses = value

    @property
    def pf_coil_vertical_thicknesses(self):
        return self._pf_coil_vertical_thicknesses

    @pf_coil_vertical_thicknesses.setter
    def pf_coil_vertical_thicknesses(self, value):
        if not isinstance(value, list):
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

    def create_solids(self):
        """Creates a list of paramak.Shape for components and saves it in
        self.shapes_and_components
        """

        uncut_shapes = []

        uncut_shapes.append(self._make_plasma())
        self._make_radial_build()
        self._make_vertical_build()
        uncut_shapes.append(self._make_inboard_tf_coils())
        uncut_shapes.append(self._make_center_column_shield())
        uncut_shapes += self._make_blankets_layers()
        uncut_shapes += self._make_divertor()
        uncut_shapes += self._make_tf_coils()
        pf_coils = self._make_pf_coils()

        if pf_coils is None:
            shapes_and_components = uncut_shapes
        else:
            for shape in uncut_shapes:
                for pf_coil in pf_coils:
                    shape.solid = shape.solid.cut(pf_coil.solid)
            shapes_and_components = uncut_shapes + pf_coils

        self.shapes_and_components = shapes_and_components

    def _make_plasma(self):

        inner_equatorial_point = (
            self.inner_bore_radial_thickness
            + self.inboard_tf_leg_radial_thickness
            + self.center_column_shield_radial_thickness
            + self.inner_plasma_gap_radial_thickness
        )
        outer_equatorial_point = inner_equatorial_point + self.plasma_radial_thickness

        # sets major radius and minor radius from equatorial_points to allow a
        # radial build. This helps avoid the plasma overlapping the center
        # column and other components
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

        self._divertor_start_radius = self._center_column_shield_end_radius
        self._divertor_end_radius = self._center_column_shield_end_radius + self.divertor_radial_thickness

        self._firstwall_start_radius = (
            self._center_column_shield_end_radius
            + self.inner_plasma_gap_radial_thickness
            + self.plasma_radial_thickness
            + self.outer_plasma_gap_radial_thickness
        )
        self._firstwall_end_radius = self._firstwall_start_radius + self.firstwall_radial_thickness

        self._blanket_start_radius = self._firstwall_end_radius
        self._blanket_end_radius = self._blanket_start_radius + self.blanket_radial_thickness

        self._blanket_rear_wall_start_radius = self._blanket_end_radius
        self._blanket_rear_wall_end_radius = (
            self._blanket_rear_wall_start_radius + self.blanket_rear_wall_radial_thickness
        )

    def _make_vertical_build(self):

        # this is the vertical build sequence, components build on each other
        # in a similar manner to the radial build

        self._firstwall_start_height = self._plasma.high_point[1] + self.plasma_gap_vertical_thickness
        self._firstwall_end_height = self._firstwall_start_height + self.firstwall_radial_thickness

        self._blanket_start_height = self._firstwall_end_height
        self._blanket_end_height = self._blanket_start_height + self.blanket_radial_thickness

        self._blanket_rear_wall_start_height = self._blanket_end_height
        self._blanket_rear_wall_end_height = (
            self._blanket_rear_wall_start_height + self.blanket_rear_wall_radial_thickness
        )

        self._tf_coil_start_height = self._blanket_rear_wall_end_height + self.divertor_to_tf_gap_vertical_thickness

        self._center_column_shield_height = self._blanket_rear_wall_end_height * 2

        if self.rear_blanket_to_tf_gap is not None:
            self._tf_coil_start_radius = self._blanket_rear_wall_end_radius + self.rear_blanket_to_tf_gap
            self._tf_coil_end_radius = self._tf_coil_start_radius + self.outboard_tf_coil_radial_thickness

    def _make_inboard_tf_coils(self):

        self._inboard_tf_coils = paramak.CenterColumnShieldCylinder(
            height=self._tf_coil_start_height * 2,
            inner_radius=self._inboard_tf_coils_start_radius,
            outer_radius=self._inboard_tf_coils_end_radius,
            rotation_angle=self.rotation_angle,
            name="inboard_tf_coils",
            color=(0, 0, 1),
        )
        return self._inboard_tf_coils

    def _make_center_column_shield(self):

        self._center_column_shield = paramak.CenterColumnShieldCylinder(
            height=self._center_column_shield_height,
            inner_radius=self._center_column_shield_start_radius,
            outer_radius=self._center_column_shield_end_radius,
            rotation_angle=self.rotation_angle,
            color=(0.0, 0.333, 0.0),
            name="center_column_shield",
        )
        return self._center_column_shield

    def _make_blankets_layers(self):

        offset_from_plasma = [
            self.major_radius - self.minor_radius,
            self.plasma_gap_vertical_thickness,
            self.outer_plasma_gap_radial_thickness,
            self.plasma_gap_vertical_thickness,
            self.major_radius - self.minor_radius,
        ]

        self._center_column_cutter = paramak.CenterColumnShieldCylinder(
            # extra 0.5 to ensure overlap,
            height=self._center_column_shield_height * 1.5,
            inner_radius=0,
            outer_radius=self._center_column_shield_end_radius,
            rotation_angle=360,
            color=(0.0, 0.0, 1.0),
        )

        self._firstwall = paramak.BlanketFP(
            plasma=self._plasma,
            thickness=self.firstwall_radial_thickness,
            offset_from_plasma=offset_from_plasma,
            start_angle=-180,
            stop_angle=180,
            rotation_angle=self.rotation_angle,
            color=(0.5, 0.5, 0.5),
            name="firstwall",
            cut=[self._center_column_cutter],
            allow_overlapping_shape=True,
        )

        self._blanket = paramak.BlanketFP(
            plasma=self._plasma,
            thickness=self.blanket_radial_thickness,
            offset_from_plasma=[e + self.firstwall_radial_thickness for e in offset_from_plasma],
            start_angle=-180,
            stop_angle=180,
            rotation_angle=self.rotation_angle,
            color=(0.0, 1.0, 0.498),
            name="blanket",
            cut=[self._center_column_cutter],
            allow_overlapping_shape=True,
        )

        self._blanket_rear_wall = paramak.BlanketFP(
            plasma=self._plasma,
            thickness=self.blanket_rear_wall_radial_thickness,
            offset_from_plasma=[
                e + self.firstwall_radial_thickness + self.blanket_radial_thickness for e in offset_from_plasma
            ],
            start_angle=-180,
            stop_angle=180,
            rotation_angle=self.rotation_angle,
            color=(0.0, 1.0, 1.0),
            name="blanket_rear_wall",
            cut=[self._center_column_cutter],
            allow_overlapping_shape=True,
        )

        return [self._firstwall, self._blanket, self._blanket_rear_wall]

    def _make_divertor(self):

        offset_from_plasma = [
            self.major_radius - self.minor_radius,
            self.plasma_gap_vertical_thickness,
            self.outer_plasma_gap_radial_thickness,
            self.plasma_gap_vertical_thickness,
            self.major_radius - self.minor_radius,
        ]

        # used as an intersect when making the divertor
        self._blanket_fw_rear_wall_envelope = paramak.BlanketFP(
            plasma=self._plasma,
            thickness=self.firstwall_radial_thickness
            + self.blanket_radial_thickness
            + self.blanket_rear_wall_radial_thickness,
            offset_from_plasma=offset_from_plasma,
            start_angle=-180,
            stop_angle=180,
            rotation_angle=self.rotation_angle,
            allow_overlapping_shape=True,
        )

        divertor_height = self._blanket_rear_wall_end_height * 2

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
                intersect=self._blanket_fw_rear_wall_envelope,
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
                intersect=self._blanket_fw_rear_wall_envelope,
                name="divertor_upper",
                color=(1.0, 0.667, 0.0),
                rotation_angle=self.rotation_angle,
            )

        for component in [self._firstwall, self._blanket, self._blanket_rear_wall]:
            if self.divertor_position in ["upper", "both"]:
                component.cut.append(self._divertor_upper)
            if self.divertor_position in ["lower", "both"]:
                component.cut.append(self._divertor_lower)

        if self.divertor_position == "upper":
            return [self._divertor_upper]
        if self.divertor_position == "lower":
            return [self._divertor_lower]
        if self.divertor_position == "both":
            return [self._divertor_upper, self._divertor_lower]

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

        raise ValueError(
            "pf_coil_vertical_thicknesses, pf_coil_radial_thicknesses, "
            "pf_coil_radial_position, pf_coil_vertical_position are not "
            "the same length so can not make PF coils"
        )

    def _make_tf_coils(self):
        comp = []
        # checks that all the required information has been input by the user
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

            self._tf_coil = paramak.ToroidalFieldCoilRectangle(
                with_inner_leg=False,
                horizontal_start_point=(
                    self._inboard_tf_coils_start_radius,
                    self._tf_coil_start_height,
                ),
                vertical_mid_point=(self._tf_coil_start_radius, 0),
                thickness=self.outboard_tf_coil_radial_thickness,
                number_of_coils=self.number_of_tf_coils,
                distance=self.outboard_tf_coil_poloidal_thickness,
                name="tf_coil",
                rotation_angle=self.rotation_angle,
            )
            comp = [self._tf_coil]
        return comp
