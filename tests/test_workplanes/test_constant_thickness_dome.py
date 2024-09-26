import cadquery as cq

import paramak
import paramak.workplanes

a = paramak.constant_thickness_dome(upper_or_lower="upper")
cq.exporters.export(a, "upper.step")
a = paramak.constant_thickness_dome(upper_or_lower="lower")
cq.exporters.export(a, "lower.step")
