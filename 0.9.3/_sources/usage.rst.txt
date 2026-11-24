Usage
=====

There are two main reactors to choose from, Tokamak and Spherical Tokamak.
These can be built with:
- A radial and vertical build
- A radial build and plasma elongation.

The former gives the user more control of the size of components allowing reactor blankets to vary both radially and vertically.
The later allows reactors to be built with a minimal number of parameters.
In all cases it is possible to add additional components such as divertors, poloidal and toroidal magnets and any self made geometry as a CadQuery Workplane.
The reactors can be varied in terms of their radial build, vertical build, elongation and triangularity which gives a lot of variability.
These examples show how to make various reactors with and without different components, each example is minimal and aims to show a single feature, you will have to combine examples to make a complete model. 



.. toctree::
   :maxdepth: 3

   usage_tokamak
   usage_spherical_tokamak


Visualization options
=====================

The reactors (cadquery.Assembly objects) and components (cadquery.Workplane objects) can be visualized in a number of ways.
First option is to export them to STEP, BREP or STL file then open the file with your favorite CAD software for example `FreeCAD <https://www.freecad.org/>`_.
See the `CadQuery documentation on saving <https://cadquery.readthedocs.io/en/latest/importexport.html#exporting-step>`_ for more information.
Other options include the built in visualization tools in CadQuery

.. code-block:: python

    from cadquery.vis import show
    show(result)  # where result is the returned reactor or component object

or the jupyter_cadquery package which allows for interactive 3D visualization in a web browser.
or the jupyter_cadquery package which allows for interactive 3D visualization in a web browser.

.. code-block:: python

    # pip install jupyter_cadquery
    # might needed to downgrade pip with ... python -m pip  install pip==24.0
    from jupyter_cadquery import show
    view = show(result)  # where result is the returned reactor or component object
    view.export_html("3d.html")
