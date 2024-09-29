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


Tokamak
-------

- The tokamak function provides a parametric tokamak shaped reactor.
- This is characterized by a continuous blanket that goes around the inboard and outboard sides of the plasma.
- This reactor requires few arguments to create as it keeps the vertical build of the blanket layers the same thickness as the radial build.

.. cadquery::
    :gridsize: 0
    :select: result
    :color: #00cd00
    :width: 100%
    :height: 600px

    import paramak
    result = paramak.tokamak_from_plasma(
        radial_builds=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 30),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 10),
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=90,
    ).toCompound()


.. code-block:: python

    import paramak
    result = paramak.tokamak_from_plasma(
        radial_builds=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 30),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 10),
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=90,
    )


Spherical tokamak from plasma
-----------------------------

- The spherical_tokamak_from_plasma function provides a parametric tokamak shaped reactor.
- This is characterized by a blanket that only goes around the outboard sides of the plasma.
- This reactor requires few arguments to create as it keeps the vertical build of the blanket layers the same thickness as the radial build.


.. cadquery::
    :gridsize: 0
    :select: result
    :color: #00cd00
    :width: 100%
    :height: 600px

    import paramak
    result = paramak.spherical_tokamak_from_plasma(
        radial_builds=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 10),
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=90,
    ).toCompound()


.. code-block:: python

    import paramak
    result = paramak.spherical_tokamak_from_plasma(
        radial_builds=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 10),
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=90,
    )
    result.save('reactor.step')



Tokamak
-------

- The spherical_tokamak function provides a parametric tokamak shaped reactor.
- This is characterized by a blanket that only goes around the outboard sides of the plasma.
- This reactor allows for a separate vertical and radial build which allows different thickness layers in the blanket.

.. cadquery::
    :gridsize: 0
    :select: result
    :color: #00cd00
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.tokamak(
        radial_builds=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 30),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 10),
        ],
        vertical_build=[
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 80),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 700),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 40),
            (paramak.LayerType.SOLID, 15),
        ],
        triangularity=0.55,
        rotation_angle=180,
    ).toCompound()

.. code-block:: python

    import paramak

    result = paramak.tokamak(
        radial_builds=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 30),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 10),
        ],
        vertical_build=[
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 80),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 700),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 40),
            (paramak.LayerType.SOLID, 15),
        ],
        triangularity=0.55,
        rotation_angle=180,
    )

    result.save(f"tokamak_minimal.step")



Spherical tokamak
-----------------

- The spherical_tokamak function provides a parametric tokamak shaped reactor.
- This is characterized by a blanket that only goes around the outboard sides of the plasma.
- This reactor allows for a separate vertical and radial build which allows different thickness layers in the blanket. 

.. cadquery::
    :gridsize: 0
    :select: result
    :color: #00cd00
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.spherical_tokamak(
        radial_builds=[
            [
                (paramak.LayerType.GAP, 10),
                (paramak.LayerType.SOLID, 50),
                (paramak.LayerType.SOLID, 10),
                (paramak.LayerType.GAP, 50),
                (paramak.LayerType.PLASMA, 300),
                (paramak.LayerType.GAP, 60),
                (paramak.LayerType.SOLID, 10),
                (paramak.LayerType.SOLID, 60),
                (paramak.LayerType.SOLID, 10),
            ]
        ],
        vertical_build=[
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 700),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 30),
            (paramak.LayerType.SOLID, 15),
        ],
        rotation_angle=180,
        triangularity=0.55,
    ).toCompound()

.. code-block:: python

    import paramak

    result = paramak.spherical_tokamak(
        radial_builds=[
            [
                (paramak.LayerType.GAP, 10),
                (paramak.LayerType.SOLID, 50),
                (paramak.LayerType.SOLID, 10),
                (paramak.LayerType.GAP, 50),
                (paramak.LayerType.PLASMA, 300),
                (paramak.LayerType.GAP, 60),
                (paramak.LayerType.SOLID, 10),
                (paramak.LayerType.SOLID, 60),
                (paramak.LayerType.SOLID, 10),
            ]
        ],
        vertical_build=[
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 700),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 30),
            (paramak.LayerType.SOLID, 15),
        ],
        rotation_angle=180,
        triangularity=0.55,
    )

    result.save(f"spherical_tokamak_minimal.step")

Reactor with divertor(s)
------------------------

- ll reactors support adding additional radial builds for the lower_divertor and or the upper_divertor.
- This example adds two divertors to a spherical_tokamak_from_plasma reactor but and other reactor would also work.

