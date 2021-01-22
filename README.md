
[![N|Python](https://www.python.org/static/community_logos/python-powered-w-100x40.png)](https://www.python.org)
[![CircleCI](https://circleci.com/gh/ukaea/paramak/tree/main.svg?style=svg)](https://circleci.com/gh/ukaea/paramak/tree/main)
[![codecov](https://codecov.io/gh/ukaea/paramak/branch/main/graph/badge.svg)](https://codecov.io/gh/ukaea/paramak)
[![PyPI](https://img.shields.io/pypi/v/paramak?color=brightgreen&label=pypi&logo=grebrightgreenen&logoColor=green)](https://pypi.org/project/paramak/)
[![Documentation Status](https://readthedocs.org/projects/paramak/badge/?version=main)](https://paramak.readthedocs.io/en/main/?badge=main)
[![dockerhub-publish-stable](https://github.com/ukaea/paramak/workflows/dockerhub-publish-stable/badge.svg)](https://github.com/ukaea/paramak/actions?query=workflow%3Adockerhub-publish-stable)
[![DOI](https://zenodo.org/badge/269635577.svg)](https://zenodo.org/badge/latestdoi/269635577)

# Paramak

The Paramak python package allows rapid production of 3D CAD models of fusion
reactors. The purpose of the Paramak is to provide geometry for parametric
studies. It is possible to use the created geometry in engineering and
neutronics studies as the STP or STL files produced can be automatically
converted to DAGMC compatible neutronics models or meshed and used in
finite element analysis codes.

:point_right: [Documentation](https://paramak.readthedocs.io/en/main/)

:point_right: [Video presentation](https://www.youtube.com/embed/fXboew3U7rw)

:point_right: [Publication](https://f1000research.com/articles/10-27/v1)

# History

The package was originally conceived by Jonathan Shimwell and based on the
[FreeCAD Python API](https://wiki.freecadweb.org/FreeCAD_API). When 
[CadQuery 2](https://github.com/CadQuery/cadquery) was released the project
started to migrate the code base. Shortly after this migration the project
became open-source and has flourished ever since. The project has grown largely
due to two contributors in particular (John Billingsley and
Remi Delaporte-Mathurin) and others have also helped, you can see all those who
have helped the development in the 
[Authors.md](https://github.com/ukaea/paramak/blob/main/AUTHORS.md) and in the 
[GitHub contributions](https://github.com/ukaea/paramak/graphs/contributors).
The code has been professionally reviewed by [PullRequest.com](https://www.pullrequest.com/) who
produced a [report](https://github.com/ukaea/paramak/files/5704872/PULLREQUEST.Paramak.Project.Review.pdf) and inline [suggestions](https://github.com/ukaea/paramak/pull/639).

## Citing

If you use the Paramak in your research, please consider giving proper
attribution by citing the our [Publication](https://f1000research.com/articles/10-27/v1):

- J. Shimwell, J. Billingsley and R. Delaporte-Mathurin et al. The Paramak: 
  Automated Parametric Geometry Construction for Fusion Reactor Designs.
  F1000Research, vol. 10, Jan. 2021, p. 27. DOI.org (Crossref),
  doi:10.12688/f1000research.28224.1.

    <details>
        <summary>BibTex</summary>
        <pre><code class="language-html">
    @article{paramak,
        title = {The {Paramak}: automated parametric geometry construction for fusion reactor designs.},
        volume = {10},
        issn = {2046-1402},
        shorttitle = {The {Paramak}},
        url = {https://f1000research.com/articles/10-27/v1},
        doi = {10.12688/f1000research.28224.1},
        language = {en},
        urldate = {2021-01-22},
        journal = {F1000Research},
        author = {Shimwell, Jonathan and Billingsley, John and Delaporte-Mathurin, Rémi and Morbey, Declan and Bluteau, Matthew and Shriwise, Patrick and Davis, Andrew},
        month = jan,
        year = {2021},
        pages = {27},
    }
        </code></pre>
    </details>


## System Installation

To install the Paramak you need to have 
[Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/), 
[Cadquery 2](https://cadquery.readthedocs.io/en/latest/installation.html) and 
[Pip](https://anaconda.org/anaconda/pip). If you have these three dependencies 
already then you can install the Paramak using Pip:

```
pip install paramak
```

Detailed installation 
[instructions](https://paramak.readthedocs.io/en/main/#prerequisites)
can be found in the User's Guide.


## Docker Image Installation

Another option is to use the Docker image which contains all the required
dependencies.

1. Install Docker CE for
[Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/),
[Mac OS](https://store.docker.com/editions/community/docker-ce-desktop-mac), or
[Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows),
including the part where you enable docker use as a non-root user.

2. Pull the docker image from the store by typing the following command in a
terminal window, or Windows users might prefer PowerShell.

    ```docker pull ukaea/paramak```

3. Now that you have the docker image you can enable graphics linking between
your os and docker, and then run the docker container by typing the following
commands in a terminal window.

    ```sudo docker run -p 8888:8888 ukaea/paramak /bin/bash -c "jupyter notebook --notebook-dir=/opt/notebooks --ip='*' --port=8888 --no-browser" --allow-root```

4. A URL should be displayed in the terminal and can now be opened in the
internet browser of your choice. This will load up the examples folder where
you can view the 3D objects created. Alternatively the Docker imag can be run
in terminal mode ```docker run -it ukaea/paramak```

Alternatively the Docker image can be run in terminal mode .
```docker run -it ukaea/paramak```

You may also want to make use of the
[--volume](https://docs.docker.com/storage/volumes/)
flag when running Docker so that you can retrieve files from the Docker
enviroment to your base system.

Docker can also be used to run the tests using the command
```docker run --rm ukaea/paramak pytest tests```

## Features

In general the Paramak takes points and connection information in 2D space (XY)
and performs operations on them to create 3D volumes. The points and
connections can be provided by the user or when using parametric components
the points and connections are calculated by the software.

Once points and connections between the points are provided the user has
options to perform CAD operations (rotate or extrude on different orientations)
to create a 3D volume and boolean operations like cut, union and intersection.

The different families of shapes that can be made with the Paramak are shown in
the table below. The CadQuery objects created can be combined and modified
(e.g. fillet corners) using CadQueries powerful filtering capabilties to create
more complex models (e.g. a Tokamak). The Tokamak images below are coloured
based on the shape family that the component is made from. There are also
parametric components which provide convenient fusion relevant shapes for
common reactor components.
[](https://user-images.githubusercontent.com/8583900/94205189-a68f4200-feba-11ea-8c2d-789d1617ceea.png)


## Selection Of Parametric Reactors

<p align="center">
<img src="https://user-images.githubusercontent.com/8583900/99137324-fddfa200-2621-11eb-9063-f5f7f60ddd8d.png" width="713">

</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/8583900/88866536-e57a8180-d202-11ea-8e3f-2662973c6f69.gif" width="600">
<img src="https://user-images.githubusercontent.com/8583900/86237379-90136c00-bb93-11ea-80fb-54e2dab74819.gif" width="150">
</p>

## Selection Of Parametric Components

<p align="center">
<img src="https://user-images.githubusercontent.com/8583900/98823600-387eea00-242a-11eb-9fe3-df65aaa3dd21.png" width="500">
</p>


## Selection Of Parametric Shapes

|                                                         | Rotate                                                                                                                                 | Extrude                                                                                                                                   | Sweep                                                                                                                                  |
|---------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Points connected with straight lines                    | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86246786-767a2080-bba3-11ea-90e7-22d816690caa.png" height="120"></p> `RotateStraightShape()` | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86246776-724e0300-bba3-11ea-91c9-0fd239225206.png" height="120"></p>  `ExtrudeStraightShape()` | <p align="center"><img src="https://user-images.githubusercontent.com/56687624/98713447-8c80c480-237f-11eb-8615-c090e93138f6.png" height="120"></p> `SweepStraightShape()` |
| Points connected with spline curves                     | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86246785-7548f380-bba3-11ea-90b7-03249be41a00.png" height="120"></p>  `RotateSplineShape()`      | <p align="center"><img src="https://user-images.githubusercontent.com/56687624/98713431-87bc1080-237f-11eb-9075-01bca99b7018.png" height="120"></p>  `ExtrudeSplineShape()`       | <p align="center"><img src="https://user-images.githubusercontent.com/56687624/98713443-8b4f9780-237f-11eb-83bb-38ca7f222073.png" height="120"></p> `SweepSplineShape()` |
| Points connected with a mixture (splines, straights and circles) | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86258771-17240c80-bbb3-11ea-990f-e87de26b1589.png" height="120"></p>  `RotateMixedShape()`         | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86261239-34a6a580-bbb6-11ea-812c-ac6fa6a8f0e2.png" height="120"></p>  `ExtrudeMixedShape()`          | <p align="center"><img src="https://user-images.githubusercontent.com/56687624/98713440-8a1e6a80-237f-11eb-9eed-12b9d7731090.png" height="120"></p> `SweepMixedShape()` |
| Circular shapes                                         | <p align="center"><img src="https://user-images.githubusercontent.com/56687624/98713427-868ae380-237f-11eb-87af-cf6b5fe032b2.png" height="120"></p> `RotateCircleShape()`      | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86246768-6feba900-bba3-11ea-81a8-0d77a843b943.png" height="120"></p> `ExtrudeCircleShape()`         | <p align="center"><img src="https://user-images.githubusercontent.com/56687624/98713436-88ed3d80-237f-11eb-99cd-27dcb4f313b1.png" height="120"></p> `SweepCircleShape()` |

# Example Scripts

There are several example scripts for making shapes, components, reactors and
neutronics models in the 
[examples folder](https://github.com/ukaea/paramak/blob/main/examples/).
The following examples are minimal examples to demonstrate some basic usage.


## Usage - Parametric Shapes
  
There are a collection of Python scripts in the example folder that demonstrate
simple shape construction and visualisation. However here is a quick example of
a RotateStraightShape.

After importing the class the user then sets the points, by default, points
should be a list of (x,z) coordinates. In this case the points are connected
with straight lines.

```python
import paramak

my_shape = paramak.RotateStraightShape(points = [(20,0), (20,100), (100,0)])
```

Once these properties have been set users can write 3D volumes in CAD STP or
STL formats.

```python
my_shape.export_stp('example.stp')

my_shape.export_stl('example.stl')
```

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/88935761-ff0ae000-d279-11ea-8848-de9b486840d9.png" height="300"></p>


## Usage - Parametric Components

Parametric components are wrapped versions of the eight basic shapes where
parameters drive the construction of the shape. There are numerous parametric
components for a variety of different reactor components such as center columns,
blankets, poloidal field coils. This example shows the construction of a
plasma. Users could also construct a plasma by using a RotateSplineShape()
combined with coordinates for the points. However a parametric component called
Plasma can construct a plasma from more convenient parameters. Parametric
components also inherit from the Shape object so they have access to the same
methods like export_stp() and export_stl().

```python
import paramak

my_plasma = paramak.Plasma(major_radius=620, minor_radius=210, triangularity=0.33, elongation=1.85)

my_plasma.export_stp('plasma.stp')
```

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/88935871-1ea20880-d27a-11ea-82e1-1afa55ff9ba8.png" height="300"></p>


## Usage - Parametric Reactors

Parametric Reactors are wrapped versions of a combination of parametric shapes
and components that comprise a particular reactor design. Some parametric
reactors include a ball reactor and a submersion ball reactor. These allow full
reactor models to be constructed by specifying a series of simple parameters.
This example shows the construction of a simple ball reactor without the
optional outer pf and tf coils.

```python
import paramak

my_reactor = paramak.BallReactor(
    inner_bore_radial_thickness = 50,
    inboard_tf_leg_radial_thickness = 50,
    center_column_shield_radial_thickness= 50,
    divertor_radial_thickness = 100,
    inner_plasma_gap_radial_thickness = 50,
    plasma_radial_thickness = 200,
    outer_plasma_gap_radial_thickness = 50,
    firstwall_radial_thickness = 50,
    blanket_radial_thickness = 100,
    blanket_rear_wall_radial_thickness = 50,
    elongation = 2,
    triangularity = 0.55,
    number_of_tf_coils = 16,
    rotation_angle = 180

my_reactor.name = 'BallReactor'

my_reactor.export_stp()
```

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/89203299-465fdc00-d5ac-11ea-8663-a5b7eecfb584.png" height="300"></p>


## Usage - Reactor Object

A reactor object provides a container object for all Shape objects created, and
allows operations to be performed on the whole collection of Shapes.

```python
import paramak
```

Initiate a Reactor object and pass a list of all Shape objects to the
shapes_and_components parameter.

```python
my_reactor = paramak.Reactor(shapes_and_components = [my_shape, my_plasma])
```

A html graph of the combined Shapes can be created.

```python
my_reactor.export_html('reactor.html')
```

## Usage - Neutronics Model Creation

It is possible to convert a parametric Reactor model into a neutronics model.

To install additional python packages needed to run neutronics with a
modified pip install

```bash
pip install .[neutronics]
```

More information is avaialbe in the
[documentation](https://paramak.readthedocs.io/en/latest/paramak.parametric_neutronics.html#parametric-neutronics).

There are several examples in the [examples folder](https://github.com/ukaea/paramak/blob/main/examples/https://github.com/ukaea/paramak/tree/main/examples/example_neutronics_simulations).

To create the neutronics model you will need
[Trelis](https://www.coreform.com/products/trelis/) and the DAGMC plugin
installed [DAGMC plugin](https://github.com/svalinn/Trelis-plugin).

Further information on DAGMC neutronics can be found
[here](https://svalinn.github.io/DAGMC/) and information on OpenMC can be found
[here](https://openmc.readthedocs.io/). The two codes can be used together to
simulate neutron transport on the h5m file created. The
[UKAEA openmc workshop](https://github.com/ukaea/openmc_workshop) also has some
Paramak with DAGMC and OpenMC based tasks that might be of interest.
