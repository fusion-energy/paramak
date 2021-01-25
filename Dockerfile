# This Dockerfile creates an enviroment with the optional dependancies and the Paramak
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
# Building to include cadquery master, neutronics dependencies and use 8 cores.
# Run command from within the base repository directory
# docker build -t ukaea/paramak --build-arg include_neutronics=true --build-arg compile_cores=8 --build-arg cq_version=master .

# Once build the dockerimage can be run in a few different ways.
#
# Run with the following command for a terminal notebook interface
# docker run -it ukaea/paramak .
#
# Run with the following command for a jupyter notebook interface
# docker run -p 8888:8888 ukaea/paramak /bin/bash -c "jupyter notebook --notebook-dir=/examples --ip='*' --port=8888 --no-browser --allow-root"


# Once built, the docker image can be tested with either of the following commands
# docker run --rm ukaea/paramak pytest /tests
# docker run --rm ukaea/paramak  /bin/bash -c "cd .. && bash run_tests.sh"

FROM continuumio/miniconda3

# By default this Dockerfile builds with the latest release of CadQuery 2
ARG cq_version=2
ARG include_neutronics=false
ARG compile_cores=1

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 \
    PATH=/opt/openmc/bin:/opt/NJOY2016/build:$PATH \
    LD_LIBRARY_PATH=/opt/openmc/lib:$LD_LIBRARY_PATH \
    CC=/usr/bin/mpicc CXX=/usr/bin/mpicxx \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && \
    apt-get upgrade -y

RUN apt-get install -y libgl1-mesa-glx libgl1-mesa-dev libglu1-mesa-dev \
                       freeglut3-dev libosmesa6 libosmesa6-dev \
                       libgles2-mesa-dev curl && \
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

# Clone and install NJOY2016
RUN if [ "$include_neutronics" = "true" ] ; \
    then git clone --single-branch --branch master https://github.com/njoy/NJOY2016.git /opt/NJOY2016 ; \
    cd /opt/NJOY2016 ; \
    mkdir build ; \
    cd build ; \
    cmake -Dstatic=on .. ; \
    make 2>/dev/null ; \
    make install ; \
    fi

# Clone and install Embree
RUN if [ "$include_neutronics" = "true" ] ; \
    then git clone --single-branch --branch master https://github.com/embree/embree.git ; \
    cd embree ; \
    mkdir build ; \
    cd build ; \
    cmake .. -DCMAKE_INSTALL_PREFIX=.. \
             -DEMBREE_ISPC_SUPPORT=OFF ; \
    make -j"$compile_cores" ; \
    make -j"$compile_cores" install ; \
    fi

# Clone and install MOAB
RUN if [ "$include_neutronics" = "true" ] ; \
    then pip install --upgrade numpy cython ; \
    mkdir MOAB ; \
    cd MOAB ; \
    mkdir build ; \
    git clone  --single-branch --branch develop https://bitbucket.org/fathomteam/moab.git ; \
    cd build ; \
    cmake ../moab -DENABLE_HDF5=ON \
                  -DENABLE_NETCDF=ON \
                  -DENABLE_FORTRAN=OFF \
                  -DENABLE_BLASLAPACK=OFF \
                  -DBUILD_SHARED_LIBS=OFF \
                  -DCMAKE_INSTALL_PREFIX=/MOAB ; \
    make -j"$compile_cores" ; \
    make -j"$compile_cores" install ; \
    rm -rf * ; \
    cmake ../moab -DENABLE_HDF5=ON \
                  -DENABLE_PYMOAB=ON \
                  -DENABLE_FORTRAN=OFF \
                  -DBUILD_SHARED_LIBS=ON \
                  -DENABLE_BLASLAPACK=OFF \
                  -DCMAKE_INSTALL_PREFIX=/MOAB ; \
    make -j"$compile_cores" ; \
    make -j"$compile_cores" install ; \
    cd pymoab ; \
    bash install.sh ; \
    python setup.py install ; \
    fi


# Clone and install Double-Down
RUN if [ "$include_neutronics" = "true" ] ; \
    then git clone --single-branch --branch main https://github.com/pshriwise/double-down.git ; \
    cd double-down ; \
    mkdir build ; \
    cd build ; \
    cmake .. -DMOAB_DIR=/MOAB \
             -DCMAKE_INSTALL_PREFIX=.. \
             -DEMBREE_DIR=/embree ; \
    make -j"$compile_cores" ; \
    make -j"$compile_cores" install ; \
    fi

# Clone and install DAGMC
RUN if [ "$include_neutronics" = "true" ] ; \
    then mkdir DAGMC ; \
    cd DAGMC ; \
    git clone --single-branch --branch develop https://github.com/svalinn/DAGMC.git ; \
    mkdir build ; \
    cd build ; \
    cmake ../DAGMC -DBUILD_TALLY=ON \
                   -DMOAB_DIR=/MOAB \
                   -DBUILD_STATIC_EXE=OFF \
                   -DBUILD_STATIC_LIBS=OFF \
                   -DCMAKE_INSTALL_PREFIX=/DAGMC/ ; \
    make -j"$compile_cores" install ; \
    rm -rf /DAGMC/DAGMC /DAGMC/build ; \
    fi

# Clone and install OpenMC with DAGMC
RUN if [ "$include_neutronics" = "true" ] ; \
    then git clone --recurse-submodules https://github.com/openmc-dev/openmc.git /opt/openmc ; \
    cd /opt/openmc ; \
    mkdir build ; \
    cd build ; \
    cmake -Doptimize=on \
          -Ddagmc=ON \
          -DDAGMC_DIR=/DAGMC/ \
          -DHDF5_PREFER_PARALLEL=on ..  ; \
    make -j"$compile_cores" ; \
    make -j"$compile_cores" install ; \
    cd ..  ; \
    pip install -e .[test] ; \
    /opt/openmc/tools/ci/download-xs.sh ; \
    fi

ENV OPENMC_CROSS_SECTIONS=/root/nndc_hdf5/cross_sections.xml

RUN if [ "$include_neutronics" = "true" ] ; \
    then pip install vtk ; \
    pip install parametric_plasma_source ; \
    pip install neutronics_material_maker ; \
    fi

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# @pullrequest reviewer, we would like to make the copy optional but don't know
# how. Then we can build a dependency image for use in circle ci.
# Copy over the source code, examples and tests
COPY run_tests.sh run_tests.sh
COPY paramak paramak/
COPY examples examples/
COPY setup.py setup.py
COPY tests tests/
COPY README.md README.md

# using setup.py instead of pip due to https://github.com/pypa/pip/issues/5816
RUN python setup.py install

WORKDIR examples
