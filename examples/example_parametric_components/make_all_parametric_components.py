"""
This python script demonstrates the creation of all parametric shapes available
in the paramak tool
"""

import paramak


def main():

    rot_angle = 180
    all_components = []

    plasma = paramak.Plasma(
        # default parameters
        rotation_angle=rot_angle,
        stp_filename="plasma_shape.stp",
    )
    all_components.append(plasma)

    component = paramak.BlanketFP(
        plasma=plasma,
        thickness=100,
        stop_angle=90,
        start_angle=-90,
        offset_from_plasma=30,
        rotation_angle=rot_angle,
        stp_filename="blanket_constant_thickness_outboard_plasma.stp",
    )
    all_components.append(component)

    component = paramak.BlanketCutterStar(
        height=2000,
        width=2000,
        distance=100)
    all_components.append(component)

    component = paramak.BlanketFP(
        plasma=plasma,
        thickness=100,
        stop_angle=90,
        start_angle=250,
        offset_from_plasma=30,
        rotation_angle=rot_angle,
        stp_filename="blanket_constant_thickness_inboard_plasma.stp",
    )
    all_components.append(component)

    component = paramak.BlanketFP(
        plasma=plasma,
        thickness=100,
        stop_angle=250,
        start_angle=-90,
        offset_from_plasma=30,
        rotation_angle=rot_angle,
        stp_filename="blanket_constant_thickness_plasma.stp",
    )
    all_components.append(component)

    CenterColumnShieldCylinder = paramak.CenterColumnShieldCylinder(
        inner_radius=80,
        outer_radius=100,
        height=300,
        rotation_angle=rot_angle,
        stp_filename="center_column_shield_cylinder.stp",
    )
    all_components.append(CenterColumnShieldCylinder)

    component = paramak.InboardFirstwallFCCS(
        central_column_shield=CenterColumnShieldCylinder,
        thickness=50,
        rotation_angle=rot_angle,
        stp_filename="firstwall_from_center_column_shield_cylinder.stp",
    )
    all_components.append(component)

    CenterColumnShieldHyperbola = paramak.CenterColumnShieldHyperbola(
        inner_radius=50,
        mid_radius=75,
        outer_radius=100,
        height=300,
        rotation_angle=rot_angle,
        stp_filename="center_column_shield_hyperbola.stp",
    )
    all_components.append(CenterColumnShieldHyperbola)

    component = paramak.InboardFirstwallFCCS(
        central_column_shield=CenterColumnShieldHyperbola,
        thickness=50,
        rotation_angle=rot_angle,
        stp_filename="firstwall_from_center_column_shield_hyperbola.stp",
    )
    all_components.append(component)

    CenterColumnShieldCircular = paramak.CenterColumnShieldCircular(
        inner_radius=50,
        mid_radius=75,
        outer_radius=100,
        height=300,
        rotation_angle=rot_angle,
        stp_filename="center_column_shield_circular.stp",
    )
    all_components.append(CenterColumnShieldCircular)

    component = paramak.InboardFirstwallFCCS(
        central_column_shield=CenterColumnShieldCircular,
        thickness=50,
        rotation_angle=rot_angle,
        stp_filename="firstwall_from_center_column_shield_circular.stp",
    )
    all_components.append(component)

    CenterColumnShieldFlatTopHyperbola = paramak.CenterColumnShieldFlatTopHyperbola(
        inner_radius=50,
        mid_radius=75,
        outer_radius=100,
        arc_height=220,
        height=300,
        rotation_angle=rot_angle,
        stp_filename="center_column_shield_flat_top_hyperbola.stp",
    )
    all_components.append(CenterColumnShieldFlatTopHyperbola)

    component = paramak.InboardFirstwallFCCS(
        central_column_shield=CenterColumnShieldFlatTopHyperbola,
        thickness=50,
        rotation_angle=rot_angle,
        stp_filename="firstwall_from_center_column_shield_flat_top_hyperbola.stp",
    )
    all_components.append(component)

    CenterColumnShieldFlatTopCircular = paramak.CenterColumnShieldFlatTopCircular(
        inner_radius=50,
        mid_radius=75,
        outer_radius=100,
        arc_height=220,
        height=300,
        rotation_angle=rot_angle,
        stp_filename="center_column_shield_flat_top_Circular.stp",
    )
    all_components.append(CenterColumnShieldFlatTopCircular)

    component = paramak.InboardFirstwallFCCS(
        central_column_shield=CenterColumnShieldFlatTopCircular,
        thickness=50,
        rotation_angle=rot_angle,
        stp_filename="firstwall_from_center_column_shield_flat_top_Circular.stp",
    )
    all_components.append(component)

    CenterColumnShieldPlasmaHyperbola = paramak.CenterColumnShieldPlasmaHyperbola(
        inner_radius=150,
        mid_offset=50,
        edge_offset=40,
        height=800,
        rotation_angle=rot_angle,
        stp_filename="center_column_shield_plasma_hyperbola.stp",
    )
    all_components.append(CenterColumnShieldPlasmaHyperbola)

    component = paramak.InboardFirstwallFCCS(
        central_column_shield=CenterColumnShieldPlasmaHyperbola,
        thickness=50,
        rotation_angle=rot_angle,
        stp_filename="firstwall_from_center_column_shield_plasma_hyperbola.stp",
    )
    all_components.append(component)

    component = paramak.InnerTfCoilsCircular(
        inner_radius=25,
        outer_radius=100,
        number_of_coils=10,
        gap_size=5,
        height=300,
        stp_filename="inner_tf_coils_circular.stp",
    )
    all_components.append(component)

    component = paramak.InnerTfCoilsFlat(
        inner_radius=25,
        outer_radius=100,
        number_of_coils=10,
        gap_size=5,
        height=300,
        stp_filename="inner_tf_coils_flat.stp",
    )
    all_components.append(component)

    # this makes 4 pf coil cases
    pf_coil_set = paramak.PoloidalFieldCoilCaseSet(
        heights=[10, 10, 20, 20],
        widths=[10, 10, 20, 40],
        casing_thicknesses=[5, 5, 10, 10],
        center_points=[(100, 100), (100, 150), (50, 200), (50, 50)],
        rotation_angle=rot_angle,
        stp_filename="pf_coil_case_set.stp"
    )
    all_components.append(pf_coil_set)

    # this makes 4 pf coils
    pf_coil_set = paramak.PoloidalFieldCoilSet(
        heights=[10, 10, 20, 20],
        widths=[10, 10, 20, 40],
        center_points=[(100, 100), (100, 150), (50, 200), (50, 50)],
        rotation_angle=rot_angle,
        stp_filename="pf_coil_set.stp"
    )
    all_components.append(pf_coil_set)

    # this makes 4 pf coil cases for the 4 pf coils made above
    component = paramak.PoloidalFieldCoilCaseSetFC(
        pf_coils=pf_coil_set,
        casing_thicknesses=[5, 5, 10, 10],
        rotation_angle=rot_angle,
        stp_filename="pf_coil_cases_set.stp"
    )
    all_components.append(component)

    # this makes 1 pf coils
    pf_coil = paramak.PoloidalFieldCoil(
        center_point=(100, 100),
        height=20,
        width=20,
        rotation_angle=rot_angle,
        stp_filename="poloidal_field_coil.stp"
    )
    all_components.append(pf_coil)

    # this makes one PF coil case for the provided pf coil
    component = paramak.PoloidalFieldCoilCaseSetFC(
        pf_coils=[pf_coil],
        casing_thicknesses=[10],
        rotation_angle=rot_angle,
        stp_filename="pf_coil_cases_set_fc.stp")
    all_components.append(component)

    component = paramak.PoloidalFieldCoilCaseFC(
        pf_coil=pf_coil,
        casing_thickness=10,
        rotation_angle=rot_angle,
        stp_filename="poloidal_field_coil_case_fc.stp",
    )
    all_components.append(component)

    component = paramak.PoloidalFieldCoilCase(
        center_point=(100, 100),
        coil_height=20,
        coil_width=20,
        casing_thickness=10,
        rotation_angle=rot_angle,
        stp_filename="poloidal_field_coil_case.stp",
    )
    all_components.append(component)

    component = paramak.BlanketConstantThicknessArcV(
        inner_lower_point=(300, -200),
        inner_mid_point=(500, 0),
        inner_upper_point=(300, 200),
        thickness=100,
        rotation_angle=rot_angle,
        stp_filename="blanket_arc_v.stp",
    )
    all_components.append(component)

    component = paramak.BlanketConstantThicknessArcH(
        inner_lower_point=(300, -200),
        inner_mid_point=(400, 0),
        inner_upper_point=(300, 200),
        thickness=100,
        rotation_angle=rot_angle,
        stp_filename="blanket_arc_h.stp",
    )
    all_components.append(component)

    component = paramak.ToroidalFieldCoilRectangle(
        horizontal_start_point=(100, 700),
        vertical_mid_point=(800, 0),
        thickness=150,
        distance=60,
        stp_filename="tf_coil_rectangle.stp",
        number_of_coils=1,
    )
    all_components.append(component)

    component = paramak.ToroidalFieldCoilCoatHanger(
        horizontal_start_point=(200, 500),
        horizontal_length=400,
        vertical_mid_point=(700, 50),
        vertical_length=500,
        thickness=50,
        distance=50,
        stp_filename="toroidal_field_coil_coat_hanger.stp",
        number_of_coils=1,
    )
    all_components.append(component)

    component = paramak.ToroidalFieldCoilTripleArc(
        R1=80,
        h=200,
        radii=(70, 100),
        coverages=(60, 60),
        thickness=30,
        distance=30,
        number_of_coils=1,
        stp_filename="toroidal_field_coil_triple_arc.stp"
    )
    all_components.append(component)

    magnet = paramak.ToroidalFieldCoilPrincetonD(
        R1=80,
        R2=300,
        thickness=30,
        distance=30,
        number_of_coils=1,
        stp_filename="toroidal_field_coil_princeton_d.stp"
    )
    all_components.append(magnet)

    component = paramak.ITERtypeDivertor(
        # default parameters
        rotation_angle=rot_angle,
        stp_filename="ITER_type_divertor.stp",
    )
    all_components.append(component)

    component = paramak.PortCutterRotated(
        center_point=(450, 0),
        polar_coverage_angle=20,
        rotation_angle=10,
        polar_placement_angle=45,
        azimuth_placement_angle=0
    )
    all_components.append(component)

    component = paramak.PortCutterRectangular(
        distance=3,
        center_point=(0, 0),
        height=0.2,
        width=0.4,
        fillet_radius=0.02,
        azimuth_placement_angle=[0, 45, 90, 180]
    )
    all_components.append(component)

    component = paramak.PortCutterCircular(
        distance=3,
        center_point=(0.25, 0),
        radius=0.1,
        # azimuth_placement_angle=[0, 45, 90, 180], # TODO: fix issue #548
        azimuth_placement_angle=[0, 45, 90],
    )
    all_components.append(component)

    component = paramak.VacuumVessel(
        height=2, inner_radius=1, thickness=0.2, rotation_angle=270
    )
    all_components.append(component)

    component = paramak.CoolantChannelRingStraight(
        height=200,
        channel_radius=10,
        ring_radius=70,
        number_of_coolant_channels=8,
        workplane="XY",
        rotation_axis="Z",
        stp_filename="coolant_channel_ring_straight.stp",
    )
    all_components.append(component)

    component = paramak.CoolantChannelRingCurved(
        height=200,
        channel_radius=10,
        ring_radius=70,
        mid_offset=-20,
        number_of_coolant_channels=8,
        workplane="XY",
        path_workplane="XZ",
        stp_filename="coolant_channel_ring_curved.stp",
        force_cross_section=True
    )
    all_components.append(component)

    component = paramak.RotatedIsoscelesTriangle(
        height=20,
        base_length=15,
        pivot_angle=0,
        pivot_point=(100, 50),
        rotation_angle=70,
        workplane='XY',
        stp_filename='rotated_isosceles_triangle.stp'
    )
    all_components.append(component)

    component = paramak.RotatedTrapezoid(
        length_1=10,
        length_2=20,
        length_3=30,
        pivot_angle=0,
        pivot_point=(100, 50),
        rotation_angle=45,
        stp_filename='rotated_trapezoid.stp'
    )
    all_components.append(component)

    component = paramak.PoloidalSegments(
        number_of_segments=5,
        center_point=(400, 50)
    )
    all_components.append(component)

    component = paramak.TFCoilCasing(
        magnet=magnet,
        inner_offset=10,
        outer_offset=15,
        vertical_section_offset=20,
        distance=40
    )
    all_components.append(component)

    component = paramak.HexagonPin(
        length_of_side=5,
        distance=10,
        center_point=(10, 20)
    )
    all_components.append(component)

    return all_components


if __name__ == "__main__":
    all_components = main()
    filenames = []
    for components in all_components:
        components.export_stp()
        components.export_html(components.stp_filename[:-4] + '.html')
        filenames.append(components.stp_filename)
    print(filenames)
