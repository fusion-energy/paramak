
Installation
============


Prerequisites
-------------

To use the paramak tool you will need Python 3 installed using Anaconda or
Miniconda

* `Anaconda <https://www.anaconda.com/>`_
* `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_

Once you have Anaconda or MiniConda installed then CadQuery can be installed
into a new enviroment. A more detailed description of installing Cadquery 2 can
be found here:

* `Cadquery 2 installation <https://cadquery.readthedocs.io/en/latest/installation.html>`_


First create a new enviroment.

.. code-block:: python

   conda create --name paramak_env python=3.8


Then activate the new enviroment.

.. code-block:: python

   conda activate paramak_env


Then install CadQuery.

   .. code-block:: python

      conda install -c conda-forge -c cadquery cadquery=2.1

Now you are ready to install the Paramak


System Installation
-------------------

The quickest way to install the Paramak is to use pip. In the terminal type...

.. code-block:: bash

   pip install paramak

Alternatively you can download the repository using the `download link <https://github.com/fusion-energy/paramak/archive/develop.zip>`_ or clone the repository using:

.. code-block:: bash

   git clone https://github.com/fusion-energy/paramak.git

Navigate to the paramak repository and within the terminal install the paramak
package and the dependencies using pip3.

.. code-block:: bash

   pip install .

Alternatively you can install the paramak with the following command.

.. code-block:: bash

   python setup.py install

You can also install optional dependencies that add some neutronics
capabilities to the paramak. This will install neutronics_material_maker and
parametric_plasma_source. In addition to this you would need DAGMC, OpenMC,
MOAB and Trelis / Cubit.
`More details <https://paramak-neutronics.readthedocs.io>`_


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

Alternatively the Docker image can be run in terminal mode .

.. code-block:: bash

   docker run -it ghcr.io/fusion-energy/paramak

You may also want to make use of the
`--volume <https://docs.docker.com/storage/volumes/>`_
flag when running Docker so that you can retrieve files from the Docker
enviroment to your base system.
