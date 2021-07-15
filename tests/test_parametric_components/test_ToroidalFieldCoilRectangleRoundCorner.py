"""
The module contains testing functions for Paramak use. It calculates the
"""
from paramak import ToroidalFieldCoilRectangleRoundCorners as tfc
from math import pi


def surface_area(
        lower_left,
        middle_right,
        thickness,
        extrusion_length,
        with_inner_leg=False,
        test=False,
        XZ_face_only=False,
        extrusion_area_only=False):
    """
    Function calculates the total surface area of the TF coil from the coordinates given in the find_points function
    """
    test_object = tfc(
        lower_inner_coordinates=lower_left,
        mid_point_coordinates=middle_right,
        thickness=thickness,
        distance=extrusion_length,
        number_of_coils=1,
        with_inner_leg=with_inner_leg
    )

    analyse_attributes = test_object.analyse_attributes

    base, height, inner_rad, outter_rad = analyse_attributes
    print(analyse_attributes)
    # The surface area of the face in XZ plane is divisible into 5 segments
    base_segment_area = thickness * (base - inner_rad)
    vertical_segment_area = thickness * (height - (inner_rad * 2))
    corner_area = (pi / 4) * (outter_rad**2 - inner_rad**2)

    # XZ plane face area
    total_face_area = base_segment_area * 2 + \
        vertical_segment_area + corner_area * 2
    # The surface area of the planes in YZ plane
    contour_length = inner_rad * \
        (pi - 8) + pi * outter_rad + 2 * (2 * base + thickness + height)
    extrusion_area = contour_length * extrusion_length
    # Total Area
    total_bounding_surface = total_face_area * 2 + extrusion_area

    if with_inner_leg:
        # XZ plane face area
        total_face_area += thickness * height
        print(total_face_area)
        total_leg_surface_area = 2 * height * thickness + 2 * \
            extrusion_length * height + 2 * extrusion_length * thickness

        # Total bounding surface
        total_bounding_surface += total_leg_surface_area
        print("Face area: {}\nExtrusion Ares: {}\ntotal bounding area: {}".format(
            total_face_area, extrusion_area, total_bounding_surface))
    #print("Self testing:\nCalculated parameters:\nbase: {}\nheight: {}\ninner radius: {}\noutter radius: {}".format(base,height,inner_rad,outter_rad))

    if XZ_face_only:
        return total_face_area

    if extrusion_area_only:
        return extrusion_area

    return total_bounding_surface


def volume(
        lower_left,
        middle_right,
        thickness,
        extrusion_length,
        with_inner_leg=False,
        test=False):
    """
    The function calculates the volume from the given coordinates used for parametarising the component in find_points function in core module
    it takes an additional variable for extrusion length which is the thickness of the coil
    """

    face_area = surface_area(
        lower_left,
        middle_right,
        thickness,
        extrusion_length,
        test=False,
        XZ_face_only=True,
        with_inner_leg=with_inner_leg)
    print(face_area)
    total_shape_volume = face_area * extrusion_length

    if test:
        print("Self testing:\nArea of the XZ plane face:\n", face_area)
        print("Total Shape Volume is:", total_shape_volume)

    return total_shape_volume


if __name__ == "__main__":
    print("Area testing:\n")
    surface_area((50, 0), (100, 100), 20, 10, test=True, with_inner_leg=True)
    print("\nVolume testing:\n")
    volume((50, 0), (100, 100), 20, 10, test=True)
