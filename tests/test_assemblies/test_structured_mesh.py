from collections import Counter
import sys
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest

import paramak
from paramak.assemblies.assembly import Assembly
from paramak.workplanes.structured_mesh import (
    dagmc_model_from_structured_meshes,
    mesh_cad_solid_surface,
    merge_tetrahedral_meshes,
    remap_mesh_names,
    mesh_revolved_layer,
    surface_meshes_from_tetrahedral_meshes,
    tetrahedralize_cad_solid,
    tetrahedralize_center_column_layer,
    tetrahedralize_revolved_layer,
    write_tetrahedral_mesh_exodus,
)


TOKAMAK_RADIAL_BUILD = [
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
]


def mesh_volume(mesh):
    """Returns the total volume represented by tetrahedra in a mesh record."""
    points = mesh["vertices"][mesh["tetrahedra"]]
    return np.abs(np.linalg.det(points[:, 1:] - points[:, :1])).sum() / 6.0


def assert_closed_surface(mesh):
    """Checks that every surface edge belongs to exactly two triangles."""
    edge_counts = Counter(
        tuple(sorted((int(first), int(second))))
        for triangle in mesh["triangles"]
        for first, second in ((triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[2], triangle[0]))
    )
    assert edge_counts
    assert set(edge_counts.values()) == {2}


def signed_surface_volume(mesh):
    triangles = mesh["vertices"][mesh["triangles"]]
    return np.einsum(
        "ij,ij->i",
        triangles[:, 0],
        np.cross(triangles[:, 1], triangles[:, 2]),
    ).sum() / 6.0


@pytest.fixture(scope="module")
def sample_profiles():
    inner = np.array([[10, 0], [11, 1], [10, 2], [9, 1], [10, 0]], dtype=float)
    outer = inner + np.array([0.5, 0.0])
    theta = np.array([0, 90, 180, 270, 360], dtype=float)
    return inner, outer, theta


def sample_tetrahedron_mesh(name="tetra"):
    return {
        "name": name,
        "vertices": np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float),
        "tetrahedra": np.array([[0, 1, 2, 3]], dtype=np.int64),
    }


@pytest.mark.parametrize(
    "full_torus,toroidal_angles",
    [(False, [0, 45, 90]), (True, [0, 90, 180, 270])],
)
def test_mesh_revolved_layer_returns_closed_surface(sample_profiles, full_torus, toroidal_angles):
    inner, outer, theta = sample_profiles
    meshes = mesh_revolved_layer(
        inner,
        outer,
        theta,
        toroidal_angles,
        full_torus=full_torus,
    )

    assert len(meshes) == 1
    assert meshes[0]["triangles"].ndim == 2
    assert meshes[0]["triangles"].shape[1] == 3
    assert meshes[0]["triangles"].max() < len(meshes[0]["vertices"])
    assert_closed_surface(meshes[0])


def test_mesh_revolved_layer_closes_each_poloidal_segment(sample_profiles):
    inner, outer, theta = sample_profiles
    meshes = mesh_revolved_layer(
        inner,
        outer,
        theta,
        [0, 60, 120],
        segments=[("upper", 0, 2), ("lower", 2, 4)],
    )

    assert [mesh["name"] for mesh in meshes] == ["upper", "lower"]
    for mesh in meshes:
        assert_closed_surface(mesh)
    assert np.array_equal(meshes[0]["vertices"][[6, 7, 8, 15, 16, 17]], meshes[1]["vertices"][[0, 1, 2, 9, 10, 11]])


def test_mesh_revolved_layer_rejects_mismatched_profiles(sample_profiles):
    inner, outer, theta = sample_profiles
    with pytest.raises(ValueError, match="matching shape"):
        mesh_revolved_layer(inner, outer[:-1], theta, [0, 90])