.. cadquery::
    :gridsize: 0
    :select: result
    :color: #00cd00
    :width: 100%
    :height: 600px

    result = paramak.spherical_tokamak_from_plasma(
        radial_builds=[
            [
                (paramak.LayerType.GAP, 10),
                (paramak.LayerType.SOLID, 50),
                (paramak.LayerType.SOLID, 15),
                (paramak.LayerType.GAP, 50),
                (paramak.LayerType.PLASMA, 300),
                (paramak.LayerType.GAP, 60),
                (paramak.LayerType.SOLID, 15),
                (paramak.LayerType.SOLID, 60),
                (paramak.LayerType.SOLID, 10),
            ],
            [(paramak.LayerType.GAP, 75), ("lower_divertor", 100)],  # this divertor connects to the center column
            [(paramak.LayerType.GAP, 120), ("upper_divertor", 100)],  # this divertor has some blanket between the center colum and itself
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=180,
    ).toCompound()


.. code-block:: python

    result = paramak.spherical_tokamak_from_plasma(
        radial_builds=[
            [
                (paramak.LayerType.GAP, 10),
                (paramak.LayerType.SOLID, 50),
                (paramak.LayerType.SOLID, 15),
                (paramak.LayerType.GAP, 50),
                (paramak.LayerType.PLASMA, 300),
                (paramak.LayerType.GAP, 60),
                (paramak.LayerType.SOLID, 15),
                (paramak.LayerType.SOLID, 60),
                (paramak.LayerType.SOLID, 10),
            ],
            [(paramak.LayerType.GAP, 75), ("lower_divertor", 100)],  # this divertor connects to the center column
            [(paramak.LayerType.GAP, 120), ("upper_divertor", 140)],  # this divertor has some blanket between the center colum and itself
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=180,
    )
    result.save('reactor.step')

Reactor with poloidal field coils
---------------------------------

- All reactors support adding a sequence of CadQuery shapes (e.g. workplanes) to the reactor using the add_extra_cut_shapes argument
- This example adds PF coils to a spherical_tokamak_from_plasma reactor but and other reactor would also work.


.. cadquery::
    :gridsize: 0
    :select: result
    :color: #00cd00
    :width: 100%
    :height: 600px

    import paramak

    add_extra_cut_shapes = []
    for case_thickness, height, width, center_point in zip(
        [10, 15, 15, 10], [20, 50, 50, 20], [20, 50, 50, 20],
        [(500, 300), (560, 100), (560, -100), (500, -300)]
    ):
        add_extra_cut_shapes.append(
            paramak.poloidal_field_coil(
                height=height, width=width, center_point=center_point, rotation_angle=270
            )
        )
        add_extra_cut_shapes.append(
            paramak.poloidal_field_coil_case(
                coil_height=height,
                coil_width=width,
                casing_thickness=case_thickness,
                rotation_angle=270,
                center_point=center_point,
            )
        )

    result = paramak.spherical_tokamak_from_plasma(
        radial_builds=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=270,
        add_extra_cut_shapes=add_extra_cut_shapes,
    ).toCompound()


.. code-block:: python

    import paramak

    add_extra_cut_shapes = []
    for case_thickness, height, width, center_point in zip(
        [10, 15, 15, 10], [20, 50, 50, 20], [20, 50, 50, 20],
        [(500, 300), (560, 100), (560, -100), (500, -300)]
    ):
        add_extra_cut_shapes.append(
            paramak.poloidal_field_coil(
                height=height, width=width, center_point=center_point, rotation_angle=270
            )
        )
        add_extra_cut_shapes.append(
            paramak.poloidal_field_coil_case(
                coil_height=height,
                coil_width=width,
                casing_thickness=case_thickness,
                rotation_angle=270,
                center_point=center_point,
            )
        )

    result = paramak.spherical_tokamak_from_plasma(
        radial_builds=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
        ],
        elongation=2,
        triangularity=0.55,
        rotation_angle=270,
        add_extra_cut_shapes=add_extra_cut_shapes,
    )

    result.save(f"spherical_tokamak_from_plasma_with_pf_magnets.step")


Reactor with toroidal field coils
---------------------------------

- In a similar way to adding poloidal field coils one can also add toroidal field coils by making use of the add_extra_cut_shapes argument.
- All reactors support adding a sequence of CadQuery shapes (e.g. workplanes) to the reactor using the add_extra_cut_shapes argument
- This example adds TF coils to a spherical_tokamak_from_plasma reactor but and other reactor would also work.
- Also these are rectangle shaped TF coils but other shapes are also available.


.. cadquery::
    :gridsize: 0
    :select: result
    :color: #00cd00
    :width: 100%
    :height: 600px

    import paramak

    tf = paramak.toroidal_field_coil_rectangle(
        horizontal_start_point = (10, 520),
        vertical_mid_point = (600, 0),
        thickness = 50,
        distance = 40,
        with_inner_leg = True,
        azimuthal_placement_angles = [0, 30, 60, 90, 120, 150, 180],
    )

    result = paramak.spherical_tokamak_from_plasma(
        radial_builds=[
            (paramak.LayerType.GAP, 70),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
        ],
        elongation=2.5,
        rotation_angle=180,
        triangularity=0.55,
        add_extra_cut_shapes=[tf]
    ).toCompound()

.. code-block:: python

    import paramak

    tf = paramak.toroidal_field_coil_rectangle(
        horizontal_start_point = (10, 520),
        vertical_mid_point = (600, 0),
        thickness = 50,
        distance = 40,
        with_inner_leg = True,
        azimuthal_placement_angles = [0, 30, 60, 90, 120, 150, 180],
    )

    result = paramak.spherical_tokamak_from_plasma(
        radial_builds=[
            (paramak.LayerType.GAP, 70),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
        ],
        elongation=2.5,
        rotation_angle=180,
        triangularity=0.55,
        add_extra_cut_shapes=[tf]
    )

    result.save(f"spherical_tokamak_minimal.step")


Tokamak with negative triangularity
-----------------------------------

- The triangularity argument can be set to a negative value to make a plasma with a negative triangularity.
- This example makes a tokamak with a negative but this would work on any reactor.

.. cadquery::
    :gridsize: 0
    :select: result
    :color: #00cd00
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.tokamak(
        radial_builds=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 30),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 10),
        ],
        vertical_build=[
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 80),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 700),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 40),
            (paramak.LayerType.SOLID, 15),
        ],
        triangularity=-0.55,
        rotation_angle=180,
    ).toCompound()

