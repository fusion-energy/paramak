
Installation
============


Prerequisites
-------------

To use the paramak tool you will need Python 3 installed using Anaconda or
Miniconda

* `Anaconda <https://www.anaconda.com/>`_
* `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_

Once you have Anaconda or MiniConda installed then create a new enviroment
(Python 3.6, 3.7 or 3.8 are supported).


.. code-block:: bash

   conda create --name paramak_env python=3.8


Then activate the new enviroment.

.. code-block:: bash

   conda activate paramak_env


Then install the Paramak.

.. code-block:: bash

   conda install -c fusion-energy -c cadquery -c conda-forge paramak

Now you should be ready to import paramak from your new python enviroment.

Optional neutronics install
---------------------------

You can also install optional dependencies that add neutronics capabilities to
the paramak. This will install neutronics_material_maker, OpenMC and DAGMC.
`More details <https://paramak-neutronics.readthedocs.io>`_

Developer Installation
----------------------

If you want to contribute to the paramak or then you might want to install the 
package using setup tools.

Download and install MiniConda, create a new python enviroment and activate the
enviroment as covered in the installation procedure above.

Then install CadQuery.

.. code-block:: bash

   conda install -c conda-forge -c cadquery cadquery=2.1


Then install moab.

.. code-block:: bash

   conda install -c conda-forge moab


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

   docker run -it ghcr.io/fusion-energy/paramak

You may also want to make use of the
`--volume <https://docs.docker.com/storage/volumes/>`_
flag when running Docker so that you can retrieve files from the Docker
enviroment to your base system.
