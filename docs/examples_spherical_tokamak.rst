Spherical Tokamak
=================

- This is characterized by a blanket that only goes around the outboard sides of the plasma and a center column that has no inboard breeding.

Spherical tokamak
-----------------

- The spherical_tokamak function provides a parametric tokamak shaped reactor.
- This is characterized by a blanket that only goes around the outboard sides of the plasma.
- This reactor allows for a separate vertical and radial build which allows different thickness layers in the blanket.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.spherical_tokamak(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
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


Spherical tokamak from plasma
-----------------------------

- The spherical_tokamak_from_plasma function provides a parametric tokamak shaped reactor.
- This reactor requires minimal arguments to create as it keeps the vertical build of the blanket layers the same thickness as the radial build.


.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak
    result = paramak.spherical_tokamak_from_plasma(
        radial_build=[
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


Spherical tokamak with divertor
-------------------------------

- Reactors support adding additional extra intersect shapes that can be used as a divertor.
- This example adds a divertor to a spherical_tokamak_from_plasma reactor.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak
    from cadquery import Workplane

    # makes a rectangle that overlaps the lower blanket under the plasma
    # the intersection of this and the layers will form the lower divertor
    points = [(200, -700), (200, 0), (300, 0), (300, -700)]
    divertor_lower = Workplane('XZ', origin=(0,0,0)).polyline(points).close().revolve(180)
    result = paramak.spherical_tokamak_from_plasma(
        radial_build=[
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
        rotation_angle=180,
        extra_intersect_shapes=[divertor_lower]
    ).toCompound()

.. _spherical_custom_divertor:

Spherical tokamak with custom divertor
--------------------------------------

- The revolved_shape function builds a solid by revolving a custom 2D (R, Z, connection) profile. Here straight segments make a small V-shaped divertor plate.
- This example adds the revolved shape directly to the reactor assembly with ``assembly.add``, rather than passing it to ``extra_intersect_shapes``. The plate therefore keeps its full shape and can sit anywhere inside the vessel, **outside the blanket envelope** — it is not clipped to the blanket.
- For the alternative approach, where the revolved shape is intersected with the blanket so the divertor is confined to the blanket envelope, see the :ref:`tokamak_custom_divertor` example.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import cadquery as cq
    import paramak

    # small V-shaped divertor plate from straight segments, sitting in the
    # lower cavity between the plasma and the lower blanket
    points = [
        (160, -312, "straight"),
        (220, -336, "straight"),
        (280, -312, "straight"),
        (280, -330, "straight"),
        (220, -354, "straight"),
        (160, -330, "straight"),
    ]
    divertor = paramak.revolved_shape(points=points, rotation_angle=180, plane="XZ")

    result = paramak.spherical_tokamak_from_plasma(
        radial_build=[
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
        rotation_angle=180,
    )

    # add the divertor plate directly to the assembly so it is not clipped to the blanket
    result.add(divertor, name="divertor", color=cq.Color("red"))
    result = result.toCompound()

Spherical tokamak with poloidal field coils
-------------------------------------------

- All reactors support adding a sequence of CadQuery shapes (e.g. workplanes) to the reactor using the extra_cut_shapes argument.
- This example adds PF coils to a spherical_tokamak_from_plasma reactor but any other reactor would also work.


.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    extra_cut_shapes = []
    for case_thickness, height, width, center_point in zip(
        [10, 15, 15, 10], [20, 50, 50, 20], [20, 50, 50, 20],
        [(500, 300), (560, 100), (560, -100), (500, -300)]
    ):
        extra_cut_shapes.append(
            paramak.poloidal_field_coil(
                height=height, width=width, center_point=center_point, rotation_angle=270
            )
        )
        extra_cut_shapes.append(
            paramak.poloidal_field_coil_case(
                coil_height=height,
                coil_width=width,
                casing_thickness=case_thickness,
                rotation_angle=270,
                center_point=center_point,
            )
        )

    result = paramak.spherical_tokamak_from_plasma(
        radial_build=[
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
        extra_cut_shapes=extra_cut_shapes,
    ).toCompound()


Spherical tokamak with toroidal field coils
-------------------------------------------

- In a similar way to adding poloidal field coils one can also add toroidal field coils by making use of the extra_cut_shapes argument.
- All reactors support adding a sequence of CadQuery shapes (e.g. workplanes) to the reactor using the extra_cut_shapes argument.
- This example adds TF coils to a spherical_tokamak_from_plasma reactor but any other reactor would also work.
- Also these are rectangle shaped TF coils but other shapes are also available.


.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    tf_style_1 = paramak.toroidal_field_coil_rectangle(
        horizontal_start_point = (10, 520),
        vertical_mid_point = (600, 0),
        thickness = 50,
        distance = 40,
        rotation_angle = 180,
        with_inner_leg = True,
        azimuthal_placement_angles = [0, 30, 60, 90, 120, 150, 180],
    )

    result1 = paramak.spherical_tokamak_from_plasma(
        radial_build=[
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
        extra_cut_shapes=[tf_style_1]
    ).toCompound().translate((700, 0, 0))

    tf_style_2 = paramak.toroidal_field_coil_princeton_d(
        r1=5,
        r2=610,
        azimuthal_placement_angles = [0, 30, 60, 90, 120, 150, 180],
        rotation_angle = 180,
        thickness = 50,
        distance = 40
    )

    result2 = paramak.spherical_tokamak_from_plasma(
        radial_build=[
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
        extra_cut_shapes=[tf_style_2]
    ).toCompound().translate((-700, 0, 0))

    import cadquery as cq
    result = cq.Assembly()
    result.add(result1, name="rectangular_tf")
    result.add(result2, name="princeton_d_tf")
    result = result.toCompound()


Spherical tokamak with negative triangularity
---------------------------------------------

- The triangularity argument can be set to a negative value to make a plasma with a negative triangularity.
- This example makes a spherical tokamak with a negative triangularity but this would work on any reactor.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.spherical_tokamak(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 40),
            (paramak.LayerType.SOLID, 60),
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
        rotation_angle=180,
        triangularity=-0.55,
    ).toCompound()


Naming spherical tokamak parts
------------------------------

- Every part in the assembly has a name, used when assigning material tags and per-part colors. By default layers are named ``layer_1``, ``layer_2`` ... working outwards and the plasma is named ``plasma``. The name of every part can be listed with ``my_reactor.names()``.
- There are two ways to give layers meaningful names: add an optional name (a string) as the third element of a ``radial_build`` layer tuple, or rename parts after building with ``rename(old, new)``.
- Unlike the tokamak, the layers of a spherical tokamak do not revolve around the plasma: the inboard layers are concentric cylinders (the central column) and the outboard layers are the blanket. Every radial solid layer is therefore its own part and is named directly from its ``radial_build`` entry. Names are only supported in the ``radial_build``, not the ``vertical_build``.

.. code-block:: python

    import paramak

    # Option 1 - name the layers in the radial build
    my_reactor = paramak.spherical_tokamak_from_plasma(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 50, "central column"),
            (paramak.LayerType.SOLID, 15, "tf coil"),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10, "first wall"),
            (paramak.LayerType.SOLID, 30, "blanket"),
        ],
        rotation_angle=180,
    )
    print(my_reactor.names())
    # ['central column', 'tf coil', 'first wall', 'blanket', 'plasma']

.. code-block:: python

    import paramak

    # Option 2 - rename parts after building the reactor (chainable)
    my_reactor = paramak.spherical_tokamak_from_plasma(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 15),
            (paramak.LayerType.GAP, 50),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 30),
        ],
        rotation_angle=180,
    )
    my_reactor = (
        my_reactor
        .rename("layer_1", "central column")
        .rename("layer_2", "tf coil")
        .rename("layer_3", "first wall")
        .rename("layer_4", "blanket")
    )
    print(my_reactor.names())
    # ['central column', 'tf coil', 'first wall', 'blanket', 'plasma']