@pytest.mark.parametrize(
    "coil",
    [
        paramak.poloidal_field_coil(20, 10, (1000, 50), rotation_angle=90),
        paramak.poloidal_field_coil_case(20, 10, 2, (1100, 50), rotation_angle=90),
        paramak.toroidal_field_coil_rectangle(
            horizontal_start_point=(1200, 100),
            vertical_mid_point=(1350, 0),
            thickness=10,
            distance=10,
            rotation_angle=90,
            azimuthal_placement_angles=[0, 45],
        ),
        paramak.toroidal_field_coil_princeton_d(
            rotation_angle=90,
            azimuthal_placement_angles=[0, 45],
        ),
    ],
    ids=[
        "poloidal-coil",
        "poloidal-coil-case",
        "multi-placement-rectangular-toroidal-coil",
        "multi-placement-princeton-d-toroidal-coil",
    ],
)
def test_cad_coil_tessellation_produces_closed_surface_meshes(coil):
    solid_meshes = [mesh_cad_solid_surface(solid, "coil") for solid in coil.val().Solids()]

    assert solid_meshes
    for mesh in solid_meshes:
        assert_closed_surface(mesh)
        assert signed_surface_volume(mesh) > 0.0
        assert mesh["vertices"].ndim == 2
        assert mesh["triangles"].ndim == 2


def test_cad_coil_tessellation_validates_tolerance():
    coil = paramak.poloidal_field_coil(20, 10, (1000, 50), rotation_angle=90).val()
    with pytest.raises(ValueError, match="tolerance must be finite and positive"):
        mesh_cad_solid_surface(coil, "coil", tolerance=0)


def test_cad_coil_tetrahedral_mesh_uses_gmsh():
    try:
        import gmsh  # noqa: F401
    except (ImportError, OSError):
        pytest.skip("Gmsh and its shared libraries are unavailable")

    coil = paramak.poloidal_field_coil(10, 5, (100, 50), rotation_angle=90).val()
    mesh = tetrahedralize_cad_solid(coil, "coil", mesh_size=8)

    assert mesh["name"] == "coil"
    assert mesh["vertices"].ndim == 2
    assert mesh["tetrahedra"].ndim == 2
    assert mesh["tetrahedra"].shape[1] == 4
    assert np.all(mesh["tetrahedra"] < len(mesh["vertices"]))
    assert mesh_volume(mesh) > 0


def test_cad_coil_tetrahedral_mesh_reports_missing_gmsh(monkeypatch):
    monkeypatch.setitem(sys.modules, "gmsh", None)
    coil = paramak.poloidal_field_coil(10, 5, (100, 50), rotation_angle=90).val()
    with pytest.raises(ImportError, match="Gmsh is required"):
        tetrahedralize_cad_solid(coil, "coil")


def test_tetrahedralize_revolved_layer_honors_radial_subdivisions(sample_profiles):
    inner, outer, theta = sample_profiles
    meshes = tetrahedralize_revolved_layer(
        inner,
        outer,
        theta,
        [0, 90, 180, 270],
        n_radial=2,
        full_torus=True,
    )

    assert len(meshes) == 1
    assert len(meshes[0]["tetrahedra"]) == 2 * 4 * 4 * 6
    assert np.all(meshes[0]["tetrahedra"] < len(meshes[0]["vertices"]))
    assert np.all(np.isfinite(meshes[0]["vertices"]))
    with pytest.raises(ValueError, match="positive integer"):
        tetrahedralize_revolved_layer(inner, outer, theta, [0, 90], n_radial=0)


