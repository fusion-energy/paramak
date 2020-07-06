
import paramak

my_reactor = paramak.BallReactor(major_radius=300,
                                 minor_radius=100,
                                 offset_from_plasma=20,
                                 blanket_thickness=100)

my_reactor.export_stp()

my_reactor.export_neutronics_description()

