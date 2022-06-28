import paramak


plasma = paramak.Plasma(
    major_radius=330, minor_radius=113, triangularity=0.33, elongation=1.84, rotation_angle=180, name="plasma"
)

plasma_s = plasma.solid.val()

vertices, triangles = plasma_s.tessellate(tolerance=1)

print(vertices)
