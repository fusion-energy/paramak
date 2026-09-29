"""
This script sets up and runs a neutronics simulation for a tokamak reactor
using OpenMC and Paramak. The geometry combines CSG for the simple bioshield
and CAD based (DAGMC) for the reactor. This example is minimal is terms of the
tokamak geometry, materials, neutron source. It is intended to be used as a
guide for carrying out a simulation that uses both DAGMC with CSG geometry.
This is particularly useful as it avoids using DAGMC for the entire geometry
so we can benefit from DAGMC for the more complex curved surfaces of the
tokamak and benefit from the CSG speed for the simple geometry of the bioshield.
It performs the following steps:
1. Defines the tokamak reactor geometry.
2. Removes the plasma cell as this is not needed by the neutronics simulation.
3. Converts the geometry to DAGMC format.
4. Creates simplified materials.
5. Creates a bioshield complete with floor and ceiling in CSG geometry.
6. Moves the DAGMC geometry so that it is within the CSG bioshield.
7. Adds a cylindrical mesh tally to record the heat deposited in the geometry.
8. Adds a simplified neutron source term
9. Runs the simulation.
10. Saves the tally results to a VTK file.
"""

from pathlib import Path

import numpy as np
import openmc
from cad_to_dagmc import CadToDagmc

import paramak

# change this path to the cross_sections.xml to the path of your cross_sections.xml
openmc.config["cross_sections"] = "/nuclear_data/cross_sections.xml"


# parameters for the CSG parts of the geometry.
bioshield_to_reactor_gap = 500
bioshield_radial_thickness = 200
floor_vertical_thickness = 200
ceiling_vertical_thickness = 200
reactor_to_floor_gap = 100
reactor_to_ceiling_gap = 150

# creates a minimal tokamak reactor using paramak
my_reactor = paramak.tokamak_from_plasma(
    radial_build=[
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 30),  # layer_1
        (paramak.LayerType.SOLID, 50),  # layer_2
        (paramak.LayerType.SOLID, 10),  # layer_3
        (paramak.LayerType.SOLID, 120),  # layer_4
        (paramak.LayerType.SOLID, 20),  # layer_5
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300),  # plasma
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 20),  # layer_3
        (paramak.LayerType.SOLID, 120),  # layer_4
        (paramak.LayerType.SOLID, 10),  # layer_5
    ],
    elongation=2,
    triangularity=0.55,
    rotation_angle=180,
)

# removing the plasma from the CadQuery Assembly as we don't need this in the
# DAGMC mesh for the neutronics simulation.
my_reactor = my_reactor.remove(name="plasma")


# this prints all the names of the parts in the reactor, this is useful for
# knowing the material tags to use in the simulation
print(my_reactor.names())

material_tags = ["layer_1", "layer_2", "layer_3", "layer_4", "layer_5"]
my_model = CadToDagmc()

# 6 material tags as inner and outer layers are one solid there are only 6 solids in model and plasma has been removed
my_model.add_cadquery_object(cadquery_object=my_reactor, material_tags=material_tags)

script_folder = Path(__file__).resolve().parent
h5m_filename = script_folder / "dagmc.h5m"
my_model.export_dagmc_h5m_file(filename=h5m_filename, min_mesh_size=10.0, max_mesh_size=20.0)

# simplified material definitions have been used to keep this example minimal
mat_layer_1 = openmc.Material(name="layer_1")
mat_layer_1.add_element("Cu", 1, "ao")
mat_layer_1.set_density("g/cm3", 7)

mat_layer_2 = openmc.Material(name="layer_2")
mat_layer_2.add_nuclide("W186", 1, "ao")
mat_layer_2.set_density("g/cm3", 0.01)

mat_layer_3 = openmc.Material(name="layer_3")
mat_layer_3.add_nuclide("Fe56", 1, "ao")
mat_layer_3.set_density("g/cm3", 7)

mat_layer_4 = openmc.Material(name="layer_4")
mat_layer_4.add_element("Li", 1, "ao")
mat_layer_4.set_density("g/cm3", 0.5)

mat_layer_5 = openmc.Material(name="layer_5")
mat_layer_5.add_nuclide("Fe56", 1, "ao")
mat_layer_5.set_density("g/cm3", 7)

mat_concrete = openmc.Material(name="concrete")
mat_concrete.add_nuclide("Fe56", 1, "ao")
mat_concrete.set_density("g/cm3", 7)


materials = openmc.Materials([mat_layer_1, mat_layer_2, mat_layer_3, mat_layer_4, mat_layer_5, mat_concrete])

# brings the DAGMC geometry into OpenMC
dag_univ = openmc.DAGMCUniverse(filename=h5m_filename)

# gets the bounding box of the DAGMC geometry, this is used to position the CSG geometry
bbox = dag_univ.bounding_box
dagmc_geometry_offset = abs(bbox[0][2]) + floor_vertical_thickness + reactor_to_floor_gap

dagmc_radius = max(abs(bbox[0][0]), abs(bbox[0][1]), abs(bbox[1][0]), abs(bbox[1][1]))

