
from collections.abc import Iterable
from operator import itemgetter

from paramak import CuttingWedge

SAFETY_FACTOR = 3


class CuttingWedgeFS(CuttingWedge):
    """Creates a wedge from a Shape that can be useful for cutting sector
    models.

    Args:
        shape (paramak.Shape): a paramak.Shape object that is used to find the
            height and radius of the wedge
        stp_filename (str, optional): Defaults to "CuttingWedgeFS.stp".
        stl_filename (str, optional): Defaults to "CuttingWedgeFS.stl".
        material_tag (str, optional): Defaults to "cutting_slice_mat".
    """

    def __init__(
        self,
        shape,
        stp_filename="CuttingWedgeAlternate.stp",
        stl_filename="CuttingWedgeAlternate.stl",
        material_tag="cutting_slice_mat",
        **kwargs
    ):
        self.shape = shape
        super().__init__(
            height=self.height,
            radius=self.radius,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, value):
        if value.rotation_angle == 360:
            msg = 'cutting_wedge cannot be created,' + \
                ' rotation_angle must be < 360'
            raise ValueError(msg)
        self._shape = value

    @property
    def radius(self):
        self.find_radius_height()
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    @property
    def height(self):
        self.find_radius_height()
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def rotation_angle(self):
        self.rotation_angle = 360 - self.shape.rotation_angle
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        self._rotation_angle = value

    @property
    def workplane(self):
        workplanes = ["XY", "XZ", "YZ"]
        for wp in workplanes:
            if self.shape.get_rotation_axis()[1] in wp:
                self.workplane = wp
                break
        return self._workplane

    @workplane.setter
    def workplane(self, value):
        self._workplane = value

    @property
    def rotation_axis(self):
        self.rotation_axis = self.shape.rotation_axis
        return self._rotation_axis

    @rotation_axis.setter
    def rotation_axis(self, value):
        self._rotation_axis = value

    @property
    def azimuth_placement_angle(self):
        if isinstance(self.shape.azimuth_placement_angle, Iterable):
            self.azimuth_placement_angle = self.shape.rotation_angle
        else:
            self.azimuth_placement_angle = \
                self.shape.azimuth_placement_angle + self.shape.rotation_angle
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        self._azimuth_placement_angle = value

    def find_radius_height(self):
        shape = self.shape
        if shape.rotation_angle == 360:
            msg = 'cutting_wedge cannot be created,' + \
                ' rotation_angle must be < 360'
            raise ValueError(msg)
        shape_points = shape.points
        if hasattr(shape, 'radius') and len(shape_points) == 1:
            max_x = shape_points[0][0] + shape.radius
            max_y = shape_points[0][1] + shape.radius

        elif len(shape_points) > 1:
            max_x = max(shape_points, key=itemgetter(0))[0]
            if shape.get_rotation_axis()[1] not in shape.workplane and \
                    hasattr(shape, "distance"):
                max_y = shape.distance
            else:
                max_y = max(shape_points, key=itemgetter(1))[1]

        else:
            raise ValueError('cutting_wedge cannot be created')
        self.radius = SAFETY_FACTOR * max_x
        self.height = SAFETY_FACTOR * max_y
