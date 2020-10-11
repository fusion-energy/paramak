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

# CAD query is the main dependancy for the paramak
RUN conda install -c conda-forge -c cadquery cadquery=2

RUN apt-get update
RUN apt-get install -y libgl1-mesa-dev 
RUN apt-get install -y libglu1-mesa-dev
RUN apt-get install -y freeglut3-dev

# Copy over the source code
COPY paramak paramak/
COPY setup.py setup.py

RUN pip install .

# Copy over the test folder
COPY tests tests/

WORKDIR paramak/examples

CMD ["/bin/bash"]