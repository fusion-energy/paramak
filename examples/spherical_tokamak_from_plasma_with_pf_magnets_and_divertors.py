import paramak

rotation_angle = 180
poloidal_field_coils = []
for case_thickness, height, width, center_point in zip(
    [10, 15, 15, 10], [20, 50, 50, 20], [20, 50, 50, 20], [(500, 300), (560, 100), (560, -100), (500, -300)]
):
    poloidal_field_coils.append(
        paramak.poloidal_field_coil(
            height=height, width=width, center_point=center_point, rotation_angle=rotation_angle
        )
    )
    poloidal_field_coils.append(
        paramak.poloidal_field_coil_case(
            coil_height=height,
            coil_width=width,
            casing_thickness=case_thickness,
            rotation_angle=rotation_angle,
            center_point=center_point,
        )
    )

# TODO
# [(paramak.LayerType.GAP, 75), ("lower_divertor", 100)],
my_reactor = paramak.spherical_tokamak_from_plasma(
    radial_build=[
        (paramak.LayerType.GAP, 10),
        (paramak.LayerType.SOLID, 50),
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.GAP, 50),
        (paramak.LayerType.PLASMA, 300),
        (paramak.LayerType.GAP, 60),
        (paramak.LayerType.SOLID, 15),
        (paramak.LayerType.SOLID, 60),
        (paramak.LayerType.SOLID, 10),
    ],
    elongation=2,
    triangularity=0.55,
    rotation_angle=rotation_angle,
    extra_cut_shapes=poloidal_field_coils,
)
my_reactor.save("spherical_tokamak_from_plasma_with_pf_magnets_and_divertor.step")
