# This dockerfile can be built in a few different ways.

# Building using the latest release version of CadQuery (default).
# Run command from within the base repository directory
# docker build -t ukaea/paramak

# Building using master branch version of CadQuery.
# Run with the following command for terminal access
# docker build -t ukaea/paramak --build-arg cq_version=master .


# This dockerfile can be run in a few different ways.

# Run with the following command for a jupyter notebook interface
# docker run -it ukaea/paramak .

# Run with the following command for a jupyter notebook interface
# docker run -p 8888:8888 ukaea/paramak /bin/bash -c "jupyter notebook --notebook-dir=/examples --ip='*' --port=8888 --no-browser --allow-root"


# test with the folowing command
# docker run --rm ukaea/paramak pytest /tests

FROM continuumio/miniconda3

# By default this Dockerfile builds with the latest release of CadQuery 2
ARG cq_version=release

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get --yes update

RUN apt-get install -y libgl1-mesa-glx libgl1-mesa-dev libglu1-mesa-dev \
                       freeglut3-dev libosmesa6 libosmesa6-dev \
                       libgles2-mesa-dev && \
                       apt-get clean

# Installing CadQuery release
RUN if [ "$cq_version" = "release" ] ; \
    conda install -c conda-forge -c cadquery cadquery=2 ; \
    conda install jupyter -y --quiet ; \
    conda clean -afy

# Installing CadQuery master
# jupyter is installed before cadquery master version to avoid a conflict
RUN if [ "$cq_version" = "master" ] ; \
    conda install jupyter -y --quiet ; \
    conda clean -afy ; \
    conda install -c cadquery -c conda-forge cadquery=master ; \
    conda clean -afy

# Copy over the source code
COPY paramak paramak/
COPY examples examples/
COPY setup.py setup.py
COPY requirements.txt requirements.txt
COPY README.md README.md
COPY tests tests/

# includes optional dependancies like neutronics_material_maker
RUN pip install -r requirements.txt

# using setup.py instead of pip due to https://github.com/pypa/pip/issues/5816
RUN python setup.py install

WORKDIR examples
