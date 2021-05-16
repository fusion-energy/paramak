Paramak
=======

The Paramak python package allows rapid production of 3D CAD models of fusion
reactors. The purpose of the Paramak is to provide geometry for parametric
studies. It is possible to use the created geometry in engineering and
neutronics studies as the STP files produced can be automatically converted to
DAGMC compatible neutronics models or meshed and used in finite element
analysis codes.

Features have been added to address particular needs and the software is by no
means a finished product. Contributions are welcome. CadQuery functions provide
the majority of the features, and incorporating additional capabilities is
straightforward for developers with Python knowledge.

.. raw:: html

      <iframe width="560" height="315" src="https://www.youtube.com/embed/fXboew3U7rw" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


.. toctree::
   :maxdepth: 1

   paramak.parametric_shapes
   paramak.parametric_components
   paramak.parametric_reactors
   paramak.parametric_neutronics
   paramak.core_modules
   example_parametric_shapes
   example_parametric_components
   example_parametric_reactors
   example_neutronics_simulations
   tests

History
-------

The package was originally conceived by Jonathan Shimwell and based on the
`FreeCAD Python API <https://wiki.freecadweb.org/FreeCAD_API>`_  When 
`CadQuery 2 <https://github.com/CadQuery/cadquery>`_ was released the project
started to migrate the code base. Shortly after this migration the project
became open-source and has flourished ever since.

The project has grown largely due to two contributors in particular
(John Billingsley and Remi Delaporte-Mathurin) and others have also helped,
you can see all those who have helped the development in the 
`Authors.md <https://github.com/ukaea/paramak/blob/main/AUTHORS.md>`_ and in the 
`GitHub contributions <https://github.com/ukaea/paramak/graphs/contributors>`_.

The code has been professionally reviewed by
`PullRequest.com <https://www.pullrequest.com/>`_ who produced a
`report <https://github.com/ukaea/paramak/files/5704872/PULLREQUEST.Paramak.Project.Review.pdf>`_
and inline `suggestions <https://github.com/ukaea/paramak/pull/639>`_.

The Paramak source code is distributed with a permissive open-source license
(MIT) and is avaialbe from the GitHub repository 
`https://github.com/ukaea/paramak <https://github.com/ukaea/paramak>`_

Prerequisites
-------------

To use the paramak tool you will need Python 3 and Cadquery 2 installed.

* `Python 3 <https://www.python.org/downloads/>`_

* `CadQuery 2 <https://github.com/CadQuery/cadquery>`_

Python 3 and CadQuery can be installed using Conda or Miniconda

* `Anaconda <https://www.anaconda.com/>`_
* `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_
  
Once you have Conda or MiniConda installed then CadQuery can be installed
into a new enviroment and that environment can be activated using Anaconda or Miniconda. 

Cadquery 2 can be installed in a Conda environment via conda-forge.

.. code-block:: python

   conda create -n paramak_env -c conda-forge -c cadquery python=3.8 cadquery=2.1


Once you have activated a conda environment, Cadquery 2 can be installed
using the command:

.. code-block:: python

   conda activate paramak_env


A more detailed description of installing Cadquery 2 can be found here:

* `Cadquery 2 installation <https://cadquery.readthedocs.io/en/latest/installation.html>`_


System Installation
-------------------

The quickest way to install the Paramak is to use pip. In the terminal type...

.. code-block:: bash

   pip install paramak

Alternatively you can download the repository using the `download link <https://github.com/ukaea/paramak/archive/develop.zip>`_ or clone the repository using:

.. code-block:: bash

   git clone https://github.com/Shimwell/paramak.git

Navigate to the paramak repository and within the terminal install the paramak
package and the dependencies using pip3.

.. code-block:: bash

   pip install .

Alternatively you can install the paramak with the following command.

.. code-block:: bash

   python setup.py install

You can also install optional dependencies that add some neutronics
capabilities to the paramak. This will install neutronics_material_maker and
parametric_plasma_source. In addition to this you would need DAGMC, OpenMC,
MOAB and Trelis / Cubit.
`More details <https://paramak.readthedocs.io/en/latest/paramak.parametric_neutronics.html>`_

