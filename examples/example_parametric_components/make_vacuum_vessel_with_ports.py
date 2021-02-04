
"""
This python script demonstrates the creation of a vacuum vessel with shaped
different ports cut out.
"""

import numpy as np
import paramak


def main():

    number_of_ports_in_360_degrees = 12
    angles_for_ports = np.linspace(0, 360, number_of_ports_in_360_degrees)

    # makes the upper row of ports
    rotated_ports = paramak.PortCutterRotated(
        center_point=(0, 0),
        polar_coverage_angle=10,
        rotation_angle=10,
        polar_placement_angle=25,
        azimuth_placement_angle=angles_for_ports
    )

    # makes the middle row of ports
    circular_ports = paramak.PortCutterCircular(
        distance=5,
        center_point=(0, 0),
        radius=0.2,
        azimuth_placement_angle=angles_for_ports
    )

    # makes the lower row of ports
    rectangular_ports = paramak.PortCutterRectangular(
        distance=5,
        center_point=(-1, 0),
        height=0.3,
        width=0.4,
        fillet_radius=0.08,
        azimuth_placement_angle=angles_for_ports
    )

    # creates the hollow cylinder vacuum vessel and cuts away the ports
    vacuum_vessel = paramak.VacuumVessel(
        height=4,
        inner_radius=2,
        thickness=0.2,
        cut=[rotated_ports, rectangular_ports, circular_ports]
    )

    # eports images and 3D CAD
    vacuum_vessel.export_svg('vacuum_vessel_with_ports.svg')
    vacuum_vessel.export_stp('vacuum_vessel_with_ports.stp')


if __name__ == "__main__":
    main()
