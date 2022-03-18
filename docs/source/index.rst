Paramak
=======


.. cadquery::
   :select: text
   :gridsize: 0
   :height: 100px

   import cadquery as cq
   text = cq.Workplane().text(
      txt="Paramak",
      fontsize=0.8,
      distance=-0.5,
      cut=True,
      font="Sans"
   )

The Paramak python package allows rapid production of 3D CAD models of fusion
reactors. The purpose of the Paramak is to provide geometry for parametric
studies in a variety of geometry formats including STL, STP, Brep, HTML and DAGMC h5m
files.

CadQuery functions provide the majority of the features, and incorporating
additional capabilities is straightforward for developers with Python knowledge.

Contributions are welcome.

.. raw:: html

      <iframe width="560" height="315" src="https://www.youtube.com/embed/fXboew3U7rw" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


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
`GitHub contributions <https://github.com/fusion-energy/paramak/graphs/contributors>`_.

The code has been professionally reviewed by
`PullRequest.com <https://www.pullrequest.com/>`_ who produced a
`report <https://github.com/ukaea/paramak/files/5704872/PULLREQUEST.Paramak.Project.Review.pdf>`_
and inline `suggestions <https://github.com/ukaea/paramak/pull/639>`_.

The Paramak source code is distributed with a permissive open-source license
(MIT) and is available from the GitHub repository
`https://github.com/fusion-energy/paramak <https://github.com/fusion-energy/paramak>`_


Publications and Presentations
------------------------------

- Published in F1000 Research. `https://f1000research.com/articles/10-27 <https://f1000research.com/articles/10-27>`_

- Presented at the Spanish Fusion HPC Workshop and available in the 3rd video and starts at minute 41. `https://hpcfusion2020.bsc.es/media <https://hpcfusion2020.bsc.es/media>`_ also available directly `here <https://www.youtube.com/embed/fXboew3U7rw>`_

- Slides from first released presentation. `Link <https://github.com/ukaea/paramak/files/5260982/UKAEA_Paramak_shimwell.pdf>`_

- Paramak used for geometry creation in an ARC reactor study. `https://iopscience.iop.org/article/10.1088/1741-4326/ac5450 <https://iopscience.iop.org/article/10.1088/1741-4326/ac5450>`_


Features
--------

In general the Paramak takes input arguments and creates 3D objects. This can
be accomplished via the use of parametric Shapes, parametric Components and
parametric Reactors with each level building upon the level below.

Parametric Shapes are the simplest and accept points and connection information
in 2D space (defaults to x,z plane) and performs operations on them to create 3D
volumes. The points and connections are provided by the user when making
parametric Shapes. Supported CAD operations include (rotate, extrude, sweep)
and Boolean operations such as cut, union and intersect. Additionally the
CadQuery objects created can be combined and modified using CadQuery's powerful
filtering capabilities to further customise the shapes by performing operations
like edge filleting.

Parametric Components build on top of this foundation and will calculate the
points and connections for you when provided with input arguments. The inputs
differ between components as a center column requires different inputs to a
breeder blanket or a magnet.

Parametric Reactors build upon these two lower level objects to create an
entire reactor model from input parameters. Linkage between the components is
encoded in each parametric Rector design.

Some of the different parametric reactor families are shown below.

.. image:: https://user-images.githubusercontent.com/8583900/118414245-58be8880-b69b-11eb-981e-c5806f721e0f.png
   :width: 713
   :align: center

A sub section of the available parametric Components are shown below.

.. image:: https://user-images.githubusercontent.com/8583900/98823600-387eea00-242a-11eb-9fe3-df65aaa3dd21.png
   :width: 713
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

Table Of Contents

.. toctree::
   :maxdepth: 3

   install
   quick-tour
   examples
   API-Reference
