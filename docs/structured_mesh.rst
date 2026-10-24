Structured meshing
==================

Use structured meshing when you want named meshes for the layers in a
generated tokamak. This guide walks through the workflow: build the reactor,
optionally add divertors and coils, then create the surface or volume mesh you
need.

The structured layer workflow supports tokamaks built with ``tokamak`` or
``tokamak_from_plasma``. The model must keep its generated layer data. Cuts
that change the generated geometry (including ``extra_intersect_shapes``)
prevent structured meshing. Non-intersecting ``extra_cut_shapes`` can be
included as separate CAD components.

Build and prepare the reactor
-----------------------------

Start with a generated tokamak. The mesher uses the analytic layer
descriptions created by these constructors:

.. code-block:: python

   import paramak

   reactor = paramak.tokamak_from_plasma(
       radial_build=radial_build,
       rotation_angle=180,
   )

Add divertors before meshing. A divertor replaces blanket material inside its
poloidal footprint and adds the named divertor layers there. Separate upper
and lower divertors should have non-overlapping poloidal extents:

.. code-block:: python

   reactor = reactor.add_divertor(
       poloidal_start_angle=75,
       poloidal_extent_angle=30,
       divertor_layer_names=["divertor_armor", "divertor_heatsink"],
       divertor_layer_thicknesses=[10, 30],
   )

You can also define poloidal segments and toroidal sectors in the tokamak
build. Their names are retained in the meshes, and toroidal gaps remain empty.
Partial rotations include their two end planes. A full 360 degree mesh omits
the duplicate seam plane.

Add coils and other CAD solids to the assembly before meshing. They are
meshed as separate named components, so they should not overlap the generated
layers:

.. code-block:: python

   coil = paramak.toroidal_field_coil_rectangle(
       horizontal_start_point=(850, 800),
       vertical_mid_point=(1100, 0),
       thickness=40,
       distance=30,
       rotation_angle=180,
       azimuthal_placement_angles=[0, 60, 120, 180],
   )
   reactor.add(coil, name="toroidal_field_coil")

Create a surface mesh
---------------------

Call ``mesh_structured_layers`` to get a list of named mesh records. Each
record has ``name``, ``vertices`` and ``triangles`` arrays. It includes the
generated blanket and divertor layers, central-column layers when present,
and added CAD components such as coils.

.. code-block:: python

   meshes = reactor.mesh_structured_layers(
       n_poloidal=128,
       n_toroidal=32,
       n_axial=64,
       coil_tolerance=0.5,
   )

``n_poloidal`` and ``n_toroidal`` control the angular resolution. ``n_axial``
controls the central-column resolution along its height and defaults to
``n_poloidal``. For CAD component surfaces, ``coil_tolerance`` is a linear
tessellation tolerance in model units (cm), and ``coil_angular_tolerance`` is
an angular tolerance in radians. The CAD surfaces are checked for a closed,
two-manifold boundary.

Create a tetrahedral volume mesh
--------------------------------

Call ``mesh_structured_layer_volumes`` when you need volume elements. Blanket,
divertor and central-column layers use Paramak's structured grids. Use
``n_radial`` to set the number of elements through a layer thickness and
``n_axial`` for the central column.

.. code-block:: python

   volumes = reactor.mesh_structured_layer_volumes(
       n_poloidal=128,
       n_toroidal=32,
       n_radial=2,
       n_axial=64,
       coil_mesh_size=10,
   )

Added CAD components are included by default and tetrahedralized with Gmsh.
``coil_mesh_size`` is the approximate Gmsh element size in model units (cm).
Pass ``include_added_components=False`` to mesh only the generated blanket,
divertor and central-column layers.

Export the meshes
-----------------

For a DAGMC H5M file, create a model from the surface meshes and write it:

.. code-block:: python

   dagmc_model = reactor.create_structured_layer_dagmc_model(
       n_poloidal=128, n_toroidal=32, n_axial=64
   )
   dagmc_model.write_file("reactor.h5m")

