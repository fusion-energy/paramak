import pytest
from pathlib import Path

import dagmc_h5m_file_inspector as di
import paramak


@pytest.fixture
def reactor_1():
    test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)], name="test_shape")

    test_shape_3 = paramak.PoloidalFieldCoilSet(heights=[2, 2], widths=[3, 3], center_points=[(50, -100), (50, 100)])

    # this reactor has a compound shape in the geometry
    test_reactor_compound = paramak.Reactor([test_shape, test_shape_3])
    return test_reactor_compound


@pytest.fixture
def reactor_2():
    test_shape = paramak.RotateStraightShape(points=[(0, 0), (0, 20), (20, 20)], name="test_shape")
    test_shape2 = paramak.ExtrudeStraightShape(
        points=[(100, 100), (50, 100), (50, 50)], distance=20, name="test_shape2"
    )
    reactor_2 = paramak.Reactor([test_shape, test_shape2])
    return reactor_2


def test_dagmc_h5m_custom_tags_export(reactor_1, reactor_2):
    """Exports a reactor with two shapes checks that the tags are correctly
    named in the resulting h5m file"""

    reactor_1.rotation_angle = 180
    reactor_1.export_dagmc_h5m("dagmc_reactor.h5m", tags=["1", "2"])

    vols = di.get_volumes_from_h5m("dagmc_reactor.h5m")
    assert vols == [1, 2, 3]  # there are three volumes in reactor_1

    mats = di.get_materials_from_h5m("dagmc_reactor.h5m")
    assert mats == ["1", "2"]

    vols_and_mats = di.get_volumes_and_materials_from_h5m("dagmc_reactor.h5m")
    assert vols_and_mats == {
        1: "1",
        2: "2",
        3: "2",
    }

    # default shape names used as tags
    reactor_2.export_dagmc_h5m("reactor_2.h5m")
    assert di.get_volumes_and_materials_from_h5m("reactor_2.h5m") == {
        1: "test_shape",
        2: "test_shape2",
    }


def test_dagmc_h5m_export(reactor_1):
    """Exports a reactor with two shapes checks that the tags are correctly
    named in the resulting h5m file"""

    reactor_1.rotation_angle = 180
    reactor_1.export_dagmc_h5m("dagmc_reactor.h5m")

    vols = di.get_volumes_from_h5m("dagmc_reactor.h5m")
    assert vols == [1, 2, 3]  # there are two shapes three volumes in reactor_1

    mats = di.get_materials_from_h5m("dagmc_reactor.h5m")
    print(mats)
    assert mats == ["pf_coil", "test_shape"]

    vols_and_mats = di.get_volumes_and_materials_from_h5m("dagmc_reactor.h5m")
    assert vols_and_mats == {
        1: "test_shape",
        2: "pf_coil",
        3: "pf_coil",
    }


def test_dagmc_h5m_export_mesh_size(reactor_1):
    """Exports h5m file with higher resolution mesh and checks that the
    file sizes increases"""

    reactor_1.export_dagmc_h5m("dagmc_default.h5m", min_mesh_size=10, max_mesh_size=20)
    reactor_1.export_dagmc_h5m("dagmc_bigger.h5m", min_mesh_size=2, max_mesh_size=9)

    assert Path("dagmc_bigger.h5m").stat().st_size > Path("dagmc_default.h5m").stat().st_size


def test_dagmc_h5m_export_error_handling(reactor_1):
    """Exports a shape with the wrong amount of tags"""

    with pytest.raises(ValueError):
        reactor_1.rotation_angle = 180
        reactor_1.export_dagmc_h5m("dagmc_reactor.h5m", tags=["1"])

    with pytest.raises(ValueError):
        reactor_1.rotation_angle = 180
        reactor_1.export_dagmc_h5m("dagmc_reactor.h5m", tags=["1", "2", "3"])


def test_center_column_study_reactor():
    """Exports the CenterColumnStudyReactor with default parameters"""
    reactor = paramak.CenterColumnStudyReactor()
    reactor.export_dagmc_h5m("CenterColumnStudyReactor.h5m")
    assert di.get_volumes_and_materials_from_h5m("CenterColumnStudyReactor.h5m") == {
        1: "plasma",
        2: "inboard_tf_coils",
        3: "center_column_shield",
        4: "inboard_first_wall",
        5: "blanket",
        6: "divertor",
        7: "divertor",
    }
