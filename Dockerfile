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
# docker build -t ukaea/paramak .
#
# Building to include cadquery master.
# Run command from within the base repository directory
# docker build -t ukaea/paramak --build-arg cq_version=master .
#
# Once build the dockerimage can be run in a few different ways.
#
# Run with the following command for a terminal notebook interface
# docker run -it ukaea/paramak .
#
# Run with the following command for a jupyter notebook interface
# docker run -p 8888:8888 ukaea/paramak /bin/bash -c "jupyter notebook --notebook-dir=/examples --ip='*' --port=8888 --no-browser --allow-root"
#
# Once built, the docker image can be tested with either of the following commands
# docker run --rm ukaea/paramak pytest /tests
# docker run --rm ukaea/paramak  /bin/bash -c "cd .. && bash run_tests.sh"

FROM continuumio/miniconda3:4.9.2 as dependencies

# By default this Dockerfile builds with the latest release of CadQuery 2
ARG cq_version=2.1


ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 \
    PATH=/opt/openmc/bin:/opt/NJOY2016/build:$PATH \
    LD_LIBRARY_PATH=/opt/openmc/lib:$LD_LIBRARY_PATH \
    CC=/usr/bin/mpicc CXX=/usr/bin/mpicxx \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get --allow-releaseinfo-change update
RUN apt-get update -y && \
    apt-get upgrade -y

RUN apt-get install -y libgl1-mesa-glx libgl1-mesa-dev libglu1-mesa-dev \
                       freeglut3-dev libosmesa6 libosmesa6-dev \
                       libgles2-mesa-dev curl imagemagick && \
                       apt-get clean

# Installing CadQuery
RUN echo installing CadQuery version $cq_version && \
    conda install -c conda-forge -c python python=3.8 && \
    conda install -c conda-forge -c cadquery cadquery="$cq_version" && \
    pip install jupyter-cadquery==2.2.0 && \
    conda clean -afy

# Download Cubit
RUN wget -O coreform-cubit-2021.5.deb https://f002.backblazeb2.com/file/cubit-downloads/Coreform-Cubit/Releases/Linux/Coreform-Cubit-2021.5%2B15962_5043ef39-Lin64.deb

# install Cubit dependencies
RUN apt-get install -y libx11-6 
RUN apt-get install -y libxt6 
RUN apt-get install -y libgl1
RUN apt-get install -y libglu1-mesa
RUN apt-get install -y libgl1-mesa-glx
RUN apt-get install -y libxcb-icccm4 
RUN apt-get install -y libxcb-image0 
RUN apt-get install -y libxcb-keysyms1 
RUN apt-get install -y libxcb-render-util0 
RUN apt-get install -y libxkbcommon-x11-0 
RUN apt-get install -y libxcb-randr0 
RUN apt-get install -y libxcb-xinerama0

# Install cubit
RUN dpkg -i coreform-cubit-2021.5.deb

# installs svalinn plugin for cubit
RUN wget https://github.com/svalinn/Cubit-plugin/releases/download/0.2.1/svalinn-plugin_debian-10.10_cubit_2021.5.tgz
RUN tar -xzvf svalinn-plugin_debian-10.10_cubit_2021.5.tgz -C /opt/Coreform-Cubit-2021.5

# writes a non commercial license file
RUN mkdir -p /root/.config/Coreform/licenses
RUN printf 'Fri May 28 2021' >> /root/.config/Coreform/licenses/cubit-learn.lic

# helps to identify Cubit related errrors
ENV CUBIT_VERBOSE=5

# dagmc is needed as it includes the make_watertight command and moab
# conda install -c conda-forge -c moab # now included with dagmc
RUN conda install -c conda-forge dagmc && \
    conda clean -afy

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


RUN mkdir /home/paramak
EXPOSE 8888
WORKDIR /home/paramak


FROM dependencies as final

COPY run_tests.sh run_tests.sh
COPY paramak paramak/
COPY examples examples/
COPY setup.py setup.py
COPY tests tests/
COPY README.md README.md

# using setup.py instead of pip due to https://github.com/pypa/pip/issues/5816
RUN python setup.py install

# this helps prevent the kernal failing
RUN echo "#!/bin/bash\n\njupyter lab --notebook-dir=/home/paramak --port=8888 --no-browser --ip=0.0.0.0 --allow-root" >> /home/paramak/docker-cmd.sh
CMD bash /home/paramak/docker-cmd.sh
