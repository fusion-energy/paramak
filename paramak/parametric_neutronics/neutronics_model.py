
import json
import math
import os
import warnings
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

try:
    import openmc
except BaseException:
    warnings.warn('OpenMC not found, NeutronicsModelFromReactor.simulate \
            method not available', UserWarning)

try:
    import neutronics_material_maker as nmm
except BaseException:
    warnings.warn("neutronics_material_maker not found, \
            NeutronicsModelFromReactor.materials can't accept strings or \
            neutronics_material_maker objects", UserWarning)


class NeutronicsModel():
    """Creates a neuronics model of the provided shape geometry with assigned
    materials, source and neutronics tallies. There are three methods
    available for producing the imprinted and merged h5m geometry (PyMoab, PPP
    or Trelis) and one method of producing non imprinted and non merged
    geometry (PyMoab). make_watertight is also used to seal the DAGMC geoemtry.
    If using the Trelis option you must have the
    make_faceteted_neutronics_model.py in the same directory as your Python
    script. Further details on imprinting and merging are available on the
    DAGMC homepage
    https://svalinn.github.io/DAGMC/usersguide/trelis_basics.html
    The Parallel-PreProcessor is an open-source tool available
    https://github.com/ukaea/parallel-preprocessor and can be used in
    conjunction with the OCC_faceter
    (https://github.com/makeclean/occ_faceter) to create imprinted and
    merged geometry while Trelis (also known as Cubit) is available from
    the CoreForm website https://www.coreform.com/

    Arguments:
        geometry (paramak.Shape, paramak.Rector): The geometry to convert to a
            neutronics model. e.g. geometry=paramak.RotateMixedShape() or
            reactor=paramak.BallReactor() .
        cell_tallies (list of strings): the cell based tallies to calculate,
            options include TBR, heating and flux
        materials (dict): Where the dictionary keys are the material tag
            and the dictionary values are either a string, openmc.Material,
            neutronics-material-maker.Material or
            neutronics-material-maker.MultiMaterial. All components within the
            geometry object must be accounted for. Material tags required
            for a Reactor or Shape can be obtained with .material_tags.
        mesh_tally_2D (list of strings): the mesh based tallies to calculate,
            options include tritium_production, heating and flux
        fusion_power (float): the power in watts emitted by the fusion
            reaction recalling that each DT fusion reaction emitts 17.6 MeV or
            2.819831e-12 Joules
        simulation_batches (int): the number of batch to simulate.
        simulation_particles_per_batch: (int): particles per batch.
        source (openmc.Source()): the particle source to use during the
            OpenMC simulation.
        merge_tolerance (float): the tolerance to use when merging surfaces.
            Defaults to 1e-4.
        faceting_tolerance (float): the tolerance to use when faceting surfaces.
            Defaults to 1e-1.
        mesh_2D_resolution (tuple of ints): The mesh resolution in the height
            and width directions. The larger the resolution the finer the mesh
            and more computational intensity is required to converge each mesh
            element.
    """

    def __init__(
        self,
        geometry,
        source,
        materials,
        cell_tallies=None,
        mesh_tally_2D=None,
        mesh_tally_3D=None,
        simulation_batches=100,
        simulation_particles_per_batch=10000,
        max_lost_particles=10,
        faceting_tolerance=1e-1,
        merge_tolerance=1e-4,
        mesh_2D_resolution=(400, 400),
        mesh_3D_resolution=(100, 100, 100),
        fusion_power=1e9  # convert from watts to activity source_activity
    ):

        self.materials = materials
        self.geometry = geometry
        self.source = source
        self.cell_tallies = cell_tallies
        self.mesh_tally_2D = mesh_tally_2D
        self.mesh_tally_3D = mesh_tally_3D
        self.simulation_batches = simulation_batches
        self.simulation_particles_per_batch = simulation_particles_per_batch
        self.max_lost_particles = max_lost_particles
        self.faceting_tolerance = faceting_tolerance
        self.merge_tolerance = merge_tolerance
        self.mesh_2D_resolution = mesh_2D_resolution
        self.mesh_3D_resolution = mesh_3D_resolution
        self.model = None
        self.fusion_power = fusion_power

    @property
    def faceting_tolerance(self):
        return self._faceting_tolerance

    @faceting_tolerance.setter
    def faceting_tolerance(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError(
                "NeutronicsModelFromReactor.faceting_tolerance should be a\
                number (floats or ints are accepted)")
        if value < 0:
            raise ValueError(
                "NeutronicsModelFromReactor.faceting_tolerance should be a\
                positive number")
        self._faceting_tolerance = value

    @property
    def merge_tolerance(self):
        return self._merge_tolerance

    @merge_tolerance.setter
    def merge_tolerance(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError(
                "NeutronicsModelFromReactor.merge_tolerance should be a\
                number (floats or ints are accepted)")
        if value < 0:
            raise ValueError(
                "NeutronicsModelFromReactor.merge_tolerance should be a\
                positive number")
        self._merge_tolerance = value

    @property
    def cell_tallies(self):
        return self._cell_tallies

    @cell_tallies.setter
    def cell_tallies(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise ValueError(
                    "NeutronicsModelFromReactor.cell_tallies should be a\
                    list")
            output_options = ['TBR', 'heating', 'flux', 'fast flux', 'dose']
            for entry in value:
                if entry not in output_options:
                    raise ValueError(
                        "NeutronicsModelFromReactor.cell_tallies argument",
                        entry,
                        "not allowed, the following options are supported",
                        output_options)
        self._cell_tallies = value

    @property
    def mesh_tally_2D(self):
        return self._mesh_tally_2D

    @mesh_tally_2D.setter
    def mesh_tally_2D(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise TypeError(
                    "NeutronicsModelFromReactor.mesh_tally_2D should be a\
                    list")
            output_options = ['tritium_production', 'heating', 'flux',
                              'fast flux', 'dose']
            for entry in value:
                if entry not in output_options:
                    raise ValueError(
                        "NeutronicsModelFromReactor.mesh_tally_2D argument",
                        entry,
                        "not allowed, the following options are supported",
                        output_options)
        self._mesh_tally_2D = value

    @property
    def mesh_tally_3D(self):
        return self._mesh_tally_3D

    @mesh_tally_3D.setter
    def mesh_tally_3D(self, value):
        if value is not None:
            if not isinstance(value, list):
                raise TypeError(
                    "NeutronicsModelFromReactor.mesh_tally_3D should be a\
                    list")
            output_options = ['tritium_production', 'heating', 'flux',
                              'fast flux', 'dose']
            for entry in value:
                if entry not in output_options:
                    raise ValueError(
                        "NeutronicsModelFromReactor.mesh_tally_3D argument",
                        entry,
                        "not allowed, the following options are supported",
                        output_options)
        self._mesh_tally_3D = value

    @property
    def materials(self):
        return self._materials

    @materials.setter
    def materials(self, value):
        if not isinstance(value, dict):
            raise ValueError("NeutronicsModelFromReactor.materials should be a\
                dictionary")
        self._materials = value

    @property
    def simulation_batches(self):
        return self._simulation_batches

    @simulation_batches.setter
    def simulation_batches(self, value):
        if isinstance(value, float):
            value = int(value)
        if not isinstance(value, int):
            raise ValueError(
                "NeutronicsModelFromReactor.simulation_batches should be an int")
        if value < 2:
            raise ValueError(
                "The minimum of setting for simulation_batches is 2"
            )
        self._simulation_batches = value

    @property
    def simulation_particles_per_batch(self):
        return self._simulation_particles_per_batch

    @simulation_particles_per_batch.setter
    def simulation_particles_per_batch(self, value):
        if isinstance(value, float):
            value = int(value)
        if not isinstance(value, int):
            raise ValueError(
                "NeutronicsModelFromReactor.simulation_particles_per_batch\
                    should be an int")
        self._simulation_particles_per_batch = value

    def create_material(self, material_tag, material_entry):
        if isinstance(material_entry, str):
            openmc_material = nmm.Material(
                material_entry,
                material_tag=material_tag).openmc_material
        elif isinstance(material_entry, openmc.Material):
            # sets the material name in the event that it had not been set
            material_entry.name = material_tag
            openmc_material = material_entry
        elif isinstance(material_entry, (nmm.Material, nmm.MultiMaterial)):
            # sets the material tag in the event that it had not been set
            material_entry.material_tag = material_tag
            openmc_material = material_entry.openmc_material
        else:
            raise ValueError("materials must be either a str, \
                openmc.Material, nmm.MultiMaterial or nmm.Material object \
                not a ", type(material_entry), material_entry)
        return openmc_material

    def create_materials(self):
        # # checks all the required materials are present
        # for reactor_material in self.geometry.material_tags:
        #     if reactor_material not in self.materials.keys():
        #         raise ValueError(
        #             "material included by the reactor model has not \
        #             been added", reactor_material)

        # # checks that no extra materials we added
        # for reactor_material in self.materials.keys():
        #     if reactor_material not in self.geometry.material_tags:
        #         raise ValueError(
        #             "material has been added that is not needed for this \
        #             reactor model", reactor_material)

        openmc_materials = {}
        for material_tag, material_entry in self.materials.items():
            openmc_material = self.create_material(
                material_tag, material_entry)
            openmc_materials[material_tag] = openmc_material

        self.openmc_materials = openmc_materials

        self.mats = openmc.Materials(list(self.openmc_materials.values()))

        return self.mats

    def create_neutronics_geometry(self, method=None):
        """Produces a dagmc.h5m neutronics file compatable with DAGMC
        simulations.

        Arguments:
            method: (str): The method to use when making the imprinted and
                merged geometry. Options are "ppp", "trelis", "pymoab".
                Defaults to None.
        """

        os.system('rm dagmc_not_watertight.h5m')
        os.system('rm dagmc.h5m')

        if method not in ['ppp', 'trelis', 'pymoab']:
            raise ValueError(
                "the method using in create_neutronics_geometry \
                should be either ppp or trelis not", method)

        if method == 'ppp':

            self.geometry.export_stp()
            self.geometry.export_neutronics_description()
            # as the installer connects to the system python not the conda
            # python this full path is needed for now
            if os.system(
                    '/usr/bin/python3 /usr/bin/geomPipeline.py manifest.json') != 0:
                raise ValueError(
                    "geomPipeline.py failed, check PPP is installed")

            # TODO allow tolerance to be user controlled
            if os.system(
                    'occ_faceter manifest_processed/manifest_processed.brep') != 0:
                raise ValueError(
                    "occ_faceter failed, check occ_faceter is install and the \
                    occ_faceter/bin folder is in the path directory")
            self._make_watertight()

        elif method == 'trelis':
            self.geometry.export_stp()
            self.geometry.export_neutronics_description()

            if not Path("make_faceteted_neutronics_model.py").is_file():
                raise ValueError("The make_faceteted_neutronics_model.py was \
                    not found in the directory")
            os.system("trelis -batch -nographics make_faceteted_neutronics_model.py \"faceting_tolerance='" +
                      str(self.faceting_tolerance) + "'\" \"merge_tolerance='" + str(self.merge_tolerance) + "'\"")

            if not Path("dagmc_not_watertight.h5m").is_file():
                raise ValueError("The dagmc_not_watertight.h5m was not found \
                    in the directory, the Trelis stage has failed")
            self._make_watertight()

        elif method == 'pymoab':

            self.geometry.export_h5m(
                filename='dagmc.h5m',
                tolerance=self.faceting_tolerance
            )

        print('neutronics model saved as dagmc.h5m')

    def _make_watertight(self):
        """Runs the DAGMC make_watertight script thatt seals the facetets of
        the geometry"""

        if not Path("dagmc_not_watertight.h5m").is_file():
            raise ValueError(
                "Failed to create a dagmc_not_watertight.h5m file")

        if os.system(
                "make_watertight dagmc_not_watertight.h5m -o dagmc.h5m") != 0:
            raise ValueError(
                "make_watertight failed, check DAGMC is install and the \
                    DAGMC/bin folder is in the path directory")

    def create_neutronics_model(self, method=None):
        """Uses OpenMC python API to make a neutronics model, including tallies
        (cell_tallies and mesh_tally_2D), simulation settings (batches,
        particles per batch).

        Arguments:
            method: (str): The method to use when making the imprinted and
                merged geometry. Options are "ppp", "trelis", "pymoab".
                Defaults to None.
        """

        self.create_materials()

        self.create_neutronics_geometry(method=method)

        # this is the underlying geometry container that is filled with the
        # faceteted DGAMC CAD model
        self.universe = openmc.Universe()
        geom = openmc.Geometry(self.universe)

        # settings for the number of neutrons to simulate
        settings = openmc.Settings()
        settings.batches = self.simulation_batches
        settings.inactive = 0
        settings.particles = self.simulation_particles_per_batch
        settings.run_mode = "fixed source"
        settings.dagmc = True
        settings.photon_transport = True
        settings.source = self.source
        settings.max_lost_particles = self.max_lost_particles

        # details about what neutrons interactions to keep track of (tally)
        tallies = openmc.Tallies()

        if self.mesh_tally_3D is not None:
            mesh_xyz = openmc.RegularMesh()
            mesh_xyz.dimension = self.mesh_3D_resolution
            mesh_xyz.lower_left = [
                -self.geometry.largest_dimension,
                -self.geometry.largest_dimension,
                -self.geometry.largest_dimension
            ]

            mesh_xyz.upper_right = [
                self.geometry.largest_dimension,
                self.geometry.largest_dimension,
                self.geometry.largest_dimension
            ]

            for standard_tally in self.mesh_tally_3D:
                if standard_tally == 'tritium_production':
                    score = '(n,Xt)'  # where X is a wild card
                    prefix = 'tritium_production'
                else:
                    score = standard_tally
                    prefix = standard_tally

                mesh_filter = openmc.MeshFilter(mesh_xyz)
                tally = openmc.Tally(name=prefix + '_on_3D_mesh')
                tally.filters = [mesh_filter]
                tally.scores = [score]
                tallies.append(tally)

        if self.mesh_tally_2D is not None:

            # Create mesh which will be used for tally
            mesh_xz = openmc.RegularMesh()

            mesh_xz.dimension = [
                self.mesh_2D_resolution[1],
                1,
                self.mesh_2D_resolution[0]
            ]

            mesh_xz.lower_left = [
                -self.geometry.largest_dimension,
                -1,
                -self.geometry.largest_dimension
            ]

            mesh_xz.upper_right = [
                self.geometry.largest_dimension,
                1,
                self.geometry.largest_dimension
            ]

            mesh_xy = openmc.RegularMesh()
            mesh_xy.dimension = [
                self.mesh_2D_resolution[1],
                self.mesh_2D_resolution[0],
                1
            ]

            mesh_xy.lower_left = [
                -self.geometry.largest_dimension,
                -self.geometry.largest_dimension,
                -1
            ]

            mesh_xy.upper_right = [
                self.geometry.largest_dimension,
                self.geometry.largest_dimension,
                1
            ]

            mesh_yz = openmc.RegularMesh()
            mesh_yz.dimension = [
                1,
                self.mesh_2D_resolution[1],
                self.mesh_2D_resolution[0]
            ]

            mesh_yz.lower_left = [
                -1,
                -self.geometry.largest_dimension,
                -self.geometry.largest_dimension
            ]

            mesh_yz.upper_right = [
                1,
                self.geometry.largest_dimension,
                self.geometry.largest_dimension
            ]

            for standard_tally in self.mesh_tally_2D:
                if standard_tally == 'tritium_production':
                    score = '(n,Xt)'  # where X is a wild card
                    prefix = 'tritium_production'
                else:
                    score = standard_tally
                    prefix = standard_tally

                for mesh_filter, plane in zip(
                        [mesh_xz, mesh_xy, mesh_yz], ['xz', 'xy', 'yz']):
                    mesh_filter = openmc.MeshFilter(mesh_filter)
                    tally = openmc.Tally(name=prefix + '_on_2D_mesh_' + plane)
                    tally.filters = [mesh_filter]
                    tally.scores = [score]
                    tallies.append(tally)

        if self.cell_tallies is not None:

            for standard_tally in self.cell_tallies:
                if standard_tally == 'TBR':
                    score = '(n,Xt)'  # where X is a wild card
                    sufix = 'TBR'
                else:
                    score = standard_tally
                    sufix = standard_tally

                for key, value in self.openmc_materials.items():
                    if key != 'DT_plasma':
                        material_filter = openmc.MaterialFilter(value)
                        tally = openmc.Tally(name=key + "_" + sufix)
                        tally.filters = [material_filter]
                        tally.scores = [score]
                        tallies.append(tally)

        # make the model from gemonetry, materials, settings and tallies
        self.model = openmc.model.Model(geom, self.mats, settings, tallies)

    def simulate(self, verbose=True, method=None):
        """Run the OpenMC simulation. Deletes exisiting simulation output
        (summary.h5) if files exists.

        Arguments:
            verbose (Boolean, optional): Print the output from OpenMC (true)
                to the terminal and don't print the OpenMC output (false).
                Defaults to True.
            method (str): The method to use when making the imprinted and
                merged geometry. Options are "ppp", "trelis", "pymoab".
                Defaults to pymoab.

        Returns:
            dict: the simulation output filename
        """

        self.create_neutronics_model(method=method)

        # Deletes summary.h5m if it already exists.
        # This avoids permission problems when trying to overwrite the file
        os.system('rm summary.h5')

        self.output_filename = self.model.run(output=verbose)
        self.results = self.get_results()

        return self.output_filename

    def get_results(self):
        """Reads the output file from the neutronics simulation
        and prints the TBR tally result to screen

        Returns:
            dict: a dictionary of the simulation results
        """

        # open the results file
        sp = openmc.StatePoint(self.output_filename)

        results = defaultdict(dict)

        # access the tallies
        for key, tally in sp.tallies.items():

            if tally.name == 'TBR':

                df = tally.get_pandas_dataframe()
                tally_result = df["mean"].sum()
                tally_std_dev = df['std. dev.'].sum()
                results[tally.name] = {
                    'result': tally_result,
                    'std. dev.': tally_std_dev,
                }

            if tally.name.endswith('heating'):

                df = tally.get_pandas_dataframe()
                tally_result = df["mean"].sum()
                tally_std_dev = df['std. dev.'].sum()
                results[tally.name]['MeV per source particle'] = {
                    'result': tally_result / 1e6,
                    'std. dev.': tally_std_dev / 1e6,
                }
                results[tally.name]['Watts'] = {
                    'result': tally_result * 1.602176487e-19 * (self.fusion_power / ((17.58 * 1e6) / 6.2415090744e18)),
                    'std. dev.': tally_std_dev * 1.602176487e-19 * (self.fusion_power / ((17.58 * 1e6) / 6.2415090744e18)),
                }

            if tally.name.endswith('flux'):

                df = tally.get_pandas_dataframe()
                tally_result = df["mean"].sum()
                tally_std_dev = df['std. dev.'].sum()
                results[tally.name]['Flux per source particle'] = {
                    'result': tally_result,
                    'std. dev.': tally_std_dev,
                }

            if tally.name.startswith('tritium_production_on_2D_mesh'):

                my_tally = sp.get_tally(name=tally.name)
                my_slice = my_tally.get_slice(scores=['(n,Xt)'])

                my_slice.mean.shape = self.mesh_2D_resolution

                fig = plt.subplot()
                fig.imshow(my_slice.mean).get_figure().savefig(
                    'tritium_production_on_2D_mesh' + tally.name[-3:], dpi=300)
                fig.clear()

            if tally.name.startswith('heating_on_2D_mesh'):

                my_tally = sp.get_tally(name=tally.name)
                my_slice = my_tally.get_slice(scores=['heating'])

                my_slice.mean.shape = self.mesh_2D_resolution

                fig = plt.subplot()
                fig.imshow(my_slice.mean).get_figure().savefig(
                    'heating_on_2D_mesh' + tally.name[-3:], dpi=300)
                fig.clear()

            if tally.name.startswith('flux_on_2D_mesh'):

                my_tally = sp.get_tally(name=tally.name)
                my_slice = my_tally.get_slice(scores=['flux'])

                my_slice.mean.shape = self.mesh_2D_resolution

                fig = plt.subplot()
                fig.imshow(my_slice.mean).get_figure().savefig(
                    'flux_on_2D_mesh' + tally.name[-3:], dpi=300)
                fig.clear()

            if '_on_3D_mesh' in tally.name:
                mesh_id = 1
                mesh = sp.meshes[mesh_id]

                xs = np.linspace(
                    mesh.lower_left[0],
                    mesh.upper_right[0],
                    mesh.dimension[0] + 1
                )
                ys = np.linspace(
                    mesh.lower_left[1],
                    mesh.upper_right[1],
                    mesh.dimension[1] + 1
                )
                zs = np.linspace(
                    mesh.lower_left[2],
                    mesh.upper_right[2],
                    mesh.dimension[2] + 1
                )
                tally = sp.get_tally(name=tally.name)

                data = tally.mean[:, 0, 0]
                error = tally.std_dev[:, 0, 0]

                data = data.tolist()
                error = error.tolist()

                for c, i in enumerate(data):
                    if math.isnan(i):
                        data[c] = 0.

                for c, i in enumerate(error):
                    if math.isnan(i):
                        error[c] = 0.

                self.write_vtk(
                    xs=xs,
                    ys=ys,
                    zs=zs,
                    tally_label=tally.name,
                    tally_data=data,
                    error_data=error,
                    outfile=tally.name + '.vtk'
                )

        self.results = json.dumps(results, indent=4, sort_keys=True)

        return results

    def write_vtk(
            self,
            xs,
            ys,
            zs,
            tally_label,
            tally_data,
            error_data,
            outfile):
        try:
            import vtk
        except (ImportError, ModuleNotFoundError) as e:
            msg = "Conversion to VTK requested," \
                "but the Python VTK module is not installed."
            raise ImportError(msg)

        vtk_box = vtk.vtkRectilinearGrid()

        vtk_box.SetDimensions(len(xs), len(ys), len(zs))

        vtk_x_array = vtk.vtkDoubleArray()
        vtk_x_array.SetName('x-coords')
        vtk_x_array.SetArray(xs, len(xs), True)
        vtk_box.SetXCoordinates(vtk_x_array)

        vtk_y_array = vtk.vtkDoubleArray()
        vtk_y_array.SetName('y-coords')
        vtk_y_array.SetArray(ys, len(ys), True)
        vtk_box.SetYCoordinates(vtk_y_array)

        vtk_z_array = vtk.vtkDoubleArray()
        vtk_z_array.SetName('z-coords')
        vtk_z_array.SetArray(zs, len(zs), True)
        vtk_box.SetZCoordinates(vtk_z_array)

        tally = np.array(tally_data)
        tally_data = vtk.vtkDoubleArray()
        tally_data.SetName(tally_label)
        tally_data.SetArray(tally, tally.size, True)

        error = np.array(error_data)
        error_data = vtk.vtkDoubleArray()
        error_data.SetName("error_tag")
        error_data.SetArray(error, error.size, True)

        vtk_box.GetCellData().AddArray(tally_data)
        vtk_box.GetCellData().AddArray(error_data)

        writer = vtk.vtkRectilinearGridWriter()

        writer.SetFileName(outfile)

        writer.SetInputData(vtk_box)

        print('Writing %s' % outfile)

        writer.Write()
