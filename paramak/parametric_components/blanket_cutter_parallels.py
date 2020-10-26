
from collections import Iterable

import cadquery as cq
from paramak import ExtrudeStraightShape


class BlanketCutterParallels(ExtrudeStraightShape):
    """Creates an extruded shape with a parallel rectangular section repeated
    around the reactor. The shape is used to cut other components (eg. blankets
    and firstwalls) in order to create a banana section of the blankets with
    parrallel sides.Typically used to divide a blanket into vertical
    sections with a fixed distance between each section.

    Args:
        distance (float): extruded distance (cm) of the cutter which translates
            to being the gap size between blankets when the cutter is used to
            segment blankets.
        gap_size (float): the distance between the inner edges of the two
            parrallel extrusions
        azimuth_placement_angle (float, optional): the azimuth angle(s) used
            when positioning the shape. If an iterable of angles is provided,
            the shape is duplicated at all angles. Defaults to [0., 36.,
            72., 108., 144., 180., 216., 252., 288., 324.]
        height (float, optional): height (cm) of the port. Defaults to 2000
        width (float, optional): width (cm) of the port. Defaults to 2000
        stp_filename (str, optional): defaults to "BlanketCutterParallels.stp".
        stl_filename (str, optional): defaults to "BlanketCutterParallels.stl".
        name (str, optional): defaults to "blanket_cutter_Parallels".
        material_tag (str, optional): defaults to
            "blanket_cutter_parallels_mat".
    """

    def __init__(
        self,
        distance,
        gap_size,
        azimuth_placement_angle=[0., 36., 72., 108., 144., 180., 216., 252.,
                                 288., 324.],
        height=2000,
        width=2000,
        stp_filename="BlanketCutterParallels.stp",
        stl_filename="BlanketCutterParallels.stl",
        name="blanket_cutter_parallels",
        material_tag="blanket_cutter_parallels_mat",
        **kwargs
    ):

        super().__init__(
            distance=distance,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            material_tag=material_tag,
            **kwargs
        )

        self.azimuth_placement_angle = azimuth_placement_angle
        self.height = height
        self.width = width
        self.distance = distance
        self.gap_size = gap_size
        self.find_points()

    def find_points(self):

        points = [
            (0, -self.height / 2),
            (self.width, -self.height / 2),
            (self.width, self.height / 2),
            (0, self.height / 2)
        ]
        self.points = points

    def create_solid(self):
        """Creates a 3d solid using points with straight edges.

        Returns:
           A CadQuery solid: A 3D solid volume
        """

        small_solid = (
            cq.Workplane(self.workplane)
            .polyline([(p[0], p[1]) for p in self.points])
            .close()
            .extrude(distance=self.gap_size / 2.0, both=True)
        )

        large_solid = (
            cq.Workplane(self.workplane)
            .polyline([(p[0], p[1]) for p in self.points])
            .close()
            .extrude(distance=self.gap_size / 2.0 + self.distance, both=True)
        )

        solid = large_solid.cut(small_solid)

        # Checks if the azimuth_placement_angle is a list of angles
        if isinstance(self.azimuth_placement_angle, Iterable):
            rotated_solids = []
            # Perform seperate rotations for each angle
            for angle in self.azimuth_placement_angle:
                rotated_solids.append(
                    solid.rotate(
                        (0, 0, -1), (0, 0, 1), angle))
            solid = cq.Workplane(self.workplane)

            # Joins the seperate solids together
            for i in rotated_solids:
                solid = solid.union(i)
        else:
            # Peform rotations for a single azimuth_placement_angle angle
            solid = solid.rotate(
                (0, 0, 1), (0, 0, -1), self.azimuth_placement_angle)

        self.perform_boolean_operations(solid)

        return solid