# we have a 180 degree model and the YPlane acts as a reflective boundary
side_surface = openmc.YPlane(y0=0, boundary_type="reflective", surface_id=1001)
bioshield_inner_surface = openmc.ZCylinder(r=dagmc_radius + bioshield_to_reactor_gap, surface_id=1002)
ceiling_upper_surface = openmc.ZPlane(
    z0=floor_vertical_thickness
    + reactor_to_floor_gap
    + reactor_to_ceiling_gap
    + bbox.width[2]
    + ceiling_vertical_thickness,
    boundary_type="vacuum",
    surface_id=1003,
)
ceiling_lower_surface = openmc.ZPlane(
    z0=floor_vertical_thickness + reactor_to_floor_gap + reactor_to_ceiling_gap + bbox.width[2], surface_id=1004
)
floor_upper_surface = openmc.ZPlane(z0=floor_vertical_thickness, surface_id=1005)
floor_lower_surface = openmc.ZPlane(z0=0, boundary_type="vacuum", surface_id=1006)
bioshield_outer_surface = openmc.ZCylinder(
    r=dagmc_radius + bioshield_to_reactor_gap + bioshield_radial_thickness, boundary_type="vacuum", surface_id=1007
)

# this is a CSG region that is the inner bioshield surface
wedge_region = -bioshield_inner_surface & +floor_upper_surface & -ceiling_lower_surface & +side_surface

# this is a CSG cell that is filled with the DAGMC geometry
dagmc_filled_cell = openmc.Cell(fill=dag_univ, cell_id=1000, region=wedge_region)
# moving the geometry so that it is within the CSG geometry bioshield.
# The CSG geometry starts at z=0, with a floor and then a gap to the reactor.
# We need to move the geometry up so that it is within the bioshield.
dagmc_filled_cell.translation = (0, 0, dagmc_geometry_offset)


bioshield_region = (
    -bioshield_outer_surface & +bioshield_inner_surface & +floor_upper_surface & -ceiling_lower_surface & +side_surface
)
bioshield_cell = openmc.Cell(region=bioshield_region, fill=mat_concrete, cell_id=1001)

floor_region = -floor_upper_surface & +floor_lower_surface & -bioshield_outer_surface & +side_surface
floor_cell = openmc.Cell(region=floor_region, fill=mat_concrete, cell_id=1002)

ceiling_region = -ceiling_upper_surface & +ceiling_lower_surface & -bioshield_outer_surface & +side_surface
ceiling_cell = openmc.Cell(region=ceiling_region, fill=mat_concrete, cell_id=1003)

geometry = openmc.Geometry([dagmc_filled_cell, floor_cell, bioshield_cell, ceiling_cell])

# initializes a new source object
my_source = openmc.IndependentSource()

# the distribution of radius is just a single value
radius = openmc.stats.Discrete([my_reactor.major_radius], [1])

# the distribution of source z values is just a single value
z_values = openmc.stats.Discrete([dagmc_geometry_offset], [1])

# the distribution of source azimuthal angles values is a uniform distribution between 0 and 2 Pi
angle = openmc.stats.Uniform(a=0.0, b=np.pi)

# this makes the ring source using the three distributions and a radius
my_source.space = openmc.stats.CylindricalIndependent(r=radius, phi=angle, z=z_values, origin=(0.0, 0.0, 0.0))

# sets the direction to isotropic
my_source.angle = openmc.stats.Isotropic()

# sets the energy distribution to a Muir distribution neutrons
my_source.energy = openmc.stats.muir(e0=14080000.0, m_rat=5.0, kt=20000.0)


# specifies the simulation computational intensity
settings = openmc.Settings(batches=10, particles=10000, run_mode="fixed source", source=my_source)

# adds a tally to record the heat deposited in a mesh overlaid over entire geometry

mesh = openmc.CylindricalMesh(
    r_grid=np.linspace(0, dagmc_radius + bioshield_to_reactor_gap + bioshield_radial_thickness, 100),
    z_grid=np.linspace(
        0,
        floor_vertical_thickness
        + reactor_to_floor_gap
        + reactor_to_ceiling_gap
        + bbox.width[2]
        + ceiling_vertical_thickness,
        100,
    ),
    origin=(0, 0, 0),
    phi_grid=np.linspace(0, np.pi, 100),
)
mesh_tally = openmc.Tally(name="heating")
mesh_tally.filters = [openmc.MeshFilter(mesh)]
mesh_tally.scores = ["heating"]
tallies = openmc.Tallies([mesh_tally])

# builds the openmc model
my_model = openmc.Model(materials=materials, geometry=geometry, settings=settings, tallies=tallies)

# starts the simulation
output_file = my_model.run()

# loads up the output file from the simulation
statepoint = openmc.StatePoint(output_file)

my_heating_mesh_tally = statepoint.get_tally(name="heating")

mesh.write_data_to_vtk(
    curvilinear=True,
    datasets={"mean": my_heating_mesh_tally.mean.flatten()},
    filename="structured_mesh_tally_results.vtk",
)

print("VTK file saved to structured_mesh_tally_results.vtk")