.. code-block:: bash

   pip install .[neutronics]

You could consider installing
[jupyter-cadquery](https://github.com/bernhard-42/jupyter-cadquery) which adds
3D viewing in Jupyter lab as shown in the example notebooks.

.. code-block:: bash

   pip install jupyter-cadquery



Docker Image Installation
-------------------------

Another option is to use the Docker image which contains all the required
dependencies.

1. Install Docker CE for `Ubuntu <https://docs.docker.com/install/linux/docker-ce/ubuntu/>`_ ,
`Mac OS <https://store.docker.com/editions/community/docker-ce-desktop-mac>`_ or
`Windows <https://hub.docker.com/editions/community/docker-ce-desktop-windows>`_
including the part where you enable docker use as a non-root user.

2. Pull the docker image from the store by typing the following command in a
terminal window, or Windows users might prefer PowerShell.

.. code-block:: bash

   docker pull ukaea/paramak

3. Now that you have the docker image you can enable graphics linking between
your os and docker, and then run the docker container by typing the following
commands in a terminal window.

.. code-block:: bash

   sudo docker run -p 8888:8888 ukaea/paramak

4. A URL should be displayed in the terminal and can now be opened in the
internet browser of your choice. This will load up the examples folder where
you can view the 3D objects created.

Alternatively the Docker image can be run in terminal mode .

.. code-block:: bash

   docker run -it ukaea/paramak

You may also want to make use of the
`--volume <https://docs.docker.com/storage/volumes/>`_
flag when running Docker so that you can retrieve files from the Docker
enviroment to your base system.

Publications and Presentations
------------------------------

Published in F1000 Research.
`https://f1000research.com/articles/10-27 <https://f1000research.com/articles/10-27>`_

Presented at the Spanish Fusion HPC Workshop and available in the 3rd video at minute 41.
`https://hpcfusion2020.bsc.es/media <https://hpcfusion2020.bsc.es/media>`_

Slides from first released presentation.
`Link <https://github.com/ukaea/paramak/files/5260982/UKAEA_Paramak_shimwell.pdf>`_


Features
--------

In general the Paramak takes input arguments and creates 3D objects. This can
be accomplished via the use of parametric Shapes, parametric Components and
parametric Reactors with each level building upon the level below.

Parametric Shapes are the simplest and accept points and connection information
in 2D space (defaults to x,z) and performs operations on them to create 3D
volumes. The points and connections are provided by the user when making
parametric Shapes. Supported CAD opperations include (rotate, extrude, sweep)
and Boolean opperations such as cut, union and intersect. Additionally the 
CadQuery objects created can be combined and modified using CadQuery's powerful 
filtering capabilties to furter customise the shapes by performing operations
like edge filleting.

Parametric Components build on top of this foundation and will calculate the
points and connections for you when provided with input arguments. The inputs
differ between components as a center column requires different inputs to a
breeder blanket or a magnet.

Parametric Reactors build upon these two lower level objects to create an
entire reactor model from input parameters. Linkage between the componets is
encoded in each parametric Ractor design.

The different parametric reactor families are shown below.

.. image:: https://user-images.githubusercontent.com/8583900/118414245-58be8880-b69b-11eb-981e-c5806f721e0f.png
   :width: 713
   :align: center

A selection of the parametric Components are shown below.

.. image:: https://user-images.githubusercontent.com/8583900/98823600-387eea00-242a-11eb-9fe3-df65aaa3dd21.png
   :width: 713
   :height: 245
   :align: center

The different families of parametric Shapes that can be made with the Paramak
are shown int he table below.



.. |rotatestraight| image:: https://user-images.githubusercontent.com/56687624/87055469-4f070180-c1fc-11ea-9679-a29e37a90e15.png
                          :height: 120px

.. |extrudestraight| image:: https://user-images.githubusercontent.com/56687624/87055493-56c6a600-c1fc-11ea-8c58-f5b62ae72e0e.png
                          :height: 120px

.. |sweepstraight| image:: https://user-images.githubusercontent.com/56687624/98713447-8c80c480-237f-11eb-8615-c090e93138f6.png
                          :height: 120px

.. |rotatespline| image:: https://user-images.githubusercontent.com/56687624/87055473-50382e80-c1fc-11ea-95dd-b4932b1e78d9.png
                          :height: 120px

.. |extrudespline| image:: https://user-images.githubusercontent.com/56687624/98713431-87bc1080-237f-11eb-9075-01bca99b7018.png
                          :height: 120px

.. |sweepspline| image:: https://user-images.githubusercontent.com/56687624/98713443-8b4f9780-237f-11eb-83bb-38ca7f222073.png
                          :height: 120px

.. |rotatecircle| image:: https://user-images.githubusercontent.com/56687624/98713427-868ae380-237f-11eb-87af-cf6b5fe032b2.png
                          :height: 120px

.. |extrudecircle| image:: https://user-images.githubusercontent.com/56687624/87055517-5b8b5a00-c1fc-11ea-83ef-d4329c6815f7.png
                          :height: 120px

.. |sweepcircle| image:: https://user-images.githubusercontent.com/56687624/98713436-88ed3d80-237f-11eb-99cd-27dcb4f313b1.png
                          :height: 120px

.. |rotatemixed| image:: https://user-images.githubusercontent.com/56687624/87055483-53cbb580-c1fc-11ea-878d-92835684c8ff.png
                          :height: 120px

.. |extrudemixed| image:: https://user-images.githubusercontent.com/56687624/87055511-59c19680-c1fc-11ea-8740-8c7987745c45.png
                          :height: 120px

.. |sweepmixed| image:: https://user-images.githubusercontent.com/56687624/98713440-8a1e6a80-237f-11eb-9eed-12b9d7731090.png
                          :height: 120px






+--------------------------------------+--------------------------------------+---------------------------------------+---------------------------------------+
|                                      | Rotate                               | Extrude                               | Sweep                                 |
+======================================+======================================+=======================================+=======================================+
| Points connected with straight lines | |rotatestraight|                     | |extrudestraight|                     | |sweepstraight|                       |
|                                      |                                      |                                       |                                       |
|                                      |                                      |                                       |                                       |
|                                      |                                      |                                       |                                       |
|                                      |                                      |                                       |                                       |
|                                      | ::                                   | ::                                    | ::                                    |
|                                      |                                      |                                       |                                       |
|                                      |     RotateStraightShape()            |     ExtrudeStraightShape()            |     SweepStraightShape()              |
+--------------------------------------+--------------------------------------+---------------------------------------+---------------------------------------+
| Points connected with spline curves  | |rotatespline|                       | |extrudespline|                       | |sweepspline|                         |
|                                      |                                      |                                       |                                       |
|                                      |                                      |                                       |                                       |
|                                      |                                      |                                       |                                       |
|                                      |                                      |                                       |                                       |
|                                      | ::                                   | ::                                    | ::                                    |
|                                      |                                      |                                       |                                       |
|                                      |     RotateSplineShape()              |     ExtrudeSplineShape()              |     SweepSplineShape()                |
+--------------------------------------+--------------------------------------+---------------------------------------+---------------------------------------+
| Points connected with a circle       | |rotatecircle|                       | |extrudecircle|                       | |sweepcircle|                         |
|                                      |                                      |                                       |                                       |
|                                      |                                      |                                       |                                       |
|                                      |                                      |                                       |                                       |
|                                      |                                      |                                       |                                       |
|                                      | ::                                   | ::                                    | ::                                    |
|                                      |                                      |                                       |                                       |
|                                      |     RotateCircleShape()              |     ExtrudeCircleShape()              |     SweepCircleShape()                |
+--------------------------------------+--------------------------------------+---------------------------------------+---------------------------------------+
| Points connected with a mixture      | |rotatemixed|                        | |extrudemixed|                        | |sweepmixed|                          |
|                                      |                                      |                                       |                                       |
| ::                                   |                                      |                                       |                                       |
|                                      |                                      |                                       |                                       |
| (splines, straights and circles)     |                                      |                                       |                                       |
|                                      | ::                                   | ::                                    | ::                                    |
|                                      |                                      |                                       |                                       |
|                                      |     RotateMixedShape()               |     ExtrudeMixedShape()               |     SweepMixedShape()                 |
+--------------------------------------+--------------------------------------+---------------------------------------+---------------------------------------+


Usage - Parametric Shapes
-------------------------

There are a collection of Python scripts in the example folder that demonstrate
simple shape construction and visualisation. However here is a quick example of
a RotateStraightShape.

After importing the class the user then sets the points. By default, points
should be a list of (x,z) points. In this case the points are connected with
straight lines.

.. code-block:: python

   import paramak

   my_shape = paramak.RotateStraightShape(points = [(20,0), (20,100), (100,0)])

Once these properties have been set then users can write 3D volumes in CAD STP
or STL formats.

.. code-block:: python

   my_shape.export_stp('example.stp')

   my_shape.export_stl('example.stl')

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

   my_plasma = paramak.Plasma(major_radius=620, minor_radius=210, triangularity=0.33, elongation=1.85)

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
      number_of_tf_coils = 16,
      rotation_angle = 180
   )

   my_reactor.name = 'BallReactor'
   
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


