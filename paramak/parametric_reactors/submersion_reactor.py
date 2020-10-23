
import warnings

import cadquery as cq

import paramak


class SubmersionTokamak(paramak.Reactor):
    """Creates geometry for a simple submersion reactor including a
    plasma, cylindrical center column shielding, square toroidal field
    coils. There is an inboard breeder blanket on this ball reactor.

    Arguments:
        inner_bore_radial_thickness (float): the radial thickness of the
            inner bore (cm)
        inboard_tf_leg_radial_thickness (float): the radial thickness of
            the inner leg of the toroidal field coils (cm)
        center_column_shield_radial_thickness (float): the radial thickness
            of the center column shield (cm)
        inboard_blanket_radial_thickness (float): the radial thickness of
            the inboard blanket (cm)
        firstwall_radial_thickness (float): the radial thickness of the
            first wall (cm)
        inner_plasma_gap_radial_thickness (float): the radial thickness of
            the inboard gap between the plasma and the center column shield
            (cm)
        plasma_radial_thickness (float): the radial thickness of the plasma
            (cm)
        divertor_radial_thickness (float): the radial thickness of the
            divertors (cm)
        support_radial_thickness (float): the radial thickness of the upper
            and lower supports (cm)
        outer_plasma_gap_radial_thickness (float): the radial thickness of
            the outboard gap between the plasma and the first wall (cm)
        outboard_blanket_radial_thickness (float): the radial thickness of
            the blanket (cm)
        blanket_rear_wall_radial_thickness (float): the radial thickness of
            the rear wall of the blanket (cm)
        plasma_high_point (tuple of 2 floats): the (x,z) coordinate value of
            the top of the plasma (cm)
        number_of_tf_coils (int, optional): the number of tf coils. Defaults
            to 16.
        rotation_angle (float, optional): the angle of the sector that is
            desired. Defaults to 360.0.
        outboard_tf_coil_radial_thickness (float, optional): the radial
            thickness of the toroidal field coil. Defaults to None.
        tf_coil_to_rear_blanket_radial_gap (float, optional): the radial
            distance between the rear of the blanket and the toroidal field
            coil. Defaults to None.
        outboard_tf_coil_poloidal_thickness (float, optional): the vertical
            thickness of each poloidal field coil. Defaults to None.
        pf_coil_vertical_thicknesses (list of floats, optional): the vertical
            thickness of each poloidal field coil. Defaults to None.
        pf_coil_radial_thicknesses (list of floats, optional): the radial
            thickness of  each poloidal field coil. Defaults to None.
        pf_coil_to_tf_coil_radial_gap (float, optional): the radial distance
            between the rear of the poloidal field coil and the toroidal field
            coil. Defaults to None.
    """

    def __init__(
        self,
        inner_bore_radial_thickness,
        inboard_tf_leg_radial_thickness,
        center_column_shield_radial_thickness,
        inboard_blanket_radial_thickness,
        firstwall_radial_thickness,
        inner_plasma_gap_radial_thickness,
        plasma_radial_thickness,
        divertor_radial_thickness,
        support_radial_thickness,
        outer_plasma_gap_radial_thickness,
        outboard_blanket_radial_thickness,
        blanket_rear_wall_radial_thickness,
        plasma_high_point,
        number_of_tf_coils=16,
        rotation_angle=360.0,
        outboard_tf_coil_radial_thickness=None,
        tf_coil_to_rear_blanket_radial_gap=None,
        outboard_tf_coil_poloidal_thickness=None,
        pf_coil_vertical_thicknesses=None,
        pf_coil_radial_thicknesses=None,
        pf_coil_to_tf_coil_radial_gap=None,
    ):

        super().__init__([])

        self.inner_bore_radial_thickness = inner_bore_radial_thickness
        self.inboard_tf_leg_radial_thickness = inboard_tf_leg_radial_thickness
        self.center_column_shield_radial_thickness = (
            center_column_shield_radial_thickness
        )
        self.inboard_blanket_radial_thickness = inboard_blanket_radial_thickness
        self.firstwall_radial_thickness = firstwall_radial_thickness
        self.inner_plasma_gap_radial_thickness = inner_plasma_gap_radial_thickness
        self.plasma_radial_thickness = plasma_radial_thickness
        self.outer_plasma_gap_radial_thickness = outer_plasma_gap_radial_thickness
        self.outboard_blanket_radial_thickness = outboard_blanket_radial_thickness
        self.blanket_rear_wall_radial_thickness = blanket_rear_wall_radial_thickness
        self.pf_coil_radial_thicknesses = pf_coil_radial_thicknesses
        self.pf_coil_to_tf_coil_radial_gap = pf_coil_to_tf_coil_radial_gap
        self.outboard_tf_coil_radial_thickness = outboard_tf_coil_radial_thickness
        self.outboard_tf_coil_poloidal_thickness = outboard_tf_coil_poloidal_thickness
        self.divertor_radial_thickness = divertor_radial_thickness
        self.support_radial_thickness = support_radial_thickness
        self.plasma_high_point = plasma_high_point
        self.tf_coil_to_rear_blanket_radial_gap = tf_coil_to_rear_blanket_radial_gap
        self.pf_coil_vertical_thicknesses = pf_coil_vertical_thicknesses
        self.number_of_tf_coils = number_of_tf_coils
        self.rotation_angle = rotation_angle

        # these are set later by the plasma when it is created
        self.major_radius = None
        self.minor_radius = None
        self.elongation = None
        self.triangularity = None

        self.shapes_and_components = []

        self.create_solids()

    def create_solids(self):
        """Creates a 3d solids for each component.

           Returns:
              A list of CadQuery solids: A list of 3D solid volumes

        """

        self._rotation_angle_check()
        self._make_radial_build()
        self._make_vertical_build()
        self._make_inboard_tf_coils()
        self._make_center_column_shield()
        self._make_plasma()
        self._make_inboard_blanket_and_firstwall()
        self._make_divertor()
        self._make_outboard_blanket()
        self._make_supports()
        self._make_component_cuts()

        return self.shapes_and_components

    def _rotation_angle_check(self):

        if self.rotation_angle == 360:
            warnings.warn(
                "360 degree rotation may result in a Standard_ConstructionError or AttributeError",
                UserWarning)

    def _make_radial_build(self):

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

        self._inboard_blanket_start_radius = self._center_column_shield_end_radius
        self._inboard_blanket_end_radius = (
            self._inboard_blanket_start_radius +
            self.inboard_blanket_radial_thickness)

        self._inboard_firstwall_start_radius = self._inboard_blanket_end_radius
        self._inboard_firstwall_end_radius = (
            self._inboard_firstwall_start_radius +
            self.firstwall_radial_thickness)

        self._inner_plasma_gap_start_radius = self._inboard_firstwall_end_radius
        self._inner_plasma_gap_end_radius = (
            self._inner_plasma_gap_start_radius +
            self.inner_plasma_gap_radial_thickness)

        self._plasma_start_radius = self._inner_plasma_gap_end_radius
        self._plasma_end_radius = self._plasma_start_radius + self.plasma_radial_thickness

        self._outer_plasma_gap_start_radius = self._plasma_end_radius
        self._outer_plasma_gap_end_radius = (
            self._outer_plasma_gap_start_radius +
            self.outer_plasma_gap_radial_thickness)

        self._outboard_firstwall_start_radius = self._outer_plasma_gap_end_radius
        self._outboard_firstwall_end_radius = (
            self._outboard_firstwall_start_radius +
            self.firstwall_radial_thickness)

        self._outboard_blanket_start_radius = self._outboard_firstwall_end_radius
        self._outboard_blanket_end_radius = (
            self._outboard_blanket_start_radius +
            self.outboard_blanket_radial_thickness)

        self._blanket_rear_wall_start_radius = self._outboard_blanket_end_radius
        self._blanket_rear_wall_end_radius = (
            self._blanket_rear_wall_start_radius +
            self.blanket_rear_wall_radial_thickness)

        self._tf_info_provided = False
        if (
            self.outboard_tf_coil_radial_thickness is not None
            and self.tf_coil_to_rear_blanket_radial_gap is not None
            and self.outboard_tf_coil_poloidal_thickness is not None
        ):
            self._tf_info_provided = True
            self._outboard_tf_coil_start_radius = (
                self._blanket_rear_wall_end_radius +
                self.tf_coil_to_rear_blanket_radial_gap)
            self._outboard_tf_coil_end_radius = (
                self._outboard_tf_coil_start_radius +
                self.outboard_tf_coil_radial_thickness)

        self._pf_info_provided = False
        if (
            self.pf_coil_vertical_thicknesses is not None
            and self.pf_coil_radial_thicknesses is not None
            and self.pf_coil_to_tf_coil_radial_gap is not None
        ):
            self._pf_info_provided = True

        self._divertor_start_radius = (
            self.plasma_high_point[0] - 0.5 * self.divertor_radial_thickness
        )
        self._divertor_end_radius = (
            self.plasma_high_point[0] + 0.5 * self.divertor_radial_thickness
        )

        self._support_start_radius = (
            self.plasma_high_point[0] - 0.5 * self.support_radial_thickness
        )
        self._support_end_radius = (
            self.plasma_high_point[0] + 0.5 * self.support_radial_thickness
        )

    def _make_vertical_build(self):

        # this is the vertical build sequence, componets build on each other in
        # a similar manner to the radial build

        self._plasma_start_height = 0
        self._plasma_end_height = self._plasma_start_height + \
            self.plasma_high_point[1]

        self._plasma_to_divertor_gap_start_height = self._plasma_end_height
        self._plasma_to_divertor_gap_end_height = (
            self._plasma_to_divertor_gap_start_height +
            self.outer_plasma_gap_radial_thickness)

        # the firstwall is cut by the divertor but uses the same control points
        self._firstwall_start_height = self._plasma_to_divertor_gap_end_height
        self._firstwall_end_height = self._firstwall_start_height + \
            self.firstwall_radial_thickness

        self._blanket_start_height = self._firstwall_end_height
        self._blanket_end_height = (
            self._blanket_start_height + self.outboard_blanket_radial_thickness
        )

        self._blanket_rear_wall_start_height = self._blanket_end_height
        self._blanket_rear_wall_end_height = (
            self._blanket_rear_wall_start_height +
            self.blanket_rear_wall_radial_thickness)

        if self._tf_info_provided and self._pf_info_provided:
            self._number_of_pf_coils = len(self.pf_coil_vertical_thicknesses)

            y_position_step = (2 * self._blanket_rear_wall_end_height) / (
                self._number_of_pf_coils + 1
            )

            self._pf_coils_xy_values = []
            # adds in coils with equal spacing strategy, should be updated to
            # allow user positions
            for i in range(self._number_of_pf_coils):
                y_value = (
                    self._blanket_rear_wall_end_height
                    + self.pf_coil_to_tf_coil_radial_gap
                    - y_position_step * (i + 1)
                )
                x_value = (
                    self._outboard_tf_coil_end_radius
                    + self.pf_coil_to_tf_coil_radial_gap
                    + 0.5 * self.pf_coil_radial_thicknesses[i]
                )
                self._pf_coils_xy_values.append((x_value, y_value))

            self._pf_coil_start_radius = (
                self._outboard_tf_coil_end_radius +
                self.pf_coil_to_tf_coil_radial_gap)
            self._pf_coil_end_radius = self._pf_coil_start_radius + max(
                self.pf_coil_radial_thicknesses
            )

        # raises an error if the plasma high point is not above part of the
        # plasma
        if self.plasma_high_point[0] < self._plasma_start_radius:
            raise ValueError(
                "The first value in plasma high_point is too small, it should be larger than",
                self._plasma_start_radius,
            )
        if self.plasma_high_point[0] > self._plasma_end_radius:
            raise ValueError(
                "The first value in plasma high_point is too large, it should be smaller than",
                self._plasma_end_radius,
            )

    def _make_inboard_tf_coils(self):

        # self.shapes_and_components.append(inboard_tf_coils)
        self._inboard_tf_coils = paramak.CenterColumnShieldCylinder(
            height=self._blanket_rear_wall_end_height * 2,
            inner_radius=self._inboard_tf_coils_start_radius,
            outer_radius=self._inboard_tf_coils_end_radius,
            rotation_angle=self.rotation_angle,
            stp_filename="inboard_tf_coils.stp",
            stl_filename="inboard_tf_coils.stl",
            name="inboard_tf_coils",
            material_tag="inboard_tf_coils_mat",
        )
        self.shapes_and_components.append(self._inboard_tf_coils)

    def _make_center_column_shield(self):

        self._center_column_shield = paramak.CenterColumnShieldCylinder(
            height=self._blanket_rear_wall_end_height * 2,
            inner_radius=self._center_column_shield_start_radius,
            outer_radius=self._center_column_shield_end_radius,
            rotation_angle=self.rotation_angle,
            stp_filename="center_column_shield.stp",
            stl_filename="center_column_shield.stl",
            name="center_column_shield",
            material_tag="center_column_shield_mat",
        )
        self.shapes_and_components.append(self._center_column_shield)

    def _make_plasma(self):

        self._plasma = paramak.PlasmaFromPoints(
            outer_equatorial_x_point=self._plasma_end_radius,
            inner_equatorial_x_point=self._plasma_start_radius,
            high_point=self.plasma_high_point,
            rotation_angle=self.rotation_angle,
        )

        self.major_radius = self._plasma.major_radius
        self.minor_radius = self._plasma.minor_radius
        self.elongation = self._plasma.elongation
        self.triangularity = self._plasma.triangularity

        self.shapes_and_components.append(self._plasma)

    def _make_inboard_blanket_and_firstwall(self):

        # this is used to cut the inboard blanket and then fused / unioned with
        # the firstwall
        self._inboard_firstwall = paramak.BlanketFP(
            plasma=self._plasma,
            offset_from_plasma=self.inner_plasma_gap_radial_thickness,
            start_angle=90,
            stop_angle=270,
            thickness=self.firstwall_radial_thickness,
            rotation_angle=self.rotation_angle,
        )

        self._inboard_blanket = paramak.CenterColumnShieldCylinder(
            height=self._blanket_end_height * 2,
            inner_radius=self._inboard_blanket_start_radius,
            outer_radius=max([item[0] for item in self._inboard_firstwall.points]),
            rotation_angle=self.rotation_angle,
            cut=self._inboard_firstwall,
        )

        # this takes a single solid from a compound of solids by finding the
        # solid nearest to a point
        self._inboard_blanket.solid = self._inboard_blanket.solid.solids(
            cq.selectors.NearestToPointSelector((0, 0, 0))
        )

        self._firstwall = paramak.BlanketFP(
            plasma=self._plasma,
            offset_from_plasma=self.outer_plasma_gap_radial_thickness,
            start_angle=90,
            stop_angle=-90,
            thickness=self.firstwall_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename="outboard_firstwall.stp",
            stl_filename="outboard_firstwall.stl",
            name="outboard_firstwall",
            material_tag="firstwall_mat",
            union=self._inboard_firstwall,
        )

    def _make_divertor(self):

        self._divertor = paramak.CenterColumnShieldCylinder(
            height=self._blanket_rear_wall_end_height * 2,
            inner_radius=self._divertor_start_radius,
            outer_radius=self._divertor_end_radius,
            rotation_angle=self.rotation_angle,
            stp_filename="divertor.stp",
            stl_filename="divertor.stl",
            name="divertor",
            material_tag="divertor_mat",
            intersect=self._firstwall,
        )
        self.shapes_and_components.append(self._divertor)

    def _make_outboard_blanket(self):

        # this is the outboard fused /unioned with the inboard blanket

        self._blanket = paramak.BlanketFP(
            plasma=self._plasma,
            start_angle=90,
            stop_angle=-90,
            offset_from_plasma=self.outer_plasma_gap_radial_thickness
            + self.firstwall_radial_thickness,
            thickness=self.outboard_blanket_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename="blanket.stp",
            stl_filename="blanket.stl",
            name="blanket",
            material_tag="blanket_mat",
            union=self._inboard_blanket,
        )

    def _make_supports(self):

        self._supports = paramak.CenterColumnShieldCylinder(
            height=self._blanket_rear_wall_end_height * 2,
            inner_radius=self._support_start_radius,
            outer_radius=self._support_end_radius,
            rotation_angle=self.rotation_angle,
            stp_filename="supports.stp",
            stl_filename="supports.stl",
            name="supports",
            material_tag="supports_mat",
            intersect=self._blanket,
        )
        self.shapes_and_components.append(self._supports)

    def _make_component_cuts(self):

        # the divertor is cut away then the firstwall can be added to the
        # reactor using CQ operations
        self._firstwall.solid = self._firstwall.solid.cut(self._divertor.solid)
        self.shapes_and_components.append(self._firstwall)

        # cutting the supports away from the blanket
        self._blanket.solid = self._blanket.solid.cut(self._supports.solid)
        self.shapes_and_components.append(self._blanket)

        self._outboard_rear_blanket_wall_upper = paramak.RotateStraightShape(
            points=[
                (self._center_column_shield_end_radius, self._blanket_rear_wall_start_height),
                (self._center_column_shield_end_radius, self._blanket_rear_wall_end_height),
                (
                    max([item[0] for item in self._inboard_firstwall.points]),
                    self._blanket_rear_wall_end_height,
                ),
                (
                    max([item[0] for item in self._inboard_firstwall.points]),
                    self._blanket_rear_wall_start_height,
                ),
            ],
            rotation_angle=self.rotation_angle,
        )

        self._outboard_rear_blanket_wall_lower = paramak.RotateStraightShape(
            points=[
                (self._center_column_shield_end_radius, -self._blanket_rear_wall_start_height),
                (self._center_column_shield_end_radius, -self._blanket_rear_wall_end_height),
                (
                    max([item[0] for item in self._inboard_firstwall.points]),
                    -self._blanket_rear_wall_end_height,
                ),
                (
                    max([item[0] for item in self._inboard_firstwall.points]),
                    -self._blanket_rear_wall_start_height,
                ),
            ],
            rotation_angle=self.rotation_angle,
        )

        self._outboard_rear_blanket_wall = paramak.BlanketFP(
            plasma=self._plasma,
            start_angle=90,
            stop_angle=-90,
            offset_from_plasma=self.outer_plasma_gap_radial_thickness +
            self.firstwall_radial_thickness +
            self.outboard_blanket_radial_thickness,
            thickness=self.blanket_rear_wall_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename="outboard_rear_blanket_wall.stp",
            stl_filename="outboard_rear_blanket_wall.stl",
            name="outboard_rear_blanket_wall",
            material_tag="rear_blanket_wall_mat",
            union=[
                self._outboard_rear_blanket_wall_upper,
                self._outboard_rear_blanket_wall_lower],
        )

        self.shapes_and_components.append(self._outboard_rear_blanket_wall)

        if self._tf_info_provided:
            self._tf_coil = paramak.ToroidalFieldCoilRectangle(
                with_inner_leg=False,
                horizontal_start_point=(
                    self._inboard_tf_coils_start_radius,
                    self._blanket_rear_wall_end_height,
                ),
                vertical_mid_point=(self._outboard_tf_coil_start_radius, 0),
                thickness=self.outboard_tf_coil_radial_thickness,
                number_of_coils=self.number_of_tf_coils,
                distance=self.outboard_tf_coil_poloidal_thickness,
                stp_filename="outboard_tf_coil.stp",
                stl_filename="outboard_tf_coil.stl",
            )
            self.shapes_and_components.append(self._tf_coil)

            if self._pf_info_provided:

                self._pf_coil = paramak.PoloidalFieldCoilSet(
                    heights=self.pf_coil_vertical_thicknesses,
                    widths=self.pf_coil_radial_thicknesses,
                    center_points=self._pf_coils_xy_values,
                    rotation_angle=self.rotation_angle,
                    stp_filename='pf_coils.stp',
                    name="pf_coil",
                    material_tag="pf_coil_mat",
                )

                self.shapes_and_components.append(self._pf_coil)