@pytest.mark.parametrize("inner_radius", [0.0, 5.0])
def test_tetrahedralize_center_column_layer_builds_valid_cylinder_mesh(inner_radius):
    meshes = tetrahedralize_center_column_layer(
        inner_radius,
        inner_radius + 2.0,
        6.0,
        [0, 90, 180, 270],
        n_axial=2,
        n_radial=2,
        full_torus=True,
        name="column",
    )

    assert len(meshes) == 1
    assert meshes[0]["name"] == "column"
    assert np.all(meshes[0]["tetrahedra"] < len(meshes[0]["vertices"]))
    tetrahedra = meshes[0]["vertices"][meshes[0]["tetrahedra"]]
    jacobians = np.einsum(
        "ij,ij->i",
        tetrahedra[:, 1] - tetrahedra[:, 0],
        np.cross(tetrahedra[:, 2] - tetrahedra[:, 0], tetrahedra[:, 3] - tetrahedra[:, 0]),
    )
    assert np.all(np.abs(jacobians) > 0.0)
    assert_closed_surface(surface_meshes_from_tetrahedral_meshes(meshes)[0])


def test_tetrahedralize_center_column_layer_validates_resolution():
    with pytest.raises(ValueError, match="n_axial"):
        tetrahedralize_center_column_layer(1, 2, 3, [0, 90], n_axial=0)
    with pytest.raises(ValueError, match="central-column radii and height"):
        tetrahedralize_center_column_layer(2, 1, 3, [0, 90])


def test_merge_tetrahedral_meshes_welds_shared_coordinates():
    meshes = [sample_tetrahedron_mesh("first"), sample_tetrahedron_mesh("second")]
    vertices, connectivity, blocks = merge_tetrahedral_meshes(meshes)

    assert vertices.shape == (4, 3)
    assert connectivity.shape == (2, 4)
    assert np.array_equal(blocks["first"], [0])
    assert np.array_equal(blocks["second"], [1])


def test_remap_mesh_names_combines_export_blocks():
    meshes = [sample_tetrahedron_mesh("first_wall_upper_sector_1"), sample_tetrahedron_mesh("first_wall_upper_sector_2")]
    remapped = remap_mesh_names(
        meshes,
        {
            "first_wall_upper_sector_1": "first_wall",
            "first_wall_upper_sector_2": "first_wall",
        },
    )

    _, connectivity, blocks = merge_tetrahedral_meshes(remapped)

    assert connectivity.shape == (2, 4)
    assert list(blocks) == ["first_wall"]
    assert np.array_equal(blocks["first_wall"], [0, 1])


def test_remap_mesh_names_rejects_unknown_names():
    with pytest.raises(ValueError, match="unknown mesh names"):
        remap_mesh_names([sample_tetrahedron_mesh("blanket")], {"misspelled": "mat"})


def test_remap_mesh_names_requires_nonempty_target_names():
    with pytest.raises(ValueError, match="non-empty strings"):
        remap_mesh_names([sample_tetrahedron_mesh("blanket")], {"blanket": ""})


def test_merge_tetrahedral_meshes_rejects_invalid_connectivity():
    mesh = sample_tetrahedron_mesh()
    mesh["tetrahedra"] = np.array([[0, 1, 2, 4]])
    with pytest.raises(IndexError, match="invalid tetrahedral connectivity"):
        merge_tetrahedral_meshes([mesh])


def test_surface_meshes_from_tetrahedra_extracts_closed_boundary():
    surfaces = surface_meshes_from_tetrahedral_meshes([sample_tetrahedron_mesh()])

    assert len(surfaces) == 1
    assert surfaces[0]["triangles"].shape == (4, 3)
    assert_closed_surface(surfaces[0])


def test_surface_meshes_from_tetrahedra_rejects_degenerate_elements():
    mesh = sample_tetrahedron_mesh()
    mesh["vertices"][3] = [1, 1, 0]
    with pytest.raises(ValueError, match="degenerate tetrahedron"):
        surface_meshes_from_tetrahedral_meshes([mesh])


