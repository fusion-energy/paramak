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
