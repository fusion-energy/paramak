import inspect

import pytest

import paramak


def test_public_export():
    assert "arc_from_2026_paper" in paramak.__all__
    assert callable(paramak.arc_from_2026_paper)


def test_defaults_match_sparc():
    #ARC Replace this comparison with verified ARC defaults when data are available.
    arc = inspect.signature(paramak.arc_from_2026_paper).parameters
    sparc = inspect.signature(paramak.sparc_from_2020_paper).parameters
    assert list(arc) == list(sparc)
    for name in arc:
        assert arc[name].default == sparc[name].default


@pytest.mark.parametrize("kwargs", [{}, dict(rotation_angle=90, number_of_tf_coils=16,
                                            pf_coil_case_thickness=5, colors={"plasma": (1, 0, 0)})])
def test_valid_calls_are_unimplemented(kwargs):
    #ARC Replace with geometry assertions and shared test registration once implemented.
    with pytest.raises(NotImplementedError, match="supply ARC paper geometry"):
        paramak.arc_from_2026_paper(**kwargs)


@pytest.mark.parametrize("angle", [0, -10, 361])
def test_invalid_rotation_angle(angle):
    with pytest.raises(ValueError, match="rotation_angle"):
        paramak.arc_from_2026_paper(rotation_angle=angle)


@pytest.mark.parametrize("count", [0, -1, 2.5, True])
def test_invalid_tf_coil_count(count):
    with pytest.raises(ValueError, match="number_of_tf_coils"):
        paramak.arc_from_2026_paper(number_of_tf_coils=count)