Usage - Neutronics Model Creation
---------------------------------

First assign stp_filenames to each of the Shape objects that were created
earlier on.

.. code-block:: python

   my_shape.stp_filename = 'my_shape.stp'

   my_plasma.stp_filename = 'my_plasma.stp'

Then assign material_tags to each of the Shape objects.

.. code-block:: python

   my_shape.material_tag = 'steel'

   my_plasma.material_tag = 'DT_plasma'

Note - Tetrahedral meshes can also be assigned to Shape objects.

Now add the Shape objects to a freshly created reactor object.

.. code-block:: python

   new_reactor = Reactor([my_shape, my_plasma])

The entire reactor can now be exported as step files. This also generates a
DAGMC graveyard automatically.

.. code-block:: python

   my_reactor.export_stp()

A manifest.json file that contains all the step filenames and materials can now
be created.

.. code-block:: python

   my_reactor.export_neutronics_description()

Once you step files and the neutronics description has been exported then `Trelis <https://www.csimsoft.com/trelis>`_ can be used to generate a DAGMC geometry in the usual manner. There is also a convenient script included in task 12 of the UKAEA openmc workshop which can be used in conjunction with the neutronics description json file to automatically create a DAGMC geometry. Download `this script <https://github.com/ukaea/openmc_workshop/blob/master/tasks/task_12/make_faceteted_neutronics_model.py>`_ and place it in the same directory as the manifest.json and step files. Then run the following command from the terminal. You will need to have previously installed the `DAGMC plugin <https://github.com/svalinn/Trelis-plugin>`_ for Trelis.

::

   trelis make_faceteted_neutronics_model.py

Alternatively, run this without the GUI in batch mode using:

::

   trelis -batch -nographics make_faceteted_neutronics_model.py

This should export a h5m file for use in DAGMC.

Further information on DAGMC neutronics can be found `here <https://svalinn.github.io/DAGMC/>`__ and information on OpenMC can be found `here <https://openmc.readthedocs.io/>`__ . The two codes can be used together to simulate neutron transport on the h5m file created. The UKAEA openmc workshop also has two tasks that might be of interest `task 10 <https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_10>`_ and `task 12 <https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_12>`_ .


Example Scripts
---------------

There are several example scripts in the `examples folder <https://github.com/ukaea/paramak/blob/develop/examples/>`_ . A good one to start with is `make_CAD_from_points <https://github.com/ukaea/paramak/blob/develop/examples/make_CAD_from_points.py>`_ which makes simple examples of the different types of shapes (extrude, rotate) with different connection methods (splines, straight lines and circles).
