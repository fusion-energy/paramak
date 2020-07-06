from paramak import Reactor
import paramak

class BallReactor(Reactor):
    """Creates geometry for a simple ball reactor including a plasma,
    cylindical center column shielding, square toroidal field coils

    :param major_radius: 
    :type height: float

    :return: a shape object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        major_radius,
        minor_radius,
        offset_from_plasma,
        blanket_thickness
    ):

        super().__init__()

        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.offset_from_plasma = offset_from_plasma
        self.blanket_thickness = blanket_thickness
        self.create_components()


    def create_components(self):

        plasma = paramak.Plasma(major_radius=self.major_radius,
                                minor_radius=self.minor_radius,)
        plasma.create_solid()

        self.add_shape_or_component(plasma)

        blanket = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(plasma.minor_radius + 
                             plasma.major_radius + 
                             self.offset_from_plasma,
                             0),
            inner_upper_point=(plasma.x_point,
                               plasma.z_point+self.offset_from_plasma),
            inner_lower_point=(plasma.x_point,
                               -(plasma.z_point+self.offset_from_plasma)),
            thickness=self.blanket_thickness
        )

        self.add_shape_or_component(blanket)
