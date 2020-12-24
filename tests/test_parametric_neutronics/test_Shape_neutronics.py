
import os
import unittest
from pathlib import Path

import openmc
import paramak
import pytest


class TestObjectNeutronicsArguments(unittest.TestCase):
    """Tests Shape object arguments that involve neutronics usage"""

    def setUp(self):
        self.test_shape = paramak.ExtrudeMixedShape(
            points=[
                (50, 0, "straight"),
                (50, 50, "spline"),
                (60, 70, "spline"),
                (70, 50, "circle"),
                (60, 25, "circle"),
                (70, 0, "straight")],
            distance=50
        )

    def test_export_h5m_creates_file(self):
        """Tests the Shape.export_h5m method results in an outputfile."""
        os.system('rm test_shape.h5m')
        self.test_shape.export_h5m(filename='test_shape.h5m')
        assert Path("test_shape.h5m").exists() is True

    def test_export_h5m_creates_file_even_without_extention(self):
        """Tests the Shape.export_h5m method results in an outputfile even
        when the filename does not include the .h5m"""
        os.system('rm test_shape.h5m')
        self.test_shape.export_h5m(filename='test_shape')
        assert Path("test_shape.h5m").exists() is True

    def test_offset_from_graveyard_sets_attribute(self):
        os.system('rm test_shape.h5m')
        self.test_shape.export_h5m(
            filename='test_shape.h5m',
            graveyard_offset=101)
        assert self.test_shape.graveyard_offset == 101

    def test_tolerance_increases_filesize(self):
        os.system('rm test_shape.h5m')
        self.test_shape.export_h5m(
            filename='test_shape_0001.h5m',
            tolerance=0.001)
        self.test_shape.export_h5m(
            filename='test_shape_001.h5m',
            tolerance=0.01)
        assert Path('test_shape_0001.h5m').stat().st_size > Path(
            'test_shape_001.h5m').stat().st_size

    def test_skipping_graveyard_decreases_filesize(self):
        os.system('rm test_shape.h5m')
        self.test_shape.export_h5m(filename='skiped.h5m', skip_graveyard=True)
        self.test_shape.export_h5m(
            filename='not_skipped.h5m',
            skip_graveyard=False)
        assert Path('not_skipped.h5m').stat().st_size > Path(
            'skiped.h5m').stat().st_size

    def test_graveyard_offset_increases_voulme(self):
        os.system('rm test_shape.h5m')
        self.test_shape.make_graveyard(graveyard_offset=100)
        small_offset = self.test_shape.graveyard.volume
        self.test_shape.make_graveyard(graveyard_offset=1000)
        large_offset = self.test_shape.graveyard.volume
        assert small_offset < large_offset


