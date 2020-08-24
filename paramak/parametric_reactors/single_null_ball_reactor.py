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

        # this calls each method for constructing the reactor components

        shapes_or_components = []

        self.make_plasma(shapes_or_components)
        self.make_radial_build(shapes_or_components)
        self.make_vertical_build(shapes_or_components)
        self.make_inboard_tf_coils(shapes_or_components)
        self.make_center_column_shield(shapes_or_components)
        self.make_blanket_and_firstwall(shapes_or_components)
        self.make_divertor_single_null(shapes_or_components)
        self.make_component_cuts(shapes_or_components)

        self.shapes_and_components = shapes_or_components

    def make_divertor_single_null(self, shapes_or_components):

        # used as an intersect when making the divertor
        self._blanket_fw_rear_wall_envelope = paramak.BlanketConstantThicknessArcV(
            inner_mid_point=(self._firstwall_start_radius, 0),
            inner_upper_point=(self._plasma.high_point[0], self._firstwall_start_height),
            inner_lower_point=(self._plasma.low_point[0], -self._firstwall_start_height),
            thickness=self.firstwall_radial_thickness
            + self.blanket_radial_thickness
            + self.blanket_rear_wall_radial_thickness,
            rotation_angle=self.rotation_angle,
            union=[
                self._extra_blanket_upper,
                self._extra_firstwall_upper,
                self._extra_blanket_rear_wall_upper,
                self._extra_blanket_lower,
                self._extra_firstwall_lower,
                self._extra_blanket_rear_wall_lower,
            ],
            stp_filename="test.stp",
        )

        if self.divertor_position == "upper":
            divertor_height = self._blanket_rear_wall_end_height
        elif self.divertor_position == "lower":
            divertor_height = -self._blanket_rear_wall_end_height

        self._divertor = paramak.RotateStraightShape(
            points=[
                (self._divertor_start_radius, 0),
                (self._divertor_end_radius, 0),
                (self._divertor_end_radius, divertor_height),
                (self._divertor_start_radius, divertor_height)
            ],
            intersect=self._blanket_fw_rear_wall_envelope,
            stp_filename="divertor.stp",
            stl_filename="divertor.stl",
            name="divertor",
            material_tag="divertor_mat",
            rotation_angle=self.rotation_angle
        )
        shapes_or_components.append(self._divertor)
