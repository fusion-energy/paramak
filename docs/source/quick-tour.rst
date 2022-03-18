Quick Tour
==========


Usage - Parametric Shapes
-------------------------

There are a collection of Python scripts in the `examples <https://github.com/fusion-energy/paramak/tree/main/examples>`_
folder that demonstrate simple shape construction and visualisation.
However here is a quick example of a RotateStraightShape.

After importing the class the user then sets the points. By default, points
should be a list of (x,z) points. In this case the points are connected with
straight lines.

.. code-block:: python

   import paramak

   my_shape = paramak.RotateStraightShape(points = [(20,0), (20,100), (100,0)])

Once these properties have been set then users can write 3D volumes in CAD STP
or STL, Brep, HTML and h5m formats.

.. code-block:: python

   my_shape.export_stp('example.stp')

   my_shape.export_stl('example.stl')

   my_shape.export_brep('example.brep')

   my_shape.export_dagmc_h5m('example.h5m')

   my_shape.export_html_3d('example.html')

.. image:: https://user-images.githubusercontent.com/56687624/88935761-ff0ae000-d279-11ea-8848-de9b486840d9.png
   :width: 350
   :height: 300
   :align: center

Usage - Parametric Components
-----------------------------

Parametric components are wrapped versions of the eight basic shapes where
parameters drive the construction of the shape. There are numerous parametric
components for a variety of different reactor components such as center columns,
blankets, poloidal field coils. This example shows the construction of a
plasma. Users could also construct a plasma by using a RotateSplineShape()
combined with coordinates for the points. However a parametric component called
Plasma can construct a plasma from more convenient parameters. Parametric
components also inherit from the Shape object so they have access to the same
methods like export_stp() and export_stl().

.. code-block:: python

   import paramak

   my_plasma = paramak.Plasma(
      major_radius=620,
      minor_radius=210,
      triangularity=0.33,
      elongation=1.85
   )

   my_plasma.export_stp('plasma.stp')

.. image:: https://user-images.githubusercontent.com/56687624/88935871-1ea20880-d27a-11ea-82e1-1afa55ff9ba8.png
   :width: 350
   :height: 300
   :align: center

Usage - Parametric Reactors
---------------------------

Parametric Reactors() are wrapped versions of a combination of parametric
shapes and components that comprise a particular reactor design. Some
parametric reactors include a ball reactor and a submersion ball reactor. These
allow full reactor models to be constructed by specifying a series of simple
parameters. This example shows the construction of a simple ball reactor
without the optional outer pf and tf coils.

.. code-block:: python

   import paramak

   my_reactor = paramak.BallReactor(
      inner_bore_radial_thickness = 50,
      inboard_tf_leg_radial_thickness = 50,
      center_column_shield_radial_thickness= 50,
      divertor_radial_thickness = 100,
      inner_plasma_gap_radial_thickness = 50,
      plasma_radial_thickness = 200,
      outer_plasma_gap_radial_thickness = 50,
      firstwall_radial_thickness = 50,
      blanket_radial_thickness = 100,
      blanket_rear_wall_radial_thickness = 50,
      elongation = 2,
      triangularity = 0.55,
      rotation_angle = 180
   )

   my_reactor.export_stp()

.. image:: https://user-images.githubusercontent.com/56687624/89203299-465fdc00-d5ac-11ea-8663-a5b7eecfb584.png
   :width: 350
   :height: 300
   :align: center

Usage - Reactor Object
----------------------

A reactor object provides a container object for all Shape objects created, and
allows operations to be performed on the whole collection of Shapes.

.. code-block:: python

   import paramak

Initiate a Reactor object and pass a list of all Shape objects to the
shapes_and_components parameter.

.. code-block:: python

   my_reactor = paramak.Reactor(shapes_and_components = [my_shape, my_plasma])

A html graph of the combined Shapes can be created.

.. code-block:: python

   my_reactor.export_html('reactor.html')

An interactive 3D object can be embedded into a portable html file.

.. code-block:: python

   my_reactor.export_html_3d('reactor.html')
