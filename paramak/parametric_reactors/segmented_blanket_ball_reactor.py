
import paramak
import numpy as np
import cadquery as cq


class SegmentedBlanketBallReactor(paramak.BallReactor):
    """Creates geometry for a single ball reactor with a single divertor
    including a plasma, cylindrical center column shielding, square toroidal
    field coils. There is no inboard breeder blanket on this ball reactor like
    most spherical reactors.

    Arguments:
        gap_between_blankets (float): the distance between adjacent blanket
            segments,
        number_of_blanket_segments (int): the number of segments to divide the
            blanket up into. This for a full 360 degrees rotation
        blanket_fillet_radius (float): the fillet radius to apply to the
            interface between the firstwall and th breeder zone. Set to 0 for
            no fillet. Defaults to 10.0.
    """

    def __init__(
            self,
            gap_between_blankets,
            number_of_blanket_segments,
            blanket_fillet_radius=10.0,
            **kwargs
    ):

        self.gap_between_blankets = gap_between_blankets
        self.number_of_blanket_segments = number_of_blanket_segments
        self.blanket_fillet_radius = blanket_fillet_radius

        super().__init__(**kwargs)

    @property
    def gap_between_blankets(self):
        return self._gap_between_blankets

    @gap_between_blankets.setter
    def gap_between_blankets(self, value):
        """Sets the SegmentedBlanketBallReactor.gap_between_blankets
        attribute which controls the horitzonal distance between blanket
        segments."""
        if isinstance(value, (float, int)) and value > 0:
            self._gap_between_blankets = float(value)
        else:
            raise ValueError(
                "gap_between_blankets but be a positive value float")

    @property
    def number_of_blanket_segments(self):
        """Sets the SegmentedBlanketBallReactor.number_of_blanket_segments
        attribute which controls the number of blanket segments."""
        return self._number_of_blanket_segments

    @number_of_blanket_segments.setter
    def number_of_blanket_segments(self, value):
        if isinstance(value, int) and value > 2:
            self._number_of_blanket_segments = value
        else:
            raise ValueError(
                "number_of_blanket_segments but be an int greater than 2")

    def _make_blankets_layers(self):
        super()._make_blankets_layers()
        azimuth_placement_angles = np.linspace(
            0, 360, self.number_of_blanket_segments, endpoint=False)
        thin_cutter = paramak.BlanketCutterStar(
            distance=self.gap_between_blankets,
            azimuth_placement_angle=azimuth_placement_angles)

        thick_cutter = paramak.BlanketCutterStar(
            distance=self.gap_between_blankets +
            2 * self.firstwall_radial_thickness,
            azimuth_placement_angle=azimuth_placement_angles)

        self._blanket.cut = [self._center_column_cutter, thick_cutter]

        if self.blanket_fillet_radius != 0:
            # tried firstwall start radius here already
            x = self.major_radius + 1
            front_face_b = self._blanket.solid.faces(
                cq.NearestToPointSelector((0, x, 0)))
            front_edge_b = front_face_b.edges(
                cq.NearestToPointSelector((0, x, 0)))
            front_edge_length_b = front_edge_b.val().Length()
            self._blanket.solid = self._blanket.solid.edges(
                paramak.EdgeLengthSelector(front_edge_length_b)).fillet(
                self.blanket_fillet_radius)
        self._firstwall.thickness += self.blanket_radial_thickness
        self._firstwall.cut = [
            self._center_column_cutter,
            thin_cutter,
            self._blanket]

        # TODO this segfaults at the moment but works as an opperation on the
        # reactor after construction in jupyter
        # tried different x values and (0, x, 0)
        # noticed that it much quicker as a post process so perhaps some
        # unwanted looping is happening
        # if self.blanket_fillet_radius != 0:
        #     x = self.major_radius # tried firstwall start radius here already
        #     front_face = \
        #       self._firstwall.solid.faces(
        #           cq.NearestToPointSelector((x, 0, 0)))
        #     print('found front face')
        #     front_edge = front_face.edges(
        #           cq.NearestToPointSelector((x, 0, 0)))
        #     print('found front edge')
        #     front_edge_length = front_edge.val().Length()
        #     print('found front edge length', front_edge_length)
        #     self._firstwall.solid = self._firstwall.solid.edges(
        #         paramak.EdgeLengthSelector(front_edge_length)).fillet(self.blanket_fillet_radius)
        # print('finished')

        return [self._firstwall, self._blanket, self._blanket_rear_wall]
