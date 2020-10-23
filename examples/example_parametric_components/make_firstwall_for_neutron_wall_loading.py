
"""
For some neutronics tallies such as neutron wall loading it is necessary to
segment the geometry so that individual neutronics tallies can be recorded
for each face. This can be done using the PoloidalSegments(). With this
segmented geometry it is then easier to find neutron wall loading as a function
of poloidal angle.
"""

import paramak


def make_segmented_firstwall():

    # makes the firstwall
    firstwall = paramak.BlanketFP(minor_radius=150,
                                  major_radius=450,
                                  triangularity=0.55,
                                  elongation=2.0,
                                  thickness=2,
                                  start_angle=270,
                                  stop_angle=-90,
                                  rotation_angle=10)

    # segments the firstwall poloidally into 40 equal angle segments
    segmented_firstwall = paramak.PoloidalSegments(
        shape_to_segment=firstwall,
        center_point=(450, 0),  # this is the middle of the plasma
        number_of_segments=40,
    )

    # saves the segmented firstwall as an stp file
    segmented_firstwall.export_stp('segmented_firstwall.stp')


if __name__ == "__main__":
    make_segmented_firstwall()
