Python API reference
====================


.. currentmodule:: paramak

Assemblies
----------

.. autofunction:: tokamak
.. autofunction:: tokamak_from_plasma
.. autofunction:: spherical_tokamak
.. autofunction:: spherical_tokamak_from_plasma

Utilities
---------

.. autofunction:: poloidal_arc_length
.. autofunction:: spherical_poloidal_arc_length
.. autofunction:: toroidal_arc_length

Workplanes
----------

.. autofunction:: blanket_from_plasma
.. autofunction:: center_column_shield_cylinder
.. autofunction:: constant_thickness_dome
.. autofunction:: cutting_wedge
.. autofunction:: dished_vacuum_vessel
.. autofunction:: plasma_simplified
.. autofunction:: poloidal_field_coil_case
.. autofunction:: poloidal_field_coil
.. autofunction:: revolved_shape
.. autofunction:: toroidal_field_coil_rectangle
.. autofunction:: u_shaped_dome

Structured meshing
------------------

.. automethod:: paramak.assemblies.assembly.Assembly.mesh_structured_layers
.. automethod:: paramak.assemblies.assembly.Assembly.mesh_structured_layer_volumes
.. automethod:: paramak.assemblies.assembly.Assembly.create_structured_layer_dagmc_model
.. automethod:: paramak.assemblies.assembly.Assembly.export_structured_layers_exodus

.. autofunction:: paramak.workplanes.structured_mesh.mesh_revolved_layer
.. autofunction:: paramak.workplanes.structured_mesh.mesh_cad_solid_surface
.. autofunction:: paramak.workplanes.structured_mesh.tetrahedralize_center_column_layer
.. autofunction:: paramak.workplanes.structured_mesh.tetrahedralize_cad_solid
