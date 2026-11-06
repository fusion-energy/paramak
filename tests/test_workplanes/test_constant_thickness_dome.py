import pytest

import cadquery as cq

import paramak
import paramak.workplanes

a = paramak.constant_thickness_dome(upper_or_lower="upper")
cq.exporters.export(a, "upper.step")
a = paramak.constant_thickness_dome(upper_or_lower="lower")
cq.exporters.export(a, "lower.step")


@pytest.mark.parametrize("upper_or_lower", ["upper", "lower"])
def test_origin_moves_the_whole_dome(upper_or_lower):
    dome = paramak.constant_thickness_dome(upper_or_lower=upper_or_lower)
    moved = paramak.constant_thickness_dome(upper_or_lower=upper_or_lower, origin=(0, 0, 100))
    bb, moved_bb = dome.val().BoundingBox(), moved.val().BoundingBox()
    assert moved_bb.zmin == pytest.approx(bb.zmin + 100, abs=1e-3)
    assert moved_bb.zmax == pytest.approx(bb.zmax + 100, abs=1e-3)
    assert moved_bb.xmax == pytest.approx(bb.xmax, abs=1e-3)
    assert moved.val().Volume() == pytest.approx(dome.val().Volume(), rel=1e-6)
