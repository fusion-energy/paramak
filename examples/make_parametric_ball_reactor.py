
import paramak

my_reactor = paramak.BallReactor(major_radius=5,
                                 minor_radius=1)

my_reactor.export_stp()

my_reactor.export_neutronics_description()

