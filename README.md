
[![N|Python](https://www.python.org/static/community_logos/python-powered-w-100x40.png)](https://www.python.org)
[![CircleCI](https://circleci.com/gh/ukaea/paramak/tree/main.svg?style=svg)](https://circleci.com/gh/ukaea/paramak/tree/main)
[![codecov](https://codecov.io/gh/ukaea/paramak/branch/main/graph/badge.svg)](https://codecov.io/gh/ukaea/paramak)
[![PyPI version](https://badge.fury.io/py/paramak.svg)](https://badge.fury.io/py/paramak)
[![Documentation Status](https://readthedocs.org/projects/paramak/badge/?version=main)](https://paramak.readthedocs.io/en/main/?badge=main)
[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/openmcworkshop/paramak)](https://hub.docker.com/r/openmcworkshop/paramak)


# Paramak

The Paramak python package allows rapid production of 3D CAD models of fusion reactors. The purpose of the Paramak is to provide geometry for parametric studies. It is possible to use the created geometry in engineering and neutronics studies as the STP files produced can be automatically converted to DAGMC compatable neutronics models or meshed and used in finite element analysis codes.

:point_right: [Documentation](https://paramak.readthedocs.io/en/main/)


## Installation

To install the Paramak you need to have [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/), [Cadquery 2](https://cadquery.readthedocs.io/en/latest/installation.html) and [Pip](https://anaconda.org/anaconda/pip). If you have these three dependancies already then you can install the Paramak using Pip:

```
pip install paramak
```

Detailed [installation instructions](https://paramak.readthedocs.io/en/main/#prerequisites) can be found in the User's Guide.

 

## Features

In general the Paramak takes points and connection information in 2D space and performs operations on them to create 3D volumes. The points and connections can be provided by the user or when using parametric_components the points and connections are calculated by the software.

Once points and connections between the points are provided the user has options to perform CAD operations (rotate or extrude on different orientations) to create a 3D volume and boolean operations like cut.

The different families of shapes that can be made with the Paramak are shown in the table below. The CadQuery objects created can be combined and modified (e.g. fillet corners) using CadQueries powerful filtering capabilties to create more complex models (e.g. a Tokamak). The Tokamak images below are coloured based on the shape family that the component is made from. There are also parametric components which provide convenient fusion relevent shapes for common reactor components.

<p align="center">
<img src="https://user-images.githubusercontent.com/8583900/86237379-90136c00-bb93-11ea-80fb-54e2dab74819.gif" width="150" height="200">
<img src="https://user-images.githubusercontent.com/8583900/86237165-2c893e80-bb93-11ea-8fcd-838eb3180c95.png" width="150" height="200">
<img src="https://user-images.githubusercontent.com/8583900/86237161-2b581180-bb93-11ea-99ff-01cc1cec62ef.png" width="150" height="200">
<img src="https://user-images.githubusercontent.com/8583900/86237158-2abf7b00-bb93-11ea-9a78-a987f20359a3.png" width="150" height="200">
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/8583900/88866536-e57a8180-d202-11ea-8e3f-2662973c6f69.gif" width="800" height="300">
</p>


|                                                         | Rotate                                                                                                                                 | Extrude                                                                                                                                   |
|---------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Points connected with straight lines                    | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86246786-767a2080-bba3-11ea-90e7-22d816690caa.png" height="120"></p> `RotateStraightShape()` | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86246776-724e0300-bba3-11ea-91c9-0fd239225206.png" height="120"></p>  `ExtrudeStraightShape()` |
| Points connected with spline curves                     | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86246785-7548f380-bba3-11ea-90b7-03249be41a00.png" height="120"></p>  `RotateSplineShape()`      | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86246774-71b56c80-bba3-11ea-94cb-d2496365ff18.png" height="120"></p>  `ExtrudeSplineShape()`       |
| Points connected with a mixture (splines, straights and circles) | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86258771-17240c80-bbb3-11ea-990f-e87de26b1589.png" height="120"></p>  `RotateMixedShape()`         | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86261239-34a6a580-bbb6-11ea-812c-ac6fa6a8f0e2.png" height="120"></p>  `ExtrudeMixedShape()`          |
| Circular shapes                                         | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86246778-72e69980-bba3-11ea-9b33-d74e2c2d084b.png" height="120"></p> `RotateCircleShape()`      | <p align="center"><img src="https://user-images.githubusercontent.com/8583900/86246768-6feba900-bba3-11ea-81a8-0d77a843b943.png" height="120"></p> `ExtrudeCircleShape()`         |


## Usage - Parametric Shapes
  
There are a collection of Python scripts in the example folder that demonstrate simple shape construction and visualisation. However here is a quick example of a RotateStraightShape.

After importing the class the user then sets the points. By default, points should be a list of (x,z) points. In this case the points are connected with straight lines.

```python
import paramak

my_shape = paramak.RotateStraightShape(points = [(20,0), (20,100), (100,0)])
```

Once these properties have been set users can write 3D volumes in CAD STP or STL formats.

```python
my_shape.export_stp('example.stp')

my_shape.export_stl('example.stl')
```

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/88935761-ff0ae000-d279-11ea-8848-de9b486840d9.png" height="300"></p>


## Usage - Parametric Components

Parametric components are wrapped versions of the eight basic shapes where parameters drive the construction of the shape. There are numerous parametric components for a varity of different reactor components such as center columns, blankets, poloidal field coils. This example shows the construction of a plasma. Users could also construct a plasma by using a RotateSplineShape() combined with coordinates for the points. However a parametric component called Plasma can construct a plasma from more convenient parameters. Parametric components also inherit from the Shape object so they have access to the same methods like export_stp() and export_stl().

```python
import paramak

my_plasma = paramak.Plasma(major_radius=620, minor_radius=210, triangularity=0.33, elongation=1.85)

my_plasma.export_stp('plasma.stp')
```

<p align="center"><img src="https://user-images.githubusercontent.com/56687624/88935871-1ea20880-d27a-11ea-82e1-1afa55ff9ba8.png" height="300"></p>


## Usage - Parametric Reactors

Parametric Reactors are wrapped versions of a combination of parametric shapes and components that comprise a particular reactor design. Some parametric reactors include a ball reactor and
a submersion ball reactor. These allow full reactor models to be constructed by specifying a series of simple parameters. This example shows the construction of a simple ball reactor without the
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



## Usage - Reactor object

A reactor object provides a container object for all Shape objects created, and allows operations to be performed on the whole collection of Shapes.

```python
import paramak
```

Initiate a Reactor object and pass a list of all Shape objects to the shapes_and_components parameter.

```python
my_reactor = paramak.Reactor(shapes_and_components = [my_shape, my_plasma])
```

A html graph of the combined Shapes can be created.

```python
my_reactor.export_html('reactor.html')
```


## Usage - Neutronics model creation

First assign stp_filenames to each of the Shape objects that were created earlier on.

```python
my_shape.stp_filename = 'my_shape.stp'

my_plasma.stp_filename = 'my_plasma.stp'
```

Then assign material_tags to each of the Shape objects.

```python
my_shape.material_tag = 'steel'

my_plasma.material_tag = 'DT_plasma'
```

Note - Tetrahedral meshes can also be assigned to Shape objects

Now add the Shape objects to a freshly created reactor object.

```python
new_reactor = paramak.Reactor(shapes_and_components = [my_shape, my_plasma])
```

The entire reactor can now be exported as step files. This also generates a DAGMC graveyard automatically.

```python
my_reactor.export_stp()
```

A manifest.json file that contains all the step filenames and materials can now be created.

```python
my_reactor.export_neutronics_description()
```

Once you step files and the neutronics description has been exported then [Trelis](https://www.csimsoft.com/trelis) can be used to generate a DAGMC geometry in the usual manner. There is also a convenient script included in task 12 of the UKAEA openmc workshop which can be used in conjunction with the neutronics description json file to automatically create a DAGMC geometry. Download [this script](https://github.com/ukaea/openmc_workshop/blob/master/tasks/task_12/make_faceteted_neutronics_model.py) and place it in the same directory as the manifest.json and step files. Then run the following command from the terminal. You will need to have previously installed the [DAGMC plugin](https://github.com/svalinn/Trelis-plugin) for Trelis.

```python
trelis make_faceteted_neutronics_model.py
```

Alternatively, run this without the GUI in batch mode using:

```python
trelis -batch -nographics make_faceteted_neutronics_model.py
```

This should export a h5m file for use in DAGMC.

Further information on DAGMC neutronics can be found [here](https://svalinn.github.io/DAGMC/) and information on OpenMC can be found [here](https://openmc.readthedocs.io/). The two codes can be used together to simulate neutron transport on the h5m file created. The UKAEA openmc workshop also has two tasks that might be of interest [task 10](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_10) and [task 12](https://github.com/ukaea/openmc_workshop/tree/master/tasks/task_12).


# Example scripts

There are several example scripts in the [examples folder](https://github.com/ukaea/paramak/blob/main/examples/). A good one to start with is [make_CAD_from_points.py](https://github.com/ukaea/paramak/blob/main/examples/example_parametric_shapes/make_CAD_from_points.py) which makes simple examples of the different types of shapes (extrude, rotate) with different connection methods (splines, straight lines and circles).
