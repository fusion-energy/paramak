
import paramak


class SingleNullBallReactor(paramak.BallReactor):
    """Creates geometry for a single ball reactor with a single divertor
    including a plasma, cylindrical center column shielding, square toroidal
    field coils. There is no inboard breeder blanket on this ball reactor like
    most spherical reactors.

    Arguments:

    """

    def __init__(
        self,
        divertor_position="upper",
        **kwargs
    ):

        self.divertor_position = divertor_position

        super().__init__(**kwargs)

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

    def _make_divertor(self):
        if self.divertor_position == "upper":
            divertor_height = self._blanket_rear_wall_end_height
        elif self.divertor_position == "lower":
            divertor_height = -self._blanket_rear_wall_end_height

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
            start_angle=-180,
            stop_angle=180,
            rotation_angle=self.rotation_angle,
        )

        self._divertor = paramak.RotateStraightShape(
            points=[
                (self._divertor_start_radius, 0),
                (self._divertor_end_radius, 0),
                (self._divertor_end_radius, divertor_height),
                (self._divertor_start_radius, divertor_height)
            ],
            intersect=self._blanket_fw_rear_wall_envelope,
            stp_filename="divertor.stp",
            stl_filename="divertor.stl",
            name="divertor",
            material_tag="divertor_mat",
            rotation_angle=self.rotation_angle
        )

        return self._divertor
