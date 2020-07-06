Paramak
=======

The Paramak python package allows rapid production of 3D CAD models of fusion reactors. The original purpose of the Paramak was to provide geometry for parametric neutronics studies as the STP files produced can be automaticallya converted to DAGMC compatable neutronics models.

Features have been added to address particular needs and the software is by no means a finished product. Contributions are welcome. CadQuery functions provide the majority the features, and incorporating additional capabilities is straight forward for developers with Python knowledge.

.. toctree::
   :maxdepth: 1

   paramak
   paramak.parametric_components
   tests
   

Prerequisites
-------------

To use the paramak tool you will need Python 3 and Cadquery 2.0 or newer installed.

* `Python 3 <https://www.python.org/downloads/>`_

* `CadQuery 2.0 <https://github.com/CadQuery/cadquery>`_

Cadquery 2.0 must be installed in a conda environment via conda-forge.
Conda environments are activated using Anaconda or Miniconda. 

* `Anaconda <https://www.anaconda.com/>`_
* `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_

Once you have activated a conda environment, Cadquery 2.0 can be installed using the command:

::

   conda install -c conda-forge -c cadquery cadquery=2

A more detailed description of installing Cadquery 2.0 can be found here:

* `Cadquery 2.0 installation <https://cadquery.readthedocs.io/en/latest/installation.html>`_


Installation
------------

The quickest way to install the Paramak is to use pip. In the terminal type...

::

   pip install paramak

Alternativly you can download the repository using the `download link <https://github.com/Shimwell/freecad_parametric_example/archive/master.zip>`_ or clone the repository using `git <https://git-scm.com/downloads>`_.

::

   git clone https://github.com/Shimwell/paramak.git

Navigate to the paramak repository and within the terminal install the paramak package and the dependencies using pip3.

::

   pip install .

Alternatively you can install the paramak with following command.

::

   python setup.py install

Features
--------

In general the Paramak takes points and connection information in 2D space (x,z) and performs operations on them to create 3D volumes. The points and connections can be provided by the user or when using parametric_shapes the points and connections are calculated by the software.

Once points and connections between the points are provided the user has options to perform CAD operations (rotate or extrude) to create a 3D volume and boolean operations like cut.

The different families of shapes that can be made with the Paramak are shown in the table below. The CadQuery objects created can be combined and modified using CadQueries powerful filtering capabilties to create more complex models (e.g. a Tokamak).


.. |rotatestraight| image:: https://user-images.githubusercontent.com/8583900/86246786-767a2080-bba3-11ea-90e7-22d816690caa.png 
                          :height: 200px

.. |extrudestraight| image:: https://user-images.githubusercontent.com/8583900/86246776-724e0300-bba3-11ea-91c9-0fd239225206.png
                          :height: 200px

.. |rotatespline| image:: https://user-images.githubusercontent.com/8583900/86246785-7548f380-bba3-11ea-90b7-03249be41a00.png
                          :height: 200px

.. |extrudespline| image:: https://user-images.githubusercontent.com/8583900/86246774-71b56c80-bba3-11ea-94cb-d2496365ff18.png
                          :height: 200px

.. |rotatecircle| image:: https://user-images.githubusercontent.com/8583900/86246778-72e69980-bba3-11ea-9b33-d74e2c2d084b.png
                          :height: 200px

.. |extrudecircle| image:: https://user-images.githubusercontent.com/8583900/86246768-6feba900-bba3-11ea-81a8-0d77a843b943.png
                          :height: 200px

.. |rotatemixed| image:: https://user-images.githubusercontent.com/8583900/86258771-17240c80-bbb3-11ea-990f-e87de26b1589.png
                          :height: 200px

.. |extrudemixed| image:: https://user-images.githubusercontent.com/8583900/86261239-34a6a580-bbb6-11ea-812c-ac6fa6a8f0e2.png
                          :height: 200px