def test_dagmc_conversion_creates_volumes_and_named_material_groups(monkeypatch):
    class FakeCore:
        def __init__(self):
            self.triangles = []

        def create_vertices(self, coordinates):
            return SimpleNamespace(to_array=lambda: np.arange(len(coordinates)))

        def create_elements(self, element_type, connectivity):
            self.triangles.append((element_type, connectivity))
            return np.arange(len(connectivity))

        def add_entities(self, handle, elements):
            pass

    class FakeModel:
        def __init__(self, moab):
            self.mb = moab
            self.volumes = []
            self.surfaces = []
            self.groups = []

        def create_volume(self):
            volume = SimpleNamespace(handle=object())
            self.volumes.append(volume)
            return volume

        def create_surface(self):
            surface = SimpleNamespace(handle=object(), senses=None)
            self.surfaces.append(surface)
            return surface

    class FakeGroup:
        @classmethod
        def create(cls, model, name):
            group = cls()
            group.name = name
            model.groups.append(group)
            return group

        def add_set(self, volume):
            self.volumes = getattr(self, "volumes", [])
            self.volumes.append(volume)

    moab = ModuleType("pymoab")
    moab.core = SimpleNamespace(Core=FakeCore)
    moab.types = SimpleNamespace(MBTRI="triangle")
    pydagmc = ModuleType("pydagmc")
    pydagmc.dagnav = SimpleNamespace(Model=FakeModel)
    pydagmc.Group = FakeGroup
    monkeypatch.setitem(sys.modules, "pymoab", moab)
    monkeypatch.setitem(sys.modules, "pydagmc", pydagmc)

    surfaces = surface_meshes_from_tetrahedral_meshes([sample_tetrahedron_mesh()])
    model = dagmc_model_from_structured_meshes(surfaces)

    assert len(model.volumes) == 1
    assert len(model.surfaces) == 1
    assert model.groups[0].name == "mat:tetra"
    assert len(model.groups[0].volumes) == 1
    assert sum(len(connectivity) for _, connectivity in model.mb.triangles) == 4


def test_dagmc_conversion_combines_mapped_parts_in_one_material_group(monkeypatch):
    class FakeCore:
        def create_vertices(self, coordinates):
            return SimpleNamespace(to_array=lambda: np.arange(len(coordinates)))

        def create_elements(self, element_type, connectivity):
            return np.arange(len(connectivity))

        def add_entities(self, handle, elements):
            pass

    class FakeModel:
        def __init__(self, moab):
            self.mb = moab
            self.volumes = []
            self.surfaces = []
            self.groups = []

        def create_volume(self):
            volume = SimpleNamespace(handle=object())
            self.volumes.append(volume)
            return volume

        def create_surface(self):
            surface = SimpleNamespace(handle=object(), senses=None)
            self.surfaces.append(surface)
            return surface

    class FakeGroup:
        @classmethod
        def create(cls, model, name):
            group = cls()
            group.name = name
            group.volumes = []
            model.groups.append(group)
            return group

        def add_set(self, volume):
            self.volumes.append(volume)

    moab = ModuleType("pymoab")
    moab.core = SimpleNamespace(Core=FakeCore)
    moab.types = SimpleNamespace(MBTRI="triangle")
    pydagmc = ModuleType("pydagmc")
    pydagmc.dagnav = SimpleNamespace(Model=FakeModel)
    pydagmc.Group = FakeGroup
    monkeypatch.setitem(sys.modules, "pymoab", moab)
    monkeypatch.setitem(sys.modules, "pydagmc", pydagmc)

    first = sample_tetrahedron_mesh("first_wall_upper")
    second = sample_tetrahedron_mesh("first_wall_lower")
    second["vertices"] = second["vertices"] + np.array([3, 0, 0])
    surfaces = surface_meshes_from_tetrahedral_meshes([first, second])
    model = dagmc_model_from_structured_meshes(
        surfaces,
        tag_names={"first_wall_upper": "first_wall", "first_wall_lower": "first_wall"},
    )

    assert len(model.volumes) == 2
    assert len(model.groups) == 1
    assert model.groups[0].name == "mat:first_wall"
    assert len(model.groups[0].volumes) == 2


