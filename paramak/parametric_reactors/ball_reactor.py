
import warnings

import paramak


class BallReactor(paramak.Reactor):
    """Creates geometry for a simple ball reactor including a plasma,
    cylindrical center column shielding, square toroidal field coils.
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
            (cm), this fills the gap between the center column shield and
            blanket
        inner_plasma_gap_radial_thickness (float): the radial thickness of the
            inboard gap between the plasma and the center column shield (cm)
        plasma_radial_thickness (float): the radial thickness of the plasma
        outer_plasma_gap_radial_thickness (float): the radial thickness of the
            outboard gap between the plasma and firstwall (cm)
        firstwall_radial_thickness (float): the radial thickness of the first
            wall (cm)
        blanket_radial_thickness (float): the radial thickness of the blanket
            (cm)
        blanket_rear_wall_radial_thickness (float): the radial thickness of the
            rear wall of the blanket (cm)
        elongation (float): the elongation of the plasma
        triangularity (float): the triangularity of the plasma
        number_of_tf_coils (int, optional): the number of tf coils
        pf_coil_to_rear_blanket_radial_gap (float, optional): the radial
            distance between the rear blanket and the closest poloidal field
            coil. Defaults to None.
        pf_coil_radial_thicknesses (list of floats, optional): the radial
            thickness of each poloidal field coil. Defaults to None.
        pf_coil_vertical_thicknesses (list of floats, optional): the vertical
            thickness of each poloidal field coil. Defaults to None.
        pf_coil_to_tf_coil_radial_gap (float, optional): the radial distance
            between the rear of the poloidal field coil and the toroidal field
            coil. Defaults to None.
        outboard_tf_coil_radial_thickness (float, optional): the radial
            thickness of the toroidal field coil. Defaults to None.
        outboard_tf_coil_poloidal_thickness (float, optional): the poloidal
            thickness of the toroidal field coil. Defaults to None.
        rotation_angle (float): the angle of the sector that is desired.
            Defaults to 360.0.
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
        number_of_tf_coils=12,
        pf_coil_to_rear_blanket_radial_gap=None,
        pf_coil_radial_thicknesses=None,
        pf_coil_vertical_thicknesses=None,
        pf_coil_to_tf_coil_radial_gap=None,
        outboard_tf_coil_radial_thickness=None,
        outboard_tf_coil_poloidal_thickness=None,
        rotation_angle=360.0,
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
        # this helps avoid the plasma overlapping the center column and other
        # components

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

        self.shapes_and_components = []

        self.create_solids()

    def create_solids(self):
        """Creates a 3d solids for each component.

           Returns:
              A list of CadQuery solids: A list of 3D solid volumes

        """
        self._rotation_angle_check()
        self._make_plasma()
        self._make_radial_build()
        self._make_vertical_build()
        self._make_inboard_tf_coils()
        self._make_center_column_shield()
        self._make_blankets_layers()
        self._make_divertor()
        self._make_component_cuts()

        return self.shapes_and_components

    def _rotation_angle_check(self):

        if self.rotation_angle == 360:
            warnings.warn(
                "360 degree rotation may result in a Standard_ConstructionError or AttributeError",
                UserWarning)

    def _make_plasma(self):

        plasma = paramak.Plasma(
            major_radius=self.major_radius,
            minor_radius=self.minor_radius,
            elongation=self.elongation,
            triangularity=self.triangularity,
            rotation_angle=self.rotation_angle,
            stl_filename="plasma.stl",
        )
        plasma.create_solid()

        self.shapes_and_components.append(plasma)

        self._plasma = plasma

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

    def _make_vertical_build(self):

        # this is the vertical build sequence, components build on each other in
        # a similar manner to the radial build

        self.plasma_gap_vertical_thickness = self.outer_plasma_gap_radial_thickness

        self._firstwall_start_height = (
            self._plasma.high_point[1] + self.plasma_gap_vertical_thickness
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

            self._pf_coils_xy_values = []
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
                self._pf_coils_xy_values.append((x_value, y_value))

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

    def _make_inboard_tf_coils(self):

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
        self.shapes_and_components.append(self._inboard_tf_coils)

    def _make_center_column_shield(self):

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
        self.shapes_and_components.append(self._center_column_shield)

    def _make_blankets_layers(self):

        center_column_cutter = paramak.CenterColumnShieldCylinder(
            height=self._center_column_shield_height * 1.5,  # extra 0.5 to ensure overlap,
            inner_radius=0,
            outer_radius=self._center_column_shield_end_radius,
            rotation_angle=360
        )

        self._firstwall = paramak.BlanketFP(
            plasma=self._plasma,
            thickness=self.firstwall_radial_thickness,
            offset_from_plasma=[
                self.inner_plasma_gap_radial_thickness,
                self.plasma_gap_vertical_thickness,
                self.outer_plasma_gap_radial_thickness,
                self.plasma_gap_vertical_thickness,
                self.inner_plasma_gap_radial_thickness],
            start_angle=-179,
            stop_angle=179,
            rotation_angle=self.rotation_angle,
            stp_filename="firstwall.stp",
            cut=center_column_cutter
        )

        self._blanket = paramak.BlanketFP(
            plasma=self._plasma,
            thickness=self.blanket_radial_thickness,
            offset_from_plasma=[
                self.inner_plasma_gap_radial_thickness +
                self.firstwall_radial_thickness,
                self.plasma_gap_vertical_thickness +
                self.firstwall_radial_thickness,
                self.outer_plasma_gap_radial_thickness +
                self.firstwall_radial_thickness,
                self.plasma_gap_vertical_thickness +
                self.firstwall_radial_thickness,
                self.inner_plasma_gap_radial_thickness +
                self.firstwall_radial_thickness],
            start_angle=-
            179,
            stop_angle=179,
            rotation_angle=self.rotation_angle,
            stp_filename="blanket.stp",
            cut=center_column_cutter)

        self._blanket_rear_wall = paramak.BlanketFP(
            plasma=self._plasma,
            thickness=self.blanket_rear_wall_radial_thickness,
            offset_from_plasma=[
                self.inner_plasma_gap_radial_thickness +
                self.firstwall_radial_thickness +
                self.blanket_radial_thickness,
                self.plasma_gap_vertical_thickness +
                self.firstwall_radial_thickness +
                self.blanket_radial_thickness,
                self.outer_plasma_gap_radial_thickness +
                self.firstwall_radial_thickness +
                self.blanket_radial_thickness,
                self.plasma_gap_vertical_thickness +
                self.firstwall_radial_thickness +
                self.blanket_radial_thickness,
                self.inner_plasma_gap_radial_thickness +
                self.firstwall_radial_thickness +
                self.blanket_radial_thickness],
            start_angle=-
            179,
            stop_angle=179,
            rotation_angle=self.rotation_angle,
            stp_filename="blanket_rear_wall.stp",
            cut=center_column_cutter)

    def _make_divertor(self):

        # # used as an intersect when making the divertor
        self._blanket_fw_rear_wall_envelope = paramak.BlanketFP(
            plasma=self._plasma,
            thickness=self.firstwall_radial_thickness +
            self.blanket_radial_thickness + self.blanket_rear_wall_radial_thickness,
            offset_from_plasma=[
                self.major_radius - self.minor_radius,
                self.plasma_gap_vertical_thickness,
                self.outer_plasma_gap_radial_thickness,
                self.plasma_gap_vertical_thickness,
                # self.inner_plasma_gap_radial_thickness],
                self.major_radius - self.minor_radius],
            start_angle=-179,
            stop_angle=179,
            rotation_angle=self.rotation_angle,
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
        self.shapes_and_components.append(self._divertor)

        blanket_cutter = paramak.CenterColumnShieldCylinder(
            height=self._center_column_shield_height * 1.5,  # extra 0.5 to ensure overlap,
            inner_radius=0,
            outer_radius=self._divertor_end_radius,
            rotation_angle=360
        )

        self._firstwall.solid = self._firstwall.solid.cut(blanket_cutter.solid)
        self._blanket.solid = self._blanket.solid.cut(blanket_cutter.solid)
        self._blanket_rear_wall.solid = self._blanket_rear_wall.solid.cut(
            blanket_cutter.solid)
        self.shapes_and_components.append(self._firstwall)
        self.shapes_and_components.append(self._blanket)
        self.shapes_and_components.append(self._blanket_rear_wall)

    def _make_component_cuts(self):

        if (
            self.pf_coil_vertical_thicknesses is not None
            and self.pf_coil_radial_thicknesses is not None
            and self.pf_coil_to_rear_blanket_radial_gap is not None
        ):

            self._pf_coil = paramak.PoloidalFieldCoilSet(
                heights=self.pf_coil_vertical_thicknesses,
                widths=self.pf_coil_radial_thicknesses,
                center_points=self._pf_coils_xy_values,
                rotation_angle=self.rotation_angle,
                stp_filename='pf_coils.stp',
                stl_filename='pf_coils.stl',
                name="pf_coil",
                material_tag="pf_coil_mat",
            )

            self.shapes_and_components.append(self._pf_coil)

            if (
                self.pf_coil_to_tf_coil_radial_gap is not None
                and self.outboard_tf_coil_radial_thickness is not None
            ):

                self._tf_coil = paramak.ToroidalFieldCoilRectangle(
                    with_inner_leg=False,
                    horizontal_start_point=(
                        self._inboard_tf_coils_start_radius,
                        self._tf_coil_height),
                    vertical_mid_point=(
                        self._tf_coil_start_radius, 0),
                    thickness=self.outboard_tf_coil_radial_thickness,
                    number_of_coils=self.number_of_tf_coils,
                    distance=self.outboard_tf_coil_poloidal_thickness,
                    stp_filename="tf_coil.stp",
                    name="tf_coil",
                    material_tag="tf_coil_mat",
                    stl_filename="tf_coil.stl",
                )

                self.shapes_and_components.append(self._tf_coil)