+-----------------------------------------------------------+-----------------------------------------------------------+------------------------------------------------------------+
|                                                           | Rotate                                                    | Extrude                                                    |
+===========================================================+===========================================================+============================================================+
| Points connected with straight lines                      | |rotatestraight|                                          | |extrudestraight|                                          |
|                                                           |                                                           |                                                            |
|                                                           |                                                           |                                                            |
|                                                           |                                                           |                                                            |
|                                                           |                                                           |                                                            |
|                                                           | ::                                                        | ::                                                         |
|                                                           |                                                           |                                                            |
|                                                           |     RotateStraightShape()                                 |     ExtrudeStraightShape()                                 |
+-----------------------------------------------------------+-----------------------------------------------------------+------------------------------------------------------------+
| Points connected with spline curves                       | |rotatespline|                                            | |extrudespline|                                            |
|                                                           |                                                           |                                                            |
|                                                           |                                                           |                                                            |
|                                                           |                                                           |                                                            |
|                                                           |                                                           |                                                            |
|                                                           | ::                                                        | ::                                                         |
|                                                           |                                                           |                                                            |
|                                                           |     RotateSplineShape()                                   |     ExtrudeSplineShape()                                   |
+-----------------------------------------------------------+-----------------------------------------------------------+------------------------------------------------------------+
| Points connected with a circles                           | |rotatecircle|                                            | |extrudecircle|                                            |
|                                                           |                                                           |                                                            |
|                                                           |                                                           |                                                            |
|                                                           |                                                           |                                                            |
|                                                           |                                                           |                                                            |
|                                                           | ::                                                        | ::                                                         |
|                                                           |                                                           |                                                            |
|                                                           |     RotateCircleShape()                                   |     ExtrudeCircleShape()                                   |
+-----------------------------------------------------------+-----------------------------------------------------------+------------------------------------------------------------+
| Points connected with a mixture                           | |rotatemixed|                                             | |extrudemixed|                                             |
|                                                           |                                                           |                                                            |
| ::                                                        |                                                           |                                                            |
|                                                           |                                                           |                                                            |
| (splines, straights and circles)                          |                                                           |                                                            |
|                                                           | ::                                                        | ::                                                         |
|                                                           |                                                           |                                                            |
|                                                           |     RotateMixedShape()                                    |     ExtrudeMixedShape()                                    |
+-----------------------------------------------------------+-----------------------------------------------------------+------------------------------------------------------------+


Usage - Shape creation
----------------------

There are a collection of Python scripts in the example folder than demonstrate simple shape construction, visualisation creation and reactor construction. However here is a quick example of a RotatedStraightShape

After importing the class the user then sets the points. Points should be a list of x,z points where the last point is the same as the first point.

::

   from paramak import RotatedStraightShape

   my_shape = RotatedStraightShape(points = [(20, 0), (20, 100), (100, 0), (20, 0)])

Once these properties have been set then users can write 3D volumes in CAD STP or STL formats

::

   my_shape.export_stp('example.stp')

   my_shape.export_stl('example.stl')


Usage - Creating a Plasma
-------------------------

The plasma also inherits from the Shape object so has access to the same methods like export_stp() and export_stl().

The plasma requires additional inputs and a simple plasma shape can be created in the following manner.


::

   from paramak.parametric_shapes import PlasmaShape

   my_plasma = PlasmaShape()

   my_plasma.major_radius =620

   my_plasma.minor_radius =210

   my_plasma.triangularity = 0.33

   my_plasma.elongation = 1.85

   my_plasma.export_stp('plasma.stp')


Usage - Reactor creation
------------------------

A reactor object provides a contain object for all the Shape objects created and allows operations on the whole collection of Shapes such as creation of a bounding box (DGMC graveyard) which is needed for neutronics simulations.

Import the Reactor object

::

   from paramak import Reactor

Initiate a Reactor object with an output folder

::

   my_reactor = Reactor()

Reactor inherites from dictionary so Shapes can be added to it in the same way you would add to a dictionary.

::

   my_reactor.add(my_shape)

   my_reactor.add(my_plasma)

A 3D rendering of the combined Shapes can be created

::

   my_reactor.export_3d_image('reactor.png')


Once all your Shapes have been added reactor methods can be used to create and simulate the neutronics model using additional tools, the currently codes to learn are `DAGMC <https://svalinn.github.io/DAGMC/>`_ , `Trelis <https://www.csimsoft.com/trelis>`_ and `OpenMC <https://openmc.readthedocs.io/>`_ .


Example Scripts
---------------

There are several example scripts in the examples folder the introduction, a good one to start with is

* make_CAD_from_points.py examples of the different families of shapes (extrude, roate) and different connection methods (points connected with splines and or straights or a mixture) with different CAD operations (cut, union).



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
