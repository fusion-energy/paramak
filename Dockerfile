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
# docker run -it paramak
#
# Run with the following command for a jupyter notebook interface
# docker run -p 8888:8888 paramak /bin/bash -c "jupyter notebook --notebook-dir=/examples --ip='*' --port=8888 --no-browser --allow-root"
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

# Installing CadQuery
RUN echo installing CadQuery version $cq_version && \
    conda install -c conda-forge -c python python=3.8 && \
    conda install -c conda-forge -c cadquery cadquery="$cq_version" && \
    pip install jupyter-cadquery==2.2.0 && \
    conda clean -afy

# installs dependancies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# installs required packages for dependancies
COPY requirements-test.txt requirements-test.txt
RUN pip install -r requirements-test.txt


RUN mkdir /home/paramak
EXPOSE 8888
WORKDIR /home/paramak


FROM ghcr.io/fusion-energy/paramak:dependencies as final

COPY run_tests.sh run_tests.sh
COPY paramak paramak/
COPY examples examples/
COPY setup.py setup.py
COPY tests tests/
COPY README.md README.md

# using setup.py instead of pip due to https://github.com/pypa/pip/issues/5816
RUN python setup.py install

# this helps prevent the kernal failing
RUN echo "#!/bin/bash\n\njupyter lab --notebook-dir=/home/paramak/examples --port=8888 --no-browser --ip=0.0.0.0 --allow-root" >> docker-cmd.sh
CMD bash docker-cmd.sh
