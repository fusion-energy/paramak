import numpy as np
import math
from paramak import ExtrudeStraightShape, CenterColumnShieldCylinder, CenterColumnShieldHyperbola, CenterColumnShieldFlatTopHyperbola, CenterColumnShieldPlasmaHyperbola, CenterColumnShieldCircular, CenterColumnShieldFlatTopCircular


class InboardFirstwallFCCS(ExtrudeStraightShape):
    """An inboard firstwall component that builds a constant thickness layer
    from the central column shield.

    Args:
        central_column_shield (paramak.Shape): The central column shield object to build from
        thickness (float): the radial thickness of the firstwall (cm)
        
    Keyword Args:
        name (str): the legend name used when exporting a html graph of the shape.
        color (sequences of 3 or 4 floats each in the range 0-1): the color to use when
            exportin as html graphs or png images.
        material_tag (str): The material name to use when exporting the neutronics description.
        stp_filename (str): The filename used when saving stp files as part of a reactor.
        azimuth_placement_angle (float or iterable of floats): The angle or angles to use when
            rotating the shape on the azimuthal axis.
        rotation_angle (float): The rotation angle to use when revolving the solid (degrees).
        workplane (str): The orientation of the CadQuery workplane. Options are XY, YZ or XZ.
        intersect (CadQuery object): An optional CadQuery object to perform a boolean intersect with
            this object.
        cut (CadQuery object): An optional CadQuery object to perform a boolean cut with this object.
        union (CadQuery object): An optional CadQuery object to perform a boolean union with this object.
        tet_mesh (str): Insert description.
        physical_groups (type): Insert description.

    Returns:
        a paramak shape object: A shape object that has generic functionality
        with points determined by the find_points() method. A CadQuery solid
        of the shape can be called via shape.solid.
    """

    def __init__(
        self,
        central_column_shield,
        thickness,
        stp_filename="InboardFirstwallFCCS.stp",
        stl_filename="InboardFirstwallFCCS.stl",
        color=(0.5, 0.5, 0.5),
        azimuth_placement_angle=0,
        material_tag="firstwall_mat",
        name=None,
        **kwargs
    ):

        default_dict = {
            "points": None,
            "workplane": "XY",
            "solid": None,
            "intersect": None,
            "cut": None,
            "union": None,
            "tet_mesh": None,
            "physical_groups": None,
        }

        for arg in kwargs:
            if arg in default_dict:
                default_dict[arg] = kwargs[arg]

        super().__init__(
            distance=distance,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            color=color,
            azimuth_placement_angle=azimuth_placement_angle,
            material_tag=material_tag,
            name=name,
            hash_value=None,
            **default_dict
        )

        self.central_column_shield = central_column_shield
        self.thickness = thickness
        self.outer_radius = outer_radius

        self.find_points()

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

    def find_points(self):
        """Finds the points that describe the 2D profile of the tf coil shape"""

    def create_solid(self):
        """Creates a 3d solid

           Returns:
              A CadQuery solid: A 3D solid volume
        """

        if isinstance(self.central_column_shield, CenterColumnShieldCylinder):
            solid = CenterColumnShieldCylinder(
                height=self.central_column_shield.height,
                inner_radius=self.central_column_shield.inner_radius
                outer_radius=self.central_column_shield.outer_radius+self.thickness,
                cut = self.central_column_shield)
#         if isinstance(self.central_column_shield, CenterColumnShieldHyperbola):


# height, inner_radius, mid_radius, outer_radius

#         if isinstance(self.central_column_shield, CenterColumnShieldFlatTopHyperbola):
            
#             height, arc_height, inner_radius, mid_radius, outer_radius
#         if isinstance(self.central_column_shield, CenterColumnShieldPlasmaHyperbola):
# height, inner_radius, mid_offset, edge_offset
#         if isinstance(self.central_column_shield, CenterColumnShieldCircular):
# height, inner_radius, mid_radius, outer_radius
#         if isinstance(self.central_column_shield, CenterColumnShieldFlatTopCircular):
# height, arc_height, inner_radius, mid_radius, outer_radius

        self.hash_value = self.get_hash()

        return solid