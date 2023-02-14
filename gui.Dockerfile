# This Dockerfile creates a paramak Graphical User Interface that forms part
# of the xsplot.com webapps
#
# There are build args availalbe for specifying the:
# - cq_version
#   The version of CadQuery to use master or 2.1
#   Default is 2.1
#   Options: [master, 2, 2.1]
#
# Example builds:
# Building using the defaults (cq_version master)
# docker build -t paramak_gui .
#
# Building to include cadquery master.
# Run command from within the base repository directory
# docker build -t paramak_gui --build-arg cq_version=master .
#
# Once build the dockerimage can be run in a few different ways.
#
# Run with the following command for a jupyter notebook interface
# docker run -p 8050:8050 paramak_gui


FROM continuumio/miniconda3:4.12.0 as dependencies
#
# By default this Dockerfile builds with the latest release of CadQuery 2
ARG cq_version=master

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
    pip install jupyter-cadquery && \
    conda clean -afy


FROM dependencies as install

RUN mkdir paramak
COPY src paramak/src/
COPY pyproject.toml paramak/pyproject.toml

COPY README.md paramak/README.md
COPY LICENSE.txt paramak/LICENSE.txt

ARG paramak_version=1.0.0
# SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PARAMAK is used to allow versioning
# https://github.com/pypa/setuptools_scm/blob/main/README.rst#usage-from-dockerZ
RUN cd paramak && \
    SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PARAMAK=${paramak_version} pip install .[tests,docs]

ENV PORT 8501

EXPOSE 8501

# solves bug of streamlit not running in container
# https://github.com/streamlit/streamlit/issues/4842
ENTRYPOINT [ "streamlit", "run" ]
CMD [ "paramak/src/paramak/gui/app.py", "--server.headless", "true", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"]
