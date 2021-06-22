
import warnings
from typing import Optional

from paramak import ExtrudeMixedShape, ExtrudeStraightShape
from paramak.utils import add_thickness, cut_solid, union_solid


class TFCoilCasing(ExtrudeMixedShape):
    """Casing component for TF coils

    Args:
        magnet: TF coil shape
        inner_offset: radial distance between inner coil surface and inner
            casing surface (cm)
        outer_offset: radial distance between outer coil surface and outer
            casing surface (cm)
        vertical_section_offset: radial distance between outer coil surface and
            outer vertical section surface (cm)
        distance: extrusion distance (cm)
    """

    def __init__(
        self,
        magnet,
        inner_offset: float,
        outer_offset: float,
        vertical_section_offset: float,
        stp_filename: Optional[str] = "TFCoilCasing.stp",
        stl_filename: Optional[str] = "TFCoilCasing.stl",
        material_tag: Optional[str] = "TF_coil_casing_mat",
        **kwargs
    ) -> None:

        self.magnet = magnet

        super().__init__(
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.inner_offset = inner_offset
        self.outer_offset = outer_offset
        self.vertical_section_offset = vertical_section_offset
        self.leg_shape = ExtrudeStraightShape(
            distance=self.distance,
            azimuth_placement_angle=self.azimuth_placement_angle,
            workplane=self.magnet.workplane)
        self.inner_bore_cutting_points = None
        self.workplane = self.magnet.workplane

    @property
    def azimuth_placement_angle(self):
        self.azimuth_placement_angle = self.magnet.azimuth_placement_angle
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        correct_angles = self.magnet.azimuth_placement_angle
        if value != correct_angles:
            msg = "Casing azimuth_placement_angle should be the" + \
                " same value as TFCoilCasing.magnet."
            warnings.warn(msg, UserWarning)
        self._azimuth_placement_angle = correct_angles

    def find_points(self):
        inner_points_magnet = self.magnet.inner_points
        outer_points_magnet = self.magnet.outer_points
        inner_points_magnet = (
            inner_points_magnet[:, 0],
            inner_points_magnet[:, 1]
        )
        outer_points_magnet = (
            outer_points_magnet[:, 0],
            outer_points_magnet[:, 1]
        )
        inner_points = add_thickness(
            *inner_points_magnet,
            thickness=-self.inner_offset,
        )

        outer_points = add_thickness(
            *outer_points_magnet,
            thickness=-self.outer_offset
        )
        curve_points = []
        for distrib_points in [inner_points, outer_points]:
            curve_points.append([[R, Z, 'spline'] for R, Z in zip(
                distrib_points[0], distrib_points[1])])

        curve_points[0][-1][2] = 'straight'
        curve_points[1][-1][2] = "straight"

        points = curve_points[0] + curve_points[1]
        self.points = points

        yA = outer_points[1][outer_points[0].index(
            min(outer_points[0], key=lambda x:abs(x - min(inner_points[0]))))]
        self.leg_points = [
            (
                min(outer_points[0]) -
                self.vertical_section_offset + self.outer_offset,
                min(outer_points[1])),
            (
                outer_points[0][outer_points[1].index(min(outer_points[1]))],
                min(outer_points[1])),
            (
                inner_points[0][inner_points[1].index(min(inner_points[1]))],
                min(inner_points[1])),
            (min(inner_points[0]), min(
                yA, self.magnet.vertical_displacement - yA)),
            # not having this line avoid unexpected surfaces
            (inner_points[0][-1], inner_points[1][-1]),
            (min(inner_points[0]), max(
                yA, self.magnet.vertical_displacement - yA)),
            (
                inner_points[0][inner_points[1].index(min(inner_points[1]))],
                max(inner_points[1])),
            (
                outer_points[0][outer_points[1].index(min(outer_points[1]))],
                max(outer_points[1])),
            (
                min(outer_points[0]) - \
                self.vertical_section_offset + self.outer_offset,
                max(outer_points[1])),
        ]

        self.inner_bore_cutting_points = [
            (0, self.leg_points[0][1]),
            self.leg_points[0],
            self.leg_points[-1],
            (0, self.leg_points[-1][1])
        ]

    def create_solid(self):
        solid = super().create_solid()

        self.leg_shape.points = self.leg_points
        self.leg_shape.distance = self.distance
        self.leg_shape.azimuth_placement_angle = \
            self.azimuth_placement_angle
        solid = union_solid(solid, self.leg_shape)
        solid = cut_solid(solid, self.magnet)

        # cut away excess casing outlined in #789
        inner_bore_cutting_shape = ExtrudeStraightShape(
            points=self.inner_bore_cutting_points,
            distance=self.distance,
            azimuth_placement_angle=self.azimuth_placement_angle
        )
        solid = cut_solid(solid, inner_bore_cutting_shape)

        self.solid = solid
        return solid
