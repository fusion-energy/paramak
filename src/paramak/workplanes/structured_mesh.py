"""Structured triangular surface meshes for toroidally swept layers.

This module is the low-level starting point for a structured Paramak-to-DAGMC
workflow.  It meshes a poloidal strip between matching inner and outer R-Z
curves.  Segment boundaries are indices into the shared poloidal grid, so
neighboring segments use the same boundary vertices.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np


def _quad_triangles(a, b, c, d, reverse=False):
    """Split a quad into two triangles, keeping a consistent diagonal."""
    triangles = [(a, b, c), (a, c, d)]
    return [(triangle[0], triangle[2], triangle[1]) for triangle in triangles] if reverse else triangles


def tetrahedralize_revolved_layer(
    inner_profile,
    outer_profile,
    poloidal_angles,
    toroidal_angles,
    *,
    n_radial=1,
    full_torus=False,
    segments=None,
):
    """Create structured tetrahedral volume meshes for swept tokamak layers.

    Each structured hexahedral cell is split into six tetrahedra using a
    consistent face diagonal, allowing adjacent layers and poloidal segments
    to share conformal interfaces.

    Parameters
    ----------
    inner_profile, outer_profile : array-like, shape (n, 2)
        Matching ``(R, Z)`` coordinates in centimetres for the layer's inner
        and outer poloidal boundaries. Coordinates at each index correspond.
    poloidal_angles : array-like, shape (n,)
        Poloidal sample angles in degrees. They define the profile ordering.
    toroidal_angles : array-like, shape (m,)
        Toroidal sample angles in degrees. Partial tori include both end
        angles; full tori omit a duplicate 360-degree seam sample.
    n_radial : int, optional
        Number of subdivisions from the inner to outer profile. Must be at
        least 1. Defaults to 1.
    full_torus : bool, optional
        If true, connect the last toroidal sample to the first. Otherwise,
        create end faces at the first and last samples. Defaults to false.
    segments : sequence of (name, start_index, stop_index), optional
        Inclusive index ranges into the shared poloidal profile. Each segment
        produces one mesh record. Adjacent segments should share an endpoint
        index. If omitted, one closed-poloidal mesh is returned.

    Returns
    -------
    list of dict
        One record per segment. Each record contains ``name``, ``vertices``
        (``(n_vertices, 3)`` coordinates in centimetres), and ``tetrahedra``
        (``(n_tetrahedra, 4)`` zero-based vertex indices).
    """
    if not isinstance(n_radial, int) or n_radial < 1:
        raise ValueError("n_radial must be a positive integer")
    inner = np.asarray(inner_profile, dtype=float)
    outer = np.asarray(outer_profile, dtype=float)
    theta = np.asarray(poloidal_angles, dtype=float)
    phi = np.asarray(toroidal_angles, dtype=float)
    if inner.ndim != 2 or inner.shape[1] != 2 or outer.shape != inner.shape:
        raise ValueError("inner_profile and outer_profile must have matching shape (n, 2)")
    if theta.shape != (len(inner),) or len(theta) < 2:
        raise ValueError("poloidal_angles must have one value per profile point and at least two points")
    if phi.ndim != 1 or len(phi) < (3 if full_torus else 2):
        raise ValueError("toroidal_angles must be one-dimensional with enough points for the selected extent")
    if not np.all(np.isfinite(inner)) or not np.all(np.isfinite(outer)):
        raise ValueError("profile coordinates must be finite")

    if segments is None:
        segments = [(None, 0, len(theta) - 1)]
        closed_poloidal = True
    else:
        segments = list(segments)
        closed_poloidal = False
    if not segments:
        raise ValueError("at least one poloidal segment is required")

    result = []
    n_phi = len(phi)
    phi_cells = n_phi if full_torus else n_phi - 1
    tet_patterns = (
        (0, 1, 3, 7),
        (0, 3, 2, 7),
        (0, 2, 6, 7),
        (0, 6, 4, 7),
        (0, 4, 5, 7),
        (0, 5, 1, 7),
    )

    for name, start, stop in segments:
        if start < 0 or stop >= len(theta) or stop - start < 1:
            raise ValueError(f"invalid poloidal index range for segment {name!r}: ({start}, {stop})")
        indices = np.arange(start, stop + 1)
        if closed_poloidal and len(indices) > 2:
            if np.allclose(inner[indices[0]], inner[indices[-1]]) and np.allclose(
                outer[indices[0]], outer[indices[-1]]
            ):
                indices = indices[:-1]

        radial_fractions = np.linspace(0.0, 1.0, n_radial + 1)
        profile = inner[indices][None, :, :] + radial_fractions[:, None, None] * (
            outer[indices] - inner[indices]
        )[None, :, :]
        n_theta = len(indices)
        points = np.empty((n_radial + 1, n_theta, n_phi, 3), dtype=float)
        for radial_index in range(n_radial + 1):
            for theta_index in range(n_theta):
                radius, z = profile[radial_index, theta_index]
                points[radial_index, theta_index, :, 0] = radius * np.cos(np.deg2rad(phi))
                points[radial_index, theta_index, :, 1] = radius * np.sin(np.deg2rad(phi))
                points[radial_index, theta_index, :, 2] = z
        vertices = points.reshape((-1, 3))

        def vertex(radial_index, theta_index, phi_index):
            return (radial_index * n_theta + theta_index) * n_phi + phi_index

        theta_cells = n_theta if closed_poloidal else n_theta - 1
        tetrahedra = []
        for i in range(n_radial):
            for j in range(theta_cells):
                j_next = (j + 1) % n_theta
                for k in range(phi_cells):
                    k_next = (k + 1) % n_phi
                    corners = (
                        vertex(i, j, k),
                        vertex(i + 1, j, k),
                        vertex(i, j_next, k),
                        vertex(i + 1, j_next, k),
                        vertex(i, j, k_next),
                        vertex(i + 1, j, k_next),
                        vertex(i, j_next, k_next),
                        vertex(i + 1, j_next, k_next),
                    )
                    tetrahedra.extend(tuple(corners[index] for index in pattern) for pattern in tet_patterns)

        result.append(
            {
                "name": name,
                "vertices": vertices,
                "tetrahedra": np.asarray(tetrahedra, dtype=np.int64),
            }
        )
    return result


def tetrahedralize_center_column_layer(
    inner_radius,
    outer_radius,
    height,
    toroidal_angles,
    *,
    n_axial=16,
    n_radial=1,
    full_torus=False,
    name=None,
):
    """Create a structured tetrahedral mesh for a central-column cylinder.

    Parameters
    ----------
    inner_radius, outer_radius : float
        Inner and outer radii in centimetres. The inner radius may be zero;
        the outer radius must be larger.
    height : float
        Full axial height in centimetres. The cylinder is centered on Z=0.
    toroidal_angles : array-like
        Toroidal sample angles in degrees. For a partial torus, include both
        end angles; for a full torus, omit the duplicate seam angle.
    n_axial : int, optional
        Number of intervals along the cylinder height. Must be at least 1.
        Defaults to 16.
    n_radial : int, optional
        Number of intervals across the cylinder wall. Must be at least 1.
        Defaults to 1.
    full_torus : bool, optional
        Connect the final toroidal sample to the first when true. Defaults to
        false.
    name : str, optional
        Name stored in the returned mesh record. Defaults to ``None``.

    Returns
    -------
    list of dict
        A one-record list containing ``name``, ``vertices`` (coordinates in
        centimetres), and ``tetrahedra`` (zero-based vertex indices).
    """
    values = np.asarray([inner_radius, outer_radius, height], dtype=float)
    if not np.all(np.isfinite(values)) or inner_radius < 0 or outer_radius <= inner_radius or height <= 0:
        raise ValueError("central-column radii and height must be finite and satisfy 0 <= inner < outer, height > 0")
    if not isinstance(n_axial, int) or n_axial < 1:
        raise ValueError("n_axial must be a positive integer")

    z = np.linspace(-height / 2, height / 2, n_axial + 1)
    inner_profile = np.column_stack((np.full(n_axial + 1, inner_radius), z))
    outer_profile = np.column_stack((np.full(n_axial + 1, outer_radius), z))
    meshes = tetrahedralize_revolved_layer(
        inner_profile,
        outer_profile,
        np.arange(n_axial + 1, dtype=float),
        toroidal_angles,
        n_radial=n_radial,
        full_torus=full_torus,
        segments=[(name, 0, n_axial)],
    )

    # A solid cylinder has a repeated axis vertex at every toroidal sample.
    # Weld those coincident points and discard the degenerate tetrahedra at
    # the axis so the resulting mesh remains a valid volume mesh.
    if inner_radius == 0.0:
        mesh = meshes[0]
        vertices, inverse = np.unique(np.round(mesh["vertices"], decimals=10), axis=0, return_inverse=True)
        tetrahedra = inverse[mesh["tetrahedra"]]
        points = vertices[tetrahedra]
        jacobians = np.einsum(
            "ij,ij->i", points[:, 1] - points[:, 0], np.cross(points[:, 2] - points[:, 0], points[:, 3] - points[:, 0])
        )
        scale = max(outer_radius, height, 1.0)
        tetrahedra = tetrahedra[np.abs(jacobians) > np.finfo(float).eps * scale**3 * 32]
        meshes[0] = {"name": name, "vertices": vertices, "tetrahedra": tetrahedra}
    return meshes


def merge_tetrahedral_meshes(meshes):
    """Merge named component tetrahedral meshes into a shared-node mesh.

    Parameters
    ----------
    meshes : iterable of dict
        Mesh records. Each record must contain ``vertices`` with shape
        ``(n, 3)``, ``tetrahedra`` with shape ``(m, 4)``, and may contain a
        ``name`` used for its output block. Coordinates are in centimetres;
        connectivity indices are zero-based.

    Returns
    -------
    tuple
        ``(vertices, connectivity, blocks)``. ``vertices`` is an
        ``(n, 3)`` float array, ``connectivity`` is an ``(m, 4)`` integer
        array, and ``blocks`` maps each mesh name to the zero-based indices
        of its tetrahedra. Matching coordinates are welded, and records with
        the same name are grouped into one block.
    """
    vertex_ids = {}
    coordinates = []
    cells = []
    blocks = {}
    for mesh in meshes:
        points = np.asarray(mesh["vertices"], dtype=float)
        tetrahedra = np.asarray(mesh["tetrahedra"], dtype=np.int64)
        if points.ndim != 2 or points.shape[1] != 3:
            raise ValueError("mesh vertices must have shape (n, 3)")
        if tetrahedra.ndim != 2 or tetrahedra.shape[1] != 4:
            raise ValueError("mesh tetrahedra must have shape (n, 4)")
        if np.any(tetrahedra < 0) or np.any(tetrahedra >= len(points)):
            raise IndexError(f"mesh {mesh.get('name')!r} has invalid tetrahedral connectivity")

        local_to_global = []
        for point in points:
            key = tuple(np.round(point, decimals=10))
            if key not in vertex_ids:
                vertex_ids[key] = len(coordinates)
                coordinates.append(point)
            local_to_global.append(vertex_ids[key])

        block_name = str(mesh.get("name") or "material")
        block_indices = blocks.setdefault(block_name, [])
        for tetrahedron in tetrahedra:
            block_indices.append(len(cells))
            cells.append([local_to_global[int(index)] for index in tetrahedron])

    if not cells:
        raise ValueError("cannot export an empty tetrahedral mesh")
    return (
        np.ascontiguousarray(coordinates, dtype=np.float64),
        np.asarray(cells, dtype=np.int64),
        {name: np.asarray(indices, dtype=np.int64) for name, indices in blocks.items()},
    )


def remap_mesh_names(meshes, tag_names=None):
    """Return mesh records with optional source-to-export name mappings.

    Parameters
    ----------
    meshes : iterable of dict
        Mesh records containing a ``name`` field. Other record fields are
        copied unchanged.
    tag_names : mapping of str to str, optional
        Mapping from existing mesh names to export names. Names not present
        in the mapping remain unchanged. Multiple source names may map to one
        target name, grouping their tetrahedra into one Exodus block or their
        volumes into one DAGMC material group. Every mapping key must match a
        name in ``meshes``; values must be non-empty strings.

    Returns
    -------
    list of dict
        Copies of the input records with mapped ``name`` values.

    Raises
    ------
    TypeError
        If ``tag_names`` is not a mapping.
    ValueError
        If a key or value is empty or non-string, or a key does not match an
        input mesh name.
    """
    mesh_records = list(meshes)
    if tag_names is None:
        return mesh_records
    if not isinstance(tag_names, Mapping):
        raise TypeError("tag_names must be a mapping from mesh names to export names")

    for source, target in tag_names.items():
        if not isinstance(source, str) or not source.strip() or not isinstance(target, str) or not target.strip():
            raise ValueError("tag_names keys and values must be non-empty strings")

    known_names = {str(mesh.get("name") or "material") for mesh in mesh_records}
    unknown_names = set(tag_names) - known_names
    if unknown_names:
        names = ", ".join(sorted(map(str, unknown_names)))
        raise ValueError(f"tag_names contains unknown mesh names: {names}")

    remapped = []
    for mesh in mesh_records:
        name = str(mesh.get("name") or "material")
        remapped.append({**mesh, "name": tag_names.get(name, name)})
    return remapped


def surface_meshes_from_tetrahedral_meshes(meshes):
    """Extract closed, outward-oriented boundary triangles from tetra meshes.

    Parameters
    ----------
    meshes : iterable of dict
        Tetrahedral mesh records. Each must contain ``name``, ``vertices``
        with shape ``(n, 3)``, and ``tetrahedra`` with shape ``(m, 4)``.
        Connectivity is zero-based and coordinates use centimetres.

    Returns
    -------
    list of dict
        Surface records with ``name``, ``vertices`` and outward-oriented
        ``triangles`` (zero-based vertex indices). Interior faces shared by
        two tetrahedra are omitted.
    """
    result = []
    face_patterns = ((1, 2, 3), (0, 3, 2), (0, 1, 3), (0, 2, 1))
    for mesh in meshes:
        points = np.asarray(mesh["vertices"], dtype=float)
        tetrahedra = np.asarray(mesh["tetrahedra"], dtype=np.int64)
        faces = {}
        for tetrahedron in tetrahedra:
            tet = tetrahedron.copy()
            tet_points = points[tet]
            a, b, c, d = tet_points
            signed_jacobian = np.dot(b - a, np.cross(c - a, d - a))
            if signed_jacobian == 0.0 or not np.isfinite(signed_jacobian):
                raise ValueError(f"mesh {mesh.get('name')!r} contains a degenerate tetrahedron")
            if signed_jacobian < 0.0:
                tet[[2, 3]] = tet[[3, 2]]
                tet_points = points[tet]
            tet_centroid = tet_points.mean(axis=0)
            for pattern in face_patterns:
                face = tet[list(pattern)]
                face_points = points[face]
                normal = np.cross(face_points[1] - face_points[0], face_points[2] - face_points[0])
                if np.dot(normal, tet_centroid - face_points.mean(axis=0)) > 0.0:
                    face = face[[0, 2, 1]]
                key = tuple(sorted(int(index) for index in face))
                faces.setdefault(key, []).append(tuple(int(index) for index in face))
        if any(len(occurrences) > 2 for occurrences in faces.values()):
            raise ValueError(f"mesh {mesh.get('name')!r} has a non-manifold tetrahedral face")
        boundary = [occurrences[0] for occurrences in faces.values() if len(occurrences) == 1]
        if not boundary:
            raise ValueError(f"mesh {mesh.get('name')!r} has no exterior faces")
        result.append(
            {
                "name": mesh.get("name"),
                "vertices": points,
                "triangles": np.asarray(boundary, dtype=np.int64),
            }
        )
    return result


def write_tetrahedral_mesh_exodus(vertices, connectivity, blocks, exodus_filename, conversion_factor=1.0):
    """Write a named tetrahedral mesh directly to an Exodus/Genesis file.

    ``netCDF4`` is imported only when called. Connectivity and block indices
    are zero-based on input; Exodus stores them one-based.

    Parameters
    ----------
    vertices : array-like, shape (n, 3)
        Mesh node coordinates. Paramak meshes use centimetres.
    connectivity : array-like, shape (m, 4)
        Zero-based indices into ``vertices``, with one row per tetrahedron.
    blocks : mapping of str to array-like
        Element block names mapped to zero-based indices into
        ``connectivity``. Every tetrahedron must appear in exactly one block.
    exodus_filename : str or path-like
        Destination Exodus/Genesis file path.
    conversion_factor : float, optional
        Positive scale multiplied by each coordinate before writing. Use
        ``1.0`` to preserve centimetres. Defaults to 1.0.

    Returns
    -------
    str or path-like
        The destination path supplied as ``exodus_filename``.
    """
    try:
        import netCDF4
    except ImportError as error:
        raise ImportError("netCDF4 is required for direct Exodus writing") from error

    points = np.array(vertices, dtype=np.float64, copy=True)
    cells = np.asarray(connectivity, dtype=np.int64).copy()
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("vertices must have shape (n, 3)")
    if cells.ndim != 2 or cells.shape[1] != 4:
        raise ValueError("connectivity must have shape (n, 4)")
    if np.any(cells < 0) or np.any(cells >= len(points)):
        raise IndexError("tetrahedral connectivity references an invalid vertex")
    if not blocks:
        raise ValueError("at least one named Exodus block is required")
    if not np.all(np.isfinite(points)) or not np.isfinite(conversion_factor) or conversion_factor <= 0:
        raise ValueError("coordinates and conversion_factor must be finite, with conversion_factor positive")
    points *= conversion_factor

    first, second, third, fourth = (points[cells[:, index]] for index in range(4))
    jacobians = np.einsum("ij,ij->i", second - first, np.cross(third - first, fourth - first))
    inverted = jacobians < 0.0
    cells[inverted, 2], cells[inverted, 3] = cells[inverted, 3].copy(), cells[inverted, 2].copy()
    if not np.all(np.isfinite(jacobians)) or np.any(jacobians == 0.0):
        raise ValueError("tetrahedral mesh contains degenerate or invalid elements")

    block_cells = []
    names = []
    covered = set()
    for name, indices in blocks.items():
        indices = np.asarray(list(indices), dtype=np.int64)
        if np.any(indices < 0) or np.any(indices >= len(cells)):
            raise IndexError(f"element index outside tetrahedral range in block {name!r}")
        if len(indices) == 0:
            raise ValueError(f"Exodus block {name!r} is empty")
        if covered.intersection(indices.tolist()):
            raise ValueError("Exodus element blocks overlap")
        covered.update(indices.tolist())
        block_cells.append(cells[indices] + 1)
        names.append(str(name))
    if len(covered) != len(cells):
        raise ValueError("Exodus element blocks do not cover every tetrahedron")
    encoded_names = [name[:32] for name in names]
    if len(set(encoded_names)) != len(encoded_names):
        raise ValueError("Exodus block names must remain unique after truncation to 32 characters")

    with netCDF4.Dataset(str(exodus_filename), "w") as exodus:
        exodus.title = "Tetrahedral mesh generated by Paramak"
        exodus.version = np.float32(5.1)
        exodus.api_version = np.float32(5.1)
        exodus.floating_point_word_size = 8
        exodus.createDimension("num_nodes", len(points))
        exodus.createDimension("num_dim", 3)
        exodus.createDimension("num_elem", len(cells))
        exodus.createDimension("num_el_blk", len(block_cells))
        exodus.createDimension("len_string", 33)
        exodus.createDimension("time_step", None)
        exodus.createVariable("time_whole", "f4", ("time_step",))[:] = [0.0]

        coordinate_names = exodus.createVariable("coor_names", "S1", ("num_dim", "len_string"))
        for axis, name in enumerate(("X", "Y", "Z")):
            coordinate_names[axis, 0] = name.encode()
        exodus.createVariable("coord", "f8", ("num_dim", "num_nodes"))[:] = points.T

        properties = exodus.createVariable("eb_prop1", "i4", ("num_el_blk",))
        element_names = exodus.createVariable("eb_names", "S1", ("num_el_blk", "len_string"))
        element_names.set_auto_mask(False)
        for block_index, (name, block) in enumerate(zip(encoded_names, block_cells)):
            properties[block_index] = block_index + 1
            for character_index, character in enumerate(name):
                element_names[block_index, character_index] = character.encode()
            block_number = block_index + 1
            exodus.createDimension(f"num_el_in_blk{block_number}", len(block))
            exodus.createDimension(f"num_nod_per_el{block_number}", 4)
            connectivity_variable = exodus.createVariable(
                f"connect{block_number}",
                "i8",
                (f"num_el_in_blk{block_number}", f"num_nod_per_el{block_number}"),
            )
            connectivity_variable.elem_type = "TETRA"
            connectivity_variable[:] = block
    return exodus_filename


def mesh_revolved_layer(
    inner_profile,
    outer_profile,
    poloidal_angles,
    toroidal_angles,
    *,
    full_torus=False,
    closed_poloidal=None,
    segments=None,
):
    """Mesh a swept layer as one or more closed triangular surface meshes.

    Parameters
    ----------
    inner_profile, outer_profile : array-like, shape (n, 2)
        Matching ``(R, Z)`` coordinates in centimetres of the layer's inner
        and outer poloidal boundaries. Coordinates at the same index must
        correspond.
    poloidal_angles : array-like, shape (n,)
        Poloidal sample angles in degrees.  This is retained as metadata for
        callers; the profiles themselves define the mesh coordinates.
    toroidal_angles : array-like, shape (m,)
        Toroidal sample angles in degrees.  For a partial torus, include both
        end angles.  For a full torus, omit the duplicate seam angle.
    full_torus : bool, optional
        Join the final toroidal row to the first rather than creating end
        caps. Set this when the samples span a complete 360-degree torus.
    closed_poloidal : bool, optional
        Join the final poloidal row to the first rather than creating segment
        end caps. By default, this is true when ``segments`` is omitted.
    segments : sequence of (name, start_index, stop_index), optional
        Inclusive ``(start_index, stop_index)`` ranges into the shared
        poloidal grid, paired with each segment's name. Adjacent segments
        should share their boundary index. If omitted, one mesh is returned
        for the whole poloidal profile.

    Returns
    -------
    list of dict
        Each entry has ``name``, ``vertices`` (``(n, 3)`` float array), and
        ``triangles`` (``(n, 3)`` integer array).  The meshes are closed: the
        inner and outer swept faces, poloidal segment ends, and (for partial
        tori) toroidal end caps are included. Vertex coordinates are in
        centimetres; angle arrays in the record are in degrees.

    Notes
    -----
    This function only constructs surface meshes.  It does not create DAGMC
    volumes or perform CAD booleans.  Use the same poloidal and toroidal grids
    for adjacent layers to obtain matching interface triangles.
    """
    inner = np.asarray(inner_profile, dtype=float)
    outer = np.asarray(outer_profile, dtype=float)
    theta = np.asarray(poloidal_angles, dtype=float)
    phi = np.asarray(toroidal_angles, dtype=float)

    if inner.ndim != 2 or inner.shape[1] != 2 or outer.shape != inner.shape:
        raise ValueError("inner_profile and outer_profile must have matching shape (n, 2)")
    if theta.shape != (len(inner),) or len(theta) < 2:
        raise ValueError("poloidal_angles must have one value per profile point and at least two points")
    if phi.ndim != 1 or len(phi) < (3 if full_torus else 2):
        raise ValueError("toroidal_angles must be one-dimensional with enough points for the selected extent")
    if not np.all(np.isfinite(inner)) or not np.all(np.isfinite(outer)):
        raise ValueError("profile coordinates must be finite")
    if not np.all(np.isfinite(theta)) or not np.all(np.isfinite(phi)):
        raise ValueError("poloidal and toroidal angles must be finite")

    if closed_poloidal is None:
        closed_poloidal = segments is None
    if segments is None:
        segments = [(None, 0, len(theta) - 1)]
    else:
        segments = list(segments)
    if not segments:
        raise ValueError("at least one poloidal segment is required")
    for name, start, stop in segments:
        if not isinstance(start, (int, np.integer)) or not isinstance(stop, (int, np.integer)):
            raise TypeError("segment start and stop must be integer profile indices")
        if start < 0 or stop >= len(theta) or stop - start < 1:
            raise ValueError(f"invalid poloidal index range for segment {name!r}: ({start}, {stop})")

    result = []
    n_phi = len(phi)
    phi_cells = n_phi if full_torus else n_phi - 1

    for name, start, stop in segments:
        indices = np.arange(start, stop + 1)
        if closed_poloidal and len(indices) > 2:
            if np.allclose(inner[indices[0]], inner[indices[-1]]) and np.allclose(
                outer[indices[0]], outer[indices[-1]]
            ):
                indices = indices[:-1]
        # Vertex order: inner/outer boundary, poloidal index, toroidal index.
        points = np.empty((2, len(indices), n_phi, 3), dtype=float)
        for radial_index, profile in enumerate((inner, outer)):
            for local_theta, profile_index in enumerate(indices):
                radius, z = profile[profile_index]
                points[radial_index, local_theta, :, 0] = radius * np.cos(np.deg2rad(phi))
                points[radial_index, local_theta, :, 1] = radius * np.sin(np.deg2rad(phi))
                points[radial_index, local_theta, :, 2] = z
        vertices = points.reshape((-1, 3))

        def vertex(radial_index, local_theta, toroidal_index):
            return (radial_index * len(indices) + local_theta) * n_phi + toroidal_index

        triangles = []
        theta_cells = len(indices) if closed_poloidal else len(indices) - 1

        # Inner and outer swept faces.
        for radial_index in (0, 1):
            for j in range(theta_cells):
                for k in range(phi_cells):
                    k_next = (k + 1) % n_phi
                    j_next = (j + 1) % len(indices) if closed_poloidal else j + 1
                    quad = (
                        vertex(radial_index, j, k),
                        vertex(radial_index, j_next, k),
                        vertex(radial_index, j_next, k_next),
                        vertex(radial_index, j, k_next),
                    )
                    triangles.extend(_quad_triangles(*quad, reverse=radial_index == 1))

        # Poloidal segment end faces.
        if not closed_poloidal:
            for j in (0, theta_cells):
                for k in range(phi_cells):
                    k_next = (k + 1) % n_phi
                    quad = (
                        vertex(0, j, k),
                        vertex(1, j, k),
                        vertex(1, j, k_next),
                        vertex(0, j, k_next),
                    )
                    triangles.extend(_quad_triangles(*quad, reverse=j == 0))

        # Toroidal end caps for a partial torus.
        if not full_torus:
            for k in (0, n_phi - 1):
                for j in range(theta_cells):
                    j_next = (j + 1) % len(indices) if closed_poloidal else j + 1
                    quad = (
                        vertex(0, j, k),
                        vertex(0, j_next, k),
                        vertex(1, j_next, k),
                        vertex(1, j, k),
                    )
                    triangles.extend(_quad_triangles(*quad, reverse=k == 0))

        result.append(
            {
                "name": name,
                "vertices": vertices,
                "triangles": np.asarray(triangles, dtype=np.int64),
                "poloidal_angles": theta[indices].copy(),
                "toroidal_angles": phi.copy(),
            }
        )

    return result


def mesh_cad_solid_surface(solid, name, tolerance=0.5, angular_tolerance=0.1):
    """Tessellate a CadQuery solid into a closed triangular surface mesh.

    Parameters
    ----------
    solid : cadquery.Shape
        CAD solid to tessellate. The solid's coordinates are used as-is.
    name : str
        Name stored in the returned mesh record and later used as its
        material or component name.
    tolerance : float, optional
        Linear tessellation tolerance in the model's length units (centimetres
        for Paramak geometry). Smaller values generally create finer meshes.
        Must be positive. Defaults to 0.5.
    angular_tolerance : float, optional
        Angular tessellation tolerance in radians. Must be positive.
        Defaults to 0.1.

    Returns
    -------
    dict
        Mesh record with ``name``, ``vertices`` (``(n, 3)`` float array), and
        ``triangles`` (``(m, 3)`` zero-based indices). The returned surface is
        checked to be closed, two-manifold, and outward-oriented.
    """
    if not np.isfinite(tolerance) or tolerance <= 0:
        raise ValueError("tolerance must be finite and positive")
    if not np.isfinite(angular_tolerance) or angular_tolerance <= 0:
        raise ValueError("angular_tolerance must be finite and positive")

    points, triangles = solid.tessellate(tolerance, angular_tolerance)
    points = np.asarray([point.toTuple() for point in points], dtype=float)
    triangles = np.asarray(triangles, dtype=np.int64)
    if points.ndim != 2 or points.shape[1] != 3 or triangles.ndim != 2 or triangles.shape[1] != 3:
        raise ValueError(f"CAD solid {name!r} did not produce triangular surface data")
    if not np.all(np.isfinite(points)):
        raise ValueError(f"CAD solid {name!r} produced non-finite mesh coordinates")
    if np.any(triangles < 0) or np.any(triangles >= len(points)):
        raise IndexError(f"CAD solid {name!r} produced invalid triangle connectivity")

    unique_points, inverse = np.unique(np.round(points, decimals=10), axis=0, return_inverse=True)
    triangles = inverse[triangles]
    if np.any(triangles[:, 0] == triangles[:, 1]) or np.any(triangles[:, 1] == triangles[:, 2]) or np.any(
        triangles[:, 2] == triangles[:, 0]
    ):
        raise ValueError(f"CAD solid {name!r} produced a degenerate triangle")
    edges = np.sort(
        np.concatenate((triangles[:, [0, 1]], triangles[:, [1, 2]], triangles[:, [2, 0]]), axis=0),
        axis=1,
    )
    _, edge_counts = np.unique(edges, axis=0, return_counts=True)
    if np.any(edge_counts != 2):
        raise ValueError(f"CAD solid {name!r} tessellation is not a closed two-manifold surface")
    signed_volume = np.einsum(
        "ij,ij->i",
        unique_points[triangles[:, 0]],
        np.cross(unique_points[triangles[:, 1]], unique_points[triangles[:, 2]]),
    ).sum() / 6.0
    if not np.isfinite(signed_volume) or np.isclose(signed_volume, 0.0):
        raise ValueError(f"CAD solid {name!r} tessellation has zero or invalid enclosed volume")
    if signed_volume < 0.0:
        triangles = triangles[:, [0, 2, 1]]
    return {"name": name, "vertices": unique_points, "triangles": triangles}


def tetrahedralize_cad_solid(solid, name, mesh_size=10.0):
    """Create a linear tetrahedral mesh for a CAD solid with Gmsh.

    Parameters
    ----------
    solid : cadquery.Shape
        CAD solid to export temporarily to STEP and tetrahedralize with Gmsh.
    name : str
        Name stored in the returned mesh record and used as its material or
        Exodus block name.
    mesh_size : float, optional
        Target Gmsh element edge length in the model's length units
        (centimetres for Paramak geometry). Must be positive. Defaults to
        10.0.

    Returns
    -------
    dict
        Mesh record with ``name``, ``vertices`` (``(n, 3)`` float array), and
        ``tetrahedra`` (``(m, 4)`` zero-based indices).

    Raises
    ------
    ImportError
        If Gmsh or one of its required shared libraries is unavailable.
    ValueError
        If Gmsh fails to produce linear tetrahedra for the solid.
    """
    if not np.isfinite(mesh_size) or mesh_size <= 0:
        raise ValueError("mesh_size must be finite and positive")
    try:
        import gmsh
    except (ImportError, OSError) as error:
        raise ImportError("Gmsh is required to create tetrahedral meshes for CAD components") from error

    import cadquery as cq
    import tempfile
    from pathlib import Path

    initialized_here = not gmsh.isInitialized()
    if initialized_here:
        gmsh.initialize()
    model_name = f"paramak_{id(solid)}"
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("Mesh.ElementOrder", 1)
        gmsh.option.setNumber("Mesh.MeshSizeMin", mesh_size)
        gmsh.option.setNumber("Mesh.MeshSizeMax", mesh_size)
        gmsh.model.add(model_name)
        with tempfile.TemporaryDirectory() as directory:
            step_file = Path(directory) / "cad_component.step"
            cq.exporters.export(solid, str(step_file), exportType="STEP")
            gmsh.model.occ.importShapes(str(step_file))
            gmsh.model.occ.synchronize()
            gmsh.model.mesh.generate(3)
            node_tags, coordinates, _ = gmsh.model.mesh.getNodes()
            points = coordinates.reshape((-1, 3))
            node_index = {int(tag): index for index, tag in enumerate(node_tags)}

            tetrahedra = []
            element_types, _, element_nodes = gmsh.model.mesh.getElements(3)
            for element_type, tags in zip(element_types, element_nodes):
                _, dimension, order, nodes_per_element, _, _ = gmsh.model.mesh.getElementProperties(int(element_type))
                if dimension != 3 or order != 1 or nodes_per_element != 4:
                    continue
                connectivity = np.asarray(tags, dtype=np.int64).reshape((-1, 4))
                tetrahedra.extend(
                    [[node_index[int(node)] for node in tetrahedron] for tetrahedron in connectivity]
                )
            if not tetrahedra:
                raise ValueError(f"Gmsh did not create linear tetrahedra for CAD component {name!r}")
            return {
                "name": name,
                "vertices": np.asarray(points, dtype=float),
                "tetrahedra": np.asarray(tetrahedra, dtype=np.int64),
            }
    finally:
        if gmsh.model.getCurrent() == model_name:
            gmsh.model.remove()
        if initialized_here:
            gmsh.finalize()


def dagmc_model_from_structured_meshes(meshes, tag_names=None):
    """Create a PyDAGMC model from named, closed structured surface meshes.

    Mesh records are produced by :func:`mesh_revolved_layer` or
    :func:`surface_meshes_from_tetrahedral_meshes`. Coincident vertices and
    triangles are shared across records, so a triangle appearing in two
    meshes becomes a material interface. A triangle appearing once is an
    exterior boundary.

    Parameters
    ----------
    meshes : iterable of dict
        Closed surface mesh records. Each must contain ``name``, ``vertices``
        with shape ``(n, 3)``, and ``triangles`` with shape ``(m, 3)``.
        Triangle indices are zero-based. Adjacent volumes must use matching
        coordinates and triangles at shared interfaces.
    tag_names : mapping of str to str, optional
        Optional mapping from mesh record names to H5M material names, without
        the ``mat:`` prefix. Unmapped names are retained. Multiple mesh names
        can map to one material group. Every key must match an input mesh name.

    PyMOAB and PyDAGMC are imported only when this function is called.
    Coordinates are passed through unchanged; Paramak geometry is expressed
    in centimetres.

    Returns:
        pydagmc.dagnav.Model: DAGMC model. Call ``write_file(path)`` to save
        it as an H5M file.

    Raises:
        ImportError: If PyMOAB or PyDAGMC is unavailable.
        ValueError: If the meshes are invalid or a ``tag_names`` key does not
            match an input mesh name.
    """
    try:
        from pymoab import core, types
    except ImportError as error:
        raise ImportError("PyMOAB is required to create a DAGMC model") from error
    try:
        import pydagmc
    except ImportError as error:
        raise ImportError("PyDAGMC is required to create a DAGMC model") from error

    mesh_records = remap_mesh_names(meshes, tag_names)
    if not mesh_records:
        raise ValueError("at least one structured mesh is required")

    vertex_ids = {}
    coordinates = []
    face_occurrences = {}
    for mesh_index, mesh in enumerate(mesh_records):
        points = np.asarray(mesh["vertices"], dtype=float)
        triangles = np.asarray(mesh["triangles"], dtype=np.int64)
        if points.ndim != 2 or points.shape[1] != 3:
            raise ValueError(f"mesh {mesh_index} vertices must have shape (n, 3)")
        if triangles.ndim != 2 or triangles.shape[1] != 3:
            raise ValueError(f"mesh {mesh_index} triangles must have shape (n, 3)")
        if np.any(triangles < 0) or np.any(triangles >= len(points)):
            raise IndexError(f"mesh {mesh_index} contains an invalid triangle vertex index")

        local_to_global = []
        for point in points:
            key = tuple(np.round(point, decimals=10))
            if key not in vertex_ids:
                vertex_ids[key] = len(coordinates)
                coordinates.append(point)
            local_to_global.append(vertex_ids[key])

        local_faces = set()
        for triangle in triangles:
            oriented = tuple(local_to_global[int(index)] for index in triangle)
            key = tuple(sorted(oriented))
            if key in local_faces:
                raise ValueError(f"mesh {mesh_index} contains a duplicate triangle")
            local_faces.add(key)
            face_occurrences.setdefault(key, []).append((mesh_index, oriented))

    if any(len(owners) > 2 for owners in face_occurrences.values()):
        raise ValueError("a structured mesh triangle is shared by more than two volumes")

    moab_core = core.Core()
    dagmc_model = pydagmc.dagnav.Model(moab_core)
    volumes = []
    materials = []
    for mesh in mesh_records:
        dagmc_model.create_volume()
        volumes.append(dagmc_model.volumes[-1])
        materials.append(mesh.get("name") or "material")

    moab_vertices = moab_core.create_vertices(np.ascontiguousarray(coordinates, dtype=np.float64)).to_array()
    surfaces_by_sense = {}
    for owners in face_occurrences.values():
        first_index, first_face = owners[0]
        second_index = owners[1][0] if len(owners) == 2 else None
        if first_index == second_index:
            raise ValueError("a surface triangle is duplicated within one component mesh")
        surfaces_by_sense.setdefault((first_index, second_index), []).append(first_face)

    for (first_index, second_index), triangles in surfaces_by_sense.items():
        mesh_elements = moab_core.create_elements(
            types.MBTRI,
            moab_vertices[np.asarray(triangles, dtype=np.int32)],
        )
        surface = dagmc_model.create_surface()
        dagmc_model.mb.add_entities(surface.handle, mesh_elements)
        surface.senses = [volumes[first_index], None if second_index is None else volumes[second_index]]

    material_groups = {}
    for volume, material in zip(volumes, materials):
        tag = "mat:" + material
        if tag not in material_groups:
            material_groups[tag] = pydagmc.Group.create(dagmc_model, name=tag)
        material_groups[tag].add_set(volume)

    return dagmc_model
