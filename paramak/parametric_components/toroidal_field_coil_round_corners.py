from typing import Optional, Tuple, Union
from _pytest.python_api import raises

import cadquery as cq
import numpy as np
from paramak.parametric_shapes.extruded_mixed_shape import ExtrudeMixedShape
from paramak.utils import calculate_wedge_cut


class ToroidalFieldCoilRectangleRoundCorners(ExtrudeMixedShape):
    """Creates geometry for TF coil with rounded corners. Finds the coordinates
    for verteces of a TF coil, in a 2D profile on the XZ plane using the main
    function find_points() which takes 3 positional arguments for the TF coil
    parameters, and takes three additional boolean arguments.

    Arguments:
        lower_inner_coordinates (Tuple): the (X,Z) coordinate of the inner
            corner of the lower end of the coil (cm)
        mid_point_coordinates (Tuple): the (X,Z) coordinate of the mid
            point of the vertical section (cm)
        thickness: The thickness in the (X,Z) plane of the toroidal
        field coils (cm)
        extrusiondistance: The total extruded thickness of the coils
            when in the y-direction (centered extrusion)
        coil_count: The number of coils placed in the model
            (changing azimuth_placement_angle by dividing 360 by the amount
            given). Defaults to 1
        with_inner_leg: Boolean to include the inside of the Coils
            defaults to False
        file_name_stp: Defults to "ToroidalFieldCoilRectangleRoundCorners.stp"
        file_name_stl: Defaults to "ToroidalFieldCoilRectangleRoundCorners.stl"
        material_tag: Defaults to "outter_tf_coil_mat"
    """

    def __init__(
        self,
        lower_inner_coordinates: Tuple[float, float],
        mid_point_coordinates: Tuple[float, float],
        thickness: Union[float, int],
        distance: float,
        number_of_coils: int = 1,
        with_inner_leg: Optional[bool] = False,
        stp_filename: Optional[str] = "ToroidalFieldCoilRectangleRoundCorners.stp",
        stl_filename: Optional[str] = "ToroidalFieldCoilRectangleRoundCorners.stl",
        material_tag: Optional[str] = "outter_tf_coil_mat",
        **kwargs
    ) -> None:

        super().__init__(
            distance=distance,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            material_tag=material_tag,
            **kwargs
        )

        self._lower_inner_coordinates = lower_inner_coordinates
        self._mid_point_coordinates = mid_point_coordinates
        self._thickness = thickness
        self._distance = distance
        self.number_of_coils = number_of_coils
        self._with_inner_leg = with_inner_leg
        self._inner_leg_connection_points = []
        self._analyse_attributes = [
            0,
            0,
            0,
            0
        ]
        self._base_length = 0
        self._height = 0
        self._inner_curve_radius = 0
        self._outter_curve_radius = 0

        if len(lower_inner_coordinates) != 2 or len(
                mid_point_coordinates) != 2:
            msg = ('The input tuples are too long or too short, they must be '
                   '2 element long')
            raise ValueError(msg)

        if self._lower_inner_coordinates[0] > self._mid_point_coordinates[0]:
            raise ValueError(
                "The middle point's x-coordinate must be larger than the lower",
                "inner point's x-coordinate")

    def _find_base_and_height(self):
        # Adding hidden attributes for analyse list population
        # inner base length of the coil
        self._base_length = self._mid_point_coordinates[0] - \
            self._lower_inner_coordinates[0]
        self._analyse_attributes[0] = self._base_length

        # height of the coil
        self._height = abs(
            self.mid_point_coordinates[1] - self.lower_inner_coordinates[1]) * 2
        self._analyse_attributes[1] = self._height

    def _find_radii(self):
        # Inner and outter radius of curvature for the corners
        # The inner curvature is scales as a function of the base length
        # of the coil and its thickness as long as the thickness does not exceed the base length
        # if the thickness/base length ratio is larger or equal to 1
        # it takes 10% of the thickness as the inner curve radius
        # this to avoid having coordinates before the previous or at the same spot as Paramak
        # cannot compute it
        self._find_base_and_height()
        if self._thickness / self._base_length >= 1:
            self._inner_curve_radius = self._thickness * 0.1
            self._outter_curve_radius = self._thickness * 1.1
        else:
            self._outter_curve_radius = (
                1 + (self._thickness / self._base_length)) * self._thickness
            self._inner_curve_radius = (self._thickness**2) / self._base_length

        self._analyse_attributes[2] = self._inner_curve_radius
        self._analyse_attributes[3] = self._outter_curve_radius

    @property
    def azimuth_placement_angle(self):
        self.find_azimuth_placement_angle()
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, val):
        self._azimuth_placement_angle = val

    @property
    def lower_inner_coordinates(self):
        return self._lower_inner_coordinates

    @lower_inner_coordinates.setter
    def lower_inner_coordinates(self, val):
        if not isinstance(val, tuple):
            raise TypeError("Input Coordinate must be a tuple!")
        if len(val) != 2:
            raise ValueError("Input Tuple must be 2 elements long!")
        if not isinstance(val[0], (float, int)):
            raise TypeError("Input X Coordinates must be a number!")
        if not isinstance(val[1], (float, int)):
            raise TypeError("Input Z Coordinates must be a number!")
        if val[0] > self._mid_point_coordinates[0]:
            raise ValueError(
                "Mid Point's x-coordinate, must be larger than lower point's!")
        self._lower_inner_coordinates = val

    @property
    def mid_point_coordinates(self):
        return self._mid_point_coordinates

    @mid_point_coordinates.setter
    def mid_point_coordinates(self, val):
        if not isinstance(val, tuple):
            raise TypeError("Input Coordinate must be a tuple!")
        if len(val) != 2:
            raise ValueError("Input Tuple must be 2 elements long!")
        if not isinstance(val[0], (float, int)):
            raise TypeError("Input X Coordinates must be a number!")
        if not isinstance(val[1], (float, int)):
            raise TypeError("Input Z Coordinates must be a number!")
        if val[0] < self._lower_inner_coordinates[0]:
            raise ValueError(
                "Mid Point's x-coordinate, must be larger than lower point's!")
        self._mid_point_coordinates = val

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Input Thickness must be a number!")
        self._find_radii()
        self._thickness = val

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Input Distance must be a number!")
        self._distance = val

    @property
    def number_of_coils(self):
        return self._number_of_coils

    @number_of_coils.setter
    def number_of_coils(self, val):
        if not isinstance(val, int):
            raise TypeError("Input Distance must be an integer number!")
        self._number_of_coils = val

    @property
    def analyse_attributes(self):
        self.find_points()
        return self._analyse_attributes

    @property
    def with_inner_leg(self):
        return self._with_inner_leg

    @with_inner_leg.setter
    def with_inner_leg(self, val):
        if not isinstance(val, bool):
            raise TypeError("With Inner Leg must be True or False")

    def find_points(self):
        """
        lower_inner_coordinates must be a 2 element tuple
        mid_point_coordinates must be a 2 elemenet tuple
        thickness must be a float or an int
        """
        self._find_radii()

        lower_x, lower_z = self._lower_inner_coordinates
        mid_x, mid_z = self._mid_point_coordinates

        # redifine values to be floats to make it look consistent
        lower_x, lower_z, mid_x, mid_z, thickness = float(lower_x), float(
            lower_z), float(mid_x), float(mid_z), float(self._thickness)

        # Define differences to avoid miss claculation due to signs
        base_length = self._analyse_attributes[0]
        height = self._analyse_attributes[1]

        # 10 points/tuples for initial calculation and to get aux points
        point1 = (lower_x, lower_z)
        point2 = (point1[0] + base_length, point1[1])
        point3 = (point2[0], point2[1] + height)
        point4 = (point1[0], point1[1] + height)
        point5 = (point4[0], point4[1] + thickness)
        point6 = (point3[0], point4[1] + thickness)
        #point7 = (point3[0] + thickness, point3[1])
        point8 = (point2[0] + thickness, point2[1])
        #point9 = (point2[0], point2[1] - thickness)
        point10 = (lower_x, lower_z - thickness)

        inner_curve_radius = self._analyse_attributes[2]
        outter_curve_radius = self._analyse_attributes[3]

        #  New subroutines to calculate inner and outter curve mid-points,    #
        #  x and y displacement from existing points                          #
        #  long shift does a sin(45)*radius of curvature shift                #
        #  short shift does a (1-sin(45))*radius of curvature shift           #

        def shift_long(radius):
            """radius is the radius of curvature"""
            return (2**0.5) * 0.5 * radius

        def shift_short(radius):
            """radius is the radius of curvature"""
            return (2 - (2**0.5)) * 0.5 * radius

        point11 = (point2[0] - inner_curve_radius, point2[1])
        point12 = (point11[0] + shift_long(inner_curve_radius),
                   point11[1] + shift_short(inner_curve_radius))
        point13 = (point2[0], point2[1] + inner_curve_radius)
        point14 = (point3[0], point3[1] - inner_curve_radius)
        point15 = (point14[0] - shift_short(inner_curve_radius),
                   point14[1] + shift_long(inner_curve_radius))
        point16 = (point3[0] - inner_curve_radius, point3[1])
        point17 = (point6[0] - inner_curve_radius, point6[1])
        point18 = (point17[0] + shift_long(outter_curve_radius),
                   point17[1] - shift_short(outter_curve_radius))
        point19 = (point14[0] + thickness, point14[1])
        point20 = (point8[0], point8[1] + inner_curve_radius)
        point21 = (point18[0], point20[1] - shift_long(outter_curve_radius))
        point22 = (point11[0], point11[1] - thickness)

        # List holding the points that are being returned by the function
        points = [
            point1,
            point11,
            point12,
            point13,
            point14,
            point15,
            point16,
            point4,
            point5,
            point17,
            point18,
            point19,
            point20,
            point21,
            point22,
            point10]
        # List that holds the points with the corresponding line types
        tri_points = []
        lines = ["straight"] + ['circle'] * 2 + ['straight'] \
            + ['circle'] * 2 + ['straight'] * 3 + ['circle'] * 2 \
            + ['straight'] + ['circle'] * 2 + ['straight'] * 2

        for i in enumerate(points):
            tri_points.append(points[i[0]] + (lines[i[0]],))

        self.points = tri_points

        inner_point1 = (point1[0], point1[1])
        inner_point2 = (point1[0] + thickness, point1[1])
        inner_point3 = (point4[0] + thickness, point4[1])
        inner_point4 = (point4[0], point4[1])

        self._inner_leg_connection_points = [
            inner_point1, inner_point2, inner_point3, inner_point4]

        return tri_points

    def find_azimuth_placement_angle(self):
        """ Finds the placement angles from the number of coils
            given in a 360 degree """

        angles = list(
            np.linspace(
                0,
                360,
                self._number_of_coils,
                endpoint=False))
        self.azimuth_placement_angle = angles

    def create_solid(self):
        """ Creates a Cadquery 3D geometry

        Returns:
            CadQuery solid: A 3D solid Volume """

        # Create solid from points
        points = [ps[:2] for ps in self.processed_points]

        wire = cq.Workplane(self.workplane).moveTo(points[0][0], points[0][1]) \
            .lineTo(points[1][0], points[1][1]) \
            .threePointArc((points[2][0], points[2][1]), (points[3][0], points[3][1])) \
            .lineTo(points[4][0], points[4][1]) \
            .threePointArc((points[5][0], points[5][1]), (points[6][0], points[6][1])) \
            .lineTo(points[7][0], points[7][1]) \
            .lineTo(points[8][0], points[8][1]) \
            .lineTo(points[9][0], points[9][1]) \
            .threePointArc((points[10][0], points[10][1]), (points[11][0], points[11][1])) \
            .lineTo(points[12][0], points[12][1]) \
            .threePointArc((points[13][0], points[13][1]), (points[14][0], points[14][1])) \
            .lineTo(points[15][0], points[15][1]) \
            .lineTo(points[16][0], points[16][1]).close().consolidateWires()

        solid = wire.extrude(distance=-self._distance / 2, both=True)
        solid = self.rotate_solid(solid)

        cutting_wedge = calculate_wedge_cut(self)
        solid = self.perform_boolean_operations(solid, wedge_cut=cutting_wedge)

        self.solid = solid

        if self._with_inner_leg:
            inner_leg_solid = cq.Workplane(self.workplane)
            inner_leg_solid = inner_leg_solid.polyline(
                self._inner_leg_connection_points).close().extrude(
                distance=-self._distance / 2, both=True)

            inner_leg_solid = self.rotate_solid(inner_leg_solid)
            inner_leg_solid = self.perform_boolean_operations(
                inner_leg_solid, wedge_cut=cutting_wedge)

            solid = cq.Compound.makeCompound(
                [a.val() for a in [inner_leg_solid, solid]])

            self.solid = solid

        return solid
