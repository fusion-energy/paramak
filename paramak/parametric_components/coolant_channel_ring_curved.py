
from typing import Optional
import numpy as np
from paramak import SweepCircleShape


class CoolantChannelRingCurved(SweepCircleShape):
    """A ring of equally-spaced curved circular coolant channels with
    constant thickness.

    Args:
        height: height of each coolant channel in ring.
        channel_radius: radius of each coolant channel in ring.
        number_of_coolant_channels: number of coolant channels in ring.
        ring_radius: radius of coolant channel ring.
        start_angle: angle at which the first channel in the ring is placed.
            Defaults to 0.0.
        stp_filename: Defaults to "CoolantChannelRingCurved.stp".
        stl_filename: Defaults to "CoolantChannelRingCurved.stl".
        material_tag: Defaults to "coolant_channel_mat".
        rotation_axis: azimuthal axis around which the separate coolant channels
            are placed. Default calculated by workplane and path_workplane.
        workplane (str, optional): plane in which the cross-sections of the
            coolant channels lie. Defaults to "XY".
        path_workplane (str, optional): plane in which the cross-sections of the
            coolant channels are swept. Defaults to "XZ".
        force_cross_section (bool, optional): forces coolant channels to have a
            more constant cross-section along their curve. Defaults to False.
    """

    def __init__(
        self,
        height: float,
        channel_radius: float,
        number_of_coolant_channels: int,
        ring_radius: float,
        mid_offset: float,
        start_angle: Optional[float] = 0.0,
        stp_filename: Optional[str] = "CoolantChannelRingCurved.stp",
        stl_filename: Optional[str] = "CoolantChannelRingCurved.stl",
        material_tag: Optional[str] = "coolant_channel_mat",
        **kwargs
    ) -> None:

        self.ring_radius = ring_radius
        self.mid_offset = mid_offset
        self.height = height
        self.start_angle = start_angle

        super().__init__(
            path_points=self.path_points,
            radius=channel_radius,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.channel_radius = channel_radius
        self.number_of_coolant_channels = number_of_coolant_channels

    @property
    def azimuth_placement_angle(self):
        self.find_azimuth_placement_angle()
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        self._azimuth_placement_angle = value

    @property
    def path_points(self):
        self.find_path_points()
        return self._path_points

    @path_points.setter
    def path_points(self, value):
        self._path_points = value

    def find_azimuth_placement_angle(self):
        """Calculates the azimuth placement angles based on the number of
        coolant channels."""

        angles = list(
            np.linspace(
                0 + self.start_angle,
                360 + self.start_angle,
                self.number_of_coolant_channels,
                endpoint=False))

        self.azimuth_placement_angle = angles

    def find_path_points(self):

        path_points = [
            (self.ring_radius, -self.height / 2),
            (self.ring_radius + self.mid_offset, 0),
            (self.ring_radius, self.height / 2)
        ]

        self.path_points = path_points
