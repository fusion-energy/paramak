Developer install
=================

Here are some guide lines for installing the code as a developer.

To clone the repository and install the paramak in developer mode.

.. code-block:: bash

   git clone https://github.com/fusion-energy/paramak.git
   cd paramak
   pip install -e .[tests]

A few dependencies are not available on pip, these can be conda installed.
First install conda, you could use `miniconda3 <https://docs.conda.io/en/latest/miniconda.html>`_
or `anaconda3 <https://www.anaconda.com/products/individual>`_ but we use
`miniforge <https://github.com/conda-forge/miniforge>`_ in this example.

.. code-block:: bash

   # download miniforge
   wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O miniforge.sh

   # install miniforge
   bash miniforge.sh -b -p $HOME/miniforge

   # To activate and use Miniconda
   source $HOME/miniforge/bin/activate

   # create and activate a new conda enviroment
   conda create --name paramak_env python=3.9 -y
   conda activate paramak_env

   # install the dependencies that are not available on pip
   conda install -c cadquery -c conda-forge cadquery=master
   conda install -c conda-forge moab


Test Suite and automation
=========================

A series of unit and integration tests are run automatically with every pull
request or merge to the Github repository. Running the tests locally is also
possible by running pytest within a cloned Paramak repo. The testing
dependencies may be installed alongside Paramak with the following terminal
commands.

Running the tests locally:

.. code-block:: bash

   pytest tests

The status of the tests is available on the CircleCI account
`CircleCI account. <https://app.circleci.com/pipelines/github/fusion-energy/paramak?branch=main>`_

The test suite can be explored on the
`Gihub source code repository. <https://github.com/fusion-energy/paramak/tree/main/tests>`_

In addition to automated tests we also have automated code style formatting
using  `autopep8 and Github Actions. <https://github.com/fusion-energy/paramak/actions?query=workflow%3Aautopep8>`_

Continuing the theme of automation we also have automated distribution updates.
The distribution is performed by `PyPI <https://pypi.org/>`_ and Conda. These
are kept up to date using Github Actions.
`(upload python package) <https://github.com/fusion-energy/paramak/actions>`_

We use pre commits, black and flake8 to keep the code well formatted.
