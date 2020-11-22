
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

        super().__init__(divertor_position=divertor_position, **kwargs)
