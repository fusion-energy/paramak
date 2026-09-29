"""
This script makes a Tokamak model and performs a neutronics simulation
using OpenMC. The model is created using the paramak package and then converted
using cad_to_dagmc package. The model is a 180 degree model so we add a wedge
shaped bounding region with reflective surfaces to make it a full torus.
This example aims to demonstrate how to use cad_to_dagmc to make a surface DAGMC
mesh and an unstructured mesh to use in an unstructured mesh tally. The script
uses minimal materials, tallies, source to keep the example concise.
"""


from pathlib import Path

import openmc
from cad_to_dagmc import CadToDagmc

import paramak

openmc.config["cross_sections"] = "/nuclear_data/cross_sections.xml"

my_reactor = paramak.tokamak(
    radial_build=[
        (paramak.LayerType.GAP, 10),  # inner bore
        (paramak.LayerType.SOLID, 30),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 120),  # breeder
        (paramak.LayerType.SOLID, 10),  # first wall
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300),  # plasma
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 10),  # first wall
        (paramak.LayerType.SOLID, 120),  # breeder
        (paramak.LayerType.SOLID, 10),
    ],
    vertical_build=[
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.SOLID, 100),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.GAP, 50),
        (paramak.LayerType.PLASMA, 700),  # plasma
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 100),
        (paramak.LayerType.SOLID, 15),
    ],
    triangularity=0.55,
    rotation_angle=180,
)

my_reactor = my_reactor.remove(name="plasma")  # removing as we don't need the plasma for this neutronics simulation

my_model = CadToDagmc()
# as inner and outer layers are one solid there are only 6 solids in model
material_tags = ["layer_1", "layer_2", "layer_3", "layer_4", "layer_5"]
my_model.add_cadquery_object(cadquery_object=my_reactor, material_tags=material_tags)
# my_model.export_dagmc_h5m_file(min_mesh_size=10.0, max_mesh_size=20.0, filename="dagmc.h5m")
# my_model.export_unstructured_mesh_file(min_mesh_size=10.0, max_mesh_size=20.0, filename="unstructured_mesh.vtk")


script_folder = Path(__file__).resolve().parent
h5m_filename = script_folder / "dagmc.h5m"


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


materials = openmc.Materials([mat_layer_1, mat_layer_2, mat_layer_3, mat_layer_4, mat_layer_5])


dag_univ = openmc.DAGMCUniverse(filename=h5m_filename)

# gets the bounding box as we need this to create the correctly sized bounding cell.
bbox = dag_univ.bounding_box
dagmc_radius = max(abs(bbox[0][0]), abs(bbox[0][1]), abs(bbox[1][0]), abs(bbox[1][1]))

cylinder_surface = openmc.ZCylinder(r=dagmc_radius, boundary_type="vacuum", surface_id=1000)
lower_z = openmc.ZPlane(bbox[0][2], boundary_type="vacuum", surface_id=1003)
upper_z = openmc.ZPlane(bbox[1][2], boundary_type="vacuum", surface_id=1004)

# this is the surface along the side of the 180 degree model
side_surface = openmc.YPlane(y0=0, boundary_type="reflective", surface_id=1001)

wedge_region = -cylinder_surface & +lower_z & -upper_z & +side_surface

# bounding cell is a wedge shape filled with the DAGMC universe
bounding_cell = openmc.Cell(fill=dag_univ, cell_id=1000, region=wedge_region)

# bound_dag_univ = dag_univ.bounded_universe()
geometry = openmc.Geometry([bounding_cell])

# initializes a new source object
my_source = openmc.IndependentSource()

# the distribution of radius is just a single value
radius = openmc.stats.Discrete([my_reactor.major_radius], [1])

# the distribution of source z values is just a single value
z_values = openmc.stats.Discrete([0], [1])

# the distribution of source azimuthal angles values is a uniform distribution between 0 and 2 Pi
angle = openmc.stats.Uniform(a=0.0, b=2 * 3.14159265359)

# this makes the ring source using the three distributions and a radius
my_source.space = openmc.stats.CylindricalIndependent(r=radius, phi=angle, z=z_values, origin=(0.0, 0.0, 0.0))

# sets the direction to isotropic
my_source.angle = openmc.stats.Isotropic()

# sets the energy distribution to a Muir distribution neutrons
my_source.energy = openmc.stats.muir(e0=14080000.0, m_rat=5.0, kt=20000.0)


# specifies the simulation computational intensity
settings = openmc.Settings(batches=10, particles=10000, run_mode="fixed source", source=my_source)

mesh = openmc.UnstructuredMesh(filename="unstructured_mesh.vtk", library="moab", mesh_id=1)

# adds a tally to record the heat deposited in entire geometry
mesh_tally = openmc.Tally(name="flux")
mesh_tally.filters = [openmc.MeshFilter(mesh)]
mesh_tally.scores = ["flux"]

# groups the two tallies
tallies = openmc.Tallies([mesh_tally])

# builds the openmc model
my_model = openmc.Model(materials=materials, geometry=geometry, settings=settings, tallies=tallies)

# starts the simulation
output_file = my_model.run()

# loads up the output file from the simulation
statepoint = openmc.StatePoint(output_file)

mesh_tally_result = statepoint.get_tally(name="flux")

umesh_from_sp = mesh_tally_result.find_filter(openmc.MeshFilter).mesh

centroids = umesh_from_sp.centroids  # not needed in the next release of openmc
mesh_vols = umesh_from_sp.volumes  # not needed in the next release of openmc

# writes the tally data to a VTK file for visualisation
umesh_from_sp.write_data_to_vtk(
    datasets={"mean": mesh_tally_result.mean.flatten()},
    filename="unstructured_mesh_tally_results.vtk",
)

print("VTK file saved to unstructured_mesh_tally_results.vtk")
