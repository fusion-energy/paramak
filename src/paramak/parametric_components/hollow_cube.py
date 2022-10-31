from typing import Tuple

import cadquery as cq
from paramak import Shape


class HollowCube(Shape):
    """A hollow cube with a constant thickness. Can be used to create a DAGMC
    Graveyard.

    Arguments:
        length: The length to use for the height, width, depth of the
            inner dimensions of the cube.
        thickness: thickness of the vessel.
        center_coordinate: the location the center of the cube.
    """

    def __init__(
        self,
        length: float,
        thickness: float = 10.0,
        center_coordinate: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        name: str = "hollow_cube",
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.length = length
        self.thickness = thickness
        self.center_coordinate = center_coordinate

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        self._thickness = value

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        self._length = value

    def create_solid(self):

        # creates a small box that surrounds the geometry
        inner_box = cq.Workplane("front").box(self.length, self.length, self.length).translate(self.center_coordinate)

        # creates a large box that surrounds the smaller box
        outer_box = (
            cq.Workplane("front")
            .box(
                self.length + self.thickness,
                self.length + self.thickness,
                self.length + self.thickness,
            )
            .translate(self.center_coordinate)
        )

        # subtracts the two boxes to leave a hollow box
        new_shape = outer_box.cut(inner_box)

        self.solid = new_shape

        return new_shape
