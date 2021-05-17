
Installation
============


Prerequisites
-------------

To use the paramak tool you will need Python 3 and Cadquery 2 installed.

* `Python 3 <https://www.python.org/downloads/>`_

* `CadQuery 2 <https://github.com/CadQuery/cadquery>`_

Python 3 and CadQuery can be installed using Conda or Miniconda

* `Anaconda <https://www.anaconda.com/>`_
* `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_
  
Once you have Conda or MiniConda installed then CadQuery can be installed
into a new enviroment and that environment can be activated using Anaconda or Miniconda. 

Cadquery 2 can be installed in a Conda environment via conda-forge.

.. code-block:: python

   conda create -n paramak_env -c conda-forge -c cadquery python=3.8 cadquery=2.1


Once you have activated a conda environment, Cadquery 2 can be installed
using the command:

.. code-block:: python

   conda activate paramak_env


A more detailed description of installing Cadquery 2 can be found here:

* `Cadquery 2 installation <https://cadquery.readthedocs.io/en/latest/installation.html>`_


System Installation
-------------------

The quickest way to install the Paramak is to use pip. In the terminal type...

.. code-block:: bash

   pip install paramak

Alternatively you can download the repository using the `download link <https://github.com/ukaea/paramak/archive/develop.zip>`_ or clone the repository using:

.. code-block:: bash

   git clone https://github.com/Shimwell/paramak.git

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
`More details <https://paramak.readthedocs.io/en/latest/paramak.parametric_neutronics.html>`_

.. code-block:: bash

   pip install .[neutronics]

You could consider installing
[jupyter-cadquery](https://github.com/bernhard-42/jupyter-cadquery) which adds
3D viewing in Jupyter lab as shown in the example notebooks.

.. code-block:: bash

   pip install jupyter-cadquery



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

   docker pull ukaea/paramak

3. Now that you have the docker image you can enable graphics linking between
your os and docker, and then run the docker container by typing the following
commands in a terminal window.

.. code-block:: bash

   sudo docker run -p 8888:8888 ukaea/paramak

4. A URL should be displayed in the terminal and can now be opened in the
internet browser of your choice. This will load up the examples folder where
you can view the 3D objects created.

Alternatively the Docker image can be run in terminal mode .

.. code-block:: bash

   docker run -it ukaea/paramak

You may also want to make use of the
`--volume <https://docs.docker.com/storage/volumes/>`_
flag when running Docker so that you can retrieve files from the Docker
enviroment to your base system.
