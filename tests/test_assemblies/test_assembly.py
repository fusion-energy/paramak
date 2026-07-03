import cadquery as cq
import pytest
from paramak.assemblies.assembly import Assembly

def test_remove_and_names():

    sphere1 = cq.Workplane().moveTo(2, 2).sphere(1)
    box1 = cq.Workplane().box(1, 1, 1)
    assembly = Assembly()
    assembly.add(box1, name="box1", color=cq.Color(0.5, 0.5, 0.5))
    assembly.add(sphere1, name="sphere")

    assembly2 = assembly.remove('sphere')
    assembly3 = assembly.remove('box1')
    assembly4 = assembly.remove('bosdfsdf')

    assert assembly.names() == ['box1', 'sphere']
    assert assembly2.names() == ['box1']
    assert assembly3.names() == ['sphere']
    assert assembly4.names() == ['box1', 'sphere']

def test_split_solids():
    # A compound with 2 solids (two spheres at different positions)
    multi_solid = cq.Compound.makeCompound([
        cq.Workplane().moveTo(0, 0).sphere(1).val(),
        cq.Workplane().moveTo(10, 0).sphere(1).val(),
    ])
    single_solid = cq.Workplane().box(1, 1, 1)

    assembly = Assembly()
    assembly.add(multi_solid, name="multi")
    assembly.add(single_solid, name="single")

    split = assembly.split_solids()

    # single-solid part keeps its name unchanged
    # multi-solid part becomes multi_1 and multi_2
    assert split.names() == ['multi_1', 'multi_2', 'single']


def test_rename_single_and_chain():
    assembly = Assembly()
    assembly.add(cq.Workplane().box(1, 1, 1), name="layer_1")
    assembly.add(cq.Workplane().moveTo(5, 0).box(1, 1, 1), name="layer_2")

    renamed = assembly.rename("layer_1", "first wall").rename("layer_2", "blanket")

    assert renamed.names() == ["first wall", "blanket"]
    # the original assembly is left unchanged
    assert assembly.names() == ["layer_1", "layer_2"]


def test_rename_missing_name_warns_and_is_unchanged():
    assembly = Assembly()
    assembly.add(cq.Workplane().box(1, 1, 1), name="layer_1")

    with pytest.warns(UserWarning):
        result = assembly.rename("does_not_exist", "foo")

    assert result.names() == ["layer_1"]


def test_rename_to_existing_name_raises():
    assembly = Assembly()
    assembly.add(cq.Workplane().box(1, 1, 1), name="layer_1")
    assembly.add(cq.Workplane().moveTo(5, 0).box(1, 1, 1), name="layer_2")

    with pytest.raises(ValueError):
        assembly.rename("layer_1", "layer_2")


def test_rename_split_solid_group():
    multi_solid = cq.Compound.makeCompound([
        cq.Workplane().moveTo(0, 0).sphere(1).val(),
        cq.Workplane().moveTo(10, 0).sphere(1).val(),
    ])
    assembly = Assembly()
    assembly.add(multi_solid, name="coil")

    split = assembly.split_solids()
    assert split.names() == ["coil_1", "coil_2"]

    renamed = split.rename("coil", "tf coil")
    assert renamed.names() == ["tf coil_1", "tf coil_2"]
