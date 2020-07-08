import math
from collections import Iterable

import cadquery as cq

from paramak import Shape

from hashlib import blake2b


class ExtrudeCircleShape(Shape):
    """Extrude a circular 3d CadQuery solid from a central point and a radius

       :param points: A list of a single XZ coordinate which is the central
            point of the circle. For example, [(10, 10)].
       :type points: a tuple containing X (float), Z (float) value for the central point
       :param radius: The radius of the circle
       :type radius: float
       :param stp_filename: the filename used when saving stp files as part of a reactor
       :type stp_filename: str
       :param color: the color to use when exporting as html graphs or png images
       :type color: Red, Green, Blue, [Alpha] values. RGB and RGBA are sequences of,
            3 or 4 floats respectively each in the range 0-1
       :param distance: The extrude distance to use (cm units if used for neutronics)
       :type distance: float
       :param azimuth_placement_angle: the angle or angles to use when rotating the 
            shape on the azimuthal axis
       :type azimuth_placement_angle: float or iterable of floats
       :param cut: An optional cadquery object to perform a boolean cut with this object
       :type cut: cadquery object
       :param material_tag: The material name to use when exporting the neutronics description
       :type material_tag: str
       :param name: The legend name used when exporting a html graph of the shape
       :type name: str
       :param workplane: The orientation of the CadQuery workplane. Options are XY, YZ, XZ
       :type workplane: str
    """

    def __init__(
        self,
        points,
        distance,
        radius,
        workplane="XZ",
        stp_filename=None,
        solid=None,
        color=None,
        azimuth_placement_angle=0,
        cut=None,
        material_tag=None,
        name=None,
        hash_value=None,
    ):

        super().__init__(
            points,
            name,
            color,
            material_tag,
            stp_filename,
            azimuth_placement_angle,
            workplane,
        )

        self.cut = cut
        self.radius = radius
        self.distance = distance
        self.hash_value = hash_value
        self.solid = solid

    @property
    def cut(self):
        return self._cut

    @cut.setter
    def cut(self, cut):
        self._cut = cut

    @property
    def solid(self):
        if self.get_hash() != self.hash_value:
            self.create_solid()
        return self._solid

    @solid.setter
    def solid(self, solid):
        self._solid = solid

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value

    @property
    def hash_value(self):
        return self._hash_value

    @hash_value.setter
    def hash_value(self, value):
        self._hash_value = value

    def get_hash(self):
        hash_object = blake2b()
        hash_object.update(
            str(self.points).encode("utf-8")
            + str(self.distance).encode("utf-8")
            + str(self.radius).encode("utf-8")
            + str(self.workplane).encode("utf-8")
            + str(self.name).encode("utf-8")
            + str(self.color).encode("utf-8")
            + str(self.material_tag).encode("utf-8")
            + str(self.stp_filename).encode("utf-8")
            + str(self.azimuth_placement_angle).encode("utf-8")
            + str(self.cut).encode("utf-8")
        )
        value = hash_object.hexdigest()
        return value

    def create_solid(self):
        """Creates a 3d solid using points with straight connections
        edges, azimuth_placement_angle and rotation angle.

        :return: a 3d solid volume
        :rtype: a cadquery solid
        """

        # print('create_solid() has been called')

        # Creates hash value for current solid
        self.hash_value = self.get_hash()

        # Creates a cadquery solid from points and revolves
        solid = (
            cq.Workplane(self.workplane)
            .moveTo(self.points[0][0], self.points[0][1])
            .circle(self.radius)
            .extrude(distance=-self.distance / 2.0, both=True)
        )

        # Checks if the azimuth_placement_angle is a list of angles
        if isinstance(self.azimuth_placement_angle, Iterable):
            rotated_solids = []
            # Perform seperate rotations for each angle
            for angle in self.azimuth_placement_angle:
                rotated_solids.append(solid.rotate((0, 0, -1), (0, 0, 1), angle))
            solid = cq.Workplane(self.workplane)

            # Joins the seperate solids together
            for i in rotated_solids:
                solid = solid.union(i)
        else:
            # Peform rotations for a single azimuth_placement_angle angle
            solid = solid.rotate((0, 0, 1), (0, 0, -1), self.azimuth_placement_angle)

        # If a cut solid is provided then perform a boolean cut
        if self.cut is not None:
            # Allows for multiple cuts to be applied
            if isinstance(self.cut, Iterable):
                for cutting_solid in self.cut:
                    solid = solid.cut(cutting_solid.solid)
            else:
                solid = solid.cut(self.cut.solid)

        self.solid = solid

        return solid
