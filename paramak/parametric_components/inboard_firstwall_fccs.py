from paramak import RotateMixedShape, CenterColumnShieldCylinder, \
    CenterColumnShieldHyperbola, CenterColumnShieldFlatTopHyperbola, \
    CenterColumnShieldPlasmaHyperbola, CenterColumnShieldCircular, \
    CenterColumnShieldFlatTopCircular


class InboardFirstwallFCCS(RotateMixedShape):
    """An inboard firstwall component that builds a constant thickness layer
    from the central column shield. The center column shields can be of type:
    CenterColumnShieldCylinder, CenterColumnShieldHyperbola,
    CenterColumnShieldFlatTopHyperbola, CenterColumnShieldCircular,
    CenterColumnShieldPlasmaHyperbola or CenterColumnShieldFlatTopCircular

    Args:
        central_column_shield (paramak.Shape): The central column shield object
            to build from
        thickness (float): the radial thickness of the firstwall (cm)
        stp_filename (str, optional): Defaults to "InboardFirstwallFCCS.stp".
        stl_filename (str, optional): Defaults to "InboardFirstwallFCCS.stl".
        material_tag (str, optional): Defaults to "firstwall_mat".
    """

    def __init__(
        self,
        central_column_shield,
        thickness,
        stp_filename="InboardFirstwallFCCS.stp",
        stl_filename="InboardFirstwallFCCS.stl",
        material_tag="firstwall_mat",
        **kwargs
    ):

        super().__init__(
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            material_tag=material_tag,
            **kwargs
        )

        self.central_column_shield = central_column_shield
        self.thickness = thickness

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        self._thickness = value

    @property
    def central_column_shield(self):
        return self._central_column_shield

    @central_column_shield.setter
    def central_column_shield(self, value):
        self._central_column_shield = value

    @property
    def solid(self):
        if self.get_hash() != self.hash_value:
            self.create_solid()
        return self._solid

    @solid.setter
    def solid(self, value):
        self._solid = value

    def create_solid(self):
        """Creates a CadQuery 3D solid

           Returns:
              A CadQuery solid: A 3D solid volume
        """

        if isinstance(self.central_column_shield, CenterColumnShieldCylinder):
            firstwall = CenterColumnShieldCylinder(
                height=self.central_column_shield.height,
                inner_radius=self.central_column_shield.inner_radius,
                outer_radius=self.central_column_shield.outer_radius + self.thickness,
                cut=self.central_column_shield,
                rotation_angle=self.rotation_angle)

        elif isinstance(self.central_column_shield, CenterColumnShieldHyperbola):
            firstwall = CenterColumnShieldHyperbola(
                height=self.central_column_shield.height,
                inner_radius=self.central_column_shield.inner_radius,
                mid_radius=self.central_column_shield.mid_radius + self.thickness,
                outer_radius=self.central_column_shield.outer_radius + self.thickness,
                cut=self.central_column_shield,
                rotation_angle=self.rotation_angle)

        elif isinstance(self.central_column_shield, CenterColumnShieldFlatTopHyperbola):
            firstwall = CenterColumnShieldFlatTopHyperbola(
                height=self.central_column_shield.height,
                arc_height=self.central_column_shield.arc_height,
                inner_radius=self.central_column_shield.inner_radius,
                mid_radius=self.central_column_shield.mid_radius + self.thickness,
                outer_radius=self.central_column_shield.outer_radius + self.thickness,
                cut=self.central_column_shield,
                rotation_angle=self.rotation_angle)

        elif isinstance(self.central_column_shield, CenterColumnShieldPlasmaHyperbola):
            firstwall = CenterColumnShieldPlasmaHyperbola(
                height=self.central_column_shield.height,
                inner_radius=self.central_column_shield.inner_radius,
                mid_offset=self.central_column_shield.mid_offset - self.thickness,
                edge_offset=self.central_column_shield.edge_offset - self.thickness,
                cut=self.central_column_shield,
                rotation_angle=self.rotation_angle)

        elif isinstance(self.central_column_shield, CenterColumnShieldCircular):
            firstwall = CenterColumnShieldCircular(
                height=self.central_column_shield.height,
                inner_radius=self.central_column_shield.inner_radius,
                mid_radius=self.central_column_shield.mid_radius + self.thickness,
                outer_radius=self.central_column_shield.outer_radius + self.thickness,
                cut=self.central_column_shield,
                rotation_angle=self.rotation_angle)

        elif isinstance(self.central_column_shield, CenterColumnShieldFlatTopCircular):
            firstwall = CenterColumnShieldFlatTopCircular(
                height=self.central_column_shield.height,
                arc_height=self.central_column_shield.arc_height,
                inner_radius=self.central_column_shield.inner_radius,
                mid_radius=self.central_column_shield.mid_radius + self.thickness,
                outer_radius=self.central_column_shield.outer_radius + self.thickness,
                cut=self.central_column_shield,
                rotation_angle=self.rotation_angle)

        else:

            raise ValueError(
                "InboardFirstwallFCCS.central_column_shield must be an \
                instance of CenterColumnShieldCylinder, CenterColumnShieldHyperbola, \
                CenterColumnShieldFlatTopHyperbola, CenterColumnShieldPlasmaHyperbola, \
                CenterColumnShieldCircular, CenterColumnShieldFlatTopCircular")

        self.solid = firstwall.solid

        self.hash_value = self.get_hash()

        return firstwall.solid
