
import paramak


class SingleNullSubmersionTokamak(paramak.SubmersionTokamak):
    """Creates geometry for a submersion reactor with a single divertor
    including a plasma, cylindrical center column shielding, square toroidal
    field coils. There is an inboard breeder blanket on this submersion
    reactor.

    Arguments:
        divertor_position (str): Defaults to "upper".
        support_position (str): Defaults to "upper".
    """

    def __init__(
        self,
        divertor_position="upper",
        support_position="upper",
        **kwargs
    ):

        super().__init__(
            divertor_position=divertor_position,
            support_position=support_position,
            **kwargs)
