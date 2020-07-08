
__doc__ = """This python script demonstrates the creation of a breeder blanket from points"""

from paramak import RotateMixedShape

blanket = RotateMixedShape(
    points=[
        (538, 305, "straight"),
        (538, -305, "straight"),
        (322, -305, "spline"),
        (470, 0, "spline"),
        (322, 305, "straight")
    ]
)

blanket.rotation_angle = 180
blanket.export_stp("blanket_from_points.stp")