class TestSimulationResultsVsCsg(unittest.TestCase):
    """Makes a geometry in the paramak and in CSG geometry, simulates and
    compares the results"""

    def simulate_cylinder_cask_csg(
            self,
            material,
            source,
            height,
            outer_radius,
            thickness,
            batches,
            particles):
        """Makes a CSG cask geometry runs a simulation and returns the result"""

        mats = openmc.Materials([material])

        outer_cylinder = openmc.ZCylinder(r=outer_radius)
        inner_cylinder = openmc.ZCylinder(r=outer_radius - thickness)
        inner_top = openmc.ZPlane(z0=height * 0.5)
        inner_bottom = openmc.ZPlane(z0=-height * 0.5)
        outer_top = openmc.ZPlane(z0=(height * 0.5) + thickness)
        outer_bottom = openmc.ZPlane(z0=(-height * 0.5) - thickness)

        sphere_1 = openmc.Sphere(r=100, boundary_type='vacuum')

        cylinder_region = -outer_cylinder & +inner_cylinder & -inner_top & + inner_bottom
        cylinder_cell = openmc.Cell(region=cylinder_region)
        cylinder_cell.fill = material

        top_cap_region = -outer_top & +inner_top & -outer_cylinder
        top_cap_cell = openmc.Cell(region=top_cap_region)
        top_cap_cell.fill = material

        bottom_cap_region = +outer_bottom & -inner_bottom & -outer_cylinder
        bottom_cap_cell = openmc.Cell(region=bottom_cap_region)
        bottom_cap_cell.fill = material

        inner_void_region = -inner_cylinder & -inner_top & +inner_bottom
        inner_void_cell = openmc.Cell(region=inner_void_region)

        # sphere 1 region is below -sphere_1 and not (~) in the other regions
        sphere_1_region = -sphere_1
        sphere_1_cell = openmc.Cell(
            region=sphere_1_region
            & ~bottom_cap_region
            & ~top_cap_region
            & ~cylinder_region
            & ~inner_void_region
        )

        universe = openmc.Universe(cells=[
            inner_void_cell, cylinder_cell, top_cap_cell,
            bottom_cap_cell, sphere_1_cell
        ])

        geom = openmc.Geometry(universe)

        # Instantiate a Settings object
        sett = openmc.Settings()
        sett.batches = batches
        sett.particles = particles
        sett.inactive = 0
        sett.run_mode = 'fixed source'
        sett.photon_transport = True
        sett.source = source

        cell_filter = openmc.CellFilter([
            cylinder_cell,
            top_cap_cell,
            bottom_cap_cell])

        tally = openmc.Tally(name='csg_heating')
        tally.filters = [cell_filter]
        tally.scores = ['heating']
        tallies = openmc.Tallies()
        tallies.append(tally)

        model = openmc.model.Model(geom, mats, sett, tallies)
        sp_filename = model.run()

        # open the results file
        results = openmc.StatePoint(sp_filename)

        # access the tally using pandas dataframes
        tally = results.get_tally(name='csg_heating')
        tally_df = tally.get_pandas_dataframe()

        return tally_df['mean'].sum()

    def simulate_cylinder_cask_cad(
            self,
            material,
            source,
            height,
            outer_radius,
            thickness,
            batches,
            particles):
        """Makes a CAD cask geometry runs a simulation and returns the result"""

        top_cap_cell = paramak.RotateStraightShape(
            stp_filename='top_cap_cell.stp',
            material_tag='test_mat',
            points=[
                (outer_radius, height * 0.5),
                (outer_radius, (height * 0.5) + thickness),
                (0, (height * 0.5) + thickness),
                (0, height * 0.5),
            ],
        )

        bottom_cap_cell = paramak.RotateStraightShape(
            stp_filename='bottom_cap_cell.stp',
            material_tag='test_mat',
            points=[
                (outer_radius, -height * 0.5),
                (outer_radius, (-height * 0.5) - thickness),
                (0, (-height * 0.5) - thickness),
                (0, -height * 0.5),
            ]
        )

        cylinder_cell = paramak.CenterColumnShieldCylinder(
            height=height,
            inner_radius=outer_radius - thickness,
            outer_radius=outer_radius,
            material_tag='test_mat',
        )

        my_geometry = paramak.Reactor(
            [cylinder_cell, bottom_cap_cell, top_cap_cell])

        my_model = paramak.NeutronicsModel(
            geometry=my_geometry,
            source=source,
            simulation_batches=batches,
            simulation_particles_per_batch=particles,
            materials={'test_mat': material},
            cell_tallies=['heating']
        )

        my_model.simulate(method='pymoab')

        # scaled from MeV to eV
        return my_model.results['test_mat_heating']['MeV per source particle']['result'] * 1e6

    def test_cylinder_cask(self):
        """Runs the same source and material with CAD and CSG geoemtry"""

        height = 100
        outer_radius = 50
        thickness = 10

        batches = 10
        particles = 500

        test_material = openmc.Material(name='test_material')
        test_material.set_density('g/cm3', 7.75)
        test_material.add_element('Fe', 0.95, percent_type='wo')
        test_material.add_element('C', 0.05, percent_type='wo')

        source = openmc.Source()
        source.space = openmc.stats.Point((0, 0, 0))
        source.angle = openmc.stats.Isotropic()
        source.energy = openmc.stats.Discrete([14e6], [1.0])

        csg_result = self.simulate_cylinder_cask_csg(
            test_material, source, height, outer_radius, thickness, batches, particles)

        cad_result = self.simulate_cylinder_cask_cad(
            test_material, source, height, outer_radius, thickness, batches, particles)

        assert pytest.approx(csg_result, rel=0.001) == cad_result


if __name__ == "__main__":
    unittest.main()
