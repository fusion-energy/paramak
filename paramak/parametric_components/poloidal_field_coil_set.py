
import cadquery as cq
from paramak import RotateStraightShape


class PoloidalFieldCoilSet(RotateStraightShape):
    """Creates a series of rectangular poloidal field coils.

    Args:
        heights (float): the vertical (z axis) heights of the coil (cm).
        widths (float): the horizontal (x axis) widths of the coil (cm).
        center_points (tuple of floats): the center of the coil (x,z) values
            (cm).
        stp_filename (str, optional): Defaults to "PoloidalFieldCoil.stp".
        stl_filename (str, optional): Defaults to "PoloidalFieldCoil.stl".
        name (str, optional): Defaults to "pf_coil".
        material_tag (str, optional): Defaults to "pf_coil_mat".
    """

    def __init__(
        self,
        heights,
        widths,
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

        if len(
            self.widths) != len(
            self.heights) or len(
            self.heights) != len(
                self.center_points):
            raise ValueError("The length of widthts, height and center_points \
                must be the same when making a PoloidalFieldCoilSet")

    @property
    def solid(self):
        """Returns a CadQuery compound object consisting of 1 or more 3d
        volumes"""
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
    def center_points(self, value):
        if not isinstance(value, list):
            raise ValueError(
                "PoloidalFieldCoilSet center_points must be a list")
        self._center_points = value

    @property
    def heights(self):
        return self._heights

    @heights.setter
    def heights(self, value):
        if not isinstance(value, list):
            raise ValueError("PoloidalFieldCoilSet heights must be a list")
        self._heights = value

    @property
    def widths(self):
        return self._widths

    @widths.setter
    def widths(self, value):
        if not isinstance(value, list):
            raise ValueError("PoloidalFieldCoilSet widths must be a list")
        self._widths = value

    def find_points(self):
        """Finds the XZ points joined by straight connections that describe
        the 2D profile of the poloidal field coil shape."""

        all_points = []

        for height, width, center_point in zip(
                self.heights, self.widths, self.center_points):

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
            ]

        self.points = all_points

    def create_solid(self):
        """Creates a 3d solid using points with straight connections
        edges, azimuth_placement_angle and rotation angle.
        individual solids in the compound can be accessed using .Solids()[i]
        where i is an int

           Returns:
              A CadQuery solid: A 3D solid volume
        """

        iter_points = iter(self.points)
        pf_coils_set = []
        for p1, p2, p3, p4 in zip(
                iter_points, iter_points, iter_points, iter_points):

            solid = (
                cq.Workplane(self.workplane)
                .polyline([p1, p2, p3, p4])
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