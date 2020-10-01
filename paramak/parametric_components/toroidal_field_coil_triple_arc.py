
import cadquery as cq
import numpy as np
from paramak import ExtrudeMixedShape
from collections import Iterable


class ToroidalFieldCoilTripleArc(ExtrudeMixedShape):
    """Toroidal field coil made of three arcs

    Args:
        R1 (float): smallest radius (cm)
        h (float): height of the straight section (cm)
        radii ((float, float)): radii of the small and medium arcs (cm)
        coverages ((float, float)): coverages of the small and medium arcs
            (deg)
        thickness (float): magnet thickness (cm)
        distance (float): extrusion distance (cm)
        number_of_coils (int): the number of tf coils. This changes by the
            azimuth_placement_angle dividing up 360 degrees by the number of
            coils.
        vertical_displacement (float, optional): vertical displacement (cm).
            Defaults to 0.
        with_inner_leg (Boolean): Include the inner tf leg (default True)

    Keyword Args:
        stp_filename (str, optional): The filename used when saving stp files
            as part of a reactor.
            Defaults to "ToroidalFieldCoilPrincetonD.stp".
        stl_filename (str, optional): The filename used when saving stl files
            as part of a reactor.
            Defaults to "ToroidalFieldCoilPrincetonD.stl".
        color ((float, float, float), optional): the color to use when
            exportin as html graphs or png images. Defaults to None.
        azimuth_placement_angle (float, optional): The angle or angles to use
            when rotating the shape on the azimuthal axis. Defaults to 0.
        name (str, optional): the legend name used when exporting a html
            graph of the shape. Defaults to None.
        material_tag (str, optional): The material name to use when exporting
            the neutronics description.. Defaults to "outer_tf_coil_mat".
    """

    def __init__(
        self,
        R1,
        h,
        radii,
        coverages,
        thickness,
        distance,
        number_of_coils,
        vertical_displacement=0.0,
        stp_filename="ToroidalFieldCoilPrincetonD.stp",
        stl_filename="ToroidalFieldCoilPrincetonD.stl",
        color=(0.5, 0.5, 0.5),
        azimuth_placement_angle=0,
        name=None,
        material_tag="outer_tf_coil_mat",
        with_inner_leg=True,
        **kwargs
    ):

        default_dict = {
            "points": None,
            "workplane": "XZ",
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
        self.R1 = R1
        self.h = h
        self.small_radius, self.mid_radius = radii

        self.small_coverage, self.mid_coverage = coverages
        self.thickness = thickness
        self.distance = distance
        self.number_of_coils = number_of_coils
        self.vertical_displacement = vertical_displacement
        self.with_inner_leg = with_inner_leg

    @property
    def azimuth_placement_angle(self):
        self.find_azimuth_placement_angle()
        return self._azimuth_placement_angle

    @azimuth_placement_angle.setter
    def azimuth_placement_angle(self, value):
        self._azimuth_placement_angle = value

    def compute_curve(self, R1, h, radii, coverages):
        npoints = 500

        small_radius, mid_radius = radii
        small_coverage, mid_coverage = coverages
        asum = small_coverage + mid_coverage

        # small arc
        theta = np.linspace(
            0, small_coverage, round(0.5 * npoints * small_coverage / np.pi))
        small_arc_R = R1 + small_radius * (1 - np.cos(theta))
        small_arc_Z = h + small_radius * np.sin(theta)
        R = small_arc_R
        Z = small_arc_Z

        # mid arc
        theta = np.linspace(
            theta[-1], asum, round(0.5 * npoints * mid_coverage / np.pi))
        mid_arc_R = R[-1] + mid_radius * \
            (np.cos(small_coverage) - np.cos(theta))
        mid_arc_Z = Z[-1] + mid_radius * \
            (np.sin(theta) - np.sin(small_coverage))
        R = np.append(R, mid_arc_R[1:])
        Z = np.append(Z, mid_arc_Z[1:])

        # large arc
        large_radius = (Z[-1]) / np.sin(np.pi - asum)
        theta = np.linspace(theta[-1], np.pi, 60)
        large_arc_R = R[-1] + large_radius * \
            (np.cos(np.pi - theta) - np.cos(np.pi - asum))
        large_arc_Z = Z[-1] - large_radius * \
            (np.sin(asum) - np.sin(np.pi - theta))
        R = np.append(R, large_arc_R[1:])
        Z = np.append(Z, large_arc_Z[1:])

        R = np.append(R, np.flip(R)[1:])
        Z = np.append(Z, -np.flip(Z)[1:])
        return R, Z

    def find_points(self):
        """Finds the XZ points joined by connections that describe the 2D
        profile of the toroidal field coil shape."""

        thickness = self.thickness
        small_radius, mid_radius = self.small_radius, self.mid_radius
        small_coverage, mid_coverage = self.small_coverage, self.mid_coverage
        small_coverage *= np.pi / 180  # convert to radians
        mid_coverage *= np.pi / 180

        # create inner coordinates
        R_inner, Z_inner = self.compute_curve(
            self.R1, self.h*0.5, radii=(small_radius, mid_radius),
            coverages=(small_coverage, mid_coverage))

        # create outer coordinates
        R_outer, Z_outer = self.compute_curve(
            self.R1 - thickness, self.h*0.5,
            radii=(small_radius + thickness, mid_radius + thickness),
            coverages=(small_coverage, mid_coverage))
        R_outer, Z_outer = np.flip(R_outer), np.flip(Z_outer)

        # add vertical displacement
        Z_outer += self.vertical_displacement
        Z_inner += self.vertical_displacement

        # create points with connections
        points = []
        for i in range(len(R_inner)):
            points.append([R_inner[i], Z_inner[i], 'spline'])
        points[-1][2] = 'straight'
        for i in range(len(R_outer)):
            points.append([R_outer[i], Z_outer[i], 'spline'])
        points[-1][2] = 'straight'
        self.points = points

        # extract helping points for inner leg
        inner_leg_connection_points = []

        inner_leg_connection_points.append(
            (R_inner[0], Z_inner[0]))
        inner_leg_connection_points.append(
            (R_inner[-1], Z_inner[-1]))
        inner_leg_connection_points.append(
            (R_outer[0], Z_outer[0]))
        inner_leg_connection_points.append(
            (R_outer[-1], Z_outer[-1]))

        self.inner_leg_connection_points = inner_leg_connection_points

    def find_azimuth_placement_angle(self):
        """Calculates the azimuth placement angles based on the number of tf coils"""

        angles = list(
            np.linspace(
                0,
                360,
                self.number_of_coils,
                endpoint=False))

        self.azimuth_placement_angle = angles

    def create_solid(self):
        """Creates a 3d solid using points with straight and spline
        connections edges, azimuth_placement_angle and distance.

        :return: a 3d solid volume
        :rtype: a cadquery solid
        """

        # obtains the first two values of the points list
        XZ_points = [(p[0], p[1]) for p in self.points]

        # obtains the last values of the points list
        connections = [p[2] for p in self.points[:-1]]

        current_linetype = connections[0]
        current_points_list = []
        instructions = []
        # groups together common connection types
        for i, c in enumerate(connections):
            if c == current_linetype:
                current_points_list.append(XZ_points[i])
            else:
                current_points_list.append(XZ_points[i])
                instructions.append({current_linetype: current_points_list})
                current_linetype = c
                current_points_list = [XZ_points[i]]
        instructions.append({current_linetype: current_points_list})

        if list(instructions[-1].values())[0][-1] != XZ_points[0]:
            keyname = list(instructions[-1].keys())[0]
            instructions[-1][keyname].append(XZ_points[0])

        solid = cq.Workplane(self.workplane)
        solid.moveTo(XZ_points[0][0], XZ_points[0][1])

        for entry in instructions:
            if list(entry.keys())[0] == "spline":
                solid = solid.spline(listOfXYTuple=list(entry.values())[0])
            if list(entry.keys())[0] == "straight":
                solid = solid.polyline(list(entry.values())[0])

        # performs extrude in both directions, hence distance / 2
        solid = solid.close().extrude(distance=-self.distance / 2.0, both=True)

        if self.with_inner_leg is True:
            inner_leg_solid = cq.Workplane(self.workplane)
            inner_leg_solid.moveTo(XZ_points[0][0], XZ_points[0][1])
            inner_leg_solid = inner_leg_solid.polyline(
                self.inner_leg_connection_points)
            inner_leg_solid = inner_leg_solid.close().extrude(
                distance=-self.distance / 2.0, both=True)

            solid = cq.Compound.makeCompound(
                [a.val() for a in [inner_leg_solid, solid]]
            )

        # Checks if the azimuth_placement_angle is a list of angles
        if isinstance(self.azimuth_placement_angle, Iterable):
            rotated_solids = []
            # Perform seperate rotations for each angle
            for angle in self.azimuth_placement_angle:
                rotated_solids.append(
                    solid.rotate(
                        (0, 0, -1), (0, 0, 1), angle))
            solid = cq.Workplane(self.workplane)

            # Joins the seperate solids together
            for i in rotated_solids:
                solid = solid.union(i)
        else:
            # Peform rotations for a single azimuth_placement_angle angle
            solid = solid.rotate(
                (0, 0, 1), (0, 0, -1), self.azimuth_placement_angle)

        self.perform_boolean_operations(solid)

        return solid