.. code-block:: python

    import paramak

    result = paramak.tokamak(
        radial_builds=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 30),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 120),
            (paramak.LayerType.SOLID, 10),
        ],
        vertical_build=[
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 80),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 700),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 40),
            (paramak.LayerType.SOLID, 15),
        ],
        triangularity=-0.55,
        rotation_angle=180,
    )

    result.save(f"tokamak_minimal.step")



Spherical tokamak with negative triangularity
---------------------------------------------

- The triangularity argument can be set to a negative value to make a plasma with a negative triangularity.
- This example makes a spherical tokamak with a negative but this would work on any reactor.

.. cadquery::
    :gridsize: 0
    :select: result
    :color: #00cd00
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.spherical_tokamak(
        radial_builds=[
            [
                (paramak.LayerType.GAP, 10),
                (paramak.LayerType.SOLID, 50),
                (paramak.LayerType.SOLID, 15),
                (paramak.LayerType.GAP, 50),
                (paramak.LayerType.PLASMA, 300),
                (paramak.LayerType.GAP, 60),
                (paramak.LayerType.SOLID, 40),
                (paramak.LayerType.SOLID, 60),
                (paramak.LayerType.SOLID, 10),
            ]
        ],
        vertical_build=[
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 80),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 700),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 40),
            (paramak.LayerType.SOLID, 15),
        ],
        rotation_angle=180,
        triangularity=-0.55,
    ).toCompound()

.. code-block:: python

    import paramak

    result = paramak.spherical_tokamak(
        radial_builds=[
            [
                (paramak.LayerType.GAP, 10),
                (paramak.LayerType.SOLID, 50),
                (paramak.LayerType.SOLID, 15),
                (paramak.LayerType.GAP, 50),
                (paramak.LayerType.PLASMA, 300),
                (paramak.LayerType.GAP, 60),
                (paramak.LayerType.SOLID, 10),
                (paramak.LayerType.SOLID, 60),
                (paramak.LayerType.SOLID, 10),
            ]
        ],
        vertical_build=[
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.SOLID, 80),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 700),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 40),
            (paramak.LayerType.SOLID, 15),
        ],
        rotation_angle=180,
        triangularity=-0.55,
    )
    result.save(f"spherical_tokamak_minimal.step")