def test_dagmc_conversion_rejects_invalid_triangle_indices(monkeypatch):
    # Imports are stubbed because the connectivity validation follows optional dependency loading.
    moab = ModuleType("pymoab")
    moab.core = SimpleNamespace(Core=object)
    moab.types = SimpleNamespace(MBTRI=0)
    pydagmc = ModuleType("pydagmc")
    pydagmc.dagnav = SimpleNamespace(Model=object)
    pydagmc.Group = object
    monkeypatch.setitem(sys.modules, "pymoab", moab)
    monkeypatch.setitem(sys.modules, "pydagmc", pydagmc)

    mesh = {"name": "bad", "vertices": np.zeros((3, 3)), "triangles": np.array([[0, 1, 3]])}
    with pytest.raises(IndexError, match="invalid triangle vertex index"):
        dagmc_model_from_structured_meshes([mesh])


def test_exodus_writer_creates_named_tetrahedral_block(tmp_path):
    netcdf4 = pytest.importorskip("netCDF4")
    mesh = sample_tetrahedron_mesh("steel")
    filename = tmp_path / "mesh.e"
    write_tetrahedral_mesh_exodus(
        mesh["vertices"],
        mesh["tetrahedra"],
        {"steel": np.array([0])},
        filename,
    )

    with netcdf4.Dataset(filename) as exodus:
        assert len(exodus.dimensions["num_elem"]) == 1
        assert exodus.variables["connect1"].elem_type == "TETRA"
        assert exodus.variables["connect1"][0].tolist() == [1, 2, 3, 4]


@pytest.fixture(scope="module")
def partial_tokamak():
    return paramak.tokamak_from_plasma(TOKAMAK_RADIAL_BUILD, rotation_angle=90)


def test_assembly_surface_mesh_supports_partial_rotation(partial_tokamak):
    meshes = partial_tokamak.mesh_structured_layers(n_poloidal=8, n_toroidal=5)

    assert meshes
    assert "layer_4" in {mesh["name"] for mesh in meshes}
    for mesh in meshes:
        assert mesh["triangles"].ndim == 2
        assert mesh["triangles"].shape[1] == 3
        assert mesh["triangles"].max() < len(mesh["vertices"])
        assert_closed_surface(mesh)
    assert {"layer_1", "layer_2"}.issubset({mesh["name"] for mesh in meshes})


def test_assembly_surface_mesh_includes_added_coils():
    reactor = paramak.tokamak_from_plasma(TOKAMAK_RADIAL_BUILD, rotation_angle=90)
    poloidal_coil = paramak.poloidal_field_coil(20, 10, (1000, 50), rotation_angle=90)
    toroidal_coil = paramak.toroidal_field_coil_rectangle(
        horizontal_start_point=(1200, 100),
        vertical_mid_point=(1350, 0),
        thickness=10,
        distance=10,
        rotation_angle=90,
        azimuthal_placement_angles=[0, 45],
    )
    reactor.add(poloidal_coil, name="poloidal_coil")
    reactor.add(toroidal_coil, name="toroidal_coil")

    meshes = reactor.mesh_structured_layers(n_poloidal=8, n_toroidal=5, n_axial=2)
    coil_meshes = {mesh["name"]: mesh for mesh in meshes if mesh["name"] in {"poloidal_coil", "toroidal_coil"}}

    assert set(coil_meshes) == {"poloidal_coil", "toroidal_coil"}
    assert len(coil_meshes["toroidal_coil"]["triangles"]) == 2 * len(
        mesh_cad_solid_surface(toroidal_coil.val().Solids()[0], "toroidal_coil")["triangles"]
    )
    for mesh in coil_meshes.values():
        assert_closed_surface(mesh)


