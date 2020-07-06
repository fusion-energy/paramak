
import paramak

my_reactor = paramak.BallReactor(major_radius=300,
                                 minor_radius=100,
                                 offset_from_plasma=20,
                                 blanket_thickness=100,
                                 center_column_shield_outer_radius=180,
                                 center_column_shield_inner_radius=120,
                                 number_of_tf_coils=16
                                 )

my_reactor.export_stp()

my_reactor.export_neutronics_description()

