from collections import Iterable
from hashlib import blake2b

import cadquery as cq

from paramak import Shape
from paramak.utils import cut_solid, intersect_solid, union_solid


class RotateCircleShape(Shape):
    """Rotates a circular 3d CadQuery solid from a central point and a radius

       Args:
          points (a list of tuples each containing X (float), Z (float)): A list of a single
             XZ coordinate which is the central point of the circle. For example, [(10, 10)].
          radius (float): The radius of the circle.
          name (str): The legend name used when exporting a html graph of the shape.
          color (RGB or RGBA - sequences of 3 or 4 floats, respectively, each in the range 0-1):
             The color to use when exporting as html graphs or png images.
          material_tag (str): The material name to use when exporting the neutronics description.
          stp_filname (str): The filename used when saving stp files as part of a reactor.
          azimuth_placement_angle (float or iterable of floats): The angle or angles to use when
             rotating the shape on the azimuthal axis.
          rotation_angle (float): The rotation angle to use when revolving the solid (degrees).
          cut (CadQuery object): An optional CadQuery object to perform a boolean cut with this
             object.
    """

    def __init__(
        self,
        points,
        radius,
        workplane="XZ",
        stp_filename="RotateCircleShape.stp",
        stl_filename="RotateCircleShape.stl",
        solid=None,
        color=None,
        azimuth_placement_angle=0,
        rotation_angle=360,
        cut=None,
        intersect=None,
        union=None,
        material_tag=None,
        name=None,
        **kwargs
    ):

        default_dict = {"tet_mesh": None,
                        "physical_groups": None}

        for arg in kwargs:
            if arg in default_dict:
                default_dict[arg] = kwargs[arg]

        super().__init__(
            points=points,
            name=name,
            color=color,
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            azimuth_placement_angle=azimuth_placement_angle,
            workplane=workplane,
            **default_dict
        )

        self.cut = cut
        self.intersect = intersect
        self.union = union
        self.radius = radius
        self.rotation_angle = rotation_angle
        self.hash_value = None
        self.solid = solid

    @property
    def cut(self):
        return self._cut

    @cut.setter
    def cut(self, value):
        self._cut = value

    @property
    def intersect(self):
        return self._intersect

    @intersect.setter
    def intersect(self, value):
        self._intersect = value

    @property
    def union(self):
        return self._union

    @union.setter
    def union(self, value):
        self._union = value

    @property
    def solid(self):
        if self.get_hash() != self.hash_value:
            self.create_solid()
        return self._solid

    @solid.setter
    def solid(self, value):
        self._solid = value

    @property
    def rotation_angle(self):
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        self._rotation_angle = value

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    @property
    def hash_value(self):
        return self._hash_value

    @hash_value.setter
    def hash_value(self, value):
        self._hash_value = value

    def get_hash(self):
        hash_object = blake2b()
        shape_dict = dict(self.__dict__)
        # set _solid and _hash_value to None to prevent unnecessary
        # reconstruction
        shape_dict["_solid"] = None
        shape_dict["_hash_value"] = None

        hash_object.update(str(list(shape_dict.values())).encode("utf-8"))
        value = hash_object.hexdigest()
        return value

    def create_solid(self):
        """Creates a 3d solid using points, radius, azimuth_placement_angle and
           rotation_angle.

           Returns:
              A CadQuery solid: A 3D solid volume
        """

        # print('create_solid() has been called')

        solid = (
            cq.Workplane(self.workplane)
            .moveTo(self.points[0][0], self.points[0][1])
            .circle(self.radius)
            # .close()
            .revolve(self.rotation_angle)
        )

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

        # If a cut solid is provided then perform a boolean cut
        if self.cut is not None:
            solid = cut_solid(solid, self.cut)

        # If an intersect is provided then perform a boolean intersect
        if self.intersect is not None:
            solid = intersect_solid(solid, self.intersect)

        # If an intersect is provided then perform a boolean intersect
        if self.union is not None:
            solid = union_solid(solid, self.union)

        self.solid = solid

        # Calculate hash value for current solid
        self.hash_value = self.get_hash()

        return solid