def test_non_intersecting_coil_cutters_remain_structurally_meshable(monkeypatch):
    coil = paramak.poloidal_field_coil(20, 10, (1200, 800), rotation_angle=90)
    reactor = paramak.tokamak_from_plasma(
        TOKAMAK_RADIAL_BUILD,
        rotation_angle=90,
        extra_cut_shapes=[coil],
    )

    assert reactor.structured_layer_data is not None
    meshes = reactor.mesh_structured_layers(n_poloidal=8, n_toroidal=5, n_axial=2)
    coil_mesh = next(mesh for mesh in meshes if mesh["name"] == "poloidal_field_coil_1")
    assert_closed_surface(coil_mesh)

    from paramak.workplanes import structured_mesh

    monkeypatch.setattr(
        structured_mesh,
        "tetrahedralize_cad_solid",
        lambda solid, name, mesh_size: sample_tetrahedron_mesh(name),
    )
    volume_meshes = reactor.mesh_structured_layer_volumes(n_poloidal=8, n_toroidal=5, n_axial=2)
    assert "poloidal_field_coil_1" in {mesh["name"] for mesh in volume_meshes}


def test_assembly_volume_mesh_radial_resolution_and_validation(partial_tokamak):
    one_radial_cell = partial_tokamak.mesh_structured_layer_volumes(
        n_poloidal=8, n_toroidal=5, n_radial=1
    )
    two_radial_cells = partial_tokamak.mesh_structured_layer_volumes(
        n_poloidal=8, n_toroidal=5, n_radial=2
    )
    assert len(two_radial_cells[0]["tetrahedra"]) == 2 * len(one_radial_cell[0]["tetrahedra"])

    with pytest.raises(ValueError, match="n_poloidal"):
        partial_tokamak.mesh_structured_layers(n_poloidal=2)
    with pytest.raises(ValueError, match="n_toroidal"):
        partial_tokamak.mesh_structured_layer_volumes(n_toroidal=1)
    with pytest.raises(ValueError, match="n_radial"):
        partial_tokamak.mesh_structured_layer_volumes(n_radial=0)
    with pytest.raises(ValueError, match="n_axial"):
        partial_tokamak.mesh_structured_layer_volumes(n_axial=0)
    with pytest.raises(ValueError, match="generated tokamak"):
        Assembly().mesh_structured_layers()


def test_assembly_volume_mesh_includes_named_center_column_layers(partial_tokamak):
    meshes = partial_tokamak.mesh_structured_layer_volumes(
        n_poloidal=8,
        n_toroidal=5,
        n_radial=2,
        n_axial=3,
    )
    center_column_meshes = [mesh for mesh in meshes if mesh["name"] in {"layer_1", "layer_2"}]

    assert {mesh["name"] for mesh in center_column_meshes} == {"layer_1", "layer_2"}
    for mesh in center_column_meshes:
        assert len(mesh["tetrahedra"])
        assert np.all(np.isfinite(mesh["vertices"]))


def test_partial_toroidal_sectors_mesh_as_distinct_regions():
    rotation_angle = 90.0
    arc_length = paramak.toroidal_arc_length(TOKAMAK_RADIAL_BUILD, rotation_angle)
    sectors = [
        (paramak.LayerType.SOLID, arc_length / 2, "half"),
        (paramak.LayerType.SOLID, arc_length / 2, "half"),
    ]
    reactor = paramak.tokamak_from_plasma(
        TOKAMAK_RADIAL_BUILD,
        rotation_angle=rotation_angle,
        toroidal_build=[None, None, sectors, None],
    )

    meshes = reactor.mesh_structured_layer_volumes(n_poloidal=8, n_toroidal=8)
    sector_meshes = [mesh for mesh in meshes if mesh["name"].startswith("layer_4_half_")]

    assert sorted(mesh["name"] for mesh in sector_meshes) == ["layer_4_half_1", "layer_4_half_2"]
    unsegmented = paramak.tokamak_from_plasma(TOKAMAK_RADIAL_BUILD, rotation_angle=rotation_angle)
    baseline = unsegmented.mesh_structured_layer_volumes(n_poloidal=8, n_toroidal=8)
    baseline_layer = next(mesh for mesh in baseline if mesh["name"] == "layer_4")
    assert sum(mesh_volume(mesh) for mesh in sector_meshes) == pytest.approx(mesh_volume(baseline_layer), rel=1e-3)


