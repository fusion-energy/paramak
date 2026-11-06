import cadquery as cq
import pytest

from paramak.assemblies.assembly import Assembly


def _box_and_sphere_assembly():
    assembly = Assembly()
    assembly.add(cq.Workplane().box(1, 1, 1), name="box1", color=cq.Color(0.5, 0.5, 0.5))
    assembly.add(cq.Workplane().moveTo(2, 2).sphere(1), name="sphere")
    return assembly


def test_names():
    assert _box_and_sphere_assembly().names() == ['box1', 'sphere']


def test_remove_uses_cadquery_remove():
    # paramak relies on cadquery's Assembly.remove rather than overriding it
    assert Assembly.remove is cq.Assembly.remove


def test_remove_is_in_place_and_returns_self():
    assembly = _box_and_sphere_assembly()

    result = assembly.remove('sphere')

    assert result is assembly
    assert isinstance(result, Assembly)
    assert assembly.names() == ['box1']
    assert 'sphere' not in assembly.objects
    assert len(assembly.toCompound().Solids()) == 1


def test_remove_each_part():
    assembly = _box_and_sphere_assembly()
    assert assembly.remove('box1').names() == ['sphere']

    assembly = _box_and_sphere_assembly()
    assert assembly.remove('sphere').remove('box1').names() == []


def test_remove_missing_name_raises():
    assembly = _box_and_sphere_assembly()

    with pytest.raises(ValueError, match='bosdfsdf'):
        assembly.remove('bosdfsdf')

    assert assembly.names() == ['box1', 'sphere']


def test_remove_nested_part_and_subassembly():
    sub = Assembly(name="magnets")
    sub.add(cq.Workplane().box(1, 1, 1), name="coil_1")
    sub.add(cq.Workplane().moveTo(5, 0).box(1, 1, 1), name="coil_2")

    assembly = _box_and_sphere_assembly()
    assembly.add(sub)

    assembly.remove('magnets/coil_1')
    assert assembly.names() == ['box1', 'sphere', 'coil_2']

    assembly.remove('magnets')
    assert assembly.names() == ['box1', 'sphere']
    assert not any(key.startswith('magnets') for key in assembly.objects)


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
