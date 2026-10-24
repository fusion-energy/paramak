# Creates an assembly class that inherits from cadquery's assembly class
# and adds a few convenience methods remove() and names()

import math
import warnings

import cadquery as cq
import numpy as np

from ..workplanes.divertor import divertor


class Assembly(cq.Assembly):
    """Nested assembly of Workplane and Shape objects defining their relative positions."""

    elongation = None
    triangularity = None
    major_radius = None
    minor_radius = None
    rotation_angle = 180.0
    plasma_facing_offset = 0.0
    blanket_layer_names = ()
    structured_layer_data = None

    def _copy_metadata(self, target):
        """Copies tokamak geometry metadata to another Assembly instance."""
        target.elongation = self.elongation
        target.triangularity = self.triangularity
        target.major_radius = self.major_radius
        target.minor_radius = self.minor_radius
        target.rotation_angle = self.rotation_angle
        target.plasma_facing_offset = self.plasma_facing_offset
        target.blanket_layer_names = self.blanket_layer_names
        target.structured_layer_data = self.structured_layer_data

    def _mesh_structured_center_column_volumes(self, data, phi, n_axial, n_radial, full_torus):
        from ..workplanes.structured_mesh import tetrahedralize_center_column_layer

        return [
            mesh
            for layer in data.get("center_column_layers", ())
            for mesh in tetrahedralize_center_column_layer(
                layer["inner_radius"],
                layer["outer_radius"],
                layer["height"],
                phi,
                n_axial=n_axial,
                n_radial=n_radial,
                full_torus=full_torus,
                name=layer["name"],
            )
        ]

    def _added_component_solids(self, data):
        generated_names = set(self.blanket_layer_names)
        generated_names.update(layer["name"] for layer in data.get("center_column_layers", ()))
        generated_names.update(("plasma",))
        generated_names.update(
            name for record in data.get("divertors", ()) for name in record["layer_names"]
        )
        for obj, full_path, location, _ in self:
            name = full_path.split("/")[-1]
            if name in generated_names or not isinstance(obj, cq.Shape):
                continue
            placed_shape = obj.moved(location)
            solids = placed_shape.Solids()
            if not solids:
                continue
            yield name, solids

    def _mesh_added_component_surfaces(self, data, tolerance, angular_tolerance):
        from ..workplanes.structured_mesh import mesh_cad_solid_surface

        meshes = []
        for name, solids in self._added_component_solids(data):
            components = [
                mesh_cad_solid_surface(solid, name, tolerance, angular_tolerance)
                for solid in solids
            ]
            if len(components) == 1:
                meshes.append(components[0])
                continue
            vertices = []
            triangles = []
            for component in components:
                offset = sum(len(points) for points in vertices)
                vertices.append(component["vertices"])
                triangles.append(component["triangles"] + offset)
            meshes.append(
                {
                    "name": name,
                    "vertices": np.concatenate(vertices),
                    "triangles": np.concatenate(triangles),
                }
            )
        return meshes

    def _mesh_added_component_volumes(self, data, mesh_size):
        from ..workplanes.structured_mesh import tetrahedralize_cad_solid

        return [
            tetrahedralize_cad_solid(solid, name, mesh_size=mesh_size)
            for name, solids in self._added_component_solids(data)
            for solid in solids
        ]

    def mesh_structured_layers(
        self,
        n_poloidal=128,
        n_toroidal=32,
        n_axial=None,
        coil_tolerance=0.5,
        coil_angular_tolerance=0.1,
    ):
        """Return structured triangular surface meshes for generated tokamak layers.

        The mesh samples the analytic poloidal layer profiles on one shared
        angular grid. Poloidal segment boundaries are inserted into that grid,
        so adjacent segments and neighboring layers have matching interfaces.

        This initial implementation supports generated, axisymmetric tokamak
        blanket layers, poloidal segmentation, poloidal divertors, and toroidal
        segmentation over partial or full rotations. Additional named CAD
        solids, including coils, are tessellated as triangular surfaces.

        Args:
            n_poloidal: Number of baseline poloidal intervals. Segment
                boundaries are added in addition to these samples.
            n_toroidal: Number of toroidal samples. Partial toroidal extents
                include both end samples; a full 360 degree extent omits the
                duplicate seam sample.
            n_axial: Number of central-column axial intervals. Defaults to
                ``n_poloidal``.
            coil_tolerance: Linear tessellation tolerance in model units for
                additional CAD components such as coils.
            coil_angular_tolerance: Angular tessellation tolerance in radians
                for additional CAD components.

        Returns:
            list[dict]: Mesh records with ``name``, ``vertices``,
            ``triangles``, ``poloidal_angles`` and ``toroidal_angles``.
        """
        if self.structured_layer_data is None:
            raise ValueError(
                "Structured meshing requires a generated tokamak model without geometry-altering CAD cuts."
            )
        if not isinstance(n_poloidal, int) or n_poloidal < 3:
            raise ValueError("n_poloidal must be an integer of at least 3")
        if not isinstance(n_toroidal, int) or n_toroidal < (3 if self.rotation_angle == 360 else 2):
            raise ValueError("n_toroidal is too small for the model rotation_angle")
        if n_axial is None:
            n_axial = n_poloidal
        if not isinstance(n_axial, int) or n_axial < 1:
            raise ValueError("n_axial must be a positive integer")
        if not np.isfinite(coil_tolerance) or coil_tolerance <= 0:
            raise ValueError("coil_tolerance must be finite and positive")
        if not np.isfinite(coil_angular_tolerance) or coil_angular_tolerance <= 0:
            raise ValueError("coil_angular_tolerance must be finite and positive")

        if self.structured_layer_data.get("divertors") or any(
            sector_list is not None for sector_list in self.structured_layer_data.get("toroidal_sectors", ())
        ):
            from ..workplanes.structured_mesh import surface_meshes_from_tetrahedral_meshes

            volume_meshes = self.mesh_structured_layer_volumes(
                n_poloidal=n_poloidal,
                n_toroidal=n_toroidal,
                n_radial=1,
                n_axial=n_axial,
                include_added_components=False,
            )
            meshes = surface_meshes_from_tetrahedral_meshes(volume_meshes)
            return meshes + self._mesh_added_component_surfaces(
                self.structured_layer_data,
                coil_tolerance,
                coil_angular_tolerance,
            )

        from ..workplanes.blanket_from_plasma import offset_curve_coordinates
        from ..workplanes.structured_mesh import mesh_revolved_layer, surface_meshes_from_tetrahedral_meshes
        from .tokamak import poloidal_profile

        data = self.structured_layer_data
        rotation_angle = data["rotation_angle"]
        full_torus = math.isclose(rotation_angle, 360.0)
        poloidal_boundaries = [
            angle
            for segment_list in data["segment_angles"]
            if segment_list is not None
            for _, start, stop in segment_list
            for angle in (start, stop)
        ]
        theta = np.unique(np.concatenate((np.linspace(0.0, 360.0, n_poloidal + 1), poloidal_boundaries)))
        phi = np.linspace(0.0, rotation_angle, n_toroidal, endpoint=not full_torus)
        center_column_volumes = self._mesh_structured_center_column_volumes(
            data, phi, n_axial, 1, full_torus
        )
        meshes = surface_meshes_from_tetrahedral_meshes(center_column_volumes) if center_column_volumes else []

        for pair, segment_list in zip(data["layer_pairs"], data["segment_angles"]):
            if pair["type"] != data["solid_type"]:
                continue
            offset = poloidal_profile(*pair["offsets"])
            thickness = poloidal_profile(*pair["thicknesses"])
            inner_r, inner_z = offset_curve_coordinates(
                data["major_radius"],
                data["minor_radius"],
                data["triangularity"],
                data["elongation"],
                0.0,
                theta,
                offset(theta),
            )
            outer_r, outer_z = offset_curve_coordinates(
                data["major_radius"],
                data["minor_radius"],
                data["triangularity"],
                data["elongation"],
                0.0,
                theta,
                offset(theta) + thickness(theta),
            )
            inner_profile = np.column_stack((inner_r, inner_z))
            outer_profile = np.column_stack((outer_r, outer_z))

            if segment_list is None:
                segment_ranges = None
                full_segment_name = None
            else:
                segment_ranges = []
                for segment_name, start, stop in segment_list:
                    start_index = int(np.flatnonzero(np.isclose(theta, start, atol=1e-10))[0])
                    stop_index = int(np.flatnonzero(np.isclose(theta, stop, atol=1e-10))[0])
                    segment_ranges.append((f"{pair['name']}_{segment_name}", start_index, stop_index))
                if len(segment_ranges) == 1 and segment_ranges[0][1:] == (0, len(theta) - 1):
                    full_segment_name = segment_ranges[0][0]
                    segment_ranges = None
                else:
                    full_segment_name = None

            layer_meshes = mesh_revolved_layer(
                inner_profile,
                outer_profile,
                theta,
                phi,
                full_torus=full_torus,
                segments=segment_ranges,
            )
            if segment_ranges is None:
                layer_meshes[0]["name"] = full_segment_name or pair["name"]
            meshes.extend(layer_meshes)

        meshes.extend(
            self._mesh_added_component_surfaces(data, coil_tolerance, coil_angular_tolerance)
        )
        return meshes

    def create_structured_layer_dagmc_model(
        self,
        n_poloidal=128,
        n_toroidal=32,
        n_axial=None,
        coil_tolerance=0.5,
        coil_angular_tolerance=0.1,
        tag_names=None,
    ):
        """Create a DAGMC model from this tokamak's structured blanket meshes.

        The returned model can be saved with ``model.write_file("model.h5m")``.
        It includes generated blanket, divertor, center-column, and added CAD
        component surfaces such as coils. The mesh does not include the plasma.
        ``tag_names`` maps generated mesh names to H5M material tag names
        (without the ``mat:`` prefix). Multiple mesh names can map to one tag.
        """
        from ..workplanes.structured_mesh import dagmc_model_from_structured_meshes

        meshes = self.mesh_structured_layers(
            n_poloidal=n_poloidal,
            n_toroidal=n_toroidal,
            n_axial=n_axial,
            coil_tolerance=coil_tolerance,
            coil_angular_tolerance=coil_angular_tolerance,
        )
        return dagmc_model_from_structured_meshes(meshes, tag_names=tag_names)

    def mesh_structured_layer_volumes(
        self,
        n_poloidal=128,
        n_toroidal=32,
        n_radial=1,
        n_axial=None,
        include_added_components=True,
        coil_mesh_size=10.0,
    ):
        """Return tetrahedral meshes for generated layers and added CAD components.

        Added CAD components such as coils are tetrahedralized by Gmsh. Set
        ``include_added_components=False`` to mesh only generated tokamak layers.
        """
        if self.structured_layer_data is None:
            raise ValueError(
                "Structured meshing requires a generated tokamak model without geometry-altering CAD cuts."
            )
        if not isinstance(n_poloidal, int) or n_poloidal < 3:
            raise ValueError("n_poloidal must be an integer of at least 3")
        if not isinstance(n_toroidal, int) or n_toroidal < (3 if self.rotation_angle == 360 else 2):
            raise ValueError("n_toroidal is too small for the model rotation_angle")
        if not isinstance(n_radial, int) or n_radial < 1:
            raise ValueError("n_radial must be a positive integer")
        if n_axial is None:
            n_axial = n_poloidal
        if not isinstance(n_axial, int) or n_axial < 1:
            raise ValueError("n_axial must be a positive integer")
        from ..workplanes.blanket_from_plasma import offset_curve_coordinates
        from ..workplanes.structured_mesh import tetrahedralize_revolved_layer
        from .tokamak import poloidal_profile

        data = self.structured_layer_data
        rotation_angle = data["rotation_angle"]
        full_torus = math.isclose(rotation_angle, 360.0)
        boundaries = [
            angle
            for segment_list in data["segment_angles"]
            if segment_list is not None
            for _, start, stop in segment_list
            for angle in (start, stop)
        ]
        for divertor_record in data.get("divertors", ()):
            if divertor_record["poloidal_extent_angle"] < 360.0:
                start = divertor_record["poloidal_start_angle"] % 360.0
                boundaries.extend(
                    (start, (start + divertor_record["poloidal_extent_angle"]) % 360.0)
                )
        theta = np.unique(np.concatenate((np.linspace(0.0, 360.0, n_poloidal + 1), boundaries)))
        phi = np.linspace(0.0, rotation_angle, n_toroidal, endpoint=not full_torus)
        meshes = self._mesh_structured_center_column_volumes(data, phi, n_axial, n_radial, full_torus)
        added_component_meshes = (
            self._mesh_added_component_volumes(data, coil_mesh_size) if include_added_components else []
        )
        has_toroidal_sectors = any(sectors is not None for sectors in data.get("toroidal_sectors", ()))
        if has_toroidal_sectors:
            return (
                meshes
                + self._mesh_structured_angular_partition(data, theta, phi, n_radial, full_torus)
                + added_component_meshes
            )
        if data.get("divertors"):
            return (
                meshes
                + self._mesh_structured_layers_with_divertors(data, theta, phi, n_radial, full_torus)
                + added_component_meshes
            )

        for pair, segment_list in zip(data["layer_pairs"], data["segment_angles"]):
            if pair["type"] != data["solid_type"]:
                continue
            offset = poloidal_profile(*pair["offsets"])
            thickness = poloidal_profile(*pair["thicknesses"])
            inner_r, inner_z = offset_curve_coordinates(
                data["major_radius"], data["minor_radius"], data["triangularity"], data["elongation"],
                0.0, theta, offset(theta)
            )
            outer_r, outer_z = offset_curve_coordinates(
                data["major_radius"], data["minor_radius"], data["triangularity"], data["elongation"],
                0.0, theta, offset(theta) + thickness(theta)
            )
            inner_profile = np.column_stack((inner_r, inner_z))
            outer_profile = np.column_stack((outer_r, outer_z))

            segment_ranges = None
            full_segment_name = None
            if segment_list is not None:
                segment_ranges = []
                for segment_name, start, stop in segment_list:
                    start_index = int(np.flatnonzero(np.isclose(theta, start, atol=1e-10))[0])
                    stop_index = int(np.flatnonzero(np.isclose(theta, stop, atol=1e-10))[0])
                    segment_ranges.append((f"{pair['name']}_{segment_name}", start_index, stop_index))
                if len(segment_ranges) == 1 and segment_ranges[0][1:] == (0, len(theta) - 1):
                    full_segment_name = segment_ranges[0][0]
                    segment_ranges = None

            layer_meshes = tetrahedralize_revolved_layer(
                inner_profile,
                outer_profile,
                theta,
                phi,
                n_radial=n_radial,
                full_torus=full_torus,
                segments=segment_ranges,
            )
            if segment_ranges is None:
                layer_meshes[0]["name"] = full_segment_name or pair["name"]
            meshes.extend(layer_meshes)
        return meshes + added_component_meshes

    def _mesh_structured_layers_with_divertors(self, data, theta, phi, n_radial, full_torus):
        """Build a shared radial/angular mesh and assign divertor replacement cells."""
        from ..workplanes.blanket_from_plasma import offset_curve_coordinates
        from ..workplanes.structured_mesh import tetrahedralize_revolved_layer
        from .tokamak import poloidal_profile

        pair_profiles = []
        radial_curves = []
        for pair, segment_list in zip(data["layer_pairs"], data["segment_angles"]):
            offset = poloidal_profile(*pair["offsets"])(theta)
            thickness = poloidal_profile(*pair["thicknesses"])(theta)
            outer = offset + thickness
            pair_profiles.append((pair, segment_list, offset, outer))
            radial_curves.extend((offset, outer))

        plasma_facing_offset = data["plasma_facing_offset"](theta)
        divertor_profiles = []
        for record in data["divertors"]:
            layer_offsets = [plasma_facing_offset.copy()]
            for thickness in record["layer_thicknesses"]:
                layer_offsets.append(layer_offsets[-1] + thickness)
            divertor_profiles.append((record, layer_offsets))
            radial_curves.extend(layer_offsets)

        unique_curves = []
        for curve in radial_curves:
            if not any(np.allclose(curve, existing, rtol=0.0, atol=1e-8) for existing in unique_curves):
                unique_curves.append(np.asarray(curve, dtype=float))
        if len(unique_curves) < 2:
            raise ValueError("could not build radial interfaces for the structured divertor mesh")
        # Blanket interfaces can change order around the poloidal profile
        # when inboard and outboard layer thicknesses differ. Divertor
        # interfaces can cross those blanket interfaces by design, since
        # divertor cells replace the blanket locally. Sort the offsets at
        # each poloidal node instead of imposing one global radial ordering.
        ordered_offsets = np.sort(np.stack(unique_curves), axis=0)
        # Curves that meet exactly at a sampled node would otherwise create
        # zero-volume tetrahedra there. Keep a negligible positive spacing at
        # that node; away from crossings the original offsets are unchanged.
        for index in range(1, len(ordered_offsets)):
            ordered_offsets[index] = np.maximum(
                ordered_offsets[index], ordered_offsets[index - 1] + 1e-9
            )

        def as_profile(offsets):
            radius, z = offset_curve_coordinates(
                data["major_radius"],
                data["minor_radius"],
                data["triangularity"],
                data["elongation"],
                0.0,
                theta,
                offsets,
            )
            return np.column_stack((radius, z))

        radial_profiles = [as_profile(curve) for curve in ordered_offsets]
        theta_centres = 0.5 * (theta[:-1] + theta[1:])
        radial_centres = [
            0.5 * (lower + upper)
            for lower, upper in zip(ordered_offsets[:-1], ordered_offsets[1:])
        ]

        def angle_in_range(angle, start, extent):
            if extent >= 360.0:
                return True
            return (angle - start) % 360.0 < extent

        labels_by_radial_interval = []
        for radial_centres_at_theta in radial_centres:
            labels = []
            for theta_index, angle in enumerate(theta_centres):
                offset_centre = radial_centres_at_theta[theta_index]
                active_divertors = [
                    (record, layer_offsets)
                    for record, layer_offsets in divertor_profiles
                    if angle_in_range(
                        angle,
                        record["poloidal_start_angle"],
                        record["poloidal_extent_angle"],
                    )
                ]
                if len(active_divertors) > 1:
                    raise ValueError("overlapping divertor footprints are not supported by structured meshing")

                material_name = None
                if active_divertors:
                    record, layer_offsets = active_divertors[0]
                    for layer_index, (lower, upper) in enumerate(zip(layer_offsets[:-1], layer_offsets[1:])):
                        if lower[theta_index] <= offset_centre < upper[theta_index]:
                            material_name = record["layer_names"][layer_index]
                            break

                if material_name is None:
                    for pair, segment_list, lower, upper in pair_profiles:
                        if pair["type"] != data["solid_type"]:
                            continue
                        if not lower[theta_index] <= offset_centre < upper[theta_index]:
                            continue
                        if segment_list is None:
                            material_name = pair["name"]
                        else:
                            for segment_name, start, stop in segment_list:
                                if angle_in_range(angle, start, stop - start):
                                    material_name = f"{pair['name']}_{segment_name}"
                                    break
                        break
                labels.append(material_name)
            labels_by_radial_interval.append(labels)

        meshes = []
        for interval_index, labels in enumerate(labels_by_radial_interval):
            inner_profile = radial_profiles[interval_index]
            outer_profile = radial_profiles[interval_index + 1]
            if labels and all(label == labels[0] for label in labels):
                if labels[0] is not None:
                    meshes.extend(
                        tetrahedralize_revolved_layer(
                            inner_profile,
                            outer_profile,
                            theta,
                            phi,
                            n_radial=n_radial,
                            full_torus=full_torus,
                        )
                    )
                    meshes[-1]["name"] = labels[0]
                continue

            cell_index = 0
            while cell_index < len(labels):
                label = labels[cell_index]
                run_start = cell_index
                while cell_index + 1 < len(labels) and labels[cell_index + 1] == label:
                    cell_index += 1
                run_stop = cell_index
                if label is not None:
                    meshes.extend(
                        tetrahedralize_revolved_layer(
                            inner_profile,
                            outer_profile,
                            theta,
                            phi,
                            n_radial=n_radial,
                            full_torus=full_torus,
                            segments=[(label, run_start, run_stop + 1)],
                        )
                    )
                cell_index += 1
        return meshes

    def _mesh_structured_angular_partition(self, data, theta, phi, n_radial, full_torus):
        """Mesh blanket/divertor cells on shared poloidal and offset-plane toroidal grids."""
        from ..workplanes.blanket_from_plasma import offset_curve_coordinates
        from .tokamak import poloidal_profile

        rotation_angle = data["rotation_angle"]
        toroidal_sectors = data.get("toroidal_sectors", [None] * len(data["layer_pairs"]))

        theta_degrees = np.asarray(theta[:-1], dtype=float)
        theta_nodes = np.deg2rad(theta_degrees)
        pair_profiles = []
        radial_curves = []
        for pair, poloidal_segments, sectors in zip(
            data["layer_pairs"], data["segment_angles"], toroidal_sectors
        ):
            offset = poloidal_profile(*pair["offsets"])(theta_degrees)
            thickness = poloidal_profile(*pair["thicknesses"])(theta_degrees)
            outer = offset + thickness
            pair_profiles.append((pair, poloidal_segments, sectors, offset, outer))
            radial_curves.extend((offset, outer))

        plasma_facing_offset = data["plasma_facing_offset"](theta_degrees)
        divertor_profiles = []
        for record in data.get("divertors", ()):
            layer_offsets = [plasma_facing_offset.copy()]
            for thickness in record["layer_thicknesses"]:
                layer_offsets.append(layer_offsets[-1] + thickness)
            divertor_profiles.append((record, layer_offsets))
            radial_curves.extend(layer_offsets)

        unique_curves = []
        for curve in radial_curves:
            if not any(np.allclose(curve, existing, rtol=0.0, atol=1e-8) for existing in unique_curves):
                unique_curves.append(np.asarray(curve, dtype=float))
        unique_curves.sort(key=lambda curve: float(np.mean(curve)))
        for lower, upper in zip(unique_curves[:-1], unique_curves[1:]):
            if np.any(upper - lower <= 1e-8):
                raise ValueError("radial layer interfaces cross or touch on the structured mesh")

        radial_nodes = []
        for lower, upper in zip(unique_curves[:-1], unique_curves[1:]):
            for subdivision in range(n_radial):
                fraction = subdivision / n_radial
                radial_nodes.append(lower + fraction * (upper - lower))
        radial_nodes.append(unique_curves[-1])
        radial_nodes = np.asarray(radial_nodes)

        geometry_r = np.empty_like(radial_nodes)
        geometry_z = np.empty_like(radial_nodes)
        for radial_index, offsets in enumerate(radial_nodes):
            geometry_r[radial_index], geometry_z[radial_index] = offset_curve_coordinates(
                data["major_radius"],
                data["minor_radius"],
                data["triangularity"],
                data["elongation"],
                0.0,
                theta_degrees,
                offsets,
            )

        boundary_specs = [(0.0, 0.0)] if full_torus else [(0.0, 0.0), (float(rotation_angle), 0.0)]
        for _, _, sectors, _, _ in pair_profiles:
            for sector in sectors or ():
                start_angle, start_offset = sector[1]
                stop_angle, stop_offset = sector[2]
                boundary_specs.extend(((start_angle, start_offset), (stop_angle, -stop_offset)))
        unique_specs = []
        for angle, offset in boundary_specs:
            spec = (float(angle), float(offset))
            if not any(np.allclose(spec, existing, rtol=0.0, atol=1e-10) for existing in unique_specs):
                unique_specs.append(spec)

        boundary_roots = []
        for angle, offset in unique_specs:
            ratio = offset / geometry_r
            if not np.all(np.isfinite(ratio)) or np.any(np.abs(ratio) >= 1.0):
                raise ValueError("a toroidal sector offset plane does not intersect the full layer mesh")
            asin_ratio = np.arcsin(ratio)
            roots = (
                math.radians(angle) + asin_ratio,
                math.radians(angle) + math.pi - asin_ratio,
            )
            for values in roots:
                if full_torus:
                    values = np.mod(values, 2 * math.pi)
                    if not any(np.allclose(values, old, rtol=0.0, atol=1e-10) for old in boundary_roots):
                        boundary_roots.append(values)
                else:
                    upper_angle = math.radians(rotation_angle)
                    tolerance = 1e-10
                    inside = (values >= -tolerance) & (values <= upper_angle + tolerance)
                    if not np.any(inside):
                        continue
                    if not np.all(inside):
                        raise ValueError("a toroidal sector boundary crosses a reactor toroidal end plane")
                    values = np.clip(values, 0.0, upper_angle)
                    if not any(np.allclose(values, old, rtol=0.0, atol=1e-10) for old in boundary_roots):
                        boundary_roots.append(values)

        if full_torus:
            means = np.asarray(
                [math.atan2(float(np.mean(np.sin(values))), float(np.mean(np.cos(values)))) % (2 * math.pi)
                 for values in boundary_roots]
            )
            ordered_means = np.sort(means)
            circular_gaps = np.diff(np.concatenate((ordered_means, [ordered_means[0] + 2 * math.pi])))
            largest_gap = int(np.argmax(circular_gaps))
            seam = (ordered_means[largest_gap] + circular_gaps[largest_gap] / 2) % (2 * math.pi)
            boundary_values = [np.zeros_like(geometry_r)]
            for values in boundary_roots:
                shifted = np.mod(values - seam, 2 * math.pi)
                if np.ptp(shifted) > math.pi:
                    raise ValueError("a toroidal sector boundary crosses the periodic mesh seam")
                if not any(np.allclose(shifted, old, rtol=0.0, atol=1e-10) for old in boundary_values):
                    boundary_values.append(shifted)
        else:
            seam = 0.0
            boundary_values = [np.zeros_like(geometry_r), np.full_like(geometry_r, math.radians(rotation_angle))]
            for values in boundary_roots:
                if not any(np.allclose(values, old, rtol=0.0, atol=1e-10) for old in boundary_values):
                    boundary_values.append(values)

        if full_torus:
            # Offset planes can exchange angular order around a full torus.
            # Order their intersections at each node to keep angular cells
            # from becoming inverted where the curves cross.
            boundary_values = list(np.sort(np.stack(boundary_values), axis=0))
        else:
            order = np.argsort([float(np.mean(values)) for values in boundary_values])
            boundary_values = [boundary_values[index] for index in order]

        for boundary_index, (lower, upper) in enumerate(zip(boundary_values[:-1], boundary_values[1:])):
            separation = upper - lower
            if np.any(separation <= 1e-10):
                minimum = float(np.min(separation))
                location = np.unravel_index(int(np.argmin(separation)), separation.shape)
                raise ValueError(
                    "toroidal sector boundaries cross or touch on the structured grid "
                    f"between curves {boundary_index} and {boundary_index + 1} "
                    f"(minimum separation {minimum:.3g} radians at grid node {location})"
                )

        # Allocate the requested toroidal resolution across the shared angular
        # intervals while preserving every sector/gap boundary.
        interval_pairs = list(zip(boundary_values[:-1], boundary_values[1:]))
        if full_torus:
            interval_pairs.append((boundary_values[-1], boundary_values[0] + 2 * math.pi))
        widths = np.asarray([np.mean(upper - lower) for lower, upper in interval_pairs])
        n_intervals = len(widths)
        target_cells = max(len(phi) if full_torus else len(phi) - 1, n_intervals)
        cell_counts = np.ones(n_intervals, dtype=int)
        remaining = target_cells - n_intervals
        if remaining:
            ideal = remaining * widths / widths.sum()
            additions = np.floor(ideal).astype(int)
            cell_counts += additions
            leftovers = remaining - int(additions.sum())
            for index in np.argsort(ideal - additions)[::-1][:leftovers]:
                cell_counts[index] += 1

        toroidal_nodes = []
        for (lower, upper), count in zip(interval_pairs, cell_counts):
            for subdivision in range(count):
                fraction = subdivision / count
                toroidal_nodes.append(lower + fraction * (upper - lower))
        if not full_torus:
            toroidal_nodes.append(boundary_values[-1])
        toroidal_nodes = np.stack(toroidal_nodes, axis=-1)
        if not full_torus and np.any(np.diff(toroidal_nodes, axis=-1) <= 1e-10):
            raise ValueError("the shared toroidal grid contains a zero-width cell")

        n_radial_nodes, n_theta = radial_nodes.shape
        n_phi_nodes = toroidal_nodes.shape[-1]
        vertices = np.empty((n_radial_nodes, n_theta, n_phi_nodes, 3), dtype=float)
        world_toroidal_nodes = toroidal_nodes + seam
        vertices[..., 0] = geometry_r[:, :, None] * np.cos(world_toroidal_nodes)
        vertices[..., 1] = geometry_r[:, :, None] * np.sin(world_toroidal_nodes)
        vertices[..., 2] = geometry_z[:, :, None]

        n_radial_cells = n_radial_nodes - 1
        n_theta_cells = n_theta
        n_phi_cells = n_phi_nodes if full_torus else n_phi_nodes - 1
        labels = np.empty((n_radial_cells, n_theta_cells, n_phi_cells), dtype=object)
        labels[:] = None

        def theta_midpoint(index):
            first = theta_nodes[index]
            second = theta_nodes[(index + 1) % n_theta]
            if second <= first:
                second += 2 * math.pi
            return 0.5 * (first + second)

        theta_centres = np.asarray([theta_midpoint(index) for index in range(n_theta_cells)])
        pair_center_profiles = []
        for pair, poloidal_segments, sectors, _, _ in pair_profiles:
            center_theta = np.mod(theta_centres, 2 * math.pi)
            center_lower = poloidal_profile(*pair["offsets"])(np.rad2deg(center_theta))
            center_upper = center_lower + poloidal_profile(*pair["thicknesses"])(np.rad2deg(center_theta))
            pair_center_profiles.append((pair, poloidal_segments, sectors, center_lower, center_upper))

        divertor_center_profiles = []
        for record, layer_offsets in divertor_profiles:
            center_offsets = [
                data["plasma_facing_offset"](np.rad2deg(np.mod(theta_centres, 2 * math.pi)))
            ]
            for thickness in record["layer_thicknesses"]:
                center_offsets.append(center_offsets[-1] + thickness)
            divertor_center_profiles.append((record, center_offsets))

        def angle_in_range(angle, start, extent):
            if extent >= 360.0:
                return True
            return (angle - start) % 360.0 < extent

        def in_sector(phi_value, radius, start, stop):
            start_angle, start_offset = start
            stop_angle, stop_offset = stop
            if stop_angle - start_angle >= 360.0 - 1e-9:
                return True
            start_phi = math.radians(start_angle) + math.asin(start_offset / radius)
            stop_phi = math.radians(stop_angle) - math.asin(stop_offset / radius)
            extent = stop_phi - start_phi
            if extent < 0.0:
                extent += 2 * math.pi
            if extent >= 2 * math.pi - 1e-10:
                return True
            return (phi_value - start_phi) % (2 * math.pi) < extent + 1e-10

        for radial_index in range(n_radial_cells):
            for theta_index in range(n_theta_cells):
                theta_next = (theta_index + 1) % n_theta
                theta_center_degrees = math.degrees(theta_centres[theta_index]) % 360.0
                for phi_index in range(n_phi_cells):
                    phi_next_index = (phi_index + 1) % n_phi_nodes
                    radial_center = 0.25 * (
                        radial_nodes[radial_index, theta_index]
                        + radial_nodes[radial_index, theta_next]
                        + radial_nodes[radial_index + 1, theta_index]
                        + radial_nodes[radial_index + 1, theta_next]
                    )
                    radius_center = 0.25 * (
                        geometry_r[radial_index, theta_index]
                        + geometry_r[radial_index, theta_next]
                        + geometry_r[radial_index + 1, theta_index]
                        + geometry_r[radial_index + 1, theta_next]
                    )
                    cell_r = (radial_index, radial_index + 1)
                    cell_theta = (theta_index, theta_next)
                    cell_phi = (phi_index, phi_next_index)
                    center_x = np.mean(
                        [
                            geometry_r[r, t] * math.cos(world_toroidal_nodes[r, t, p])
                            for r in cell_r
                            for t in cell_theta
                            for p in cell_phi
                        ]
                    )
                    center_y = np.mean(
                        [
                            geometry_r[r, t] * math.sin(world_toroidal_nodes[r, t, p])
                            for r in cell_r
                            for t in cell_theta
                            for p in cell_phi
                        ]
                    )
                    phi_center = math.atan2(center_y, center_x) % (2 * math.pi)

                    active_divertors = [
                        (record, offsets)
                        for record, offsets in divertor_center_profiles
                        if angle_in_range(
                            theta_center_degrees,
                            record["poloidal_start_angle"],
                            record["poloidal_extent_angle"],
                        )
                    ]
                    if len(active_divertors) > 1:
                        raise ValueError("overlapping divertor footprints are not supported by structured meshing")
                    material_name = None
                    if active_divertors:
                        record, offsets = active_divertors[0]
                        for layer_index, (lower, upper) in enumerate(zip(offsets[:-1], offsets[1:])):
                            if lower[theta_index] <= radial_center < upper[theta_index]:
                                material_name = record["layer_names"][layer_index]
                                break

                    if material_name is None:
                        for pair, poloidal_segments, sectors, lower, upper in pair_center_profiles:
                            if pair["type"] != data["solid_type"]:
                                continue
                            if not lower[theta_index] <= radial_center < upper[theta_index]:
                                continue
                            if poloidal_segments is None:
                                base_name = pair["name"]
                            else:
                                base_name = None
                                for segment_name, start, stop in poloidal_segments:
                                    if angle_in_range(theta_center_degrees, start, stop - start):
                                        base_name = f"{pair['name']}_{segment_name}"
                                        break
                                if base_name is None:
                                    break

                            if sectors is None:
                                material_name = base_name
                            else:
                                for sector_name, start_boundary, stop_boundary in sectors:
                                    if in_sector(phi_center, radius_center, start_boundary, stop_boundary):
                                        material_name = f"{base_name}_{sector_name}"
                                        break
                            break
                    labels[radial_index, theta_index, phi_index] = material_name

        # Split the labeled hexahedra into connected volume components before
        # converting them to closed DAGMC shells.
        visited = np.zeros(labels.shape, dtype=bool)
        components = []
        tet_patterns = (
            (0, 1, 3, 7),
            (0, 3, 2, 7),
            (0, 2, 6, 7),
            (0, 6, 4, 7),
            (0, 4, 5, 7),
            (0, 5, 1, 7),
        )

        def neighbors(cell):
            radial_index, theta_index, phi_index = cell
            for candidate in (
                (radial_index - 1, theta_index, phi_index),
                (radial_index + 1, theta_index, phi_index),
                (radial_index, (theta_index - 1) % n_theta_cells, phi_index),
                (radial_index, (theta_index + 1) % n_theta_cells, phi_index),
                (radial_index, theta_index, (phi_index - 1) % n_phi_cells if full_torus else phi_index - 1),
                (radial_index, theta_index, (phi_index + 1) % n_phi_cells if full_torus else phi_index + 1),
            ):
                i, j, k = candidate
                if 0 <= i < n_radial_cells and 0 <= k < n_phi_cells:
                    yield candidate

        for index in np.ndindex(labels.shape):
            label = labels[index]
            if label is None or visited[index]:
                continue
            visited[index] = True
            stack = [index]
            component_cells = []
            while stack:
                cell = stack.pop()
                component_cells.append(cell)
                for neighbor in neighbors(cell):
                    if not visited[neighbor] and labels[neighbor] == label:
                        visited[neighbor] = True
                        stack.append(neighbor)

            node_ids = set()
            component_tets = []
            for radial_index, theta_index, phi_index in component_cells:
                theta_next = (theta_index + 1) % n_theta
                phi_next = (phi_index + 1) % n_phi_nodes
                corners = (
                    (radial_index, theta_index, phi_index),
                    (radial_index + 1, theta_index, phi_index),
                    (radial_index, theta_next, phi_index),
                    (radial_index + 1, theta_next, phi_index),
                    (radial_index, theta_index, phi_next),
                    (radial_index + 1, theta_index, phi_next),
                    (radial_index, theta_next, phi_next),
                    (radial_index + 1, theta_next, phi_next),
                )
                flat_corners = tuple(np.ravel_multi_index(corner, vertices.shape[:3]) for corner in corners)
                node_ids.update(flat_corners)
                component_tets.extend(
                    tuple(flat_corners[corner_index] for corner_index in pattern) for pattern in tet_patterns
                )
            sorted_nodes = sorted(node_ids)
            local_node = {global_id: local_id for local_id, global_id in enumerate(sorted_nodes)}
            components.append(
                {
                    "name": label,
                    "vertices": vertices.reshape((-1, 3))[sorted_nodes],
                    "tetrahedra": np.asarray(
                        [[local_node[node] for node in tet] for tet in component_tets], dtype=np.int64
                    ),
                }
            )
        return components

    def export_structured_layers_exodus(
        self,
        filename,
        n_poloidal=128,
        n_toroidal=32,
        n_radial=1,
        n_axial=None,
        coil_mesh_size=10.0,
        tag_names=None,
    ):
        """Write the generated tokamak blanket tetrahedral mesh to Exodus.

        The Exodus element blocks use the Paramak layer, poloidal segment, or
        center-column names. Added CAD components such as coils are
        tetrahedralized with Gmsh using ``coil_mesh_size``. Requires the
        optional ``netCDF4`` and ``gmsh`` packages. ``tag_names`` maps mesh
        names to Exodus block names and can combine multiple meshes into one
        block. Geometry units are Paramak's centimetres.
        """
        from ..workplanes.structured_mesh import (
            merge_tetrahedral_meshes,
            remap_mesh_names,
            write_tetrahedral_mesh_exodus,
        )

        meshes = self.mesh_structured_layer_volumes(
            n_poloidal=n_poloidal,
            n_toroidal=n_toroidal,
            n_radial=n_radial,
            n_axial=n_axial,
            coil_mesh_size=coil_mesh_size,
        )
        meshes = remap_mesh_names(meshes, tag_names)
        vertices, connectivity, blocks = merge_tetrahedral_meshes(meshes)
        return write_tetrahedral_mesh_exodus(vertices, connectivity, blocks, filename)

    def remove(self, name: str):
        new_assembly = Assembly()
        part_found = False
        for part in self:
            if part[1].endswith(f'/{name}'):
                part_found = True
            else:
                new_assembly.add(part[0], name=part[1], color=part[3], loc=part[2])
        if not part_found:
            warnings.warn(f'Part with name {name} not found')
        self._copy_metadata(new_assembly)
        return new_assembly

    def names(self):
        names = []
        for part in self:
            names.append(part[1].split('/')[-1])
        return names

    def add_divertor(
        self,
        poloidal_start_angle: float,
        poloidal_extent_angle: float,
        divertor_layer_names,
        divertor_layer_thicknesses,
    ):
        """Returns a copy of this model with a layered poloidal divertor.

        The divertor begins at the plasma-facing surface and extends outward.
        Existing blanket geometry in the divertor region is removed and
        replaced with the supplied layers. Poloidal angles are measured
        counter-clockwise from the outboard midplane, in degrees.
        """
        if self.major_radius is None or self.minor_radius is None:
            raise ValueError("add_divertor() requires a Paramak tokamak model")
        if self.plasma_facing_offset is None:
            raise ValueError("This model does not contain plasma-facing surface metadata")

        layers = divertor(
            poloidal_start_angle=poloidal_start_angle,
            poloidal_extent_angle=poloidal_extent_angle,
            divertor_layer_names=divertor_layer_names,
            divertor_layer_thicknesses=divertor_layer_thicknesses,
            major_radius=self.major_radius,
            minor_radius=self.minor_radius,
            triangularity=self.triangularity,
            elongation=self.elongation,
            plasma_facing_offset=self.plasma_facing_offset,
            rotation_angle=self.rotation_angle,
        )
        names = self.names()
        new_names = list(divertor_layer_names)
        duplicates = set(names).intersection(new_names)
        if duplicates:
            raise ValueError(f"Divertor layer names already exist in the model: {sorted(duplicates)}")

        result = Assembly()
        cuttable_layer_names = list(self.blanket_layer_names)
        for obj, full_path, loc, color in self:
            name = full_path.split("/")[-1]
            if name in self.blanket_layer_names and isinstance(obj, cq.Shape):
                original_solid_count = len(obj.Solids())
                for layer in layers:
                    obj = obj.cut(layer.val())
                solids = obj.Solids()
                if original_solid_count == 1 and len(solids) == 2:
                    radial_order = sorted(
                        solids,
                        key=lambda solid: math.hypot(solid.Center().x, solid.Center().y),
                    )
                    inboard_name = f"{name}_inboard"
                    outboard_name = f"{name}_outboard"
                    result.add(radial_order[0], name=inboard_name, color=color, loc=loc)
                    result.add(radial_order[1], name=outboard_name, color=color, loc=loc)
                    cuttable_layer_names = [
                        layer_name
                        for layer_name in cuttable_layer_names
                        if layer_name != name
                    ] + [inboard_name, outboard_name]
                    continue
            result.add(obj, name=name, color=color, loc=loc)
        for layer in layers:
            color = cq.Color(*layer.color) if isinstance(layer.color, tuple) else layer.color
            result.add(layer, name=layer.name, color=color)
        self._copy_metadata(result)
        if self.structured_layer_data is not None:
            structured_data = dict(self.structured_layer_data)
            divertors = list(structured_data.get("divertors", ()))
            divertors.append(
                {
                    "poloidal_start_angle": float(poloidal_start_angle),
                    "poloidal_extent_angle": float(poloidal_extent_angle),
                    "layer_names": tuple(divertor_layer_names),
                    "layer_thicknesses": tuple(divertor_layer_thicknesses),
                }
            )
            structured_data["divertors"] = divertors
            result.structured_layer_data = structured_data
        else:
            result.structured_layer_data = None
        result.blanket_layer_names = tuple(cuttable_layer_names)
        return result

    def rename(self, old: str, new: str):
        """Returns a new Assembly with the part(s) named ``old`` renamed to ``new``.

        Matches either a single part whose name equals ``old``, or a group of
        solids produced by :meth:`split_solids` that share ``old`` as a base
        name (``old_1``, ``old_2`` ...). In the group case each member is
        renamed to ``new_1``, ``new_2`` ... preserving the original numbering.

        Args:
            old: the existing part name (or split-solid base name) to replace.
            new: the replacement name (or base name for a split-solid group).

        Raises:
            ValueError: if a resulting name would collide with another part,
                because cadquery assembly names must be unique.
        """
        leaf_names = self.names()

        if old in leaf_names:
            remap = {old: new}
        else:
            # fall back to a split_solids() group sharing ``old`` as base name
            remap = {}
            for leaf in leaf_names:
                base, separator, suffix = leaf.rpartition('_')
                if separator and base == old and suffix.isdigit():
                    remap[leaf] = f'{new}_{suffix}'

        if not remap:
            warnings.warn(f'Part with name {old} not found')
            return self

        # assembly names must stay unique
        unchanged = [name for name in leaf_names if name not in remap]
        targets = list(remap.values())
        for target in targets:
            if target in unchanged or targets.count(target) > 1:
                raise ValueError(
                    f'Cannot rename to {target!r}, that name already exists in the '
                    'assembly and assembly names must be unique.'
                )

        new_assembly = Assembly()
        for obj, full_path, loc, color in self:
            leaf = full_path.split('/')[-1]
            new_assembly.add(obj, name=remap.get(leaf, leaf), color=color, loc=loc)

        self._copy_metadata(new_assembly)
        return new_assembly

    def split_solids(self):
        """
        Explodes any part containing multiple solids into individually named parts.

        Naming convention:
          - Single-solid parts: name unchanged
          - Multi-solid parts:  <original_name>_1, <original_name>_2, ... <original_name>_N

        Example:
          'add_extra_cut_shape_1' with 16 solids becomes:
          'add_extra_cut_shape_1_1' through 'add_extra_cut_shape_1_16'
        """
        new_assembly = Assembly()

        for part in self:
            obj, full_path, loc, color = part
            leaf_name = full_path.split('/')[-1]

            if isinstance(obj, cq.Workplane):
                solids = obj.solids().vals()
                plane = obj.plane
            elif isinstance(obj, cq.Shape):
                solids = obj.Solids()
                plane = None
            else:
                new_assembly.add(obj, name=leaf_name, color=color, loc=loc)
                continue

            if len(solids) <= 1:
                new_assembly.add(obj, name=leaf_name, color=color, loc=loc)
            else:
                for idx, solid in enumerate(solids, start=1):
                    split_name = f"{leaf_name}_{idx}"
                    new_obj = cq.Workplane(plane).add(solid) if plane is not None else solid
                    new_assembly.add(new_obj, name=split_name, color=color, loc=loc)

        self._copy_metadata(new_assembly)
        return new_assembly
