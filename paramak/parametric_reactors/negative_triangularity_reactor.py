import numpy as np
import paramak
from paramak import shape
from paramak.utils import union_solid
from typing import List, Union, Optional


class NegativeTriangularityReactor(paramak.Reactor):
    """
    New class of reactor that builds a negative triangularity tokamak model.
    """

    def __init__(self,
                 inner_tf_coil_thickness: float,
                 vacuum_vessel_thickness: float,
                 central_shield_thickness: float,
                 wall_to_plasma_gap: float,
                 plasma_radial_thickness: float,
                 elongation: float,
                 triangularity: float,
                 inner_wall_thickness: float,
                 blanket_thickness: float,
                 rear_wall_thickness: float,
                 divertor_radial_thickness: float,
                 divertor_height_full: float,
                 number_of_coils: int,
                 tf_width: float,
                 pf_coil_heights: Optional[Union[float, list]],
                 pf_coil_widths: Optional[Union[float, list]],
                 pf_coil_center_points: Optional[Union[list, tuple]],
                 pf_coil_casing_thickness: Optional[float],

                 rotation_angle: float,

                 inner_bore_radius: Optional[float] = 5,
                 port_side_length: Optional[float] = 20,
                 port_thickness: Optional[float] = 20,
                 show_plasma: bool = True,
                 low_aspect: bool = False,
                 outer_tf_coil_thickness: float = None,
                 inner_pf_coil_width: Optional[Union[float, List[float]]] = None,
                 inner_pf_coil_height: Optional[Union[float, List[float]]] = None,
                 inner_pf_coil_case_thickness: Optional[Union[float, List[float]]] = None,
                 inner_pf_coil_center_points: Optional[Union[float, List[float]]] = None,
                 ports_enabled: Optional[bool] = False,
                 pf_enabled: Optional[bool] = False,
                 **kwargs,

                 ):

        super().__init__([])
        self.method = 'trelis'
        self._inner_tf_coil_thickness = inner_tf_coil_thickness
        self._vacuum_vessel_thickness = vacuum_vessel_thickness
        self._central_shield_thickness = central_shield_thickness
        self._wall_to_plasma_gap = wall_to_plasma_gap
        self._plasma_radial_thickness = plasma_radial_thickness
        self._elongation = elongation
        self._triangularity = -1 * abs(triangularity)
        self._inner_wall_thickness = inner_wall_thickness
        self._blanket_thickness = blanket_thickness
        self._rear_wall_thickness = rear_wall_thickness
        self._divertor_radial_thickness = divertor_radial_thickness
        self._inner_pf_coil_w = inner_pf_coil_width
        self._inner_pf_coil_h = inner_pf_coil_height
        self._inner_pf_coil_ct = inner_pf_coil_case_thickness
        self._inner_tf_coil_cp = inner_pf_coil_center_points
        self._divertor_height_full = divertor_height_full
        self._inner_bore_radius = inner_bore_radius

        if outer_tf_coil_thickness is None:
            self._outer_tf_coil_thickness = inner_tf_coil_thickness
        else:
            self._outer_tf_coil_thickness = outer_tf_coil_thickness

        self._pf_enabled = pf_enabled

        if self._pf_enabled:
            self._pf_coil_heights = pf_coil_heights
            self._pf_coil_widths = pf_coil_widths
            self._pf_coil_center_points = pf_coil_center_points
            self._pf_casing_thickness = pf_coil_casing_thickness

        self._rotation_angle = rotation_angle
        self.show_plasma = show_plasma
        self.low_aspect = low_aspect
        self._number_of_coils = number_of_coils
        self._tf_width = tf_width
        self._port_side_length = port_side_length
        self._port_thickness = port_thickness
        self._ports_enable = ports_enabled

        ########### Calculating plasma geometry from parameters above #########

        # Adjust a gap between inner TF leg and vacuum vessel to accomodate a
        # wider range of thicknesses
        core_width = self._inner_tf_coil_thickness + \
            self._vacuum_vessel_thickness + self._central_shield_thickness
        blanket_width = self._inner_wall_thickness + \
            self._blanket_thickness + self._rear_wall_thickness
        wdth_diff = blanket_width - core_width

        if wdth_diff > 0:
            self._inner_leg_to_vacuum_inner_wall_gap = wdth_diff
        else:
            self._inner_leg_to_vacuum_inner_wall_gap = 0

        # Define Equatorial points
        self._inner_equatorial_point = self._inner_bore_radius \
            + self._inner_tf_coil_thickness \
            + self._vacuum_vessel_thickness \
            + self._central_shield_thickness \
            + self._wall_to_plasma_gap \
            + self._inner_leg_to_vacuum_inner_wall_gap
        if not self.low_aspect:
            self._inner_equatorial_point += self._inner_wall_thickness \
                + self._blanket_thickness \
                + self._rear_wall_thickness

        self._outer_equatorial_point = self._inner_equatorial_point + \
            self._plasma_radial_thickness

        self._major_radius = (
            self._outer_equatorial_point + self._inner_equatorial_point) / 2
        self._minor_radius = (
            self._major_radius -
            self._inner_equatorial_point)
        print(
            "Aspect Ratio = {:.2f}".format(
                self._major_radius /
                self._minor_radius))
        print("Major Radius = {:.2f}".format(self._major_radius))
        print("Minor Radius = {:.2f}".format(self._minor_radius))

    @property
    def aspect_ratio(self):
        return (self._major_radius / self._minor_radius)

    @property
    def vacuum_vessel_thickness(self):
        return self._vacuum_vessel_thickness

    @property
    def inner_equatorial_point(self):
        return self._inner_equatorial_point

    @property
    def outer_equatorial_point(self):
        return self._outer_equatorial_point

    @property
    def tf_thickness(self):
        return self._inner_tf_coil_thickness

    @property
    def major_radius(self):
        return self._major_radius

    @property
    def minor_radius(self):
        return self._minor_radius

    @property
    def elongation(self):
        return self._elongation

    @property
    def triangularity(self):
        return self._triangularity

    @property
    def inner_bore_radius(self):
        return self._inner_bore_radius

    @inner_bore_radius.setter
    def inner_bore_radius(self, val):
        self._inner_bore_radius = val

    def create_solid(self):

        shapes_and_components = []

        self._make_plasma()
        self._make_vertical_build()
        self._make_radial_build()

        if self.show_plasma:
            shapes_and_components.append(self._make_plasma())
        else:
            print("Plasma is excluded from the model.")

        shapes_and_components += self._make_tf_inner_leg()
        shapes_and_components += self._make_vacuum_vessel_inner_wall()
        shapes_and_components += self._make_inner_shield()

        shapes_and_components += self._make_blankets()
        shapes_and_components += self._make_divertor()
        shapes_and_components += self._make_tf_coils()
        #shapes_and_components += self._make_ports()
        shapes_and_components += self._make_vacuum_vessel()

        if self._ports_enable:
            shapes_and_components += self._make_ports()

        if self._pf_enabled:
            shapes_and_components += self._make_pf_coils()

        self.shapes_and_components = shapes_and_components

    def _make_plasma(self):
        plasma = paramak.Plasma(
            major_radius=self._major_radius,
            minor_radius=self._minor_radius,
            elongation=self._elongation,
            triangularity=self._triangularity,
            rotation_angle=self._rotation_angle,
            color=(0, 0.5, 0.5)
        )
        self._plasma = plasma
        return self._plasma

    def _make_vertical_build(self):

        ### Above the plasma ###

        # Inner wall
        self._inner_wall_start_height = self._plasma.high_point[1] + \
            self._wall_to_plasma_gap
        self._inner_wall_end_height = self._inner_wall_start_height + \
            self._inner_wall_thickness
        # Blanket
        self._blanket_start_height_top = self._inner_wall_end_height
        self._blanket_end_height_top = self._blanket_start_height_top + self._blanket_thickness
        # Rear wall
        self._rear_wall_start_height_top = self._blanket_end_height_top
        self._rear_wall_end_height_top = self._rear_wall_start_height_top + \
            self._rear_wall_thickness
        # Divertor
        self._divertor_start_height = (self._plasma.high_point[1])
        self._divertor_end_height_top = self._divertor_start_height + \
            self._divertor_height_full

        ### Diverter height check ###
        min_div_h = self._rear_wall_end_height_top - self._divertor_start_height

        if (min_div_h > self._divertor_height_full):
            print(
                "Set divertor height is too low. Diverter height is set to minimum of {:.2f} cm".format(
                    (min_div_h)))
            self._divertor_end_height_top = self._divertor_start_height + min_div_h

        # Vacuum Vessel Inner Wall
        self._vacuum_vessel_start_height = self._divertor_end_height_top
        self._vacuum_vessel_end_height = self._vacuum_vessel_start_height \
            + self._vacuum_vessel_thickness
        # Central Heights
        self._inner_tf_leg_height = self._vacuum_vessel_end_height * 2
        self._vacuum_vessel_height = self._vacuum_vessel_start_height * 2
        self._inner_shield_height = self._vacuum_vessel_start_height * 2

        # Outer Blanket Height
        self._outer_blanket_height = self._inner_shield_height - \
            (2 * self._divertor_height_full)
        if self._outer_blanket_height < 0:
            raise ValueError(
                "The divertors are overlapping at the center plane.")

    def _make_radial_build(self):
        # Bore
        self._inner_bore_start_rad = 0
        self._inner_bore_stop_rad = self._inner_bore_radius
        # Inner TF Coil
        self._tf_inner_leg_start_rad = self._inner_bore_stop_rad
        self._tf_inner_leg_end_rad = self._tf_inner_leg_start_rad + \
            self._inner_tf_coil_thickness
        # Vacuum Vessel Inner wall
        self._vacuum_vessel_inwall_start_rad = self._tf_inner_leg_end_rad + \
            self._inner_leg_to_vacuum_inner_wall_gap
        self._vacuum_vessel_inwall_end_rad = self._vacuum_vessel_inwall_start_rad + \
            self._vacuum_vessel_thickness
        # Central Column Shield
        self._inner_shield_start_rad = self._vacuum_vessel_inwall_end_rad
        self._inner_shield_end_rad = self._inner_shield_start_rad + \
            self._central_shield_thickness
        # Blanket Offset
        self._blanket_offset = self._wall_to_plasma_gap + self._inner_wall_thickness
        # Rear Wall offset
        self._rear_wall_plasma_offset = self._wall_to_plasma_gap + \
            self._blanket_thickness + self._inner_wall_thickness

        # Inner PF Coils
        if self._inner_pf_coil_w is not None:
            self._inner_pf_thickness = max(self._inner_pf_coil_w)
            self._inner_pf_case_thickness = max(self._inner_pf_coil_ct)
        else:
            self._inner_pf_thickness = 0
            self._inner_pf_case_thickness = 0

        ### Run check for diverter parameters ###

        full_outer_blanket_rad = (
            self._major_radius +
            self._minor_radius +
            self._wall_to_plasma_gap +
            self._inner_wall_thickness +
            self._blanket_thickness +
            self._rear_wall_thickness)

        if not self.low_aspect:
            full_outer_blanket_rad += self._inner_wall_thickness \
                + self._blanket_thickness \
                + self._rear_wall_thickness

        width_parameter_difference = full_outer_blanket_rad - \
            self._plasma.high_point[0]

        if self._divertor_radial_thickness < width_parameter_difference:
            print("The given radial thickness of the divertor is too small. Diverter set to minimum radial thickness of {:.2f} cm".format(
                width_parameter_difference))
            self._divertor_radial_thickness = width_parameter_difference

        ### Divertor parts ###
        self._divertor_start_rad = self._plasma.high_point[0]
        self._divertor_end_rad = self._divertor_start_rad + self._divertor_radial_thickness

        # Vacuum Vessel Body
        self._vacuum_vessel_body_start_rad = self._divertor_end_rad
        self._vacuum_vessel_body_end_rad = self._vacuum_vessel_body_start_rad + \
            self._vacuum_vessel_thickness

        # TF Coils
        # Getting small radius for inner corner
        self._tf_coils_init = paramak.ToroidalFieldCoilRectangleRoundCorners(
            with_inner_leg=False,
            lower_inner_coordinates=(self._inner_bore_stop_rad, -self._inner_tf_leg_height / 2),
            mid_point_coordinates=(self._vacuum_vessel_body_end_rad, 0),
            thickness=self._outer_tf_coil_thickness,
            number_of_coils=self._number_of_coils,
            distance=self._tf_width,
            rotation_angle=self._rotation_angle,
            color=(0.2, 1, 0.2)
        )

        self._small_rad_displacement = self._tf_coils_init.analyse_attributes[2]

        self._tf_start_rad = self._vacuum_vessel_body_end_rad + self._small_rad_displacement
        self._tf_end_rad = self._tf_start_rad + self._inner_tf_coil_thickness

    def _make_tf_inner_leg(self):

        self._bore_cutter = paramak.CenterColumnShieldCylinder(
            height=self._inner_tf_leg_height + 10,
            inner_radius=0,
            outer_radius=self._inner_bore_stop_rad,
            rotation_angle=self._rotation_angle,
        )

        self._tf_inner_leg = paramak.CenterColumnShieldCylinder(
            height=self._inner_tf_leg_height,
            inner_radius=0,
            outer_radius=self._tf_inner_leg_end_rad,
            rotation_angle=self._rotation_angle,
            stp_filename="tf_inner_leg.stp",
            stl_filename="tf_inner_leg.stl",
            name="tf_inner_leg",
            material_tag="inboard_tf_coils_mat",
            cut=[self._bore_cutter],
            color=(0.2, 1, 0.2),
        )

        self._tf_inner_leg.show()
        return [self._tf_inner_leg]

    def _make_vacuum_vessel_inner_wall(self):

        self._vacuum_vessel_inner_wall = paramak.CenterColumnShieldCylinder(
            height=self._vacuum_vessel_height,
            inner_radius=self._vacuum_vessel_inwall_start_rad,
            outer_radius=self._vacuum_vessel_inwall_end_rad,
            rotation_angle=self._rotation_angle,
            stp_filename="vacuum_vessel_inner_wall.stp",
            stl_filename="vacuum_vessel_inner_wall.stl",
            name="vacuum_vessel_inner_wall",
            material_tag="vacuum_vessel_inner_mat",
            color=(0.5, 0.5, 0.5)
        )

        return [self._vacuum_vessel_inner_wall]

    def _make_inner_shield(self):

        self._inner_shield = paramak.CenterColumnShieldCylinder(
            height=self._inner_shield_height,
            inner_radius=self._inner_shield_start_rad,
            outer_radius=self._inner_shield_end_rad,
            rotation_angle=self._rotation_angle,
            stp_filename="inner_shield.stp",
            stl_filename="inner_shield.stl",
            name="inner_shield",
            material_tag="center_column_shield_mat",
            color=(1, 0.7, 0.5)
        )

        return [self._inner_shield]

    def _make_blankets(self):

        ### Cutters ###

        self._divertor_cutter_cutter = paramak.CenterColumnShieldCylinder(
            height=self._divertor_start_height * 2,
            inner_radius=0,
            outer_radius=self._divertor_end_rad + 10
        )

        self._divertor_cutter = paramak.CenterColumnShieldCylinder(
            height=self._inner_tf_leg_height + 10,
            inner_radius=self._divertor_start_rad,
            outer_radius=self._divertor_end_rad,
            cut=[self._divertor_cutter_cutter]
        )

        central_cutter = paramak.CenterColumnShieldCylinder(
            height=self._inner_tf_leg_height + 10,  # for overlap
            inner_radius=0,
            outer_radius=self._inner_shield_end_rad,
            union=[self._divertor_cutter]
        )

        self._rear_wall = paramak.BlanketFP(
            thickness=self._rear_wall_thickness,
            start_angle=180,
            stop_angle=-
            180,
            plasma=self._make_plasma(),
            rotation_angle=self._rotation_angle,
            offset_from_plasma=[
                self._rear_wall_plasma_offset +
                self._wall_to_plasma_gap,
                self._rear_wall_plasma_offset,
                self._rear_wall_plasma_offset +
                self._wall_to_plasma_gap],
            material_tag="blanket_rear_wall_mat",
            stp_filename="blanket_rear_wall.stp",
            stl_filename="blanket_rear_wall.stl",
            name="blanket_rear_wall",
            cut=[central_cutter],
            color=(
                0.3,
                0.3,
                0.3))

        self._breeder_blanket = paramak.BlanketFP(
            thickness=self._blanket_thickness,
            start_angle=180,
            stop_angle=-
            180,
            plasma=self._make_plasma(),
            rotation_angle=self._rotation_angle,
            offset_from_plasma=[
                self._blanket_offset +
                self._wall_to_plasma_gap,
                self._blanket_offset,
                self._blanket_offset +
                self._wall_to_plasma_gap],
            material_tag="blanket_mat",
            stp_filename="blanket.stp",
            stl_filename="blanket.stl",
            name="blanket",
            cut=[central_cutter],
            color=(
                0.5,
                1,
                0.5))

        self._inner_wall = paramak.BlanketFP(
            thickness=self._inner_wall_thickness,
            start_angle=180,
            stop_angle=-180,
            plasma=self._make_plasma(),
            rotation_angle=self._rotation_angle,
            offset_from_plasma=[
                self._wall_to_plasma_gap * 2,
                self._wall_to_plasma_gap,
                self._wall_to_plasma_gap * 2],
            material_tag="firstwall_mat",
            stp_filename="firstwall.stp",
            stl_filename="firstwall.stl",
            name="firstwall",
            cut=[central_cutter],
            color=(
                0.3,
                0.3,
                0.3))

        return [self._rear_wall, self._breeder_blanket, self._inner_wall]

    def _make_divertor(self):

        self._divertor_extention_cutter = paramak.BlanketFP(
            thickness=-self._wall_to_plasma_gap * 2,
            start_angle=180,
            stop_angle=-180,
            plasma=self._make_plasma(),
            rotation_angle=self._rotation_angle,
            offset_from_plasma=[
                self._wall_to_plasma_gap * 2,
                self._wall_to_plasma_gap,
                self._wall_to_plasma_gap * 2],
        )

        self._divertor_midplane_cutter = paramak.CenterColumnShieldCylinder(
            height=(self._divertor_start_height) * 2,
            inner_radius=self._divertor_start_rad,
            outer_radius=self._divertor_end_rad,
            rotation_angle=self._rotation_angle,
        )

        self._divertor = paramak.CenterColumnShieldCylinder(
            height=self._divertor_end_height_top * 2,
            inner_radius=self._divertor_start_rad,
            outer_radius=self._divertor_end_rad,
            rotation_angle=self._rotation_angle,
            cut=[
                self._divertor_extention_cutter,
                self._divertor_midplane_cutter],
            color=(
                1,
                0.2,
                0.2),
            material_tag="divertor_mat",
            stp_filename="divertor.stp",
            stl_filename="divertor.stl",
            name="divertor")

        return [self._divertor]

    def _make_vacuum_vessel(self):

        vac_cutter = paramak.CenterColumnShieldCylinder(
            height=self._vacuum_vessel_height,
            inner_radius=self._vacuum_vessel_inwall_start_rad,
            outer_radius=self._vacuum_vessel_body_start_rad,
            rotation_angle=self._rotation_angle,
            color=(0.5, 0.5, 0.5)
        )

        if self._ports_enable:
            cutting_list = [
                vac_cutter,
                self._port_cutter_top,
                self._port_cutter_mid,
                self._port_cutter_bot]
        else:
            cutting_list = [vac_cutter]

        self._vacuum_vessel_body = paramak.CenterColumnShieldCylinder(
            height=self._vacuum_vessel_height + (self._vacuum_vessel_thickness * 2),
            inner_radius=self._vacuum_vessel_inwall_start_rad,
            outer_radius=self._vacuum_vessel_body_end_rad,
            rotation_angle=self._rotation_angle,
            stp_filename="vacuum_vessel_body.stp",
            stl_filename="vacuum_vessel_body.stl",
            name="vacuum_vessel_body",
            material_tag="vacuum_vessel_mat",
            cut=cutting_list,
            color=(0.5, 0.5, 0.5)
        )

        return [self._vacuum_vessel_body]

    def _make_tf_coils(self):

        self._tf_coils = paramak.ToroidalFieldCoilRectangleRoundCorners(
            with_inner_leg=False,
            lower_inner_coordinates=(self._inner_bore_stop_rad, -self._inner_tf_leg_height / 2),
            mid_point_coordinates=(self._tf_start_rad, 0),
            thickness=self._outer_tf_coil_thickness,
            number_of_coils=self._number_of_coils,
            distance=self._tf_width,
            rotation_angle=self._rotation_angle,
            stp_filename="tf_coil_outer.stp",
            stl_filename="tf_coil_outer.stl",
            name="tf_coil_outer",
            material_tag="inboard_tf_coils_mat",
            color=(0.2, 1, 0.2)
        )

        return [self._tf_coils]

    def _make_ports(self):

        _start_angle = (360 / self._number_of_coils) / 2
        _end_angle = 360 + _start_angle
        _port_angles = np.linspace(
            _start_angle,
            _end_angle,
            self._number_of_coils + 1)

        self._port_cutter_top = paramak.PortCutterRectangular(
            height=self._port_side_length,
            width=self._port_side_length,
            distance=self._small_rad_displacement +
            self._outer_tf_coil_thickness +
            self._tf_coil_outer_end_rad,
            extrusion_start_offset=1,
            center_point=(
                self._plasma.high_point[1] -
                self._port_side_length,
                0),
            azimuth_placement_angle=_port_angles,
            rotation_angle=self._rotation_angle,
        )

        self._port_cutter_mid = paramak.PortCutterRectangular(
            height=self._port_side_length,
            width=self._port_side_length,
            distance=self._small_rad_displacement +
            self._outer_tf_coil_thickness +
            self._vacuum_vessel_body_end_rad,
            extrusion_start_offset=1,
            center_point=(
                0,
                0),
            azimuth_placement_angle=_port_angles,
            rotation_angle=self._rotation_angle,
        )

        self._port_cutter_bot = paramak.PortCutterRectangular(
            height=self._port_side_length,
            width=self._port_side_length,
            distance=self._small_rad_displacement + self._outer_tf_coil_thickness + self._vacuum_vessel_body_end_rad,
            extrusion_start_offset=1,
            center_point=(-(self._plasma.high_point[1] - self._port_side_length), 0),
            azimuth_placement_angle=_port_angles,
            rotation_angle=self._rotation_angle,

        )

        central_port_cutter = paramak.CenterColumnShieldCylinder(
            height=self._inner_tf_leg_height,
            inner_radius=0,
            outer_radius=self._vacuum_vessel_body_end_rad,
        )

        return []

    def _make_pf_coils(self):


        check_list = [x[0] >= self._tf_end_rad for x in self._pf_coil_center_points]
        if False in check_list:
            print('One or more Poloidal Field Coil is within the Reactor geometry!')


        self._pf_coils = paramak.PoloidalFieldCoilSet(
            heights=self._pf_coil_heights,
            widths=self._pf_coil_widths,
            center_points=self._pf_coil_center_points,
            stp_filename="pf_coil_set.stp",
            stl_filename="pf_coil_set.stl",
            name="pf_coil_set",
            color=(0.7, 0.7, 0.2),
            rotation_angle=self._rotation_angle

        )

        self._pf_casing = paramak.PoloidalFieldCoilCaseSet(
            heights=self._pf_coil_heights,
            widths=self._pf_coil_widths,
            center_points=self._pf_coil_center_points,
            casing_thicknesses=self._pf_casing_thickness,
            stp_filename="pf_coil_set_case.stp",
            stl_filename="pf_coil_set_case.stl",
            name="pf_coil_set_case",
            color=(0.7, 0.5, 0.2),
            rotation_angle=self._rotation_angle
        )
        return [self._pf_coils, self._pf_casing]