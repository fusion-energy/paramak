
import paramak


class SingleNullSubmersionTokamak(paramak.SubmersionTokamak):
    """Creates geometry for a submersion reactor with a single divertor
    including a plasma, cylindrical center column shielding, square toroidal
    field coils. There is an inboard breeder blanket on this submersion
    reactor.

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
        number_of_tf_coils (int): the number of tf coils
        rotation_angle (float): the angle of the sector that is desired
        outboard_tf_coil_radial_thickness (float): the radial thickness of
            the toroidal field coil (optional)
        tf_coil_to_rear_blanket_radial_gap (float): the radial distance
            between the rear of the blanket and the toroidal field coil
            (optional)
        outboard_tf_coil_poloidal_thickness (float): the vertical thickness of
            each poloidal field coil (optional)
        pf_coil_vertical_thicknesses (list of floats): the vertical thickness
            of each poloidal field coil (optional)
        pf_coil_radial_thicknesses (list of floats): the radial thickness of
            each poloidal field coil (optional)
        pf_coil_to_tf_coil_radial_gap (float): the radial distance between
            the rear of the poloidal field coil and the toroidal field coil
            (optional)
        divertor_position (str): the position of the divertor, "upper" or
            "lower"
        support_position (str): the position of the supports, "upper" or
            "lower"

    Returns:
        a paramak shape object: a Reactor object that has generic functionality
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
        divertor_position="upper",
        support_position="upper",
        **kwargs
    ):

        self.divertor_position = divertor_position
        self.support_position = support_position

        super().__init__(
            inner_bore_radial_thickness=inner_bore_radial_thickness,
            inboard_tf_leg_radial_thickness=inboard_tf_leg_radial_thickness,
            center_column_shield_radial_thickness=center_column_shield_radial_thickness,
            inboard_blanket_radial_thickness=inboard_blanket_radial_thickness,
            firstwall_radial_thickness=firstwall_radial_thickness,
            inner_plasma_gap_radial_thickness=inner_plasma_gap_radial_thickness,
            plasma_radial_thickness=plasma_radial_thickness,
            outer_plasma_gap_radial_thickness=outer_plasma_gap_radial_thickness,
            outboard_blanket_radial_thickness=outboard_blanket_radial_thickness,
            blanket_rear_wall_radial_thickness=blanket_rear_wall_radial_thickness,
            divertor_radial_thickness=divertor_radial_thickness,
            support_radial_thickness=support_radial_thickness,
            plasma_high_point=plasma_high_point,
            **kwargs)
        self.major_radius = None
        self.minor_radius = None
        self.elongation = None
        self.triangularity = None

        self.shapes_and_components = []

        self.create_solids()

    @property
    def divertor_position(self):
        return self._divertor_position

    @divertor_position.setter
    def divertor_position(self, value):
        acceptable_values = ["upper", "lower"]
        if value in acceptable_values:
            self._divertor_position = value
        else:
            raise ValueError("divertor position must be 'upper' or 'lower'")

    @property
    def support_position(self):
        return self._support_position

    @support_position.setter
    def support_position(self, value):
        acceptable_values = ["upper", "lower"]
        if value in acceptable_values:
            self._support_position = value
        else:
            raise ValueError("support position must be 'upper' or 'lower'")

    def _make_divertor(self):

        if self.divertor_position == "upper":
            divertor_height = self._blanket_rear_wall_end_height
        elif self.divertor_position == "lower":
            divertor_height = -self._blanket_rear_wall_end_height

        self._divertor = paramak.RotateStraightShape(
            points=[
                (self._divertor_start_radius, 0),
                (self._divertor_end_radius, 0),
                (self._divertor_end_radius, divertor_height),
                (self._divertor_start_radius, divertor_height)
            ],
            intersect=self._firstwall,
            rotation_angle=self.rotation_angle,
            stp_filename="divertor.stp",
            stl_filename="divertor.stl",
            name="divertor",
            material_tag="divertor_mat"
        )
        self.shapes_and_components.append(self._divertor)

    def _make_supports(self):

        if self.support_position == "upper":
            support_height = self._blanket_rear_wall_end_height
        elif self.support_position == "lower":
            support_height = -self._blanket_rear_wall_end_height

        self._supports = paramak.RotateStraightShape(
            points=[
                (self._support_start_radius, 0),
                (self._support_end_radius, 0),
                (self._support_end_radius, support_height),
                (self._support_start_radius, support_height)
            ],
            intersect=self._blanket,
            rotation_angle=self.rotation_angle,
            stp_filename="supports.stp",
            stl_filename="supports.stl",
            name="supports",
            material_tag="supports_mat",
        )
        self.shapes_and_components.append(self._supports)