def test_assembly_poloidal_segments_mesh_as_named_closed_surfaces():
    arc_length = paramak.poloidal_arc_length(TOKAMAK_RADIAL_BUILD)
    half_arc = arc_length / 2
    tiles = [
        (paramak.LayerType.SOLID, half_arc, "upper"),
        (paramak.LayerType.SOLID, half_arc, "lower"),
    ]
    reactor = paramak.tokamak_from_plasma(
        TOKAMAK_RADIAL_BUILD,
        rotation_angle=90,
        poloidal_build=[None, tiles, None, None],
    )

    meshes = reactor.mesh_structured_layers(n_poloidal=8, n_toroidal=5)
    tile_meshes = [mesh for mesh in meshes if mesh["name"].startswith("layer_3_")]

    assert {mesh["name"] for mesh in tile_meshes} == {"layer_3_upper", "layer_3_lower"}
    for mesh in tile_meshes:
        assert_closed_surface(mesh)


def test_assembly_divertor_mesh_replaces_blanket_cells():
    reactor = paramak.tokamak_from_plasma(TOKAMAK_RADIAL_BUILD, rotation_angle=90)
    reactor = reactor.add_divertor(75, 30, ["mesh_divertor"], [20])

    volume_meshes = reactor.mesh_structured_layer_volumes(n_poloidal=12, n_toroidal=5, n_radial=2)
    surface_meshes = reactor.mesh_structured_layers(n_poloidal=12, n_toroidal=5)

    divertor_volume_meshes = [mesh for mesh in volume_meshes if mesh["name"] == "mesh_divertor"]
    divertor_surface_meshes = [mesh for mesh in surface_meshes if mesh["name"] == "mesh_divertor"]
    assert len(divertor_volume_meshes) == 1
    assert len(divertor_surface_meshes) == 1
    assert len(divertor_volume_meshes[0]["tetrahedra"])
    assert_closed_surface(divertor_surface_meshes[0])


def test_divertor_mesh_handles_crossing_inboard_and_outboard_interfaces():
    radial_build = [
        (paramak.LayerType.GAP, 412.1),
        (paramak.LayerType.SOLID, 90, "cs_coil"),
        (paramak.LayerType.GAP, 4),
        (paramak.LayerType.SOLID, 10, "bss"),
        (paramak.LayerType.SOLID, 15.5, "water_manifold"),
        (paramak.LayerType.SOLID, 17.4, "pbli_manifold"),
        (paramak.LayerType.SOLID, 33.02, "bz"),
        (paramak.LayerType.SOLID, 2.5, "fw"),
        (paramak.LayerType.SOLID, 0.2, "armor"),
        (paramak.LayerType.GAP, 22.5),
        (paramak.LayerType.PLASMA, 576.6),
        (paramak.LayerType.GAP, 22.5),
        (paramak.LayerType.SOLID, 0.2),
        (paramak.LayerType.SOLID, 2.5),
        (paramak.LayerType.SOLID, 53.8),
        (paramak.LayerType.SOLID, 17.4),
        (paramak.LayerType.SOLID, 15.5),
        (paramak.LayerType.SOLID, 10),
    ]
    reactor = paramak.tokamak_from_plasma(
        radial_build,
        elongation=1.65,
        triangularity=0.33,
        rotation_angle=180,
    )
    reactor = reactor.add_divertor(
        75, 30,
        ["upper_divertor_armor", "upper_divertor_heatsink", "upper_divertor_shield"],
        [0.2, 2.5, 40],
    )
    reactor = reactor.add_divertor(
        255, 30,
        ["lower_divertor_armor", "lower_divertor_heatsink", "lower_divertor_shield"],
        [0.2, 2.5, 40],
    )

    meshes = reactor.mesh_structured_layer_volumes(n_poloidal=32, n_toroidal=5, n_axial=2)

    assert {mesh["name"] for mesh in meshes} >= {
        "upper_divertor_armor",
        "upper_divertor_heatsink",
        "upper_divertor_shield",
        "lower_divertor_armor",
        "lower_divertor_heatsink",
        "lower_divertor_shield",
    }


