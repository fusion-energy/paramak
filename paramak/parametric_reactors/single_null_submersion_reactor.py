import math
import operator

import cadquery as cq 

import paramak


class SingleNullSubmersionTokamak(paramak.SubmersionTokamak):

    def __init__(
        self,
        inner_bore_radial_thickness,
        inboard_tf_leg_radial_thickness,
        center_column_shield_radial_thickness,
        inboard_blanket_radial_thickness,
        firstwall_radial_thickness,
        inner_plasma_gap_radial_thickness,
        plasma_radial_thickness,
        divertor_radial_thickness,
        support_radial_thickness,
        outer_plasma_gap_radial_thickness,
        outboard_blanket_radial_thickness,
        blanket_rear_wall_radial_thickness,
        plasma_high_point,
        number_of_tf_coils=16,
        rotation_angle=360,
        outboard_tf_coil_radial_thickness=None,
        tf_coil_to_rear_blanket_radial_gap=None,
        tf_coil_poloidal_thickness=None,
        pf_coil_vertical_thicknesses=None,
        pf_coil_radial_thicknesses=None,
        pf_coil_to_tf_coil_radial_gap=None,
        divertor_position="upper",
        support_position="upper"
    ):

        super().__init__(
            inner_bore_radial_thickness = inner_bore_radial_thickness,
            inboard_tf_leg_radial_thickness = inboard_tf_leg_radial_thickness,
            center_column_shield_radial_thickness = center_column_shield_radial_thickness,
            inboard_blanket_radial_thickness = inboard_blanket_radial_thickness,
            firstwall_radial_thickness = firstwall_radial_thickness,
            inner_plasma_gap_radial_thickness = inner_plasma_gap_radial_thickness,
            plasma_radial_thickness = plasma_radial_thickness,
            outer_plasma_gap_radial_thickness = outer_plasma_gap_radial_thickness,
            outboard_blanket_radial_thickness = outboard_blanket_radial_thickness,
            blanket_rear_wall_radial_thickness = blanket_rear_wall_radial_thickness,
            pf_coil_radial_thicknesses = pf_coil_radial_thicknesses,
            pf_coil_to_tf_coil_radial_gap = pf_coil_to_tf_coil_radial_gap,
            outboard_tf_coil_radial_thickness = outboard_tf_coil_radial_thickness,
            tf_coil_poloidal_thickness = tf_coil_poloidal_thickness,
            divertor_radial_thickness = divertor_radial_thickness,
            support_radial_thickness = support_radial_thickness,
            plasma_high_point = plasma_high_point,
            tf_coil_to_rear_blanket_radial_gap = tf_coil_to_rear_blanket_radial_gap,
            pf_coil_vertical_thicknesses = pf_coil_vertical_thicknesses,
            number_of_tf_coils = number_of_tf_coils,
            rotation_angle = rotation_angle
        )

        self.major_radius = None
        self.minor_radius = None
        self.elongation = None
        self.triangularity = None

        self.divertor_position = divertor_position
        self.support_position = support_position
        self.create_components_single_null()
        

    @property
    def divertor_position(self):
        return self._divertor_position

    @divertor_position.setter
    def divertor_position(self, value):
        acceptable_values = ["upper", "lower"]
        if value in acceptable_values:
            self._divertor_position = value
        else:
            raise ValueError("divertor position must be 'upper' or 'lower'")

    @property
    def support_position(self):
        return self._support_position

    @support_position.setter
    def support_position(self, value):
        acceptable_values = ["upper", "lower"]
        if value in acceptable_values:
            self._support_position = value
        else:
            raise ValueError("support position must be 'upper' or 'lower'")

    def create_components_single_null(self):

        # this calls each method for constructing the reactor components by passing the
        # relevant parameters/objects to each method which return more objects

        shapes_or_components = []

        (
            inner_bore_start_radius,
            inner_bore_end_radius,
            inboard_tf_coils_start_radius,
            inboard_tf_coils_end_radius,
            center_column_shield_start_radius,
            center_column_shield_end_radius,
            inboard_blanket_start_radius,
            inboard_blanket_end_radius,
            inboard_firstwall_start_radius,
            inboard_firstwall_end_radius,
            inner_plasma_gap_start_radius,
            inner_plasma_gap_end_radius,
            plasma_start_radius,
            plasma_end_radius,
            outer_plasma_gap_start_radius,
            outer_plasma_gap_end_radius,
            outboard_firstwall_start_radius,
            outboard_firstwall_end_radius,
            outboard_blanket_start_radius,
            outboard_blanket_end_radius,
            blanket_rear_wall_start_radius,
            blanket_rear_wall_end_radius,
            tf_info_provided,
            pf_info_provided,
            divertor_start_radius,
            divertor_end_radius,
            support_start_radius,
            support_end_radius,
            outboard_tf_coil_end_radius,
            outboard_tf_coil_start_radius
        ) = self.make_radial_build()

        (
            plasma_start_height,
            plasma_end_height,
            plasma_to_divertor_gap_start_height,
            plasma_to_divertor_gap_end_height,
            firstwall_start_height,
            firstwall_end_height,
            blanket_start_height,
            blanket_end_height,
            blanket_rear_wall_start_height,
            blanket_rear_wall_end_height,
            number_of_pf_coils,
            pf_coils_y_values,
            pf_coils_x_values,
            pf_coil_start_radius,
            pf_coil_end_radius,
            cutting_slice
        ) = self.make_vertical_build(tf_info_provided, pf_info_provided, plasma_start_radius, plasma_end_radius, blanket_rear_wall_end_radius, outboard_tf_coil_end_radius, outboard_tf_coil_start_radius)

        inboard_tf_coils = self.make_inboard_tf_coils(
            blanket_rear_wall_end_height,
            inboard_tf_coils_start_radius,
            inboard_tf_coils_end_radius
        )

        center_column_shield = self.make_center_column_shield(
            shapes_or_components,
            blanket_rear_wall_end_height,
            center_column_shield_start_radius,
            center_column_shield_end_radius
        )

        plasma = self.make_plasma(
            shapes_or_components,
            plasma_end_radius,
            plasma_start_radius
        )

        inboard_firstwall, inboard_blanket, firstwall = self.make_inboard_blanket_and_firstwall(
            shapes_or_components,
            inboard_blanket_start_radius,
            plasma,
            blanket_end_height
        )

        divertor = self.make_divertor_single_null(
            shapes_or_components,
            blanket_rear_wall_end_height,
            divertor_start_radius,
            divertor_end_radius,
            firstwall
        )

        blanket = self.make_outboard_blanket(
            shapes_or_components,
            plasma,
            inboard_blanket
        )

        supports = self.make_supports_single_null(
            shapes_or_components,
            blanket_rear_wall_end_height,
            support_start_radius,
            support_end_radius,
            blanket
        )

        self.make_component_cuts(
            shapes_or_components,
            firstwall,
            center_column_shield_end_radius,
            blanket_rear_wall_start_height,
            blanket_rear_wall_end_height,
            inboard_tf_coils_start_radius,
            tf_info_provided,
            pf_info_provided,
            pf_coils_y_values,
            pf_coils_x_values,
            divertor,
            plasma,
            inboard_firstwall,
            outboard_tf_coil_start_radius,
            cutting_slice,
            supports,
            blanket
        )

        self.shapes_and_components = shapes_or_components

    def make_divertor_single_null(
        self, 
        shapes_or_components, 
        blanket_rear_wall_end_height, 
        divertor_start_radius, 
        divertor_end_radius, 
        firstwall
    ):

        if self.divertor_position == "upper":
            divertor_height = blanket_rear_wall_end_height
        elif self.divertor_position == "lower":
            divertor_height = -blanket_rear_wall_end_height

        divertor = paramak.RotateStraightShape(
            points=[
                (divertor_start_radius, 0),
                (divertor_end_radius, 0),
                (divertor_end_radius, divertor_height),
                (divertor_start_radius, divertor_height)
            ],
            intersect=firstwall,
            rotation_angle=self.rotation_angle,
            stp_filename="divertor.stp",
            stl_filename="divertor.stl",
            name="divertor",
            material_tag="divertor_mat"
        )
        shapes_or_components.append(divertor)

        return(divertor)

    def make_supports_single_null(
        self,
        shapes_or_components,
        blanket_rear_wall_end_height,
        support_start_radius,
        support_end_radius,
        blanket 
    ):

        if self.support_position == "upper":
            support_height = blanket_rear_wall_end_height
        elif self.support_position == "lower":
            support_height = -blanket_rear_wall_end_height

        supports = paramak.RotateStraightShape(
            points = [
                (support_start_radius, 0),
                (support_end_radius, 0),
                (support_end_radius, support_height),
                (support_start_radius, support_height)
            ],
            intersect=blanket,
            rotation_angle=self.rotation_angle,
            stp_filename="supports.stp",
            stl_filename="supports.stl",
            name="supports",
            material_tag="supports_mat",
        )
        shapes_or_components.append(supports)

        return supports