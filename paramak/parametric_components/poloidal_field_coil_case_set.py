
import cadquery as cq
from paramak import RotateStraightShape


class PoloidalFieldCoilCaseSet(RotateStraightShape):
    """Creates a series of rectangular poloidal field coils.

    Args:
        heights (list of floats): the vertical (z axis) heights of the coil
            (cm).
        widths (list of floats): the horizontal (x axis) widths of the coil
            (cm).
        casing_thicknesses (list of floats): the thickness of the casing (cm).
        center_points (tuple of floats): the center of the coil (x,z) values
            (cm).
        stp_filename (str, optional): defaults to "PoloidalFieldCoil.stp".
        stl_filename (str, optional): defaults to "PoloidalFieldCoil.stl".
        name (str, optional): defaults to "pf_coil".
        material_tag (str, optional): defaults to "pf_coil_mat".
    """

    def __init__(
        self,
        heights,
        widths,
        casing_thicknesses,
        center_points,
        stp_filename="PoloidalFieldCoil.stp",
        stl_filename="PoloidalFieldCoil.stl",
        name="pf_coil",
        material_tag="pf_coil_mat",
        **kwargs
    ):

        super().__init__(
            name=name,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

        self.center_points = center_points
        self.heights = heights
        self.widths = widths
        self.casing_thicknesses = casing_thicknesses

    @property
    def solid(self):
        if self.get_hash() != self.hash_value:
            self.create_solid()
        return self._solid

    @solid.setter
    def solid(self, value):
        self._solid = value

    @property
    def center_points(self):
        return self._center_points

    @center_points.setter
    def center_points(self, center_points):
        self._center_points = center_points

    @property
    def heights(self):
        return self._heights

    @heights.setter
    def heights(self, heights):
        self._heights = heights

    @property
    def widths(self):
        return self._widths

    @widths.setter
    def widths(self, widths):
        self._widths = widths

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe
        the 2D profile of the poloidal field coil shape."""

        all_points = []

        for height, width, center_point, casing_thickness in zip(
                self.heights, self.widths,
                self.center_points, self.casing_thicknesses):

            all_points = all_points + [
                (
                    center_point[0] + width / 2.0,
                    center_point[1] + height / 2.0,
                ),  # upper right
                (
                    center_point[0] + width / 2.0,
                    center_point[1] - height / 2.0,
                ),  # lower right
                (
                    center_point[0] - width / 2.0,
                    center_point[1] - height / 2.0,
                ),  # lower left
                (
                    center_point[0] - width / 2.0,
                    center_point[1] + height / 2.0,
                ),  # upper left
                (
                    center_point[0] + width / 2.0,
                    center_point[1] + height / 2.0,
                ),  # upper right
                (
                    center_point[0] + (casing_thickness + width / 2.0),
                    center_point[1] + (casing_thickness + height / 2.0),
                ),
                (
                    center_point[0] + (casing_thickness + width / 2.0),
                    center_point[1] - (casing_thickness + height / 2.0),
                ),
                (
                    center_point[0] - (casing_thickness + width / 2.0),
                    center_point[1] - (casing_thickness + height / 2.0),
                ),
                (
                    center_point[0] - (casing_thickness + width / 2.0),
                    center_point[1] + (casing_thickness + height / 2.0),
                ),
                (
                    center_point[0] + (casing_thickness + width / 2.0),
                    center_point[1] + (casing_thickness + height / 2.0),
                )
            ]

        self.points = all_points

    def create_solid(self):
        """Creates a 3d solid using points with straight edges.

           Returns:
              A CadQuery solid: A 3D solid volume
        """

        iter_points = iter(self.points)
        pf_coils_set = []
        for p1, p2, p3, p4, p5, p6, p7, p8, p9, p10 in zip(
                iter_points, iter_points, iter_points, iter_points,
                iter_points, iter_points, iter_points, iter_points,
                iter_points, iter_points,
        ):

            solid = (
                cq.Workplane(self.workplane)
                .polyline([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10])
                .close()
                .revolve(self.rotation_angle)
            )
            pf_coils_set.append(solid)

        compound = cq.Compound.makeCompound(
            [a.val() for a in pf_coils_set]
        )

        self.solid = compound

        # Calculate hash value for current solid
        self.hash_value = self.get_hash()

        return compound
