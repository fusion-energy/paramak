# Creates an assembly class that inherits from cadquery's assembly class
# and adds a few convenience methods remove() and names()

import warnings
import cadquery as cq


class Assembly(cq.Assembly):
    """Nested assembly of Workplane and Shape objects defining their relative positions."""

    elongation = None
    triangularity = None
    major_radius = None
    minor_radius = None

    def _copy_metadata(self, target):
        """Copies tokamak geometry metadata to another Assembly instance."""
        target.elongation = self.elongation
        target.triangularity = self.triangularity
        target.major_radius = self.major_radius
        target.minor_radius = self.minor_radius

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