import cadquery as cq

from paramak import Shape


class ShellFS(Shape):
    """Shell From Shape. Creates a shell casing for the provided shape object.
    Warning some shapes are too complex to shell. If using a rotated shape then
    setting the rotation angle to 360 can simplify the shell. Then intersecting
    the resulting shell with the WedgeCutterFs can reduce the shell back down
    to the original rotation angle of the shape.

    Args:
        shape: the shape to create a shell / 3D offset around
        thickness: the thickness of the shell casing around the shape (cm).
            Passed directly to CadQuery.shell(). Defaults to 10.0.
        kind: the method used to connect gaps in the resulting shelled shape.
            Options include 'arc' or 'intersection'. Use 'arc' for rounded
            edges 'intersection' for sharp edges. Passed directly to
            CadQuery.shell(). Defaults to intersection.
    """

    def __init__(self, shape: Shape, thickness: float = 10.0, kind: str = "intersection", **kwargs):

        super().__init__(**kwargs)

        self.shape = shape
        self.thickness = thickness
        self.kind = kind

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, value):
        self._shape = value

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, thickness):
        self._thickness = thickness

    def create_solid(self):
        """Creates a 3D solid by creating a shell around a Shape"""

        if isinstance(self.shape, cq.Workplane):
            solid = self.shape.shell(
                thickness=self.thickness,
                kind=self.kind,
            )
        else:
            solid = self.shape.solid.shell(
                thickness=self.thickness,
                kind=self.kind,
            )

        self.solid = solid

        return solid
