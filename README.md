
[![CircleCI](https://circleci.com/gh/ukaea/paramak.svg?style=svg)](https://circleci.com/gh/ukaea/paramak)

[![codecov](https://codecov.io/gh/Shimwell/paramak/branch/master/graph/badge.svg)](https://codecov.io/gh/Shimwell/paramak)




# Paramak

  
<!---R nit: Minor formatting now, but lines should be hard-wrapped at 79
characters for ease of viewing in traditional text editors. -->

The Paramak python package allows rapid production of 3D CAD models of fusion reactors. The original purpose of the Paramak was to provide geometry for parametric neutronics studies as the STP files produced can be automaticallya converted to DAGMC compatable neutronics models.

Features have been added to address particular needs and the software is by no means a finished product. Contributions are welcome. CadQuery functions provide the majority the features, and incorporating additional capabilities is straight forward for developers with Python knowledge.

  
  

## Prerequisites

  

To run the example parametric geometry creation scripts you will need to Python 3 and CadQuery 2.0 or newer installed.

-  [Python 3](https://www.python.org/downloads/)

-  [CadQuery 2.0](https://github.com/CadQuery/cadquery)


  

## Installation

Download the repository using the [download link](https://github.com/Shimwell/freecad_parametric_example/archive/master.zip) or clone the repository using [git](https://git-scm.com/downloads).

  `git clone https://github.com/Shimwell/paramak.git`

Navigate to the paramak repository and within the terminal install the paramak package and the dependencies using pip3.

`pip install .`

Alternatively you can install the paramak with following command.

`python setup.py install`

  

## Features

In general the Paramak takes points and connection information in 2D space (x,z) and performs operations on them to create 3D volumes. The points and connections can be provided by the user or when using parametric_shapes the points and connections are calculated by the software.

Once points and connections between the points are provided the user has options to perform CAD operations (rotate or extrude) to create a 3D volume and boolean operations like cut.

The different families of shapes that can be made with the Paramak are shown in the table below. The CadQuery objects created  can be combined and modified using CadQueries powerful filtering capabilties to create more complex models (e.g. a Tokamak).

|                                                         | Rotate                                                                                                                                 | Extrude                                                                                                                                   |
|---------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Points connected with straight lines                    | <p align="center"><img src="examples/images/rotated_straights.png" height="100"></p> `RotateStraightShape()` | <p align="center"><img src="examples/images/extruded_straights.png" height="100"></p>  `ExtrudeStraightShape()` |
| Points connected with spline curves                     | <p align="center"><img src="examples/images/rotated_splines.png" height="100"></p>  `RotateSplineShape()`      | <p align="center"><img src="examples/images/extruded_splines.png" height="100"></p>  `ExtrudeSplineShape()`       |
| Points connected with a mixture (splines and straights) | <p align="center"><img src="examples/images/rotated_mixed.png" height="100"></p>  `RotateMixedShape()`         | <p align="center"><img src="examples/images/extruded_mixed.png" height="100"></p>  `ExtrudeMixedShape()`          |

## Usage - shape creation
  
There are a collection of Python scripts in the example folder than demonstrate simple shape construction, visualisation creation and reactor construction. However here is a quick example of a RotatedStraightShape 

After importing the class the user then sets the points. Points should be a list of x,z points where the last point is the same as the first point.


`from paramak import RotatedStraightShape`

`my_shape = RotatedStraightShape(points = [(20,0),  (20,100), (100,0), (20,0)])` 


Once these properties have been set then users can write 3D volumes in CAD STP or STL formats

`my_shape.export_stp('example.stp')`

`my_shape.export_stl('example.stl')`


## Creating a plasma

The plasma also inherits from the Shape object so has access to the same methods like export_stp() and export_stl().

The plasma requires additional inputs and a simple plasma shape can be created in the following manner.

`from paramak.parametric_shapes import PlasmaShape`


`my_plasma = PlasmaShape()`

`my_plasma.major_radius =620`

`my_plasma.minor_radius =210`

`my_plasma.triangularity = 0.33`

`my_plasma.elongation = 1.85`

`my_plasma.export_stp('plasma.stp')`


## Usage - reactor creation

A reactor object provides a contain object for all the Shape objects created and allows operations on the whole collection of Shapes such as creation of a bounding box (DGMC graveyard) which is needed for neutronics simulations.

Import the Reactor object

 `from paramak import Reactor`

Initiate a Reactor object with an output folder

 `my_reactor = Reactor()`

Reactor inherites from dictionary so Shapes can be added to it in the same way you would add to a dictionary.

 `my_reactor.add(my_shape)`
 
 `my_reactor.add(my_plasma)`

A 3D rendering of the combined Shapes can be created

`my_reactor.export_3d_image('reactor.png')`

Once all your Shapes have been added reactor methods can be used to create and simulate the neutronics model using additional tools, the currently codes to learn are [DAGMC](https://svalinn.github.io/DAGMC/), [Trelis](https://www.csimsoft.com/trelis) and [OpenMC](https://openmc.readthedocs.io/).


# Example scripts

There are several example scripts in the examples folder the introduction, a good one to start with is

- make_CAD_from_points.py examples of the different families of shapes (extrude, roate) and different connection methods (points connected with splines and or straights or a mixture) with different CAD operations (cut, union).

