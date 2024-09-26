import os
from pathlib import Path

import pytest
from cadquery import exporters

import paramak

plasma = paramak.plasma_simplified(
    major_radius=450, minor_radius=150, triangularity=0.55, elongation=2, rotation_angle=160
)

test_shape = paramak.blanket_from_plasma(
    thickness=150,
    start_angle=-90,
    stop_angle=240,
)


def test_creation_plasma():
    """Checks that a cadquery solid can be created by passing a plasma to
    the BlanketFP parametric component."""

    assert test_shape.vals()[0].Volume() > 1000


def test_faces():
    """creates a blanket using the BlanketFP parametric component and checks
    that a solid with the correct number of faces is created"""

    test_shape = paramak.blanket_from_plasma(thickness=150, start_angle=-90, stop_angle=240, rotation_angle=360)
    assert len(test_shape.vals()[0].Faces()) == 4

    test_shape = paramak.blanket_from_plasma(thickness=150, start_angle=-90, stop_angle=240, rotation_angle=180)
    assert len(test_shape.vals()[0].Faces()) == 6


def test_creation_variable_thickness_from_tuple():
    """Checks that a cadquery solid can be created using the BlanketFP
    parametric component when a tuple of thicknesses is passed as an
    argument."""

    test_shape = paramak.blanket_from_plasma(start_angle=-90, stop_angle=240, thickness=(100, 200))

    assert test_shape.vals()[0].Volume() > 1000


def test_creation_variable_thickness_from_2_lists():
    """Checks that a cadquery solid can be created using the BlanketFP
    parametric component when a list of angles and a list of thicknesses
    are passed as an argument."""

    test_shape = paramak.blanket_from_plasma(start_angle=-90, stop_angle=240, thickness=[(-90, 240), [10, 30]])

    assert test_shape is not None


def test_creation_variable_thickness_function():
    """Checks that a cadquery solid can be created using the BlanketFP
    parametric component when a thickness function is passed as an
    argument."""

    def thickness(theta):
        return 10 + 0.1 * theta

    test_shape = paramak.blanket_from_plasma(start_angle=-90, stop_angle=240, thickness=thickness)

    assert test_shape.vals()[0].Volume() > 1000


def test_creation_variable_offset_from_tuple():
    """Checks that a cadquery solid can be created using the BlanketFP
    parametric component when a tuple of offsets is passed as an
    argument."""

    test_shape = paramak.blanket_from_plasma(thickness=150, start_angle=-90, stop_angle=240, offset_from_plasma=(0, 10))

    assert test_shape.vals()[0].Volume() > 1000


def test_creation_variable_offset_from_2_lists():
    """Checks that a cadquery solid can be created using the BlanketFP
    parametric component when a list of offsets and a list of angles are
    passed as an argument."""

    test_shape = paramak.blanket_from_plasma(
        thickness=150, start_angle=90, stop_angle=270, offset_from_plasma=[[270, 100, 90], [0, 5, 10]]
    )

    assert test_shape is not None


def test_creation_variable_offset_error():
    """Checks that an error is raised when two lists with different
    lengths are passed in offset_from_plasma as an argument."""

    def test_different_lengths():
        with pytest.raises(ValueError) as excinfo:
            paramak.blanket_from_plasma(
                thickness=150, start_angle=90, stop_angle=270, offset_from_plasma=[[270, 100, 90], [0, 5, 10, 15]]
            )
        assert "maximum recursion" in str(excinfo.value)


def test_creation_variable_offset_function():
    """Checks that a cadquery solid can be created using the BlanketFP
    parametric component when an offset function is passed."""

    def offset(theta):
        return 10 + 0.1 * theta

    test_shape = paramak.blanket_from_plasma(thickness=150, start_angle=-90, stop_angle=240, offset_from_plasma=offset)

    assert test_shape is not None
    assert test_shape.vals()[0].Volume() > 1000


def test_full_cov_stp_export():
    """Creates a blanket using the BlanketFP parametric component with full
    coverage and checks that an stp file can be exported using the export_stp
    method."""

    test_shape = paramak.blanket_from_plasma(thickness=150, rotation_angle=180, start_angle=0, stop_angle=360)

    exporters.export(test_shape, "test_blanket_full_cov.step")
    assert Path("test_blanket_full_cov.step").exists()
    os.system("rm test_blanket_full_cov.step")


def test_full_cov_full_rotation():
    """Creates a blanket using the BlanketFP parametric component with full
    coverage and full rotation and checks that an stp file can be exported using
    the export_stp method."""

    test_shape = paramak.blanket_from_plasma(thickness=150, rotation_angle=360, start_angle=0, stop_angle=360)

    exporters.export(test_shape, "test_blanket_full_cov_full_rot.step")
    assert Path("test_blanket_full_cov_full_rot.step").exists()
    os.system("rm test_blanket_full_cov_full_rot.step")


def test_overlapping():
    """Creates an overlapping geometry and checks that a warning is raised."""

    with pytest.warns(UserWarning, match="blanket_from_plasma: Some points with negative R"):
        paramak.blanket_from_plasma(
            major_radius=100,
            minor_radius=100,
            triangularity=0.5,
            elongation=2,
            thickness=200,
            stop_angle=360,
            start_angle=0,
        )
