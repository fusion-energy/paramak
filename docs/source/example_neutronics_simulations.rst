Examples - Neutronics Simulations
=================================

These are minimal examples of neutronics simulations that demonstrate the core
functionality of the neutronics features. In general it easy to export geomtry
in h5m format for use in DAGMC enabled simulations. There are two options for
this export. The Trelis method of converting geometry imprints and merges
surfaces while the PyMoab converts the geoemtry without imprinting and merging
surfaces.

The resulting h5m files can be used in DAGMC enabled neutronics codes such as
OpenMC and MCNP. There is also a class (NeutronicsModel) that facilitates
adding tallies, materials and a source to the geoemtry to create a complete
OpenMC neutronics model which can be simulated. The simulated results are also
extracted from the statepoint.h5 file that OpenMC produces and converted to
vtk, png and JSON files depending on the tally.


ball_reactor.ipynb
^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object

   import paramak
   my_reactor = paramak.BallReactor(
      inner_bore_radial_thickness=50,
      inboard_tf_leg_radial_thickness=200,
      center_column_shield_radial_thickness=50,
      divertor_radial_thickness=50,
      inner_plasma_gap_radial_thickness=50,
      plasma_radial_thickness=100,
      outer_plasma_gap_radial_thickness=50,
      firstwall_radial_thickness=1,
      blanket_radial_thickness=100,
      blanket_rear_wall_radial_thickness=10,
      elongation=2,
      triangularity=0.55,
      number_of_tf_coils=16,
      rotation_angle=180
   )
   
   cadquery_object = my_reactor.solid


`Link to notebook <https://github.com/ukaea/paramak/blob/main/examples/example_neutronics_simulations/ball_reactor.ipynb>`__


ball_reactor_minimal.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^

`Link to notebook <https://github.com/ukaea/paramak/blob/main/examples/example_neutronics_simulations/ball_reactor_minimal.ipynb>`__


ball_reactor_source_plot.ipynb 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Link to notebook <https://github.com/ukaea/paramak/blob/develop/examples/example_neutronics_simulations/ball_reactor_source_plot.ipynb>`__


center_column_study_reactor.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Link to notebook <https://github.com/ukaea/paramak/blob/main/examples/example_neutronics_simulations/center_column_study_reactor.ipynb>`__


center_column_study_reactor_minimal.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Link to notebook <https://github.com/ukaea/paramak/blob/main/examples/example_neutronics_simulations/center_column_study_reactor_minimal.ipynb>`__


OpenMC logo simulation
^^^^^^^^^^^^^^^^^^^^^^

`Link to notebook <https://github.com/ukaea/paramak/blob/develop/examples/example_neutronics_simulations/openmc_logo_example.ipynb>`__

.. raw:: html

   <iframe width="560" height="315" src="https://www.youtube.com/embed/40VARwD44FA" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


text_example.ipynb 
^^^^^^^^^^^^^^^^^^

`Link to notebook <https://github.com/ukaea/paramak/blob/develop/examples/example_neutronics_simulations/text_example.ipynb>`__
