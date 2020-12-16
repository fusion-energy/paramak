Parametric Neutronics
=====================

The Paramak supports automated neutronics model creation and subsequent
simulation. 

The neutronics models created are DAGMC models and are therefore compatible 
with a suite of neutronics codes (MCNP, Fluka, Geant4, OpenMC).

The automated simulations supported within the paramak are via OpenMC however
one could also carry out simulations in other neutronics codes using the
dagmc.h5m file created. Moab can be used to inspect the dagmc.h5 file and file
the material tag names. mbsize -ll dagmc.h5m | grep 'mat:'

The creation of the dagmc.h5m file can be carried out via three routes.

Option 1. Use of the `OCC_Faceter <https://github.com/makeclean/occ_faceter/>`_ 
and the `PPP <https://github.com/ukaea/parallel-preprocessor>`_

Option 2. Use of `Trelis <https://www.coreform.com/products/trelis/>`_ by
Coreform

Option 3. Use of `PyMoab <https://bitbucket.org/fathomteam/moab>`_ by
Coreform

To create a model it is also necessary to define the source and the materials
used. 

For fusion simulations you might want to used the parametric-plasma-source
`Git repository <https://github.com/open-radiation-sources/parametric-plasma-source>`_ 

Details of the Neutronics Material Maker are available from the
`documentation <https://neutronics-material-maker.readthedocs.io/en/latest/>`_ 
and the `source code repository <https://github.com/ukaea/neutronics_material_maker>`_
. However openmc.Materials can also be used directly.

NeutronicsModel()
^^^^^^^^^^^^^^^^^

.. automodule:: paramak.parametric_neutronics.neutronics_model
   :members:
   :show-inheritance:
