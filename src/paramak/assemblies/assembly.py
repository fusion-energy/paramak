# Creates an assembly class that inherits from cadquery's assembly class
# and adds a few convenience methods remove() and names()

import warnings
import cadquery as cq


class Assembly(cq.Assembly):
    """Nested assembly of Workplane and Shape objects defining their relative positions."""

    elongation=None
    triangularity=None
    major_radius=None
    minor_radius=None

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

        new_assembly.elongation = self.elongation
        new_assembly.triangularity = self.triangularity
        new_assembly.major_radius = self.major_radius
        new_assembly.minor_radius = self.minor_radius
        return new_assembly

    def names(self):
        names = []
        for part in self:
            names.append(part[1].split('/')[-1])
        return names

    def fuse_solids(self):
        """Combines multi-solid parts into single solids for export."""
        new_assembly = Assembly()
        for part in self:
            obj, name, loc, color = part
            if isinstance(obj, cq.Workplane):
                solids = obj.solids().vals()
                if len(solids) > 1:
                    fused_shape = solids[0]
                    for solid in solids[1:]:
                        fused_shape = fused_shape.fuse(solid)
                    if hasattr(fused_shape, "removeSplitter"):
                        fused_shape = fused_shape.removeSplitter()
                    obj = cq.Workplane(obj.plane).add(fused_shape).clean()
                    if len(obj.solids().vals()) > 1:
                        compound = cq.Compound.makeCompound(solids)
                        obj = cq.Workplane(obj.plane).add(compound).combine()
                    if len(obj.solids().vals()) > 1:
                        warnings.warn(f"Part {name} still has {len(obj.solids().vals())} solids after fusing")
                else:
                    obj = obj.combine()
            new_assembly.add(obj, name=name, color=color, loc=loc)

        new_assembly.elongation = self.elongation
        new_assembly.triangularity = self.triangularity
        new_assembly.major_radius = self.major_radius
        new_assembly.minor_radius = self.minor_radius
        return new_assembly
