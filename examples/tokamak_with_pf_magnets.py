import paramak

extra_cut_shapes = []
for case_thickness, height, width, center_point in zip(
    [10, 15, 15, 10], [20, 50, 50, 20], [20, 50, 50, 20], [(700, 300), (800, 100), (800, -100), (700, -300)]
):
    extra_cut_shapes.append(
        paramak.poloidal_field_coil(height=height, width=width, center_point=center_point, rotation_angle=180)
    )
    extra_cut_shapes.append(
        paramak.poloidal_field_coil_case(
            coil_height=height,
            coil_width=width,
            casing_thickness=case_thickness,
            rotation_angle=180,
            center_point=center_point,
        )
    )

my_reactor = paramak.tokamak(
    radial_build=[
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 30),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 120),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 20),
        (paramak.LayerType.SOLID, 120),
        (paramak.LayerType.SOLID, 10),
    ],
    vertical_build=[
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.SOLID, 80),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.GAP, 50),
        (paramak.LayerType.PLASMA, 700),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 10),
        (paramak.LayerType.SOLID, 40),
        (paramak.LayerType.SOLID, 15),
    ],
    triangularity=0.55,
    rotation_angle=180,
    extra_cut_shapes=extra_cut_shapes,
)

my_reactor.save(f"tokamak_with_pf_magnets.step")
print(f"Saved as tokamak_with_pf_magnets.step")

