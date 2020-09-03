import math
import operator
import warnings

import cadquery as cq

import paramak


class BallReactor(paramak.Reactor):
    """Creates geometry for a simple ball reactor including a plasma,
    cylindical center column shielding, square toroidal field coils.
    There is no inboard breeder blanket on this ball reactor like
    most spherical reactors.

    Arguments:
        inner_bore_radial_thickness (float): the radial thickness of the
            inner bore (cm)
        inboard_tf_leg_radial_thickness (float): the radial thickness of the
            inner leg of the toroidal field coils (cm)
        center_column_shield_radial_thickness (float): the radial thickness of
            the center column shield (cm)
        divertor_radial_thickness (float): the radial thickness of the divertor
            (cm), this fills the gap between the center column shield and blanket
        inner_plasma_gap_radial_thickness (float): the radial thickness of the
            inboard gap between the plasma and the center column shield (cm)
        plasma_radial_thickness (float): the radial thickness of the plasma
        outer_plasma_gap_radial_thickness (float): the radial thickness of the
            outboard gap between the plasma and firstwall (cm)
        firstwall_radial_thickness (float): the radial thickness of the first
            wall (cm)
        blanket_radial_thickness (float): the radial thickness of the blanket (cm)
        blanket_rear_wall_radial_thickness (float): the radial thickness of the
            rear wall of the blanket (cm)
        elongation (float): the elongation of the plasma
        triangularity (float): the triangularity of the plasma
        number_of_tf_coils (int): the number of tf coils
        pf_coil_to_rear_blanket_radial_gap (float): the radial distance between
            the rear blanket and the closest poloidal field coil (optional)
        pf_coil_radial_thicknesses (list of floats): the radial thickness of each
            poloidal field coil (optional)
        pf_coil_vertical_thicknesses (list of floats): the vertical thickness of
            each poloidal field coil (optional)
        pf_coil_to_tf_coil_radial_gap (float): the radial distance between the
            rear of the poloidal field coil and the toroidal field coil (optional)
        outboard_tf_coil_radial_thickness (float): the radial thickness of the
            toroidal field coil (optional)
        outboard_tf_coil_poloidal_thickness (float): the poloidal thickness of the toroidal
            field coil (optional)
        rotation_angle (float): the angle of the sector that is desired

    Returns:
        a paramak shape object: a Reactor object that has generic functionality
    """

    def __init__(
        self,
        inner_bore_radial_thickness,
        inboard_tf_leg_radial_thickness,
        center_column_shield_radial_thickness,
        divertor_radial_thickness,
        inner_plasma_gap_radial_thickness,
        plasma_radial_thickness,
        outer_plasma_gap_radial_thickness,
        firstwall_radial_thickness,
        blanket_radial_thickness,
        blanket_rear_wall_radial_thickness,
        elongation,
        triangularity,
        number_of_tf_coils,
        pf_coil_to_rear_blanket_radial_gap=None,
        pf_coil_radial_thicknesses=None,
        pf_coil_vertical_thicknesses=None,
        pf_coil_to_tf_coil_radial_gap=None,
        outboard_tf_coil_radial_thickness=None,
        outboard_tf_coil_poloidal_thickness=None,
        rotation_angle=360,
    ):

        super().__init__([])

        self.inner_bore_radial_thickness = inner_bore_radial_thickness
        self.inboard_tf_leg_radial_thickness = inboard_tf_leg_radial_thickness
        self.center_column_shield_radial_thickness = (
            center_column_shield_radial_thickness
        )
        self.divertor_radial_thickness = divertor_radial_thickness
        self.inner_plasma_gap_radial_thickness = inner_plasma_gap_radial_thickness
        self.plasma_radial_thickness = plasma_radial_thickness
        self.outer_plasma_gap_radial_thickness = outer_plasma_gap_radial_thickness
        self.firstwall_radial_thickness = firstwall_radial_thickness
        self.blanket_radial_thickness = blanket_radial_thickness
        self.blanket_rear_wall_radial_thickness = blanket_rear_wall_radial_thickness
        self.pf_coil_to_rear_blanket_radial_gap = pf_coil_to_rear_blanket_radial_gap
        self.pf_coil_radial_thicknesses = pf_coil_radial_thicknesses
        self.pf_coil_vertical_thicknesses = pf_coil_vertical_thicknesses
        self.pf_coil_to_tf_coil_radial_gap = pf_coil_to_tf_coil_radial_gap
        self.outboard_tf_coil_radial_thickness = outboard_tf_coil_radial_thickness
        self.outboard_tf_coil_poloidal_thickness = outboard_tf_coil_poloidal_thickness

        # sets major radius and minor radius from equatorial_points to allow a radial build
        # this helps avoid the plasma overlapping the center column and such
        # things

        inner_equatorial_point = (
            inner_bore_radial_thickness
            + inboard_tf_leg_radial_thickness
            + center_column_shield_radial_thickness
            + inner_plasma_gap_radial_thickness
        )
        outer_equatorial_point = inner_equatorial_point + plasma_radial_thickness
        self.major_radius = (
            inner_equatorial_point + plasma_radial_thickness + inner_equatorial_point) / 2
        self.minor_radius = (
            (outer_equatorial_point + inner_equatorial_point) / 2
        ) - inner_equatorial_point

        self.elongation = elongation
        self.triangularity = triangularity

        self.number_of_tf_coils = number_of_tf_coils
        self.rotation_angle = rotation_angle

        shapes_or_components = []

        self.rotation_angle_check()
        self.make_plasma(shapes_or_components)
        self.make_radial_build(shapes_or_components)
        self.make_vertical_build(shapes_or_components)
        self.make_inboard_tf_coils(shapes_or_components)
        self.make_center_column_shield(shapes_or_components)
        self.make_blanket_and_firstwall(shapes_or_components)
        self.make_divertor(shapes_or_components)
        self.make_component_cuts(shapes_or_components)

        self.shapes_and_components = shapes_or_components

    def rotation_angle_check(self):

        if self.rotation_angle == 360:
            warnings.warn(
                "360 degree rotation may result in a Standard_ConstructionError or AttributeError",
                UserWarning)

    def make_plasma(self, shapes_or_components):

        plasma = paramak.Plasma(
            major_radius=self.major_radius,
            minor_radius=self.minor_radius,
            elongation=self.elongation,
            triangularity=self.triangularity,
            rotation_angle=self.rotation_angle,
            stl_filename="plasma.stl",
        )
        plasma.create_solid()

        shapes_or_components.append(plasma)

        self._plasma = plasma

    def make_radial_build(self, shapes_or_components):

        # this is the radial build sequence, where one component stops and
        # another starts

        self._inner_bore_start_radius = 0
        self._inner_bore_end_radius = (
            self._inner_bore_start_radius + self.inner_bore_radial_thickness
        )

        self._inboard_tf_coils_start_radius = self._inner_bore_end_radius
        self._inboard_tf_coils_end_radius = (
            self._inboard_tf_coils_start_radius +
            self.inboard_tf_leg_radial_thickness)

        self._center_column_shield_start_radius = self._inboard_tf_coils_end_radius
        self._center_column_shield_end_radius = (
            self._center_column_shield_start_radius
            + self.center_column_shield_radial_thickness
        )

        self._divertor_start_radius = self._center_column_shield_end_radius
        self._divertor_end_radius = (
            self._center_column_shield_end_radius +
            self.divertor_radial_thickness)

        self._firstwall_start_radius = (
            self._center_column_shield_end_radius
            + self.inner_plasma_gap_radial_thickness
            + self.plasma_radial_thickness
            + self.outer_plasma_gap_radial_thickness
        )
        self._firstwall_end_radius = self._firstwall_start_radius + \
            self.firstwall_radial_thickness

        self._blanket_start_radius = self._firstwall_end_radius
        self._blanket_end_radius = self._blanket_start_radius + self.blanket_radial_thickness

        self._blanket_rear_wall_start_radius = self._blanket_end_radius
        self._blanket_read_wall_end_radius = (
            self._blanket_rear_wall_start_radius +
            self.blanket_rear_wall_radial_thickness)

    def make_vertical_build(self, shapes_or_components):

        # this is the vertical build sequence, components build on each other in
        # a similar manner to the radial build

        self._firstwall_start_height = (
            self._plasma.high_point[1] + self.outer_plasma_gap_radial_thickness
        )
        self._firstwall_end_height = self._firstwall_start_height + \
            self.firstwall_radial_thickness

        self._blanket_start_height = self._firstwall_end_height
        self._blanket_end_height = self._blanket_start_height + self.blanket_radial_thickness

        self._blanket_rear_wall_start_height = self._blanket_end_height
        self._blanket_rear_wall_end_height = (
            self._blanket_rear_wall_start_height +
            self.blanket_rear_wall_radial_thickness)

        self._tf_coil_height = self._blanket_rear_wall_end_height
        self._center_column_shield_height = self._blanket_rear_wall_end_height * 2

        if (
            self.pf_coil_vertical_thicknesses is not None
            and self.pf_coil_radial_thicknesses is not None
            and self.pf_coil_to_rear_blanket_radial_gap is not None
        ):
            self._number_of_pf_coils = len(self.pf_coil_vertical_thicknesses)

            y_position_step = (
                2
                * (
                    self._blanket_rear_wall_end_height
                    + self.pf_coil_to_rear_blanket_radial_gap
                )
            ) / (self._number_of_pf_coils + 1)

            self._pf_coils_y_values = []
            self._pf_coils_x_values = []
            # adds in coils with equal spacing strategy, should be updated to
            # allow user positions
            for i in range(self._number_of_pf_coils):
                y_value = (
                    self._blanket_rear_wall_end_height
                    + self.pf_coil_to_rear_blanket_radial_gap
                    - y_position_step * (i + 1)
                )
                x_value = (
                    self._blanket_read_wall_end_radius
                    + self.pf_coil_to_rear_blanket_radial_gap
                    + 0.5 * self.pf_coil_radial_thicknesses[i]
                )
                self._pf_coils_y_values.append(y_value)
                self._pf_coils_x_values.append(x_value)

            self._pf_coil_start_radius = (
                self._blanket_read_wall_end_radius +
                self.pf_coil_to_rear_blanket_radial_gap)
            self._pf_coil_end_radius = self._pf_coil_start_radius + max(
                self.pf_coil_radial_thicknesses
            )

            if (
                self.pf_coil_to_tf_coil_radial_gap is not None
                and self.outboard_tf_coil_radial_thickness is not None
            ):
                self._tf_coil_start_radius = (
                    self._pf_coil_end_radius +
                    self.pf_coil_to_rear_blanket_radial_gap)
                self._tf_coil_end_radius = (
                    self._tf_coil_start_radius +
                    self.outboard_tf_coil_radial_thickness)

    def make_inboard_tf_coils(self, shapes_or_components):

        # makes a large cylinder that is used to cut the TF coils when the
        # rotation angle is less than 360
        if self.rotation_angle < 360:
            max_high = 3 * self._center_column_shield_height
            max_width = 3 * self._blanket_read_wall_end_radius
            self._cutting_slice = paramak.RotateStraightShape(
                points=[
                    (0, max_high),
                    (max_width, max_high),
                    (max_width, -max_high),
                    (0, -max_high),
                ],
                rotation_angle=360 - self.rotation_angle,
                azimuth_placement_angle=360 - self.rotation_angle,
            )
        else:
            self._cutting_slice = None

        self._inboard_tf_coils = paramak.CenterColumnShieldCylinder(
            height=self._tf_coil_height * 2,
            inner_radius=self._inboard_tf_coils_start_radius,
            outer_radius=self._inboard_tf_coils_end_radius,
            rotation_angle=self.rotation_angle,
            # color=centre_column_color,
            stp_filename="inboard_tf_coils.stp",
            stl_filename="inboard_tf_coils.stl",
            name="inboard_tf_coils",
            material_tag="inboard_tf_coils_mat",
        )
        shapes_or_components.append(self._inboard_tf_coils)

    def make_center_column_shield(self, shapes_or_components):

        self._center_column_shield = paramak.CenterColumnShieldCylinder(
            height=self._center_column_shield_height,
            inner_radius=self._center_column_shield_start_radius,
            outer_radius=self._center_column_shield_end_radius,
            rotation_angle=self.rotation_angle,
            # color=centre_column_color,
            stp_filename="center_column_shield.stp",
            stl_filename="center_column_shield.stl",
            name="center_column_shield",
            material_tag="center_column_shield_mat",
        )
        shapes_or_components.append(self._center_column_shield)

    def make_blanket_and_firstwall(self, shapes_or_components):

        self._extra_blanket_upper = paramak.RotateStraightShape(
            points=[
                (self._center_column_shield_end_radius, self._blanket_start_height),
                (self._center_column_shield_end_radius, self._blanket_end_height),
                (self._plasma.high_point[0], self._blanket_end_height),
                (self._plasma.high_point[0], self._blanket_start_height),
            ],
            rotation_angle=self.rotation_angle,
        )

        self._extra_firstwall_upper = paramak.RotateStraightShape(
            points=[
                (self._center_column_shield_end_radius, self._firstwall_start_height),
                (self._center_column_shield_end_radius, self._firstwall_end_height),
                (self._plasma.high_point[0], self._firstwall_end_height),
                (self._plasma.high_point[0], self._firstwall_start_height),
            ],
            rotation_angle=self.rotation_angle,
        )

        self._extra_blanket_rear_wall_upper = paramak.RotateStraightShape(
            points=[
                (self._center_column_shield_end_radius, self._blanket_rear_wall_start_height),
                (self._center_column_shield_end_radius, self._blanket_rear_wall_end_height),
                (self._plasma.high_point[0], self._blanket_rear_wall_end_height),
                (self._plasma.high_point[0], self._blanket_rear_wall_start_height),
            ],
            rotation_angle=self.rotation_angle,
        )

        self._extra_blanket_lower = paramak.RotateStraightShape(
            points=[
                (self._center_column_shield_end_radius, -self._blanket_start_height),
                (self._center_column_shield_end_radius, -self._blanket_end_height),
                (self._plasma.high_point[0], -self._blanket_end_height),
                (self._plasma.high_point[0], -self._blanket_start_height),
            ],
            rotation_angle=self.rotation_angle,
        )

        self._extra_firstwall_lower = paramak.RotateStraightShape(
            points=[
                (self._center_column_shield_end_radius, -self._firstwall_start_height),
                (self._center_column_shield_end_radius, -self._firstwall_end_height),
                (self._plasma.high_point[0], -self._firstwall_end_height),
                (self._plasma.high_point[0], -self._firstwall_start_height),
            ],
            rotation_angle=self.rotation_angle,
        )

        self._extra_blanket_rear_wall_lower = paramak.RotateStraightShape(
            points=[
                (self._center_column_shield_end_radius, -self._blanket_rear_wall_start_height),
                (self._center_column_shield_end_radius, -self._blanket_rear_wall_end_height),
                (self._plasma.high_point[0], -self._blanket_rear_wall_end_height),
                (self._plasma.high_point[0], -self._blanket_rear_wall_start_height),
            ],
            rotation_angle=self.rotation_angle,
        )

        self._firstwall = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(self._firstwall_start_radius, 0),
            inner_upper_point=(self._plasma.high_point[0], self._firstwall_start_height),
            inner_lower_point=(self._plasma.low_point[0], -self._firstwall_start_height),
            thickness=self.firstwall_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename="firstwall.stp",
            stl_filename="firstwall.stl",
            name="firstwall",
            material_tag="firstwall_mat",
            union=[self._extra_firstwall_upper, self._extra_firstwall_lower],
        )

        self._blanket = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(self._blanket_start_radius, 0),
            inner_upper_point=(self._plasma.high_point[0], self._blanket_start_height),
            inner_lower_point=(self._plasma.low_point[0], -self._blanket_start_height),
            thickness=self.blanket_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename="blanket.stp",
            stl_filename="blanket.stl",
            name="blanket",
            material_tag="blanket_mat",
            union=[self._extra_blanket_upper, self._extra_blanket_lower],
        )

        self._blanket_rear_casing = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(self._blanket_rear_wall_start_radius, 0),
            inner_upper_point=(self._plasma.high_point[0], self._blanket_rear_wall_start_height),
            inner_lower_point=(self._plasma.low_point[0], -self._blanket_rear_wall_start_height),
            thickness=self.blanket_rear_wall_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename="blanket_rear_wall.stp",
            stl_filename="blanket_rear_wall.stl",
            name="blanket_rear_wall",
            material_tag="blanket_rear_wall_mat",
            union=[self._extra_blanket_rear_wall_upper, self._extra_blanket_rear_wall_lower],
        )

    def make_divertor(self, shapes_or_components):
        # used as an intersect when making the divertor
        self._blanket_fw_rear_wall_envelope = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(self._firstwall_start_radius, 0),
            inner_upper_point=(self._plasma.high_point[0], self._firstwall_start_height),
            inner_lower_point=(self._plasma.low_point[0], -self._firstwall_start_height),
            thickness=self.firstwall_radial_thickness
            + self.blanket_radial_thickness
            + self.blanket_rear_wall_radial_thickness,
            rotation_angle=self.rotation_angle,
            union=[
                self._extra_blanket_upper,
                self._extra_firstwall_upper,
                self._extra_blanket_rear_wall_upper,
                self._extra_blanket_lower,
                self._extra_firstwall_lower,
                self._extra_blanket_rear_wall_lower,
            ],
            stp_filename="test.stp",
        )

        self._divertor = paramak.CenterColumnShieldCylinder(
            height=self._blanket_rear_wall_end_height * 2,
            inner_radius=self._divertor_start_radius,
            outer_radius=self._divertor_end_radius,
            intersect=self._blanket_fw_rear_wall_envelope,
            stp_filename="divertor.stp",
            name="divertor",
            material_tag="divertor_mat",
            rotation_angle=self.rotation_angle
        )
        shapes_or_components.append(self._divertor)

    def make_component_cuts(self, shapes_or_components):

        self._firstwall.solid = self._firstwall.solid.cut(self._divertor.solid)
        self._blanket.solid = self._blanket.solid.cut(self._divertor.solid)
        self._blanket_rear_casing.solid = self._blanket_rear_casing.solid.cut(
            self._divertor.solid)
        shapes_or_components.append(self._firstwall)
        shapes_or_components.append(self._blanket)
        shapes_or_components.append(self._blanket_rear_casing)

        if (
            self.pf_coil_vertical_thicknesses is not None
            and self.pf_coil_radial_thicknesses is not None
            and self.pf_coil_to_rear_blanket_radial_gap is not None
        ):

            for i, (rt, vt, y_value, x_value) in enumerate(
                zip(
                    self.pf_coil_radial_thicknesses,
                    self.pf_coil_vertical_thicknesses,
                    self._pf_coils_y_values,
                    self._pf_coils_x_values,
                )
            ):

                self._pf_coil = paramak.PoloidalFieldCoil(
                    width=rt,
                    height=vt,
                    center_point=(x_value, y_value),
                    rotation_angle=self.rotation_angle,
                    stp_filename="pf_coil_" + str(i) + ".stp",
                    stl_filename="pf_coil_" + str(i) + ".stl",
                    name="pf_coil",
                    material_tag="pf_coil_mat",
                )
                shapes_or_components.append(self._pf_coil)

            if (
                self.pf_coil_to_tf_coil_radial_gap is not None
                and self.outboard_tf_coil_radial_thickness is not None
            ):
                self._tf_coil = paramak.ToroidalFieldCoilRectangle(
                    inner_upper_point=(self._inboard_tf_coils_start_radius, self._tf_coil_height),
                    inner_lower_point=(self._inboard_tf_coils_start_radius, -self._tf_coil_height),
                    inner_mid_point=(self._tf_coil_start_radius, 0),
                    thickness=self.outboard_tf_coil_radial_thickness,
                    number_of_coils=self.number_of_tf_coils,
                    distance=self.outboard_tf_coil_poloidal_thickness,
                    stp_filename="tf_coil.stp",
                    name="tf_coil",
                    material_tag="tf_coil_mat",
                    stl_filename="tf_coil.stl",
                    cut=self._cutting_slice,
                )

                shapes_or_components.append(self._tf_coil)
