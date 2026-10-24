# Creates an assembly class that inherits from cadquery's assembly class
# and adds a few convenience methods remove() and names()

import warnings

import cadquery as cq

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

    def _copy_metadata(self, target):
        """Copies tokamak geometry metadata to another Assembly instance."""
        target.elongation = self.elongation
        target.triangularity = self.triangularity
        target.major_radius = self.major_radius
        target.minor_radius = self.minor_radius
        target.rotation_angle = self.rotation_angle
        target.plasma_facing_offset = self.plasma_facing_offset
        target.blanket_layer_names = self.blanket_layer_names

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
        for obj, full_path, loc, color in self:
            name = full_path.split("/")[-1]
            if name in self.blanket_layer_names and isinstance(obj, cq.Shape):
                for layer in layers:
                    obj = obj.cut(layer.val())
            result.add(obj, name=name, color=color, loc=loc)
        for layer in layers:
            color = cq.Color(*layer.color) if isinstance(layer.color, tuple) else layer.color
            result.add(layer, name=layer.name, color=color)
        self._copy_metadata(result)
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
