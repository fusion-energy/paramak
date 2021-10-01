Parametric Shapes
=================


Rotated Shapes
--------------

RotateStraightShape()
^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.RotateStraightShape(
      points=[
        (400, 100),
        (400, 200),
        (600, 200),
        (600, 100)
           ],
      rotation_angle = 180
   )

   cadquery_object = my_component.solid

.. automodule:: paramak.parametric_shapes.rotate_straight_shape
   :members:
   :show-inheritance:

RotateSplineShape()
^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.RotateSplineShape(
      points=[
       (500, 0),
       (500, -20),
       (400, -300),
       (300, -300),
       (400, 0),
       (300, 300),
       (400, 300),
       (500, 20),
      ],
      rotation_angle = 180
   )

   cadquery_object = my_component.solid

.. automodule:: paramak.parametric_shapes.rotate_spline_shape
   :members:
   :show-inheritance:

RotateMixedShape()
^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.RotateMixedShape(
      points=[
        (100, 0, 'straight'),
        (200, 0, 'circle'),
        (250, 50, 'circle'),
        (200, 100, 'straight'),
        (150, 100, 'spline'),
        (140, 75, 'spline'),
        (110, 45, 'spline'),
      ],
      rotation_angle = 180
   )


   cadquery_object = my_component.solid

.. automodule:: paramak.parametric_shapes.rotate_mixed_shape
   :members:
   :show-inheritance:

RotateCircleShape()
^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.RotateCircleShape(
      points=[(50, 0)],
      radius=5,
      rotation_angle=180
   )

   cadquery_object = my_component.solid

.. automodule:: paramak.parametric_shapes.rotate_circle_shape
   :members:
   :show-inheritance:


Extruded Shapes
---------------

ExtrudeStraightShape()
^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.ExtrudeStraightShape(
      points=[
         (300, -300),
         (400, 0),
         (300, 300),
         (400, 300),
         (500, 0),
         (400, -300),
        ],
      distance=200
   )

   cadquery_object = my_component.solid

.. automodule:: paramak.parametric_shapes.extruded_straight_shape
   :members:
   :show-inheritance:

ExtrudeSplineShape()
^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.ExtrudeSplineShape(
      points=[
         (500, 0),
         (500, -20),
         (400, -300),
         (300, -300),
         (400, 0),
         (300, 300),
         (400, 300),
         (500, 20),
      ],
      distance=200,

   )

   cadquery_object = my_component.solid

.. automodule:: paramak.parametric_shapes.extruded_spline_shape
   :members:
   :show-inheritance:

ExtrudeMixedShape()
^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.ExtrudeMixedShape(
      points=[
        (100, 0, 'straight'),
        (200, 0, 'circle'),
        (250, 50, 'circle'),
        (200, 100, 'straight'),
        (150, 100, 'spline'),
        (140, 75, 'spline'),
        (110, 45, 'spline'),
      ],
      distance=200
   )

   cadquery_object = my_component.solid

.. automodule:: paramak.parametric_shapes.extruded_mixed_shape
   :members:
   :show-inheritance:

ExtrudeCircleShape()
^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.ExtrudeCircleShape(
      points=[(50, 0)],
      radius=5,
      distance=15
   )


   cadquery_object = my_component.solid

.. automodule:: paramak.parametric_shapes.extruded_circle_shape
   :members:
   :show-inheritance:


Swept Shapes
------------

SweepStraightShape()
^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.SweepStraightShape(
      points=[(-10, 10), (10, 10), (10, -10), (-10, -10)],
      path_points=[(50, 0), (30, 50), (70, 100), (50, 150)] 
   )

   cadquery_object = my_component.solid

.. automodule:: paramak.parametric_shapes.sweep_straight_shape
   :members:
   :show-inheritance:

SweepSplineShape()
^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.SweepSplineShape(
      points=[(-10, 10), (10, 10), (10, -10), (-10, -10)],
      path_points=[(50, 0), (30, 50), (70, 100), (50, 150)]
   )

   cadquery_object = my_component.solid

.. automodule:: paramak.parametric_shapes.sweep_spline_shape
   :members:
   :show-inheritance:

SweepMixedShape()
^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.SweepMixedShape(
      points=[(-10, -10, "straight"), (-10, 10, "spline"), (0, 20, "spline"),
      (10, 10, "circle"), (0, 0, "circle"), (10, -10, "straight")],
      path_points=[(50, 0), (30, 50), (70, 100), (50, 150)]
   )

   cadquery_object = my_component.solid

.. automodule:: paramak.parametric_shapes.sweep_mixed_shape
   :members:
   :show-inheritance:

SweepCircleShape()
^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.SweepCircleShape(
      radius=10,
      path_points=[(50, 0), (30, 50), (70, 100), (50, 150)]
   )

   cadquery_object = my_component.solid

.. automodule:: paramak.parametric_shapes.sweep_circle_shape
   :members:
   :show-inheritance:
