from typing import List, Union, Optional
import paramak


class NegativeTriangularityReactor(paramak.Reactor):
    """
    New class of reactor that builds a negative triangularity tokamak model.

    Arguments:
        inner_tf_coil_thickness: radial thickness of the Toroidal Field coil's
            inner leg (cm),
        vacuum_vessel_thickness: the radial and vertical thickness of the
            vacuum vessel (cm),
        central_shield_thickness: radial thickness of the central heat shield
            (cm),
        wall_to_plasma_gap: gap of inner blanket wall and the plasma outter
            edge (cm),
        plasma_radial_thickness: radial thickness of the plasma
            (2x minor radius) (cm),
        elongation: plasma elongation,
        triangularity: plasma triangularity - both positive or negative values
            will result in negative triangularity,
        inner_wall_thickness: plasma facing blanket wall thickness (cm),
        blanket_thickness: breeder blanket thickness (cm),
        rear_wall_thickness: outer blanket wall thickness (cm),
        divertor_radial_thickness: radial thickness of the divertor (cm),
        divertor_height_full: divertor vertical thickness (cm),
        number_of_coils: number of Toroidal Field coils around the reactor
            evenly spaced,
        tf_width: Toroidal Field coil extrusion distance / thickness (cm),
        pf_coil_heights: List of Poloidal field coil heights (cm),
        pf_coil_widths: List of Poloidal field coil widths (cm),
        pf_coil_center_points: List of Poloidal field coil center points on the
            XZ workplane (cm),
        pf_coil_casing_thickness: List of Poloidal field coil casing thickness
            (cm),
        rotation_angle: Angle of rotation arounbd the Z axis of which the
            reactor is shown - 180° shows half a reactor,
        inner_bore_radius: Inner bore radial thickness (cm); Defaults to 5 cm,
        port_side_lengths: List containing the side lengths of the ports (cm),
        port_heights: List containing the heights of the ports (cm),
        port_angles: List containing the angles of the ports center points (°),
        port_z_pos: List containing the Z position of the ports as Zero in the
            centre of the reactor (cm),
        outer_tf_coil_thickness: Outer Toroidal Field coil thickness (cm) -
            defaults to the inner Toroidal Field coil thickness,,
        low_aspect: Boolean allowing a swift switch between a lower
            aspect-ratio reactor (True) where the inner blanket is cut by the
            center column, whereas (False) non-low-aspect will produce a full
            inner blanket and only part being cut by the centre column is the
            rear blanket wall,
    """

    def __init__(
        self,
        inner_tf_coil_thickness: float = 100,
        vacuum_vessel_thickness: float = 50,
        central_shield_thickness: float = 30,
        wall_to_plasma_gap: float = 150,
        plasma_radial_thickness: float = 650,
        elongation: float = 2,
        triangularity: float = 0.6,
        inner_wall_thickness: float = 20,
        blanket_thickness: float = 105,
        rear_wall_thickness: float = 20,
        divertor_radial_thickness: float = 430,
        divertor_height_full: float = 300,
        number_of_coils: int = 12,
        tf_width: float = 75,
        pf_coil_heights: Optional[Union[float, List[float]]] = [75, 75, 150, 75, 75],
        pf_coil_widths: Optional[Union[float, List[float]]] = [70, 70, 150, 70, 70],
        pf_coil_center_points: Optional[Union[list, tuple]] = [
            (350, 850),
            (1350, 650),
            (1350, 0),
            (1350, -650),
            (350, -850),
        ],
        pf_coil_casing_thickness: Optional[List[float]] = [15, 15, 15, 15, 15],
        rotation_angle: float = 180,
        inner_bore_radius: float = 50,
        port_side_lengths: Optional[List[float]] = [200, 200, 150],
        port_heights: Optional[List[float]] = [200, 100, 400],
        port_angles: Optional[List[float]] = [75, 170, 15],
        port_z_pos: Optional[List[float]] = [500, -500, 200],
        outer_tf_coil_thickness: Optional[float] = None,
        low_aspect: bool = False,
    ):

        super().__init__([])
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
        self._divertor_height_full = divertor_height_full
        self._inner_bore_radius = inner_bore_radius

        if outer_tf_coil_thickness is None:
            self._outer_tf_coil_thickness = inner_tf_coil_thickness
        else:
            self._outer_tf_coil_thickness = outer_tf_coil_thickness

        self._pf_coil_heights = pf_coil_heights
        self._pf_coil_widths = pf_coil_widths
        self._pf_coil_center_points = pf_coil_center_points
        self._pf_casing_thickness = pf_coil_casing_thickness

        self._rotation_angle = rotation_angle
        self._low_aspect = low_aspect
        self._number_of_coils = number_of_coils
        self._tf_width = tf_width
        self._port_side_lengths = port_side_lengths
        self._port_heights = port_heights
        self._ports_angles = port_angles
        self._port_z_pos = port_z_pos

        self.input_variable_names = [
            "inner_tf_coil_thickness",
            "vacuum_vessel_thickness",
            "central_shield_thickness",
            "wall_to_plasma_gap",
            "plasma_radial_thickness",
            "elongation",
            "triangularity",
            "inner_wall_thickness",
            "blanket_thickness",
            "rear_wall_thickness",
            "divertor_radial_thickness",
            "divertor_height_full",
            "number_of_coils",
            "tf_width",
            "pf_coil_heights",
            "pf_coil_widths",
            "pf_coil_center_points",
            "pf_coil_casing_thickness",
            "rotation_angle",
            "inner_bore_radius",
            "port_side_lengths",
            "port_heights",
            "port_angles",
            "port_z_pos",
            "outer_tf_coil_thickness",
            "low_aspect",
        ]

        if None in [
            self._ports_angles,
            self._port_side_lengths,
            self._port_heights,
            self._port_z_pos,
        ]:
            self._ports_enable = False
        else:
            self._ports_enable = True

        if None in [
            self._pf_coil_heights,
            self._pf_coil_widths,
            self._pf_coil_center_points,
            self._pf_casing_thickness,
        ]:
            self._pf_enabled = False
        else:
            self._pf_enabled = True

        self._plasma_geometry()
        self._equatorial_points()

        # Set by plasma, radial or vertical build
        self._plasma = None
        self._tf_coils_init = None
        self._pf_coils = None
        self._pf_casing = None
        self._ports = None
        self._bore_cutter = None
        self._tf_inner_leg = None
        self._vacuum_vessel_inner_wall = None
        self._inner_shield = None
        self._divertor_cutter_cutter = None
        self._divertor_cutter = None
        self._rear_wall = None
        self._breeder_blanket = None
        self._inner_wall = None
        self._divertor_extention_cutter = None
        self._divertor_midplane_cutter = None
        self._divertor = None
        self._vacuum_vessel_body = None
        self._tf_coils = None

        self._inner_bore_start_rad = 0
        self._inner_bore_stop_rad = 0
        self._inner_tf_leg_height = 0
        self._tf_inner_leg_start_rad = 0
        self._tf_inner_leg_end_rad = 0
        self._inner_shield_height = 0
        self._inner_shield_start_rad = 0
        self._inner_shield_end_rad = 0
        self._blanket_start_height_top = 0
        self._blanket_end_height_top = 0
        self._blanket_offset = 0
        self._inner_wall_start_height = 0
        self._inner_wall_end_height = 0
        self._rear_wall_start_height_top = 0
        self._rear_wall_end_height_top = 0
        self._divertor_start_height = 0
        self._divertor_end_height_top = 0
        self._vacuum_vessel_start_height = 0
        self._vacuum_vessel_end_height = 0
        self._vacuum_vessel_height = 0
        self._vacuum_vessel_body_start_rad = 0
        self._vacuum_vessel_body_end_rad = 0
        self._outer_blanket_height = 0
        self._vacuum_vessel_inwall_start_rad = 0
        self._vacuum_vessel_inwall_end_rad = 0
        self._rear_wall_plasma_offset = 0
        self._divertor_start_rad = 0
        self._divertor_end_rad = 0
        self._small_rad_displacement = 0
        self._tf_start_rad = 0
        self._tf_end_rad = 0

    def _plasma_geometry(self):
        """Calculating plasma geometry from parameters. Adjust a gap between
        inner TF leg and vacuum vessel to accommodate a wider range of
        thicknesses"""
        core_width = (
            self._inner_bore_radius
            + self._inner_tf_coil_thickness
            + self._vacuum_vessel_thickness
            + self._central_shield_thickness
        )
        blanket_width = self._inner_wall_thickness + self._blanket_thickness + self._rear_wall_thickness
        wdth_diff = blanket_width - core_width

        if wdth_diff > 0:
            self._inner_leg_to_vacuum_inner_wall_gap = wdth_diff
        else:
            self._inner_leg_to_vacuum_inner_wall_gap = 0

    def _equatorial_points(self):
        # Define Equatorial points
        self._inner_equatorial_point = (
            self._inner_bore_radius
            + self._inner_tf_coil_thickness
            + self._vacuum_vessel_thickness
            + self._central_shield_thickness
            + self._wall_to_plasma_gap
            + self._inner_leg_to_vacuum_inner_wall_gap
        )
        if not self._low_aspect:
            self._inner_equatorial_point += (
                self._inner_wall_thickness + self._blanket_thickness + self._rear_wall_thickness
            )

        self._outer_equatorial_point = self._inner_equatorial_point + self._plasma_radial_thickness

        self._major_radius = (self._outer_equatorial_point + self._inner_equatorial_point) / 2
        self._minor_radius = self._major_radius - self._inner_equatorial_point

    # Getters
    @property
    def aspect_ratio(self):
        return self._major_radius / self._minor_radius

    @property
    def minor_radius(self):
        return self._minor_radius

    @property
    def major_radius(self):
        return self._major_radius

    @property
    def inner_equatorial_point(self):
        return self._inner_equatorial_point

    @property
    def outer_equatorial_point(self):
        return self._outer_equatorial_point

    @property
    def inner_bore_radius(self):
        return self._inner_bore_radius

    @property
    def inner_tf_coil_thickness(self):
        return self._inner_tf_coil_thickness

    @property
    def vacuum_vessel_thickness(self):
        return self._vacuum_vessel_thickness

    @property
    def central_shield_thickness(self):
        return self._central_shield_thickness

    @property
    def wall_to_plasma_gap(self):
        return self._wall_to_plasma_gap

    @property
    def plasma_radial_thickness(self):
        return self._plasma_radial_thickness

    @property
    def elongation(self):
        return self._elongation

    @property
    def triangularity(self):
        return self._triangularity

    @property
    def inner_wall_thickness(self):
        return self._inner_wall_thickness

    @property
    def blanket_thickness(self):
        return self._blanket_thickness

    @property
    def rear_wall_thickness(self):
        return self._rear_wall_thickness

    @property
    def divertor_radial_thickness(self):
        return self._divertor_radial_thickness

    @property
    def divertor_height(self):
        return self._divertor_height_full

    @property
    def tf_width(self):
        return self.tf_width

    @property
    def port_side_lengths(self):
        return self._port_side_lengths

    @property
    def port_heights(self):
        return self._port_heights

    @property
    def port_angles(self):
        return self._ports_angles

    @property
    def port_z_pos(self):
        return self._port_z_pos

    @property
    def pf_coil_heights(self):
        return self._pf_coil_heights

    @property
    def pf_coil_widths(self):
        return self._pf_coil_widths

    @property
    def pf_coil_center_points(self):
        return self._pf_coil_center_points

    @property
    def pf_coil_casing_thickness(self):
        return self._pf_casing_thickness

    @property
    def low_aspect(self):
        return self._low_aspect

    # Setters

    @inner_bore_radius.setter
    def inner_bore_radius(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Inbore radius must be float or integer value!")
        self._inner_bore_radius = val

    @inner_tf_coil_thickness.setter
    def inner_tf_coil_thickness(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Inbore tf coil thickness must be float or integer value!")
        self._inner_tf_coil_thickness = val

    @vacuum_vessel_thickness.setter
    def vacuum_vessel_thickness(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Vacuum vessel thickness must be float or integer value!")
        self._vacuum_vessel_thickness = val

    @central_shield_thickness.setter
    def central_shield_thickness(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Inbore heat shield thickness must be float or integer value!")
        self._central_shield_thickness = val

    @wall_to_plasma_gap.setter
    def wall_to_plasma_gap(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Plasma to wall gap must be float or integer value!")
        self._wall_to_plasma_gap = val

    @plasma_radial_thickness.setter
    def plasma_radial_thickness(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("plasma radial thickness must be float or integer value!")
        self._plasma_radial_thickness = val

    @elongation.setter
    def elongation(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Elongation must be float or integer value!")
        self._elongation = val

    @triangularity.setter
    def triangularity(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Triangularity must be float or integer value!")
        if val > 1 or val < -1:
            raise ValueError("Triangularity must be between -1 and 1!")
        self._triangularity = val

    @inner_wall_thickness.setter
    def inner_wall_thickness(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Inner blanket wall must be float or integer value!")
        self._inner_wall_thickness = val

    @blanket_thickness.setter
    def blanket_thickness(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Blanket thickness must be float or integer value!")
        self._blanket_thickness = val

    @rear_wall_thickness.setter
    def rear_wall_thickness(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("rear blanket wall must be float or integer value!")
        self._rear_wall_thickness = val

    @divertor_radial_thickness.setter
    def divertor_radial_thickness(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Divertor radial thickness must be float or integer value!")
        self._divertor_radial_thickness = val

    @divertor_height.setter
    def divertor_height(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Divertor height must be float or integer value!")
        self._divertor_height_full = val

    @tf_width.setter
    def tf_width(self, val):
        if not isinstance(val, (float, int)):
            raise TypeError("Tf coil width must be float or integer value!")
        self._tf_width = val

    @port_side_lengths.setter
    def port_side_lengths(self, val):
        if not isinstance(val, list) or False in [isinstance(x, (float, int)) for x in val]:
            raise TypeError("Port side lengths must be a list of numbers!")
        self._port_checks()
        self._port_side_lengths = val

    @port_heights.setter
    def port_heights(self, val):
        if not isinstance(val, list) or False in [isinstance(x, (float, int)) for x in val]:
            raise TypeError("Port heights must be a list of numbers!")
        self._port_checks()
        self._port_thickness = val

    @port_angles.setter
    def port_angles(self, val):
        if not isinstance(val, list) or False in [isinstance(x, (float, int)) for x in val]:
            raise TypeError("Port angles must be a list of numbers!")
        self._port_checks()
        self._ports_angles = val

    @port_z_pos.setter
    def port_z_pos(self, val):
        if not isinstance(val, list) or False in [isinstance(x, (float, int)) for x in val]:
            raise TypeError("Port Z positions must be a list of numbers!")
        self._port_checks()
        self._port_z_pos = val

    @pf_coil_heights.setter
    def pf_coil_heights(self, val):
        if not isinstance(val, list) or False in [isinstance(x, (float, int)) for x in val]:
            raise TypeError("Pf coil heights must be a list of numbers!")
        self._pf_checks(False)
        self._pf_coil_heights = val

    @pf_coil_widths.setter
    def pf_coil_widths(self, val):
        if not isinstance(val, list) or False in [isinstance(x, (float, int)) for x in val]:
            raise TypeError("Pf coil width must be a list of numbers!")
        self._pf_checks(False)
        self._pf_coil_widths = val

    @pf_coil_center_points.setter
    def pf_coil_center_points(self, val):
        if not isinstance(val, list) or False in [isinstance(x, tuple) for x in val]:
            raise TypeError("Pf coil center points must be a list of tuples!")
        self._pf_checks(True)
        self._pf_coil_center_points = val

    @pf_coil_casing_thickness.setter
    def pf_coil_casing_thickness(self, val):
        if not isinstance(val, list) or False in [isinstance(x, (float, int)) for x in val]:
            raise TypeError("Pf coil heights must be a list of numbers!")
        self._pf_checks(False)
        self._pf_casing_thickness = val

    @low_aspect.setter
    def low_aspect(self, val):
        if not isinstance(val, bool):
            raise TypeError("Low-aspect argument must be True or False!")
        self._low_aspect = val

    def create_solid(self):

        shapes_and_components = []

        self._plasma_geometry()
        self._equatorial_points()
        self._make_plasma()
        self._make_vertical_build()
        self._make_radial_build()

        shapes_and_components.append(self._make_plasma())

        if self._ports_enable:
            self._make_ports()
        if self._pf_enabled:
            shapes_and_components += self._make_pf_coils()

        shapes_and_components += self._make_tf_inner_leg()
        shapes_and_components += self._make_vacuum_vessel_inner_wall()
        shapes_and_components += self._make_inner_shield()
        shapes_and_components += self._make_blankets()
        shapes_and_components += self._make_divertor()
        shapes_and_components += self._make_tf_coils()
        shapes_and_components += self._make_vacuum_vessel()

        self.shapes_and_components = shapes_and_components

    def _make_plasma(self):
        self._plasma = paramak.Plasma(
            major_radius=self._major_radius,
            minor_radius=self._minor_radius,
            elongation=self._elongation,
            triangularity=self._triangularity,
            rotation_angle=self._rotation_angle,
            color=(0, 0.5, 0.5),
        )
        return self._plasma

    def _make_vertical_build(self):
        # Above the plasma
        # Inner wall
        self._inner_wall_start_height = self._plasma.high_point[1] + self._wall_to_plasma_gap
        self._inner_wall_end_height = self._inner_wall_start_height + self._inner_wall_thickness
        # Blanket
        self._blanket_start_height_top = self._inner_wall_end_height
        self._blanket_end_height_top = self._blanket_start_height_top + self._blanket_thickness
        # Rear wall
        self._rear_wall_start_height_top = self._blanket_end_height_top
        self._rear_wall_end_height_top = self._rear_wall_start_height_top + self._rear_wall_thickness
        # Divertor
        self._divertor_start_height = self._plasma.high_point[1]
        self._divertor_end_height_top = self._divertor_start_height + self._divertor_height_full

        # Diverter height check
        min_div_h = self._rear_wall_end_height_top - self._divertor_start_height
        if min_div_h > self._divertor_height_full:
            print(
                f"Set divertor height is too low. \
                Diverter height is set to minimum of {round(min_div_h)} cm"
            )
            self._divertor_end_height_top = self._divertor_start_height + min_div_h
        # Vacuum Vessel Inner Wall
        self._vacuum_vessel_start_height = self._divertor_end_height_top
        self._vacuum_vessel_end_height = self._vacuum_vessel_start_height + self._vacuum_vessel_thickness
        # Central Heights
        self._inner_tf_leg_height = self._vacuum_vessel_end_height * 2
        self._vacuum_vessel_height = self._vacuum_vessel_start_height * 2
        self._inner_shield_height = self._vacuum_vessel_start_height * 2
        # Outer Blanket Height
        self._outer_blanket_height = self._inner_shield_height - (2 * self._divertor_height_full)
        if self._outer_blanket_height < 0:
            raise ValueError("The divertors are overlapping at the center plane.")

    def _make_radial_build(self):
        # Bore
        self._inner_bore_start_rad = 0
        self._inner_bore_stop_rad = self._inner_bore_radius
        # Inner TF Coil
        self._tf_inner_leg_start_rad = self._inner_bore_stop_rad
        self._tf_inner_leg_end_rad = self._tf_inner_leg_start_rad + self._inner_tf_coil_thickness
        # Vacuum Vessel Inner wall
        self._vacuum_vessel_inwall_start_rad = self._tf_inner_leg_end_rad + self._inner_leg_to_vacuum_inner_wall_gap
        self._vacuum_vessel_inwall_end_rad = self._vacuum_vessel_inwall_start_rad + self._vacuum_vessel_thickness
        # Central Column Shield
        self._inner_shield_start_rad = self._vacuum_vessel_inwall_end_rad
        self._inner_shield_end_rad = self._inner_shield_start_rad + self._central_shield_thickness
        # Blanket Offset
        self._blanket_offset = self._wall_to_plasma_gap + self._inner_wall_thickness
        # Rear Wall offset
        self._rear_wall_plasma_offset = self._wall_to_plasma_gap + self._blanket_thickness + self._inner_wall_thickness

        # Run check for diverter parameters
        full_outer_blanket_rad = (
            self._major_radius
            + self._minor_radius
            + self._wall_to_plasma_gap
            + self._inner_wall_thickness
            + self._blanket_thickness
            + self._rear_wall_thickness
        )

        width_parameter_difference = full_outer_blanket_rad - self._plasma.high_point[0]

        if self._divertor_radial_thickness < width_parameter_difference:
            print(
                f"The given radial thickness of the divertor is too small.\
                Diverter set to minimum radial thickness of \
                    {round(width_parameter_difference, 2)} cm"
            )
            self._divertor_radial_thickness = width_parameter_difference

        # Divertor parts
        self._divertor_start_rad = self._plasma.high_point[0]
        self._divertor_end_rad = self._divertor_start_rad + self._divertor_radial_thickness
        # Vacuum Vessel Body
        self._vacuum_vessel_body_start_rad = self._divertor_end_rad
        self._vacuum_vessel_body_end_rad = self._vacuum_vessel_body_start_rad + self._vacuum_vessel_thickness
        # TF Coils
        # Getting small radius for inner corner
        self._tf_coils_init = paramak.ToroidalFieldCoilRectangleRoundCorners(
            with_inner_leg=False,
            lower_inner_coordinates=(
                self._inner_bore_stop_rad,
                -self._inner_tf_leg_height / 2,
            ),
            mid_point_coordinates=(self._vacuum_vessel_body_end_rad, 0),
            thickness=self._outer_tf_coil_thickness,
            number_of_coils=self._number_of_coils,
            distance=self._tf_width,
            rotation_angle=self._rotation_angle,
            color=(0.2, 1, 0.2),
        )

        self._small_rad_displacement = self._tf_coils_init.analyse_attributes[2]

        self._tf_start_rad = self._vacuum_vessel_body_end_rad + self._small_rad_displacement
        self._tf_end_rad = self._tf_start_rad + self._inner_tf_coil_thickness

    def _make_pf_coils(self):

        self._pf_checks(True)

        check_list = [x[0] >= self._tf_end_rad for x in self._pf_coil_center_points]
        if False in check_list:
            print("One or more Poloidal Field Coil is within the Reactor geometry!")

        self._pf_coils = paramak.PoloidalFieldCoilSet(
            heights=self._pf_coil_heights,
            widths=self._pf_coil_widths,
            center_points=self._pf_coil_center_points,
            name="pf_coil_set",
            color=(0.7, 0.7, 0.2),
            rotation_angle=self._rotation_angle,
        )

        self._pf_casing = paramak.PoloidalFieldCoilCaseSet(
            heights=self._pf_coil_heights,
            widths=self._pf_coil_widths,
            center_points=self._pf_coil_center_points,
            casing_thicknesses=self._pf_casing_thickness,
            name="pf_coil_set_case",
            color=(0.7, 0.5, 0.2),
            rotation_angle=self._rotation_angle,
        )
        return [self._pf_coils, self._pf_casing]

    def _make_ports(self):

        self._port_checks()

        self._ports = []

        for index, val in enumerate(self._port_side_lengths):

            _port = paramak.PortCutterRectangular(
                height=self._port_heights[index],
                width=val,
                distance=self._tf_end_rad,
                center_point=(self._port_z_pos[index], 0),
                extrusion_start_offset=0,
                azimuth_placement_angle=self._ports_angles[index],
                name=f"port_{index}",
            )
            self._ports.append(_port)
        return self._ports

    def _make_tf_inner_leg(self):

        _cutting_list = [self._pf_coils, self._pf_casing]
        if self._inner_bore_radius != 0:
            self._bore_cutter = paramak.CenterColumnShieldCylinder(
                height=self._inner_tf_leg_height + 10,
                inner_radius=0,
                outer_radius=self._inner_bore_stop_rad,
                rotation_angle=self._rotation_angle,
            )
            _cutting_list.append(self._bore_cutter)

        self._tf_inner_leg = paramak.CenterColumnShieldCylinder(
            height=self._inner_tf_leg_height,
            inner_radius=0,
            outer_radius=self._tf_inner_leg_end_rad,
            rotation_angle=self._rotation_angle,
            name="tf_inner_leg",
            cut=_cutting_list,
            color=(0.2, 1, 0.2),
        )

        return [self._tf_inner_leg]

    def _make_vacuum_vessel_inner_wall(self):

        self._vacuum_vessel_inner_wall = paramak.CenterColumnShieldCylinder(
            height=self._vacuum_vessel_height,
            inner_radius=self._vacuum_vessel_inwall_start_rad,
            outer_radius=self._vacuum_vessel_inwall_end_rad,
            rotation_angle=self._rotation_angle,
            name="vessel_inner_wall",
            color=(0.5, 0.5, 0.5),
            cut=[self._pf_coils, self._pf_casing],
        )

        return [self._vacuum_vessel_inner_wall]

    def _make_inner_shield(self):

        self._inner_shield = paramak.CenterColumnShieldCylinder(
            height=self._inner_shield_height,
            inner_radius=self._inner_shield_start_rad,
            outer_radius=self._inner_shield_end_rad,
            rotation_angle=self._rotation_angle,
            name="inner_shield",
            color=(1.0, 0.7, 0.5),
            cut=[self._pf_coils, self._pf_casing],
        )

        return [self._inner_shield]

    def _make_blankets(self):

        # Cutters

        self._divertor_cutter_cutter = paramak.CenterColumnShieldCylinder(
            height=self._divertor_start_height * 2,
            inner_radius=0,
            outer_radius=self._divertor_end_rad + 10,
        )

        self._divertor_cutter = paramak.CenterColumnShieldCylinder(
            height=self._inner_tf_leg_height + 10,
            inner_radius=self._divertor_start_rad,
            outer_radius=self._divertor_end_rad,
            cut=[self._divertor_cutter_cutter],
        )

        central_cutter = paramak.CenterColumnShieldCylinder(
            height=self._inner_tf_leg_height + 10,  # for overlap
            inner_radius=0,
            outer_radius=self._inner_shield_end_rad,
        )

        # Blanket layers

        self._rear_wall = paramak.BlanketFP(
            thickness=self._rear_wall_thickness,
            start_angle=0,
            stop_angle=360,
            plasma=self._make_plasma(),
            rotation_angle=self._rotation_angle,
            offset_from_plasma=self._inner_wall_thickness + self._blanket_thickness + self._wall_to_plasma_gap,
            name="blanket_rear_wall",
            cut=[
                central_cutter,
                self._divertor_cutter,
                self._pf_coils,
                self._pf_casing,
            ],
            color=(0.3, 0.3, 0.3),
        )

        self._breeder_blanket = paramak.BlanketFP(
            thickness=self._blanket_thickness,
            start_angle=0,
            stop_angle=360,
            plasma=self._make_plasma(),
            rotation_angle=self._rotation_angle,
            offset_from_plasma=self._inner_wall_thickness + self._wall_to_plasma_gap,
            name="blanket",
            cut=[
                central_cutter,
                self._divertor_cutter,
                self._pf_coils,
                self._pf_casing,
            ],
            color=(0.5, 1.0, 0.5),
        )

        self._inner_wall = paramak.BlanketFP(
            thickness=self._inner_wall_thickness,
            start_angle=0,
            stop_angle=360,
            plasma=self._make_plasma(),
            rotation_angle=self._rotation_angle,
            offset_from_plasma=self._wall_to_plasma_gap,
            name="firstwall",
            cut=[
                central_cutter,
                self._divertor_cutter,
                self._pf_coils,
                self._pf_casing,
            ],
            color=(0.3, 0.3, 0.3),
        )
        return [self._rear_wall, self._breeder_blanket, self._inner_wall]

    def _make_divertor(self):

        self._divertor_extention_cutter = paramak.BlanketFP(
            thickness=-self._wall_to_plasma_gap,
            start_angle=180,
            stop_angle=-180,
            plasma=self._make_plasma(),
            rotation_angle=self._rotation_angle,
            offset_from_plasma=[
                self._wall_to_plasma_gap,
                self._wall_to_plasma_gap,
                self._wall_to_plasma_gap,
            ],
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
                self._divertor_midplane_cutter,
                self._pf_coils,
                self._pf_casing,
            ],
            color=(1.0, 0.2, 0.2),
            name="divertor",
        )

        return [self._divertor]

    def _make_vacuum_vessel(self):
        vac_cutter = paramak.CenterColumnShieldCylinder(
            height=self._vacuum_vessel_height,
            inner_radius=self._vacuum_vessel_inwall_start_rad,
            outer_radius=self._vacuum_vessel_body_start_rad,
            rotation_angle=self._rotation_angle,
            color=(0.5, 0.5, 0.5),
        )
        if self._ports_enable:
            cutting_list = [vac_cutter, self._pf_coils, self._pf_casing] + self._ports
        else:
            cutting_list = [vac_cutter, self._pf_coils, self._pf_casing]
        self._vacuum_vessel_body = paramak.CenterColumnShieldCylinder(
            height=self._vacuum_vessel_height + (self._vacuum_vessel_thickness * 2),
            inner_radius=self._vacuum_vessel_inwall_start_rad,
            outer_radius=self._vacuum_vessel_body_end_rad,
            rotation_angle=self._rotation_angle,
            name="vessel_body",
            cut=cutting_list,
            color=(0.5, 0.5, 0.5),
        )
        return [self._vacuum_vessel_body]

    def _make_tf_coils(self):
        self._tf_coils = paramak.ToroidalFieldCoilRectangleRoundCorners(
            with_inner_leg=False,
            lower_inner_coordinates=(
                self._inner_bore_stop_rad,
                -self._inner_tf_leg_height / 2,
            ),
            mid_point_coordinates=(self._tf_start_rad, 0),
            thickness=self._outer_tf_coil_thickness,
            number_of_coils=self._number_of_coils,
            distance=self._tf_width,
            rotation_angle=self._rotation_angle,
            name="tf_coil_outer",
            color=(0.2, 1, 0.2),
            cut=[self._pf_coils, self._pf_casing],
        )

        return [self._tf_coils]

    # Checks and test
    def _port_checks(self):
        if (
            len(self._ports_angles) != len(self._port_heights)
            or len(self._ports_angles) != len(self._port_side_lengths)
            or len(self._port_z_pos) != len(self._port_side_lengths)
            or len(self._port_z_pos) != len(self._port_heights)
            or len(self._port_z_pos) != len(self._ports_angles)
        ):
            raise ValueError("Number of elements in Port Parameters don't match!")
        _port_coord_list = self._port_side_lengths + self._ports_angles + self._port_heights + self._ports_angles
        for cord in _port_coord_list:
            if not isinstance(cord, (float, int)):
                raise TypeError("Port parameters must be float or integer values!")

    def _pf_checks(self, tuple_bool):
        if (
            len(self._pf_coil_heights) != len(self._pf_coil_widths)
            or len(self._pf_coil_heights) != len(self._pf_coil_center_points)
            or len(self._pf_coil_heights) != len(self._pf_casing_thickness)
            or len(self._pf_coil_widths) != len(self._pf_casing_thickness)
            or len(self._pf_coil_center_points) != len(self._pf_casing_thickness)
        ):
            raise ValueError("Number of elements in PF Parameters don't match!")
        if not tuple_bool:
            _pf_lists = self._pf_coil_heights + self._pf_coil_widths + self._pf_casing_thickness

            for cord in _pf_lists:
                if not isinstance(cord, (float, int)):
                    raise TypeError("PF parameters must be float or integer values! yay")
        else:
            _pf_lists = (
                self._pf_coil_heights
                + self._pf_coil_widths
                + self._pf_casing_thickness
                + [x[0] for x in self._pf_coil_center_points]
                + [x[1] for x in self._pf_coil_center_points]
            )
            for cord in _pf_lists:
                if not isinstance(cord, (float, int)):
                    raise TypeError("PF parameters must be float or integer values!")
