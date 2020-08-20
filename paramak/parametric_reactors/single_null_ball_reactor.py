import math
import operator

import cadquery as cq

import paramak


class SingleNullBallReactor(paramak.BallReactor):

    def __init__(
        self,
        inner_bore_radial_thickness,
        inboard_tf_leg_radial_thickness,
        center_column_shield_radial_thickness,
        divertor_radial_thickness,
        inner_plasma_gap_radial_thickness,
        plasma_radial_thickness,
        outer_plasma_gap_radial_thickness,
        firstwall_radial_thickness,
        blanket_radial_thickness,
        blanket_rear_wall_radial_thickness,
        elongation,
        triangularity,
        number_of_tf_coils,
        pf_coil_to_rear_blanket_radial_gap=None,
        pf_coil_radial_thicknesses=None,
        pf_coil_vertical_thicknesses=None,
        pf_coil_to_tf_coil_radial_gap=None,
        outboard_tf_coil_radial_thickness=None,
        tf_coil_poloidal_thickness=None,
        divertor_position="upper",
        rotation_angle=360,
    ):

        super().__init__(
            inner_bore_radial_thickness=inner_bore_radial_thickness,
            inboard_tf_leg_radial_thickness=inboard_tf_leg_radial_thickness,
            center_column_shield_radial_thickness=center_column_shield_radial_thickness,
            divertor_radial_thickness=divertor_radial_thickness,
            inner_plasma_gap_radial_thickness=inner_plasma_gap_radial_thickness,
            plasma_radial_thickness=plasma_radial_thickness,
            outer_plasma_gap_radial_thickness=outer_plasma_gap_radial_thickness,
            firstwall_radial_thickness=firstwall_radial_thickness,
            blanket_radial_thickness=blanket_radial_thickness,
            blanket_rear_wall_radial_thickness=blanket_rear_wall_radial_thickness,
            elongation=elongation,
            triangularity=triangularity,
            number_of_tf_coils=number_of_tf_coils,
            pf_coil_to_rear_blanket_radial_gap=pf_coil_to_rear_blanket_radial_gap,
            pf_coil_radial_thicknesses=pf_coil_radial_thicknesses,
            pf_coil_vertical_thicknesses=pf_coil_vertical_thicknesses,
            pf_coil_to_tf_coil_radial_gap=pf_coil_vertical_thicknesses,
            outboard_tf_coil_radial_thickness=outer_plasma_gap_radial_thickness,
            tf_coil_poloidal_thickness=tf_coil_poloidal_thickness,
            rotation_angle=rotation_angle)

        self.divertor_position = divertor_position
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

    def create_components_single_null(self):

        # this calls each method for constructing the reactor components by passing the
        # relevant parameters/objects to each method which return more objects

        shapes_or_components = []

        plasma = self.make_plasma(shapes_or_components)

        (
            inner_bore_start_radius,
            inner_bore_end_radius,
            inboard_tf_coils_start_radius,
            inboard_tf_coils_end_radius,
            center_column_shield_start_radius,
            center_column_shield_end_radius,
            divertor_start_radius,
            divertor_end_radius,
            firstwall_start_radius,
            firstwall_end_radius,
            blanket_start_radius,
            blanket_end_radius,
            blanket_rear_wall_start_radius,
            blanket_read_wall_end_radius,
        ) = self.make_radial_build(shapes_or_components)

        (
            firstwall_start_height,
            firstwall_end_height,
            blanket_start_height,
            blanket_end_height,
            blanket_rear_wall_start_height,
            blanket_rear_wall_end_height,
            tf_coil_height,
            center_column_shield_height,
            pf_coil_start_radius,
            pf_coil_end_radius,
            pf_coils_y_values,
            pf_coils_x_values,
            tf_coil_start_radius,
            tf_coil_end_radius,
        ) = self.make_vertical_build(
            shapes_or_components, plasma, blanket_read_wall_end_radius
        )

        inboard_tf_coils, cutting_slice = self.make_inboard_tf_coils(
            shapes_or_components,
            center_column_shield_height,
            blanket_read_wall_end_radius,
            tf_coil_height,
            inboard_tf_coils_start_radius,
            inboard_tf_coils_end_radius
        )

        center_column_shield = self.make_center_column_shield(
            shapes_or_components,
            center_column_shield_height,
            center_column_shield_start_radius,
            center_column_shield_end_radius,
        )

        (
            firstwall,
            blanket,
            blanket_rear_casing,
            extra_blanket_upper,
            extra_firstwall_upper,
            extra_blanket_rear_wall_upper,
            extra_blanket_lower,
            extra_firstwall_lower,
            extra_blanket_rear_wall_lower,
        ) = self.make_blanket_and_firstwall(
            shapes_or_components,
            center_column_shield_end_radius,
            blanket_start_height,
            blanket_end_height,
            firstwall_start_height,
            firstwall_end_height,
            blanket_rear_wall_start_height,
            blanket_rear_wall_end_height,
            plasma,
            firstwall_start_radius,
            blanket_start_radius,
            blanket_rear_wall_start_radius,
        )

        blanket_fw_rear_wall_envelope, divertor = self.make_divertor_single_null(
            shapes_or_components,
            firstwall_start_radius,
            firstwall_start_height,
            extra_blanket_upper,
            extra_firstwall_upper,
            extra_blanket_rear_wall_upper,
            extra_blanket_lower,
            extra_firstwall_lower,
            extra_blanket_rear_wall_lower,
            plasma,
            blanket_rear_wall_end_height,
            divertor_start_radius,
            divertor_end_radius,
        )

        self.make_component_cuts(
            shapes_or_components,
            firstwall,
            blanket,
            blanket_rear_casing,
            divertor,
            pf_coils_y_values,
            pf_coils_x_values,
            inboard_tf_coils_start_radius,
            inboard_tf_coils_end_radius,
            tf_coil_height,
            tf_coil_start_radius,
            cutting_slice,
        )

        self.shapes_and_components = shapes_or_components

    def make_divertor_single_null(
        self,
        shapes_or_components,
        firstwall_start_radius,
        firstwall_start_height,
        extra_blanket_upper,
        extra_firstwall_upper,
        extra_blanket_rear_wall_upper,
        extra_blanket_lower,
        extra_firstwall_lower,
        extra_blanket_rear_wall_lower,
        plasma,
        blanket_rear_wall_end_height,
        divertor_start_radius,
        divertor_end_radius
    ):

        # used as an intersect when making the divertor
        blanket_fw_rear_wall_envelope = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(firstwall_start_radius, 0),
            inner_upper_point=(plasma.high_point[0], firstwall_start_height),
            inner_lower_point=(plasma.low_point[0], -firstwall_start_height),
            thickness=self.firstwall_radial_thickness
            + self.blanket_radial_thickness
            + self.blanket_rear_wall_radial_thickness,
            rotation_angle=self.rotation_angle,
            union=[
                extra_blanket_upper,
                extra_firstwall_upper,
                extra_blanket_rear_wall_upper,
                extra_blanket_lower,
                extra_firstwall_lower,
                extra_blanket_rear_wall_lower,
            ],
            stp_filename="test.stp",
        )

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
            intersect=blanket_fw_rear_wall_envelope,
            stp_filename="divertor.stp",
            stl_filename="divertor.stl",
            name="divertor",
            material_tag="divertor_mat",
            rotation_angle=self.rotation_angle
        )
        shapes_or_components.append(divertor)

        return blanket_fw_rear_wall_envelope, divertor
