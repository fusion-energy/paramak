import cadquery as cq
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
