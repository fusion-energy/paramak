# This dockerfile can be built in a few different ways.
# Docker build commands must be run from within the base repository directory
#
# There are build args availalbe for specifying the:
# - cq_version
#   The version of CadQuery to use master or 2. 
#   Default is 2.
#   Options: [master, 2]
#
# - include_neutronics
#   If software dependencies needed for neutronics simulations should be
#   included true or false.
#   Default is false.
#   Options: [true, false]
#
# - compile_cores
#   The number of CPU cores to compile the image with.
#   Default is 1.
#   Options: [1, 2, 3, 4, 5, 6...]
#
# Example builds:
# Building using the defaults (cq_version 2, no neutronics and 1 core compile)
# docker build -t ukaea/paramak .
#
# Building to include neutronics dependencies and using 8 cores.
# Run command from within the base repository directory
# docker build -t ukaea/paramak --build-arg include_neutronics=true --build-arg compile_cores=8 .


# Once build the dockerimage can be run in a few different ways.
#
# Run with the following command for a terminal notebook interface
# docker run -it ukaea/paramak .
#
# Run with the following command for a jupyter notebook interface
# docker run -p 8888:8888 ukaea/paramak /bin/bash -c "jupyter notebook --notebook-dir=/examples --ip='*' --port=8888 --no-browser --allow-root"


# Once build the docker image can be tested with the following command
# docker run --rm ukaea/paramak pytest /tests

FROM continuumio/miniconda3

# By default this Dockerfile builds with the latest release of CadQuery 2
ARG cq_version=2
ARG include_neutronics=false
ARG compile_cores=1

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get update -y && \
    apt-get upgrade -y

RUN apt-get install -y libgl1-mesa-glx libgl1-mesa-dev libglu1-mesa-dev \
                       freeglut3-dev libosmesa6 libosmesa6-dev \
                       libgles2-mesa-dev && \
                       apt-get clean

# Installing CadQuery
# jupyter is installed before cadquery to avoid a conflict
RUN echo installing CadQuery version $cq_version && \
    conda install jupyter -y --quiet && \
    conda install -c cadquery -c conda-forge cadquery="$cq_version" && \
    conda clean -afy

# Install neutronics dependencies from Debian package manager
RUN if [ "$include_neutronics" = "true" ] ; \
    then echo installing with include_neutronics=true ; \
         apt-get install -y \
            wget git gfortran g++ cmake \
            mpich libmpich-dev libhdf5-serial-dev libhdf5-mpich-dev \
            imagemagick ; \
    fi

# install addition packages required for MOAB
RUN if [ "$include_neutronics" = "true" ] ; \
    then echo installing with include_neutronics=true ; \
    apt-get --yes install libeigen3-dev ; \
    apt-get --yes install libblas-dev ; \
    apt-get --yes install liblapack-dev ; \
    apt-get --yes install libnetcdf-dev ; \
    apt-get --yes install libtbb-dev ; \
    apt-get --yes install libglfw3-dev ; \
    fi

# Clone and install MOAB
RUN if [ "$include_neutronics" = "true" ] ; \
    then pip install --upgrade numpy cython ; \
    mkdir MOAB ; \
    cd MOAB ; \
    mkdir build ; \
    git clone  --single-branch --branch develop https://bitbucket.org/fathomteam/moab/ ; \
    cd build ; \
    cmake ../moab -DENABLE_HDF5=ON \
                -DENABLE_NETCDF=ON \
                -DBUILD_SHARED_LIBS=OFF \
                -DENABLE_FORTRAN=OFF \
                -DCMAKE_INSTALL_PREFIX=/MOAB ; \
    make -j"$compile_cores" ; \
    make -j"$compile_cores" install ; \
    rm -rf * ; \
    cmake ../moab -DBUILD_SHARED_LIBS=ON \
                -DENABLE_HDF5=ON \
                -DENABLE_PYMOAB=ON \
                -DENABLE_BLASLAPACK=OFF \
                -DENABLE_FORTRAN=OFF \
                -DCMAKE_INSTALL_PREFIX=/MOAB ; \
    make -j"$compile_cores" ; \
    make -j"$compile_cores" install ; \
    cd pymoab ; \
    bash install.sh ; \
    python setup.py install ; \
    fi


COPY requirements.txt requirements.txt
# includes optional dependancies like neutronics_material_maker
RUN pip install -r requirements.txt

# Copy over the source code, examples and tests
COPY paramak paramak/
COPY examples examples/
COPY setup.py setup.py
COPY tests tests/
COPY README.md README.md

# using setup.py instead of pip due to https://github.com/pypa/pip/issues/5816
RUN python setup.py install

WORKDIR examples
