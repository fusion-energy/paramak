# This Dockerfile creates an enviroment with the optional dependancies and the Paramak
# This dockerfile can be built in a few different ways.
# Docker build commands must be run from within the base repository directory
#
# There are build args availalbe for specifying the:
# - cq_version
#   The version of CadQuery to use master or 2.1
#   Default is 2.1
#   Options: [master, 2, 2.1]
#
# - paramak_version
#   The version number applied to the paramak. The CI finds this version number
#   from the release tag.
#   Default is develop
#   Options: version number with three numbers separated by . for example 0.7.1
#
# Example builds:
# Building using the defaults (cq_version 2.1)
# docker build -t paramak .
#
# Building to include cadquery master.
# Run command from within the base repository directory
# docker build -t paramak --build-arg cq_version=master .
#
# Once build the dockerimage can be run in a few different ways.
#
# Run with the following command for a terminal notebook interface
# docker run -it paramak /bin/bash
#
# Run with the following command for a jupyter notebook interface
# docker run -p 8888:8888 paramak
#
# Once built, the docker image can be tested with either of the following commands
# docker run --rm paramak pytest /tests
# docker run --rm paramak  /bin/bash -c "bash run_tests.sh"

FROM continuumio/miniconda3:4.9.2 as dependencies

# By default this Dockerfile builds with the latest release of CadQuery 2
ARG cq_version=2.1

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get --allow-releaseinfo-change update
RUN apt-get update -y && \
    apt-get upgrade -y

RUN apt-get install -y libgl1-mesa-glx libgl1-mesa-dev libglu1-mesa-dev  freeglut3-dev libosmesa6 libosmesa6-dev  libgles2-mesa-dev curl imagemagick && \
                       apt-get clean

# Installing CadQuery and Gmsh
RUN echo installing CadQuery version $cq_version && \
    conda install -c conda-forge -c python python=3.8 && \
    conda install -c conda-forge -c cadquery cadquery="$cq_version" && \
    conda install -c conda-forge moab && \
    conda install -c conda-forge gmsh && \
    conda install -c conda-forge python-gmsh && \
    pip install jupyter-cadquery==2.2.0 && \
    conda clean -afy


RUN mkdir /home/paramak
EXPOSE 8888
WORKDIR /home/paramak


FROM dependencies as final

ARG paramak_version=develop

COPY run_tests.sh run_tests.sh
COPY paramak paramak/
COPY examples examples/

COPY tests tests/
COPY tests_h5m tests_h5m/
COPY tests_show tests_show/
COPY tests_examples tests_examples/

COPY setup.py setup.py
COPY setup.cfg setup.cfg
COPY pyproject.toml pyproject.toml

COPY README.md README.md
COPY LICENSE.txt LICENSE.txt


RUN SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PARAMAK=${paramak_version} pip install .[tests,docs]

CMD ["jupyter", "lab", "--notebook-dir=/home/paramak/examples", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
