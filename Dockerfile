# This docker image is available on dockerhub and can be downloaded using
# docker pull ukaea/paramak
# However the docker image can also be build locally with these commands

# Build with the following command from within the base repository directory
# sudo docker build -t ukaea/paramak .

# Run with the following command for terminal access
# sudo docker run -it ukaea/paramak

# Run with the following command for jupyter notebook interface
# sudo docker run -p 8888:8888 ukaea/paramak /bin/bash -c "jupyter notebook --notebook-dir=/opt/notebooks --ip='*' --port=8888 --no-browser --allow-root"

# test with the folowing command
# sudo docker run --rm ukaea/paramak pytest /tests

FROM continuumio/miniconda3

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get --yes update

RUN apt-get install -y libgl1-mesa-glx libgl1-mesa-dev libglu1-mesa-dev \
                       freeglut3-dev libosmesa6 libosmesa6-dev \
                       libgles2-mesa-dev && \
                       apt-get clean

RUN conda install -c conda-forge -c cadquery cadquery=2 && \
    conda install jupyter -y --quiet && \
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

