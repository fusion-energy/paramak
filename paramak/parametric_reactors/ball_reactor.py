
import operator

import cadquery as cq

import paramak


class BallReactor(paramak.Reactor):
    """Creates geometry for a simple ball reactor including a plasma,
    cylindical center column shielding, square toroidal field coils

    :param major_radius: 
    :type height: float

    :return: a shape object that has generic functionality
    :rtype: paramak shape object
    """

    def __init__(
        self,
        inner_bore_radial_thickness,
        inboard_tf_leg_radial_thickness,
        center_column_radial_thickness,
        inner_plasma_gap_radial_thickness,
        plasma_radial_thickness,
        outer_plasma_gap_radial_thickness,
        firstwall_radial_thickness,
        blanket_radial_thickness,

        elongation,
        triangularity,
        
        number_of_tf_coils,
        # divertor_width,
        rotation_angle = 180
    ):

        super().__init__()

        self.inner_bore_radial_thickness = inner_bore_radial_thickness
        self.inboard_tf_leg_radial_thickness = inboard_tf_leg_radial_thickness
        self.center_column_radial_thickness = center_column_radial_thickness
        self.inner_plasma_gap_radial_thickness = inner_plasma_gap_radial_thickness
        self.plasma_radial_thickness = plasma_radial_thickness
        self.outer_plasma_gap_radial_thickness = outer_plasma_gap_radial_thickness
        self.firstwall_radial_thickness = firstwall_radial_thickness
        self.blanket_radial_thickness = blanket_radial_thickness

        # self.outer_equatorial_point = outer_equatorial_point
        # self.inner_equatorial_point = inner_equatorial_point

        # # sets major raduis and minor radius from equatorial_points to allow a radial build
        # # this helps avoid the plasma overlapping the center column and such things

        inner_equatorial_point = inner_bore_radial_thickness + inboard_tf_leg_radial_thickness + center_column_radial_thickness + inner_plasma_gap_radial_thickness
        outer_equatorial_point = inner_equatorial_point + plasma_radial_thickness

        self.major_radius = (inner_equatorial_point + plasma_radial_thickness + inner_equatorial_point) /2
        self.minor_radius = ((outer_equatorial_point + inner_equatorial_point) /2 )-inner_equatorial_point

        self.elongation = elongation
        self.triangularity = triangularity
        self.rotation_angle = rotation_angle

        # self.offset_from_plasma = offset_from_plasma
        # self.blanket_thickness = blanket_thickness
        


        self.number_of_tf_coils = number_of_tf_coils
        # self.divertor_width = divertor_width

        self.create_components()


    def create_components(self):

        plasma = paramak.Plasma(major_radius=self.major_radius,
                                minor_radius=self.minor_radius,
                                elongation=self.elongation,
                                triangularity=self.triangularity,
                                rotation_angle=self.rotation_angle)
        plasma.create_solid()

        # the inner bore is the first measurement

        reactor_radius = self.inner_bore_radial_thickness

        inboard_tf_coils = paramak.InnerTfCoilsCircular(
            height=plasma.high_point[1] + abs(plasma.low_point[1]) + 2*self.outer_plasma_gap_radial_thickness + 2*self.blanket_radial_thickness,
            inner_radius = reactor_radius,
            outer_radius = reactor_radius+self.inboard_tf_leg_radial_thickness,
            number_of_coils = self.number_of_tf_coils,
            gap_size=10,
            stp_filename="inboard_tf_coils.stp",
            material_tag="inboard_tf_coils_material",
        )

        self.add_shape_or_component(inboard_tf_coils)

        reactor_radius = reactor_radius + self.inboard_tf_leg_radial_thickness

        center_column_shield = paramak.CenterColumnShieldCylinder(
            height=plasma.high_point[1] + abs(plasma.low_point[1]) + 2*self.outer_plasma_gap_radial_thickness + 2*self.blanket_radial_thickness,
            inner_radius=reactor_radius,
            outer_radius=reactor_radius+self.center_column_radial_thickness,
            rotation_angle=self.rotation_angle,
            # color=centre_column_color,
            stp_filename="center_column_shield.stp",
            material_tag="center_column_material",
        )
        self.add_shape_or_component(center_column_shield)

        reactor_radius = reactor_radius+self.center_column_radial_thickness
        
        reactor_radius = reactor_radius+self.inner_plasma_gap_radial_thickness

        # The plasma would go here but other components need the plasma height so it had to go earlier

        self.add_shape_or_component(plasma)

        reactor_radius = reactor_radius + self.plasma_radial_thickness

        reactor_radius = reactor_radius + self.outer_plasma_gap_radial_thickness

        firstwall = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(reactor_radius, 0),
            inner_upper_point=(plasma.high_point[0], plasma.high_point[1]+self.outer_plasma_gap_radial_thickness),
            inner_lower_point=(plasma.low_point[0], plasma.low_point[1]-self.outer_plasma_gap_radial_thickness),
            thickness=self.firstwall_radial_thickness,
            rotation_angle=self.rotation_angle,
            stp_filename='firstwall.stp'
        )

        self.add_shape_or_component(firstwall)

        reactor_radius = reactor_radius + self.firstwall_radial_thickness

        blanket = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(reactor_radius, 0),
            inner_upper_point=(plasma.high_point[0], plasma.high_point[1]+self.outer_plasma_gap_radial_thickness+self.firstwall_radial_thickness),
            inner_lower_point=(plasma.low_point[0], plasma.low_point[1]-(self.outer_plasma_gap_radial_thickness+self.firstwall_radial_thickness)),
            thickness=self.blanket_radial_thickness,
            rotation_angle=self.rotation_angle
        )

        reactor_radius = reactor_radius + self.blanket_radial_thickness

        self.add_shape_or_component(blanket)

        # space_for_divertor = plasma.x_point - self.center_column_radial_thickness

        # print('space_for_divertor', space_for_divertor)

        divertor_upper_part = paramak.RotateStraightShape(points=[
            (self.center_column_radial_thickness + self.inboard_tf_leg_radial_thickness + self.inner_bore_radial_thickness, plasma.high_point[1] + self.outer_plasma_gap_radial_thickness + self.firstwall_radial_thickness + self.blanket_radial_thickness),
            (self.center_column_radial_thickness + self.inboard_tf_leg_radial_thickness + self.inner_bore_radial_thickness, plasma.high_point[1] + self.outer_plasma_gap_radial_thickness),
            (plasma.high_point[0], plasma.high_point[1] + self.outer_plasma_gap_radial_thickness),
            (plasma.high_point[0], plasma.high_point[1] + self.outer_plasma_gap_radial_thickness+self.firstwall_radial_thickness+ self.blanket_radial_thickness),
            ],
            stp_filename='divertor_upper.stp',
            rotation_angle=self.rotation_angle,
            material_tag='divertor_material'
            )

        self.add_shape_or_component(divertor_upper_part)

        divertor_lower_part = paramak.RotateStraightShape(points=[
            (self.center_column_radial_thickness+self.inboard_tf_leg_radial_thickness+self.inner_bore_radial_thickness,plasma.low_point[1] - (self.outer_plasma_gap_radial_thickness  + self.firstwall_radial_thickness + self.blanket_radial_thickness)),
            (self.center_column_radial_thickness+self.inboard_tf_leg_radial_thickness+self.inner_bore_radial_thickness,plasma.low_point[1] - self.outer_plasma_gap_radial_thickness),
            (plasma.low_point[0], plasma.low_point[1] - self.outer_plasma_gap_radial_thickness),
            (plasma.low_point[0], plasma.low_point[1] - (self.outer_plasma_gap_radial_thickness+self.firstwall_radial_thickness+ self.blanket_radial_thickness)),
            ],
            stp_filename='divertor_lower.stp',
            rotation_angle=self.rotation_angle,
            material_tag='divertor_material'
            )

        self.add_shape_or_component(divertor_lower_part)


        # The height of this center column is calculated using the plasma high



