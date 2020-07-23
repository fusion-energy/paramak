# build with the following command
# sudo docker build -t paramak .

# Run with the follwoing command
# sudo docker run -it paramak

# We will use Ubuntu for our image
FROM ubuntu:18.04

# Updating Ubuntu packages
RUN apt-get update && yes|apt-get upgrade

# Adding wget and bzip2
RUN apt-get install -y wget bzip2 git

# Anaconda installing
RUN wget https://repo.continuum.io/archive/Anaconda3-2020.02-Linux-x86_64.sh

RUN bash Anaconda3-2020.02-Linux-x86_64.sh -b

RUN rm Anaconda3-2020.02-Linux-x86_64.sh

# Set path to conda
ENV PATH /root/anaconda3/bin:$PATH

# Configuring access to Jupyter
RUN mkdir /opt/notebooks
RUN jupyter notebook --generate-config --allow-root
RUN echo "c.NotebookApp.password = u'sha1:6a3f528eec40:6e896b6e4828f525a6e20e5411cd1c8075d68619'" >> /root/.jupyter/jupyter_notebook_config.py

# CAD query is the main dependancy for the paramak
RUN conda install -c conda-forge -c cadquery cadquery=2

RUN apt-get update
RUN apt-get install -y libgl1-mesa-dev 
RUN apt-get install -y libglu1-mesa-dev
RUN apt-get install -y freeglut3-dev

# pyrender install version 2.0-dev which breaks in docker
RUN pip uninstall pyglet 
# this installs version 1.48 which works in docker
RUN pip install pyglet

RUN git clone https://github.com/ukaea/paramak
RUN cd paramak && python setup.py install

WORKDIR paramak/examples
