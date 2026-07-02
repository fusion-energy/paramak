
Tokamak
=======

- This is characterized by a continuous blanket that goes around the inboard and outboard sides of the plasma.

Tokamak
-------

- The tokamak function provides a parametric tokamak shaped reactor.
- This is characterized by a blanket that goes around both the inboard and outboard sides of the plasma.
- This reactor allows for a separate vertical and radial build which allows different thickness layers in the blanket.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.tokamak(
        radial_build=[
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


Tokamak from plasma
-------------------

- The tokamak_from_plasma function provides a parametric tokamak shaped reactor.
- This reactor requires few arguments to create as it keeps the vertical build of the blanket layers the same thickness as the radial build.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak
    result = paramak.tokamak_from_plasma(
        radial_build=[
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

Tokamak with divertor
---------------------

- Reactors support adding additional extra intersect shapes that can be used as a divertor.
- This example adds a divertor to a tokamak_from_plasma reactor.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak
    from cadquery import Workplane

    # makes a rectangle that overlaps the lower blanket under the plasma
    # the intersection of this and the layers will form the lower divertor
    points = [(300, -700), (300, 0), (400, 0), (400, -700)]
    divertor_lower = Workplane('XZ', origin=(0,0,0)).polyline(points).close().revolve(180)
    result = paramak.tokamak_from_plasma(
        radial_build=[
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
        rotation_angle=180,
        extra_intersect_shapes=[divertor_lower]
    ).toCompound()

.. _tokamak_custom_divertor:

Tokamak with custom divertor
----------------------------

- The revolved_shape function builds a solid by revolving a custom 2D (R, Z, connection) profile, where connection is "straight", "spline" or "circle". Splines produce a smooth curved profile rather than a blocky rectangle, and the profile is closed automatically.
- This example passes the revolved shape to ``extra_intersect_shapes``, so it is intersected with the blanket layers. The divertor is therefore **confined to the blanket envelope** and cannot extend into the plasma cavity.
- For the alternative approach, where a revolved shape is added directly to the assembly so it can sit outside the blanket envelope, see the :ref:`spherical_custom_divertor` example.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    # curved divertor profile in the XZ plane, each point is (R, Z, connection)
    points = [
        (300, -700, "straight"),
        (300, -300, "spline"),
        (370, -180, "spline"),
        (470, -240, "spline"),
        (560, -180, "spline"),
        (600, -700, "straight"),
    ]
    divertor_lower = paramak.revolved_shape(points=points, rotation_angle=180, plane="XZ")

    result = paramak.tokamak_from_plasma(
        radial_build=[
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
        rotation_angle=180,
        extra_intersect_shapes=[divertor_lower]
    ).toCompound()

Tokamak with poloidal field coils
---------------------------------

- All reactors support adding a sequence of CadQuery shapes (e.g. workplanes) to the reactor using the extra_cut_shapes argument.
- This example adds PF coils to a tokamak_from_plasma reactor but any other reactor would also work.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    extra_cut_shapes = []
    for case_thickness, height, width, center_point in zip(
        [10, 15, 15, 10], [20, 50, 50, 20], [20, 50, 50, 20],
        [(730, 370), (810, 235), (810, -235), (730, -370)]
    ):
        extra_cut_shapes.append(
            paramak.poloidal_field_coil(
                height=height, width=width, center_point=center_point, rotation_angle=180
            )
        )
        extra_cut_shapes.append(
            paramak.poloidal_field_coil_case(
                coil_height=height,
                coil_width=width,
                casing_thickness=case_thickness,
                rotation_angle=180,
                center_point=center_point,
            )
        )

    result = paramak.tokamak_from_plasma(
        radial_build=[
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
        rotation_angle=180,
        extra_cut_shapes=extra_cut_shapes,
    ).toCompound()

Tokamak with toroidal field coils
---------------------------------

- Toroidal field coils can be added to any reactor using the extra_cut_shapes argument.
- This example adds rectangular TF coils to a tokamak_from_plasma reactor.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    tf = paramak.toroidal_field_coil_rectangle(
        horizontal_start_point=(10, 520),
        vertical_mid_point=(860, 0),
        thickness=50,
        distance=40,
        with_inner_leg=True,
        rotation_angle=180,
        azimuthal_placement_angles=[0, 30, 60, 90, 120, 150, 180],
    )

    result = paramak.tokamak_from_plasma(
        radial_build=[
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
        rotation_angle=180,
        extra_cut_shapes=[tf],
    ).toCompound()


Tokamak with negative triangularity
-----------------------------------

- The triangularity argument can be set to a negative value to make a plasma with a negative triangularity.
- This example makes a tokamak with a negative triangularity but this would work on any reactor.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.tokamak(
        radial_build=[
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


Tokamak with several customizations
-----------------------------------

- Combining many of the examples together to produce a Tokamak with extra blanket layers, a lower divertor, PF and TF coils.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak
    from cadquery import Workplane

    # makes a rectangle that overlaps the lower blanket under the plasma
    # the intersection of this and the layers will form the lower divertor
    points = [(300, -700), (300, 0), (400, 0), (400, -700)]
    divertor_lower = Workplane('XZ', origin=(0,0,0)).polyline(points).close().revolve(180)

    # creates a toroidal field coil
    tf = paramak.toroidal_field_coil_rectangle(
        horizontal_start_point = (10, 520),
        vertical_mid_point = (860, 0),
        thickness = 50,
        distance = 40,
        with_inner_leg = True,
        rotation_angle = 180,
        azimuthal_placement_angles = [0, 30, 60, 90, 120, 150, 180],
    )

    extra_cut_shapes = [tf]

    # creates pf coils
    for case_thickness, height, width, center_point in zip(
        [10, 15, 15, 10], [20, 50, 50, 20], [20, 50, 50, 20],
        [(730, 370), (810, 235), (810, -235), (730, -370)]
    ):
        extra_cut_shapes.append(
            paramak.poloidal_field_coil(
                height=height, width=width, center_point=center_point, rotation_angle=180
            )
        )
        extra_cut_shapes.append(
            paramak.poloidal_field_coil_case(
                coil_height=height,
                coil_width=width,
                casing_thickness=case_thickness,
                rotation_angle=180,
                center_point=center_point,
            )
        )

    result = paramak.tokamak(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 30),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
        ],
        vertical_build=[
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 650),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.SOLID, 10),
        ],
        triangularity=0.55,
        rotation_angle=180,
        extra_cut_shapes=extra_cut_shapes,
        extra_intersect_shapes=[divertor_lower]
    ).toCompound()


Naming tokamak parts
--------------------

- Every part in the assembly has a name, used when assigning material tags and per-part colors. By default layers are named ``layer_1``, ``layer_2`` ... working outwards and the plasma is named ``plasma``. The name of every part can be listed with ``my_reactor.names()``.
- There are two ways to give layers meaningful names: add an optional name (a string) as the third element of a ``radial_build`` layer tuple, or rename parts after building with ``rename(old, new)``.
- In a tokamak the inboard and outboard portions of a layer are merged into a single solid, so a name on either the inboard or outboard entry names that solid (the inboard name is used if both are given). Names are only supported in the ``radial_build``, not the ``vertical_build``.

.. code-block:: python

    import paramak

    # Option 1 - name the layers in the radial build
    my_reactor = paramak.tokamak_from_plasma(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 30, "central column"),
            (paramak.LayerType.SOLID, 20, "blanket"),
            (paramak.LayerType.SOLID, 10, "first wall"),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 10),
        ],
        rotation_angle=180,
    )
    print(my_reactor.names())
    # ['central column', 'first wall', 'blanket', 'plasma']

.. code-block:: python

    import paramak

    # Option 2 - rename parts after building the reactor (chainable)
    my_reactor = paramak.tokamak_from_plasma(
        radial_build=[
            (paramak.LayerType.GAP, 10),
            (paramak.LayerType.SOLID, 30),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 20),
            (paramak.LayerType.SOLID, 10),
        ],
        rotation_angle=180,
    )
    my_reactor = (
        my_reactor
        .rename("layer_1", "central column")
        .rename("layer_2", "first wall")
        .rename("layer_3", "blanket")
    )
    print(my_reactor.names())
    # ['central column', 'first wall', 'blanket', 'plasma']


Naming tokamak with several customizations
------------------------------------------

- Some reactor components may contain multiple disconnected solids. To view the name assigned to each solid individually, first call ``my_reactor.split_solids()`` and then use ``my_reactor.names()`` on the returned reactor object.
- For example, a toroidal field (TF) coil set may be represented as a single component but consist of seven separate TF coils. After splitting the solids, ``names()`` will return the names of all seven coils in the order they appear in the geometry.

.. code-block:: python

    # Option 1 - name all the shapes at the time of creation

    import paramak
    import cadquery as cq

    # Name a CadQuery shape directly for use in extra_intersect_shapes
    points = [(450, -700), (450, 0), (550, 0), (550, -700)]
    divertor_lower = cq.Workplane("XZ", origin=(0, 0, 0)).polyline(points).close().revolve(180)
    divertor_lower.name = "divertor"  # Default would be extra_intersect_shapes

    # Custom name for TF coils; multiple disconnected coils become toroidal_coil_1_1, toroidal_coil_1_2, etc. after splitting the solids
    tf = paramak.toroidal_field_coil_princeton_d(
        r1=200,
        r2=1000,
        thickness=50,
        distance=60,
        rotation_angle=180,
        with_inner_leg=True,
        azimuthal_placement_angles=[0, 30, 60, 90, 120, 150, 180],
        name="toroidal_coil"  # Default would be "toroidal_field_coil"
    )

    extra_cut_shapes = [tf]

    # Custom names for PF coils and their cases
    for case_thickness, height, width, center_point in zip(
        [10, 15, 15, 10], [20, 50, 50, 20], [20, 50, 50, 20], [(1030, 450), (1110, 250), (1110, -250), (1030, -450)]
    ):
        extra_cut_shapes.append(
            paramak.poloidal_field_coil(
                height=height, 
                width=width, 
                center_point=center_point, 
                rotation_angle=180, 
                name="poloidal_coil"  # Default would be "poloidal_field_coil"
            )
        )
        extra_cut_shapes.append(
            paramak.poloidal_field_coil_case(
                coil_height=height,
                coil_width=width,
                casing_thickness=case_thickness,
                rotation_angle=180,
                center_point=center_point,
                name="poloidal_coil_case",  # Default would be "poloidal_field_coil_case"
            )
        )

    my_reactor = paramak.tokamak_from_plasma(
        radial_build=[
            (paramak.LayerType.GAP, 150),
            (paramak.LayerType.SOLID, 50, "CS Coil"),
            (paramak.LayerType.GAP, 80),
            (paramak.LayerType.SOLID, 10, "Vacuum Vessel"),
            (paramak.LayerType.SOLID, 60, "Blanket"),
            (paramak.LayerType.SOLID, 60, "First Wall"),
            (paramak.LayerType.SOLID, 10, "W Armor"),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10, "W Armor"),
            (paramak.LayerType.SOLID, 60, "First Wall"),
            (paramak.LayerType.SOLID, 60, "Blanket"),
            (paramak.LayerType.SOLID, 10, "Vacuum Vessel"),
        ],
        rotation_angle=180,
        extra_cut_shapes=extra_cut_shapes,
        extra_intersect_shapes=[divertor_lower],
    )

    # Use split_solids() to inspect individual solid names before assigning material tags.
    my_reactor = my_reactor.split_solids()
    print(my_reactor.names())
    '''
    ['toroidal_coil_1_1', 'toroidal_coil_1_2', 'toroidal_coil_1_3', 'toroidal_coil_1_4', 'toroidal_coil_1_5', 
    'toroidal_coil_1_6', 'toroidal_coil_1_7', 'poloidal_coil_2', 'poloidal_coil_case_3', 'poloidal_coil_4', 
    'poloidal_coil_case_5', 'poloidal_coil_6', 'poloidal_coil_case_7', 'poloidal_coil_8', 'poloidal_coil_case_9', 
    'divertor_1', 'CS Coil', 'W Armor', 'First Wall', 'Blanket', 'Vacuum Vessel', 'plasma']
    '''

.. code-block:: python
    
    # Option 2 - rename parts after building the reactor (chainable)
    
    import paramak
    import cadquery as cq

    # Create divertor shape
    points = [(450, -700), (450, 0), (550, 0), (550, -700)]
    divertor_lower = cq.Workplane("XZ", origin=(0, 0, 0)).polyline(points).close().revolve(180)

    # Create TF coil shape
    tf = paramak.toroidal_field_coil_princeton_d(
        r1=200,
        r2=1000,
        thickness=50,
        distance=60,
        rotation_angle=180,
        with_inner_leg=True,
        azimuthal_placement_angles=[0, 30, 60, 90, 120, 150, 180],
    )

    extra_cut_shapes = [tf]

    # Create PF coils and their cases
    for case_thickness, height, width, center_point in zip(
        [10, 15, 15, 10], [20, 50, 50, 20], [20, 50, 50, 20], [(1030, 450), (1110, 250), (1110, -250), (1030, -450)]
    ):
        extra_cut_shapes.append(
            paramak.poloidal_field_coil(
                height=height, 
                width=width, 
                center_point=center_point, 
                rotation_angle=180,
            )
        )
        extra_cut_shapes.append(
            paramak.poloidal_field_coil_case(
                coil_height=height,
                coil_width=width,
                casing_thickness=case_thickness,
                rotation_angle=180,
                center_point=center_point,
            )
        )

    my_reactor = paramak.tokamak_from_plasma(
        radial_build=[
            (paramak.LayerType.GAP, 150),
            (paramak.LayerType.SOLID, 50),
            (paramak.LayerType.GAP, 80),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.PLASMA, 300),
            (paramak.LayerType.GAP, 60),
            (paramak.LayerType.SOLID, 10),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 60),
            (paramak.LayerType.SOLID, 10),
        ],
        rotation_angle=180,
        extra_cut_shapes=extra_cut_shapes,
        extra_intersect_shapes=[divertor_lower],
    )

    my_reactor = (
        my_reactor
        .rename("extra_intersect_shapes", "divertor")
        .rename("toroidal_field_coil", "toroidal_coil")
        .rename("poloidal_field_coil", "poloidal_coil")
        .rename("poloidal_field_coil_case", "poloidal_coil_case")
        .rename("layer_1", "CS Coil")
        .rename("layer_2", "W Armor")
        .rename("layer_3", "First Wall")
        .rename("layer_4", "Blanket")
        .rename("layer_5", "Vacuum Vessel")
    )

    # Use split_solids() to inspect individual solid names before assigning material tags.
    my_reactor = my_reactor.split_solids()
    print(my_reactor.names())
    '''
    ['toroidal_coil_1_1', 'toroidal_coil_1_2', 'toroidal_coil_1_3', 'toroidal_coil_1_4', 'toroidal_coil_1_5', 
    'toroidal_coil_1_6', 'toroidal_coil_1_7', 'poloidal_coil_2', 'poloidal_coil_case_3', 'poloidal_coil_4', 
    'poloidal_coil_case_5', 'poloidal_coil_6', 'poloidal_coil_case_7', 'poloidal_coil_8', 'poloidal_coil_case_9', 
    'divertor_1', 'CS Coil', 'W Armor', 'First Wall', 'Blanket', 'Vacuum Vessel', 'plasma']
    '''
