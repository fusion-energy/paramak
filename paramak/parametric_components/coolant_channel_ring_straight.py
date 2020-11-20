
import numpy as np
from paramak import ExtrudeCircleShape


class CoolantChannelRingStraight(ExtrudeCircleShape):
    """A ring of equally-spaced straight circular coolant channels with
    constant thickness.

    Args:
        height (float): height of each coolant channel in ring.
        channel_radius (float): radius of each coolant channel in ring.
        number_of_coolant_channels (float): number of coolant channels in ring.
        ring radius (float): radius of coolant channel ring.
        workplane (str, optional): plane in which the cross-sections of the
            coolant channels lie. Defaults to "XY".
        rotation_axis (str, optional): azimuthal axis around which the separate
            coolant channels are placed.
        stp_filename (str, optional): Defaults to
            "CoolantChannelRingStraight.stp".
        stl_filename (str, optional): Defaults to
            "CoolantChannelRingStraight.stl".
        material_tag (str, optional): Defaults to "coolant_channel_mat".
    """

    def __init__(
        self,
        height,
        channel_radius,
        number_of_coolant_channels,
        ring_radius,
        stp_filename="CoolantChannelRingStraight.stp",
        stl_filename="CoolantChannelRingStraight.stl",
        material_tag="coolant_channel_mat",
        **kwargs
    ):

        super().__init__(
            distance=height,
            radius=channel_radius,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.height = height
        self.channel_radius = channel_radius
        self.number_of_coolant_channels = number_of_coolant_channels
        self.ring_radius = ring_radius

    @property
    def azimuth_placement_angle(self):
        self.find_azimuth_placement_angle()
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        self._azimuth_placement_angle = value

    def find_azimuth_placement_angle(self):
        """Calculates the azimuth placement angles based on the number of
        coolant channels"""

        angles = list(
            np.linspace(
                0,
                360,
                self.number_of_coolant_channels,
                endpoint=False))

        self.azimuth_placement_angle = angles

    def find_points(self):

        points = [(self.ring_radius, 0)]

        self.points = points
