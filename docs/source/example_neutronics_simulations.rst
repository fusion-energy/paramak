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