def test_assembly_dagmc_and_exodus_methods_delegate_to_mesh_converters(monkeypatch, partial_tokamak, tmp_path):
    from paramak.workplanes import structured_mesh

    observed = {}
    dagmc_result = object()

    def create_dagmc(meshes, tag_names=None):
        observed["dagmc_meshes"] = meshes
        observed["dagmc_tag_names"] = tag_names
        return dagmc_result

    def merge_meshes(meshes):
        observed["volume_meshes"] = meshes
        return np.zeros((4, 3)), np.array([[0, 1, 2, 3]]), {"layer": np.array([0])}

    def write_exodus(vertices, connectivity, blocks, filename):
        observed["exodus_args"] = (vertices, connectivity, blocks, filename)
        return filename

    monkeypatch.setattr(structured_mesh, "dagmc_model_from_structured_meshes", create_dagmc)
    monkeypatch.setattr(structured_mesh, "merge_tetrahedral_meshes", merge_meshes)
    monkeypatch.setattr(structured_mesh, "write_tetrahedral_mesh_exodus", write_exodus)

    tag_names = {"layer_1": "first_wall"}
    assert partial_tokamak.create_structured_layer_dagmc_model(
        n_poloidal=8, n_toroidal=5, tag_names=tag_names
    ) is dagmc_result
    output = tmp_path / "assembly.e"
    assert partial_tokamak.export_structured_layers_exodus(
        output, n_poloidal=8, n_toroidal=5, n_radial=2, tag_names=tag_names
    ) == output
    assert observed["dagmc_meshes"]
    assert observed["volume_meshes"]
    assert observed["exodus_args"][3] == output
    assert {mesh["name"] for mesh in observed["dagmc_meshes"]}.issuperset({"layer_1", "layer_2"})
    assert observed["dagmc_tag_names"] == tag_names
    assert {mesh["name"] for mesh in observed["volume_meshes"]}.issuperset({"first_wall", "layer_2"})


def test_full_torus_structured_mesh_keeps_toroidal_sector_gaps():
    """A full-turn mesh has four separate sectors and leaves their gaps empty."""
    rotation_angle = 360.0
    arc_length = paramak.toroidal_arc_length(TOKAMAK_RADIAL_BUILD, rotation_angle)
    gap_width = 30.0
    sector_length = (arc_length - 4 * gap_width) / 4
    sectors = [
        (paramak.LayerType.SOLID, sector_length, "sector"),
        (paramak.LayerType.GAP, gap_width),
    ] * 4

    unsegmented = paramak.tokamak_from_plasma(
        radial_build=TOKAMAK_RADIAL_BUILD,
        rotation_angle=rotation_angle,
    )
    segmented = paramak.tokamak_from_plasma(
        radial_build=TOKAMAK_RADIAL_BUILD,
        rotation_angle=rotation_angle,
        toroidal_build=[None, None, sectors, None],
    )

    unsegmented_meshes = unsegmented.mesh_structured_layer_volumes(n_poloidal=16, n_toroidal=12)
    segmented_meshes = segmented.mesh_structured_layer_volumes(n_poloidal=16, n_toroidal=12)

    sector_names = [f"layer_4_sector_{index}" for index in range(1, 5)]
    sector_meshes = [mesh for mesh in segmented_meshes if mesh["name"] in sector_names]
    assert sorted(mesh["name"] for mesh in sector_meshes) == sector_names

    segmented_volume = sum(mesh_volume(mesh) for mesh in sector_meshes)
    unsegmented_layer = next(mesh for mesh in unsegmented_meshes if mesh["name"] == "layer_4")
    assert segmented_volume < 0.99 * mesh_volume(unsegmented_layer)
