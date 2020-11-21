
import paramak


class SingleNullSubmersionTokamak(paramak.SubmersionTokamak):
    """Creates geometry for a submersion reactor with a single divertor
    including a plasma, cylindrical center column shielding, square toroidal
    field coils. There is an inboard breeder blanket on this submersion
    reactor.

    Arguments:
        divertor_position (str): the position of the divertor, "upper" or
            "lower"
        support_position (str): the position of the supports, "upper" or
            "lower"
    """

    def __init__(
        self,
        divertor_position="upper",
        support_position="upper",
        **kwargs
    ):

        self.divertor_position = divertor_position
        self.support_position = support_position

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
        return self._divertor

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
        return self._supports
