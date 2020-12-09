
from paramak import CuttingWedgeFS, Shape


class ShellFS(Shape):
    """Shell From Shape. Creates a shell casing for the provided shape object.
    Warning some shapes are too complex to shell. The Shell is cut / trimmed
    with a paramak.CuttingWedgeFS based on the shape passed. This ensures that
    the shell does does not exceed the rotation angle of the passed shape.

    Args:
        shape (paramak.Shape): the shape to create a shell / 3D offset around
        thickness (float): the thickness of the shell casing around the shape
            (cm). Passed directly to CadQuery.shell(). Defaults to 10.
        kind (str, optional) : the method used to connect gaps in the resulting
            shelled shape. Options include 'arc' or 'intersection'. Use 'arc'
            for rounded edges 'intersection' for sharp edges. Passed directly
            to CadQuery.shell(). Defaults to intersection.
        stp_filename (str, optional): defaults to
            "ShellFS.stp".
        stl_filename (str, optional): defaults to
            "ShellFS.stl".
        material_tag (str, optional): defaults to "pf_coil_case_mat".
    """

    def __init__(
        self,
        shape,
        thickness=10,
        kind='intersection',
        stp_filename="ShellFS.stp",
        stl_filename="ShellFS.stl",
        material_tag="pf_coil_case_mat",
        **kwargs
    ):

        super().__init__(
            material_tag=material_tag,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            **kwargs
        )

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

        solid = self.shape.solid.shell(
            thickness=self.thickness,
            kind=self.kind,
        )

        if self.shape.rotation_angle < 360:
            # rotation angle is set by the self.shapes rotation angle
            cutting_wedge = CuttingWedgeFS(self.shape)
            # this trims the sold so that it does not exceed the rotation angle
            solid = solid.cut(cutting_wedge.solid)

        self.solid = solid

        return solid