The DAGMC model contains the generated layer and added CAD component surfaces;
it excludes the plasma. PyMOAB and PyDAGMC must be installed for this export.

For Exodus, call the convenience export method. It writes named tetrahedral
blocks and requires ``netCDF4`` and Gmsh:

.. code-block:: python

   reactor.export_structured_layers_exodus(
       "reactor.e",
       n_poloidal=128,
       n_toroidal=32,
       n_radial=2,
       n_axial=64,
       coil_mesh_size=10,
   )

Choose names for OpenMC and MOOSE
--------------------------------

Paramak carries each part's name into the exported mesh. Set generated layer
names in the third item of a ``radial_build`` entry. In this example, the
solid parts are named ``first_wall`` and ``blanket``:

.. code-block:: python

   radial_build = [
       (paramak.LayerType.GAP, 10),
       (paramak.LayerType.SOLID, 80, "blanket"),
       (paramak.LayerType.SOLID, 20, "first_wall"),
       (paramak.LayerType.PLASMA, 300),
   ]

Divertor parts take their names from ``divertor_layer_names``; added CAD parts
take the name passed to ``reactor.add``; and poloidal or toroidal segments
take the segment name from their build entries.

After building the reactor, inspect the names that will be exported:

.. code-block:: python

   meshes = reactor.mesh_structured_layers()
   mesh_names = [mesh["name"] for mesh in meshes]
   print(mesh_names)

Each value printed in ``mesh_names`` is a Paramak part name and identifies a
mesh record. If segmentation creates many records that should share one
material or block, pass a ``tag_names`` dictionary to the export method. Its
keys are the original names from ``mesh_names``; its values are the shared
names to write. Names absent from the dictionary are left unchanged. For
example, this map groups all four upper first-wall sectors under one name:

.. code-block:: python

   tag_names = {
       "first_wall_upper_sector_1": "first_wall",
       "first_wall_upper_sector_2": "first_wall",
       "first_wall_upper_sector_3": "first_wall",
       "first_wall_upper_sector_4": "first_wall",
   }

Pass the same map to both exports:

.. code-block:: python

   dagmc_model = reactor.create_structured_layer_dagmc_model(tag_names=tag_names)
   dagmc_model.write_file("reactor.h5m")

   reactor.export_structured_layers_exodus("reactor.e", tag_names=tag_names)

For DAGMC, each mapped name is written as a material tag with a ``mat:``
prefix. The ``first_wall`` name therefore becomes ``mat:first_wall``; use that
tag when assigning the OpenMC material. For Exodus, mapped names become
element block names for MOOSE. Keep mapped Exodus names unique after grouping
and no longer than 32 characters.

Limitations
-----------

* Structured layer meshing currently supports generated tokamak models created
  with ``tokamak`` or ``tokamak_from_plasma``. Other model types, including
  spherical tokamaks, are not supported by this workflow.
* The reactor must retain its analytic layer data. Boolean operations that
  change generated layers, including ``extra_intersect_shapes``, make the
  model unavailable to structured meshing. Non-intersecting
  ``extra_cut_shapes`` can be meshed as separate CAD parts.
* Added CAD parts are meshed independently from generated layers. They must
  not overlap those layers; the mesher does not resolve CAD intersections into
  conformal interfaces or subtract the overlap.
* The DAGMC model contains the generated solid layers and supported added CAD
  parts, but does not include the plasma. H5M export requires PyMOAB and
  PyDAGMC.
* Added CAD component surfaces are tessellated and checked for a closed,
  two-manifold boundary. Their volume meshes use Gmsh. Exodus export also
  requires ``netCDF4`` and Gmsh, and Gmsh may need system libraries such as
  ``libGLU.so.1`` on Linux.
* Exodus element block names must be unique and cannot exceed 32 characters.

The example below shows these steps together, including poloidal segmentation,
toroidal sectors, upper and lower divertors, and coils:

.. literalinclude:: ../examples/tokamak_structured_surface_mesh.py
   :language: python

