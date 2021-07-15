from typing import Optional, Tuple, Union

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
        extrusion_distance: The total extruded thickness of the coils
            when in the y-direction (centered extrusion)
        coil_count: The number of coils placed in the model
            (changing azimuth_placement_angle by dividing 360 by the amount
            given). Defaults to 1
            with_inner_leg: Boolean to include the inside of the Coils
        file_name_stp: Defults to "ToroidalFieldCoilRectangleRoundCorners.stp"
        file_name_stl: Defaults to "ToroidalFieldCoilRectangleRoundCorners.stl"
        material_tag: Defaults to "outter_tf_coil_mat"
        line_type: Sets the returned list to be populated by elements for
            MixedShape(). Defaults to True
        analyse: Defaults to False; if True returns values that are calculated
            for the 2D Shape
    """

    def __init__(
        self,
        lower_inner_coordinates: Tuple[float, float],
        mid_point_coordinates: Tuple[float, float],
        thickness: Union[float, int],
        distance: float,
        number_of_coils: int,
        with_inner_leg: Optional[bool] = True,
        stp_filename: Optional[str] = "ToroidalFieldCoilRectangleRoundCorners.stp",
        stl_filename: Optional[str] = "ToroidalFieldCoilRectangleRoundCorners.stl",
        material_tag: Optional[str] = "outter_tf_coil_mat",
        analyse: Optional[bool] = False,
        **kwargs
    ) -> None:

        super().__init__(
            distance=distance,
            stp_filename=stp_filename,
            stl_filename=stl_filename,
            material_tag=material_tag,
            **kwargs
        )

        self.lower_inner_coordinates = lower_inner_coordinates[0], lower_inner_coordinates[1]
        self.mid_point_coordinates = mid_point_coordinates[0], mid_point_coordinates[1]
        self.thickness = thickness
        self.number_of_coils = number_of_coils
        self.with_inner_leg = with_inner_leg

        self.analyse_attributes = [
            0,
            0,
            0,
            0
        ]

        ### Check if input values are what they meant to be ###
        if not isinstance(self.lower_inner_coordinates, tuple):
            raise TypeError("Invalid input - Coordinates must be a tuple")
 
                
        if not isinstance(self.mid_point_coordinates, tuple):
            raise TypeError("Invalid input - Coordinates must be a tuple")

        if not isinstance(self.thickness, float):
            if not isinstance(self.thickness, int):
                raise TypeError("Invalid input - Thickness must be a number")

        if not isinstance(distance, float):
            if not isinstance(distance, int):
                raise TypeError("Invalid input - Distance must be a number")

        if (number_of_coils % 1) != 0:
            raise TypeError(
                "Invalid input - Number of Coils must be an integer number")

        if len(lower_inner_coordinates) != 2 or len(
                mid_point_coordinates) != 2:
            raise ValueError(
                "The input tuples are too long or too short, they must be 2 element long")

        if self.lower_inner_coordinates[0] > self.mid_point_coordinates[0]:
            raise ValueError(
                "The middle point's x-coordinate must be larger than the lower inner point's x-coordinate")

        else:
            # Adding hidden attributes for analyse list population
            # inner base length of the coil
            self._base_length = mid_point_coordinates[0] - \
                lower_inner_coordinates[0]
            self.analyse_attributes[0] = self._base_length

            # height of the coil
            self._height = abs(
                mid_point_coordinates[1] - lower_inner_coordinates[1]) * 2
            self.analyse_attributes[1] = self._height

            """ Inner and outter radius of curvature for the corners
            The inner curvature is scales as a function of the base length
            of the coil and its thickness as long as the thickness does not exceed the base length
            if the thickness/base length ratio is larger or equal to 1
            it takes 10% of the thickness as the inner curve radius
            this to avoid having coordinates before the previous or at the same spot as Paramak
            cannot compute it"""

            if thickness / self._base_length >= 1:
                self._inner_curve_radius = thickness * 0.1
                self._outter_curve_radius = thickness * 1.1
                self.analyse_attributes[2] = self._inner_curve_radius
                self.analyse_attributes[3] = self._outter_curve_radius
            else:
                self._outter_curve_radius = (
                    1 + (thickness / self._base_length)) * thickness
                self._inner_curve_radius = (thickness**2) / self._base_length
                self.analyse_attributes[2] = self._inner_curve_radius
                self.analyse_attributes[3] = self._outter_curve_radius

    @property
    def azimuth_placement_angle(self):
        self.find_azimuth_placement_angle()
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, val):
        self._azimuth_placement_angle = val

    def find_points(self):
        """
        lower_inner_coordinates must be a 2 element tuple
        mid_point_coordinates must be a 2 elemenet tuple
        thickness must be a float or an int
        test=True will print the returned coordinates to console
        analyse=True will return values for volumetric and surface analysis for 3D parametric shape
        """

        lower_x, lower_z = self.lower_inner_coordinates
        mid_x, mid_z = self.mid_point_coordinates

        # redifine values to be floats to make it look consistent
        lower_x, lower_z, mid_x, mid_z, thickness = float(lower_x), float(
            lower_z), float(mid_x), float(mid_z), float(self.thickness)

        # Define differences to avoid miss claculation due to signs
        base_length = self.analyse_attributes[0]
        height = self.analyse_attributes[1]

        # 10 points/tuples for initial calculation and to get aux points
        p1 = (lower_x, lower_z)
        p2 = (p1[0] + base_length, p1[1])
        p3 = (p2[0], p2[1] + height)
        p4 = (p1[0], p1[1] + height)
        p5 = (p4[0], p4[1] + thickness)
        p6 = (p3[0], p4[1] + thickness)
        p7 = (p3[0] + thickness, p3[1])
        p8 = (p2[0] + thickness, p2[1])
        p9 = (p2[0], p2[1] - thickness)
        p10 = (lower_x, lower_z - thickness)

        inner_curve_radius = self.analyse_attributes[2]
        outter_curve_radius = self.analyse_attributes[3]

        """ New subroutines to calculate inner and outter curve mid-points, x and y displacement from existing points
            long shift does a sin(45)*radius of curvature shift
            short shift does a (1-sin(45))*radius of curvature shift """

        def shift_long(radius):
            """radius is the radius of curvature"""
            return (2**0.5) * 0.5 * radius

        def shift_short(radius):
            """radius is the radius of curvature"""
            return (2 - (2**0.5)) * 0.5 * radius

        p11 = (p2[0] - inner_curve_radius, p2[1])
        p12 = (p11[0] + shift_long(inner_curve_radius),
               p11[1] + shift_short(inner_curve_radius))
        p13 = (p2[0], p2[1] + inner_curve_radius)
        p14 = (p3[0], p3[1] - inner_curve_radius)
        p15 = (p14[0] - shift_short(inner_curve_radius),
               p14[1] + shift_long(inner_curve_radius))
        p16 = (p3[0] - inner_curve_radius, p3[1])
        p17 = (p6[0] - inner_curve_radius, p6[1])
        p18 = (p17[0] + shift_long(outter_curve_radius),
               p17[1] - shift_short(outter_curve_radius))
        p19 = (p14[0] + thickness, p14[1])
        p20 = (p8[0], p8[1] + inner_curve_radius)
        p21 = (p18[0], p20[1] - shift_long(outter_curve_radius))
        p22 = (p11[0], p11[1] - thickness)

        # List holding the points that are being returned by the function
        points = [
            p1,
            p11,
            p12,
            p13,
            p14,
            p15,
            p16,
            p4,
            p5,
            p17,
            p18,
            p19,
            p20,
            p21,
            p22,
            p10]
        # List that holds the points with the corresponding line types
        tri_points = []
        lines = ["straight"] + ['circle'] * 2 + ['straight'] + ['circle'] * 2 + \
            ['straight'] * 3 + ['circle'] * 2 + ['straight'] + ['circle'] * 2 + ['straight'] * 2

        for i in range(len(points)):
            tri_points.append(points[i] + (lines[i],))

        self.points = tri_points

        inner_p1 = (p1[0], p1[1])
        inner_p2 = (p1[0] + thickness, p1[1])
        inner_p3 = (p4[0] + thickness, p4[1])
        inner_p4 = (p4[0], p4[1])

        self.inner_leg_connection_points = [
            inner_p1, inner_p2, inner_p3, inner_p4]

    def find_azimuth_placement_angle(self):
        """ Finds the placement angles from the number of coils given in a 360 degree """
        angles = list(
            np.linspace(
                0,
                360,
                self.number_of_coils,
                endpoint=False))
        self.azimuth_placement_angle = angles

    def create_solid(self):
        """ Creates a Cadquery 3D geometry

        Returns:
            CadQuery solid: A 3D solid Volume """

        # Create solid from points
        points = [ps[:2] for ps in self.points]

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

        solid = wire.extrude(distance=-self.distance / 2, both=True)
        solid = self.rotate_solid(solid)

        cutting_wedge = calculate_wedge_cut(self)
        solid = self.perform_boolean_operations(solid, wedge_cut=cutting_wedge)

        self.solid = solid

        if self.with_inner_leg:
            inner_leg_solid = cq.Workplane(self.workplane)
            inner_leg_solid = inner_leg_solid.polyline(
                self.inner_leg_connection_points).close().extrude(
                distance=-self.distance / 2, both=True)

            inner_leg_solid = self.rotate_solid(inner_leg_solid)
            inner_leg_solid = self.perform_boolean_operations(
                inner_leg_solid, wedge_cut=cutting_wedge)

            solid = cq.Compound.makeCompound(
                [a.val() for a in [inner_leg_solid, solid]])

            self.solid = solid

        return solid
