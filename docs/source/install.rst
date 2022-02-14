
Installation
============



.. raw:: html

      <iframe width="280" height="157" src="https://www.youtube.com/embed/29nXEpAaELE" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

      <iframe width="280" height="157" src="https://www.youtube.com/embed/HJfOrDM9Avo" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


Prerequisites
-------------

To use the paramak tool you will need Python 3 installed using Miniconda or
Anaconda, or Miniforge

* `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_
* `Anaconda <https://www.anaconda.com/>`_
* `Miniforge <https://github.com/conda-forge/miniforge>`_

Once you have a version of Conda installed then proceed with the OS specific
steps.

Install (conda)
---------------

This is the recommended method.

Create a new environment (Python 3.6, 3.7 or 3.8 are supported).

.. code-block:: bash

   conda create --name paramak_env python=3.8


Then activate the new environment.

.. code-block:: bash

   conda activate paramak_env


Then install the Paramak.

.. code-block:: bash

   conda install -c fusion-energy -c cadquery -c conda-forge paramak

Now you should be ready to import paramak from your new python environment.



Install (conda + pip)
---------------------

Create a new environment (Python 3.6, 3.7 or 3.8 are supported).

.. code-block:: bash

   conda create --name paramak_env python=3.8


Then activate the new environment.

.. code-block:: bash

   conda activate paramak_env


Then install the CadQuery.

.. code-block:: bash

   conda install -c cadquery -c conda-forge cadquery=2.1

If you want to make use of the prototype export_dagmc_h5m() method then you will
need to modify the above command to target CaDQuery Master instead of 2.1.
MOAB and PyMoab are also required for the export_dagmc_h5m() feature to work.
The MOAB Conda install does not currently support Windows and therefore Windows
users will have to compile MOAB. If the export_dagmc_h5m() feature is not
needed then this stage can be skipped.

.. code-block:: bash

   conda install -c conda-forge moab=5.3.1
   conda install -c conda-forge gmsh=4.9.4
   conda install -c conda-forge python-gmsh=4.9.4

Then pip install the Paramak.

.. code-block:: bash

   pip install paramak

Now you should be ready to import paramak from your new python environment.


Optional Jupyter-CadQuery install
---------------------------------

Jupyter-Cadquery is an extension to CadQuery that allows objects to be
rendered in JupyterLab. This can improve the visualization experience for
Paramak users running Jupyter.

 `Jupyter-Cadquery GitHub page <https://github.com/bernhard-42/jupyter-cadquery>`_

Terminal command to install Jupyter-Cadquery

.. code-block:: bash

   pip install jupyter-cadquery


Optional neutronics install
---------------------------

The Paramak is ideal for making CAD geometry including stp and stl files. This
forms part of the `neutronics workflow <https://github.com/fusion-energy/neutronics_workflow>`_
which includes other packages that might be of interest.

* `cad_to_h5m <https://github.com/fusion-energy/cad_to_h5m>`_ allows automated conversion of stp or sat cad files to h5m files compatible with DAGMC enabled neutronics codes.

* `stl_to_h5m <https://github.com/fusion-energy/stl_to_h5m>`_ allows automated conversion of stl files to h5m files compatible with DAGMC enabled neutronics codes.

* `openmc_dagmc_wrapper <https://github.com/fusion-energy/openmc-dagmc-wrapper>`_ allows one to quickly utilise the h5m geometry files in a range of standard neutronics simulations.

* `openmc_data_downloader <https://github.com/openmc-data-storage/openmc_data_downloader>`_ facilitates on the fly downloading of nuclear data needed for OpenMC neutronics simulations.

* `OpenMC <https://github.com/openmc-dev/openmc>`_ The OpenMC project, a Monte Carlo particle transport code based on modern methods.

* `DAGMC <https://github.com/svalinn/DAGMC>`_ Direct Accelerated Geometry Monte Carlo Toolkit 

* `Svalinn Cubit Plugin <https://github.com/svalinn/Cubit-plugin/>`_ A plugin and command extensions for Cubit that allows h5m files to be exported.

* `Coreform Cubit <https://github.com/svalinn/Cubit-plugin/>`_ Advanced meshing for challenging simulations. Supports imprinting and merging of surfaces which speed up the neutronics transport time required for simulations through faceteted geometry.

* `MOAB and pymoab <https://github.com/svalinn/Cubit-plugin/>`_ The Mesh-Oriented datABase MOAB is a component for representing and evaluating mesh data.


Developer Installation
----------------------

If you want to contribute to the paramak or then you might want to install the 
package using setup tools.

Download and install MiniConda, create a new python environment and activate the
environment as covered in the installation procedure above.

Then install CadQuery.

.. code-block:: bash

   conda install -c conda-forge -c cadquery cadquery=2.1


Then clone the repository

.. code-block:: bash

   git clone https://github.com/fusion-energy/paramak.git

Navigate to the paramak repository and within the terminal install the paramak
package and the dependencies using pip with e -e (developer option).

.. code-block:: bash

   cd paramak
   pip install -e .


Docker Image Installation
-------------------------

Another option is to use the Docker image which contains all the required
dependencies.

1. Install Docker CE for `Ubuntu <https://docs.docker.com/install/linux/docker-ce/ubuntu/>`_ ,
`Mac OS <https://store.docker.com/editions/community/docker-ce-desktop-mac>`_ or
`Windows <https://hub.docker.com/editions/community/docker-ce-desktop-windows>`_
including the part where you enable docker use as a non-root user.

2. Pull the docker image from the store by typing the following command in a
terminal window, or Windows users might prefer PowerShell.

.. code-block:: bash

   docker pull ghcr.io/fusion-energy/paramak

3. Now that you have the docker image you can enable graphics linking between
your os and docker, and then run the docker container by typing the following
commands in a terminal window.

.. code-block:: bash

   sudo docker run -p 8888:8888 ghcr.io/fusion-energy/paramak

4. A URL should be displayed in the terminal and can now be opened in the
internet browser of your choice. This will load up the examples folder where
you can view the 3D objects created.

Alternatively the Docker image can be run in interactive terminal mode .

.. code-block:: bash

   docker run -it --entrypoint /bin/bash ghcr.io/fusion-energy/paramak

You may also want to make use of the
`--volume <https://docs.docker.com/storage/volumes/>`_
flag when running Docker so that you can retrieve files from the Docker
environment to your base system.
