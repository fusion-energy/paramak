import pytest

from cadquery import exporters

import paramak

# TODO try OCP 7.7.1 and newer cadquery
# lower with rotation_angle less than 360 can fail, OCP 7.7.0


def test_construction():
    dome_section, cylinder_section = paramak.u_shaped_dome(upper_or_lower="lower", rotation_angle=360)

    exporters.export(dome_section, "dome_section.step")
    exporters.export(cylinder_section, "cylinder_section.step")

    paramak.u_shaped_dome(upper_or_lower="upper", rotation_angle=360)
    paramak.u_shaped_dome(upper_or_lower="upper", rotation_angle=360, reference_point=("lower", 10))
    paramak.u_shaped_dome(upper_or_lower="upper", rotation_angle=360, reference_point=("center", 20))


@pytest.mark.parametrize("upper_or_lower", ["upper", "lower"])
def test_lower_reference_point_is_the_lowest_point(upper_or_lower):
    "the shape starts at the lower reference point with no gap below the cylinder"

    parts = paramak.u_shaped_dome(reference_point=("lower", 20), upper_or_lower=upper_or_lower)
    lowest = min(part.val().BoundingBox().zmin for part in parts)
    assert lowest == pytest.approx(20, abs=1e-3)
    dome, cylinder = parts
    # the dome and cylinder meet
    if upper_or_lower == "upper":
        assert dome.val().BoundingBox().zmin == pytest.approx(cylinder.val().BoundingBox().zmax, abs=1e-3)
    else:
        assert dome.val().BoundingBox().zmax == pytest.approx(cylinder.val().BoundingBox().zmin, abs=1e-3)
