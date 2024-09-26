from cadquery import exporters

import paramak

# TODO try OCP 7.7.1 and newer cadquery
# lower with rotation_angle less than 360 can fail, OCP 7.7.0


def test_construction():
    dome_section, cylinder_section = paramak.u_shaped_dome(upper_or_lower="lower", rotation_angle=360)

    exporters.export(dome_section, "dome_section.step")
    exporters.export(cylinder_section, "cylinder_section.step")

    domes = paramak.u_shaped_dome(upper_or_lower="upper", rotation_angle=360)
    domes = paramak.u_shaped_dome(upper_or_lower="upper", rotation_angle=360, reference_point=("lower", 10))
    domes = paramak.u_shaped_dome(upper_or_lower="upper", rotation_angle=360, reference_point=("center", 20))
