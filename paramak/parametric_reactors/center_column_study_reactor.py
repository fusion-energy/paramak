
import warnings

import paramak


class CenterColumnStudyReactor(paramak.Reactor):
    """Creates geometry for a simple reactor that is optimised for carrying
    out parametric studies on the center column shield. Several aspects
    such as outboard magnets are intentionally missing from this reactor
    so that the model runs quickly and only includes components that have a
    significant impact on the center column shielding. This allows the
    neutronics simulations to run quickly and the column design space to be
    explored efficiently.

    Arguments:
        inner_bore_radial_thickness (float): the radial thickness of the
            inner bore (cm)
        inboard_tf_leg_radial_thickness (float): the radial thickness of
            the inner leg of the toroidal field coils (cm)
        center_column_shield_radial_thickness_mid (float): the radial thickness
            of the center column shield at the mid point (cm)
        center_column_shield_radial_thickness_upper (float): the radial
            thickness of the center column shield at the upper point (cm)
        inboard_firstwall_radial_thickness (float): the radial thickness
            of the inboard firstwall (cm)
        divertor_radial_thickness (float): the radial thickness of the divertor
            (cm)
        inner_plasma_gap_radial_thickness (float): the radial thickness of
            the inboard gap between the plasma and the center column shield
            (cm)
        plasma_radial_thickness (float): the radial thickness of the plasma
            (cm)
        outer_plasma_gap_radial_thickness (float): the radial thickness of
            the outboard gap between the plasma and the first wall (cm)
        elongation (float): the elongation of the plasma
        triangularity (float): the triangularity of the plasma
        center_column_arc_vertical_thickness (float): height of the outer
            hyperbolic profile of the center column shield.
        plasma_gap_vertical_thickness (float): the vertical thickness of
            the upper gap between the plasma and the blanket (cm)
        rotation_angle (float): the angle of the sector that is desired.
            Defaults to 360.0.
    """

    def __init__(
        self,
        inner_bore_radial_thickness,
        inboard_tf_leg_radial_thickness,
        center_column_shield_radial_thickness_mid,
        center_column_shield_radial_thickness_upper,
        inboard_firstwall_radial_thickness,
        divertor_radial_thickness,
        inner_plasma_gap_radial_thickness,
        plasma_radial_thickness,
        outer_plasma_gap_radial_thickness,
        center_column_arc_vertical_thickness,
        elongation,
        triangularity,
        plasma_gap_vertical_thickness,
        rotation_angle=360.0,
    ):

        super().__init__([])

        self.method = 'trelis'

        self.inner_bore_radial_thickness = inner_bore_radial_thickness
        self.inboard_tf_leg_radial_thickness = inboard_tf_leg_radial_thickness
        self.center_column_shield_radial_thickness_mid = \
            center_column_shield_radial_thickness_mid
        self.center_column_shield_radial_thickness_upper = \
            center_column_shield_radial_thickness_upper
        self.inboard_firstwall_radial_thickness = \
            inboard_firstwall_radial_thickness
        self.divertor_radial_thickness = divertor_radial_thickness
        self.inner_plasma_gap_radial_thickness = \
            inner_plasma_gap_radial_thickness
        self.plasma_radial_thickness = plasma_radial_thickness
        self.outer_plasma_gap_radial_thickness = \
            outer_plasma_gap_radial_thickness
        self.plasma_gap_vertical_thickness = plasma_gap_vertical_thickness
        self.center_column_arc_vertical_thickness = \
            center_column_arc_vertical_thickness
        self.rotation_angle = rotation_angle
        self.elongation = elongation
        self.triangularity = triangularity

        # sets major radius and minor radius from equatorial_points to allow a
        # radial build this helps avoid the plasma overlapping the center
        # column and other components

        inner_equatorial_point = (
            inner_bore_radial_thickness
            + inboard_tf_leg_radial_thickness
            + center_column_shield_radial_thickness_mid
            + inner_plasma_gap_radial_thickness
        )
        outer_equatorial_point = \
            inner_equatorial_point + plasma_radial_thickness
        self.major_radius = \
            (outer_equatorial_point + inner_equatorial_point) / 2
        self.minor_radius = self.major_radius - inner_equatorial_point

    def create_solids(self):
        """Creates a 3d solids for each component.

           Returns:
              A list of CadQuery solids: A list of 3D solid volumes

        """
        shapes_and_components = []

        self._rotation_angle_check()
        shapes_and_components.append(self._make_plasma())
        self._make_radial_build()
        self._make_vertical_build()
        shapes_and_components.append(self._make_inboard_tf_coils())
        shapes_and_components.append(self._make_center_column_shield())
        shapes_and_components.append(self._make_inboard_firstwall())
        shapes_and_components.append(self._make_outboard_blanket())
        shapes_and_components.append(self._make_divertor())

        self.shapes_and_components = shapes_and_components

    def _rotation_angle_check(self):

        if self.rotation_angle == 360:
            msg = "360 degree rotation may result " + \
                "in a Standard_ConstructionError or AttributeError"
            warnings.warn(msg, UserWarning)

    def _make_plasma(self):

        plasma = paramak.Plasma(
            major_radius=self.major_radius,
            minor_radius=self.minor_radius,
            elongation=self.elongation,
            triangularity=self.triangularity,
            rotation_angle=self.rotation_angle,
        )

        self._plasma = plasma
        return plasma

    def _make_radial_build(self):

        # this is the radial build sequence, where one component stops and
        # another starts

        self._inner_bore_start_radius = 0
        self._inner_bore_end_radius = self._inner_bore_start_radius + \
            self.inner_bore_radial_thickness

        self._inboard_tf_coils_start_radius = self._inner_bore_end_radius
        self._inboard_tf_coils_end_radius = \
            self._inboard_tf_coils_start_radius + \
            self.inboard_tf_leg_radial_thickness

        self._center_column_shield_start_radius = \
            self._inboard_tf_coils_end_radius
        self._center_column_shield_end_radius_upper = \
            self._center_column_shield_start_radius + \
            self.center_column_shield_radial_thickness_upper
        self._center_column_shield_end_radius_mid = \
            self._center_column_shield_start_radius + \
            self.center_column_shield_radial_thickness_mid

        self._inboard_firstwall_start_radius = \
            self._center_column_shield_end_radius_upper
        self._inboard_firstwall_end_radius = \
            self._inboard_firstwall_start_radius + \
            self.inboard_firstwall_radial_thickness

        self._divertor_start_radius = self._inboard_firstwall_end_radius
        self._divertor_end_radius = self._divertor_start_radius + \
            self.divertor_radial_thickness

        self._inner_plasma_gap_start_radius = \
            self._center_column_shield_end_radius_mid + \
            self.inboard_firstwall_radial_thickness

        self._inner_plasma_gap_end_radius = \
            self._inner_plasma_gap_start_radius + \
            self.inner_plasma_gap_radial_thickness

        self._plasma_start_radius = self._inner_plasma_gap_end_radius
        self._plasma_end_radius = \
            self._plasma_start_radius + \
            self.plasma_radial_thickness

        self._outer_plasma_gap_start_radius = self._plasma_end_radius
        self._outer_plasma_gap_end_radius = \
            self._outer_plasma_gap_start_radius + \
            self.outer_plasma_gap_radial_thickness

        self._outboard_blanket_start_radius = self._outer_plasma_gap_end_radius
        self._outboard_blanket_end_radius = \
            self._outboard_blanket_start_radius + 100.

    def _make_vertical_build(self):

        # this is the vertical build sequence, componets build on each other in
        # a similar manner to the radial build

        self._plasma_to_blanket_gap_start_height = self._plasma.high_point[1]
        self._plasma_to_blanket_gap_end_height = \
            self._plasma_to_blanket_gap_start_height + \
            self.plasma_gap_vertical_thickness

        self._blanket_start_height = self._plasma_to_blanket_gap_end_height
        self._blanket_end_height = self._blanket_start_height + 100.

        self._center_column_shield_end_height = self._blanket_end_height
        self._inboard_firstwall_end_height = self._blanket_end_height

    def _make_inboard_tf_coils(self):

        self._inboard_tf_coils = paramak.CenterColumnShieldCylinder(
            height=self._blanket_end_height * 2,
            inner_radius=self._inboard_tf_coils_start_radius,
            outer_radius=self._inboard_tf_coils_end_radius,
            rotation_angle=self.rotation_angle,
            stp_filename="inboard_tf_coils.stp",
            stl_filename="inboard_tf_coils.stl",
            name="inboard_tf_coils",
            material_tag="inboard_tf_coils_mat",
            color=(0., 0., 1.)
        )
        return self._inboard_tf_coils

    def _make_center_column_shield(self):

        self._center_column_shield = \
            paramak.CenterColumnShieldFlatTopHyperbola(
                height=self._center_column_shield_end_height * 2.,
                arc_height=self.center_column_arc_vertical_thickness,
                inner_radius=self._center_column_shield_start_radius,
                mid_radius=self._center_column_shield_end_radius_mid,
                outer_radius=self._center_column_shield_end_radius_upper,
                rotation_angle=self.rotation_angle)
        return self._center_column_shield

    def _make_inboard_firstwall(self):

        self._inboard_firstwall = paramak.InboardFirstwallFCCS(
            central_column_shield=self._center_column_shield,
            thickness=self.inboard_firstwall_radial_thickness,
            rotation_angle=self.rotation_angle)
        return self._inboard_firstwall

    def _make_outboard_blanket(self):

        self._center_column_cutter = paramak.CenterColumnShieldCylinder(
            # extra 1.5 to ensure overlap,
            height=self._inboard_firstwall_end_height * 2.5,
            inner_radius=0,
            outer_radius=self._inboard_firstwall_end_radius,
            rotation_angle=self.rotation_angle
        )

        self._blanket = paramak.BlanketFP(
            plasma=self._plasma,
            thickness=100.,
            offset_from_plasma=[
                self.inner_plasma_gap_radial_thickness,
                self.plasma_gap_vertical_thickness,
                self.outer_plasma_gap_radial_thickness,
                self.plasma_gap_vertical_thickness,
                self.inner_plasma_gap_radial_thickness],
            start_angle=-180,
            stop_angle=180,
            color=(0., 1., 0.498),
            rotation_angle=self.rotation_angle,
            cut=[self._center_column_cutter]
        )
        return self._blanket

    def _make_divertor(self):
        self._blanket_enveloppe = paramak.BlanketFP(
            plasma=self._plasma,
            thickness=100.,
            offset_from_plasma=[
                self.inner_plasma_gap_radial_thickness,
                self.plasma_gap_vertical_thickness,
                self.outer_plasma_gap_radial_thickness,
                self.plasma_gap_vertical_thickness,
                self.inner_plasma_gap_radial_thickness],
            start_angle=-180,
            stop_angle=180,
            rotation_angle=self.rotation_angle,
            cut=[self._center_column_cutter]
        )

        self._divertor = paramak.CenterColumnShieldCylinder(
            height=self._center_column_shield_end_height *
            2.5,  # extra 0.5 to ensure overlap
            inner_radius=self._divertor_start_radius,
            outer_radius=self._divertor_end_radius,
            rotation_angle=self.rotation_angle,
            stp_filename="divertor.stp",
            stl_filename="divertor.stl",
            name="divertor",
            material_tag="divertor_mat",
            intersect=self._blanket_enveloppe,
            color=(1., 0.667, 0.),
        )
        self._blanket.cut.append(self._divertor)
        return self._divertor
