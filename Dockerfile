# Build with the following command
# sudo docker build -t paramak .

# Run with the follwoing command
# sudo docker run -it paramak

# Run with the following command
# docker run -p 8888:8888 paramak

# test with the folowing command
# sudo docker run --rm paramak pytest /tests

FROM continuumio/miniconda3

ENV PYTHONDONTWRITEBYTECODE=true

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get --yes update

RUN apt-get install -y libgl1-mesa-glx

RUN conda install -c conda-forge -c cadquery cadquery=2 && \
    conda clean -afy && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.pyc' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete

# Copy over the source code
COPY paramak paramak/
COPY setup.py setup.py
COPY README.md README.md

RUN apt-get clean

RUN pip install pytest-cov
RUN pip install plotly
RUN pip install scipy
RUN pip install sympy
RUN pip install numpy
RUN pip install tqdm
RUN pip install matplotlib
RUN pip install plasmaboundaries

RUN pip install . --verbose

# Copy over the test folder
COPY tests tests/

WORKDIR paramak/examples

CMD ["/bin/bash"]
