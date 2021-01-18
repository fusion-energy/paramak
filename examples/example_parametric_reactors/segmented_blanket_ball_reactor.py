"""
This example creates a ball reactor with segmented blankets using the
SegmentedBlanketBallReactor parametric reactor. By default the script saves
stp, stl, html and svg files. Fillets the firstwall as this is not currently
done in the SegmentedBlanketBallReactor reactor class.
"""

import cadquery as cq
import paramak


def make_ball_reactor_seg(outputs=['stp', 'neutronics', 'svg', 'stl', 'html']):

    my_reactor = paramak.SegmentedBlanketBallReactor(
        inner_bore_radial_thickness=5,
        inboard_tf_leg_radial_thickness=25,
        center_column_shield_radial_thickness=45,
        divertor_radial_thickness=150,
        inner_plasma_gap_radial_thickness=50,
        plasma_radial_thickness=300,
        outer_plasma_gap_radial_thickness=50,
        firstwall_radial_thickness=15,
        blanket_radial_thickness=50,
        blanket_rear_wall_radial_thickness=30,
        elongation=2,
        triangularity=0.55,
        number_of_tf_coils=16,
        rotation_angle=180,
        pf_coil_radial_thicknesses=[50, 50, 50, 50],
        pf_coil_vertical_thicknesses=[50, 50, 50, 50],
        pf_coil_to_rear_blanket_radial_gap=50,
        pf_coil_to_tf_coil_radial_gap=50,
        outboard_tf_coil_radial_thickness=100,
        outboard_tf_coil_poloidal_thickness=50,
        gap_between_blankets=30,
        number_of_blanket_segments=15,
        blanket_fillet_radius=15,
    )

    # finds the correct edges to fillet
    x_coord = my_reactor.major_radius
    front_face = my_reactor._blanket.solid.faces(
        cq.NearestToPointSelector((x_coord, 0, 0)))
    front_edge = front_face.edges(cq.NearestToPointSelector((x_coord, 0, 0)))
    front_edge_length = front_edge.val().Length()
    my_reactor._blanket.solid = my_reactor._blanket.solid.edges(
        paramak.EdgeLengthSelector(front_edge_length)).fillet(
        my_reactor.blanket_fillet_radius)

    # cuts away the breeder zone
    my_reactor._blanket.solid = my_reactor._blanket.solid.cut(
        my_reactor._blanket.solid)

    my_reactor._blanket.export_stp('firstwall_with_fillet.stp')

    if 'stp' in outputs:
        my_reactor.export_stp(output_folder='SegmentedBlanketBallReactor')
    if 'neutronics' in outputs:
        my_reactor.export_neutronics_description(
            'SegmentedBlanketBallReactor/manifest.json')
    if 'svg' in outputs:
        my_reactor.export_svg('SegmentedBlanketBallReactor/reactor.svg')
    if 'stl' in outputs:
        my_reactor.export_stl(output_folder='SegmentedBlanketBallReactor')
    if 'html' in outputs:
        my_reactor.export_html('SegmentedBlanketBallReactor/reactor.html')


if __name__ == "__main__":
    make_ball_reactor_seg(['stp', 'neutronics', 'svg', 'stl', 'html'])
