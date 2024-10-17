from cadquery import exporters

import paramak

solid = paramak.plasma_simplified(rotation_angle=180, triangularity=-0.55)
exporters.export(solid, "plasma_simplified.step")
# solid.exportStep("plasma_simplified.step")

# solid = paramak.plasma_simplified(rotation_angle=360)

# exporters.export(solid, "plasma_simplified.step")
# solid.exportStep("plasma_simplified.step")
