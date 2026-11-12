# New paper reactor implementation checklist

Scope: add a paper-derived reactor with the public API, documentation, and test coverage of the existing SPARC, ITER, and EU DEMO models. Paths are relative to this repository root. `arc_from_YYYY_paper` below is a placeholder; choose the name and defaults from the selected paper.

## Required changes

- [ ] **Implement the constructor in `src/paramak/assemblies/paper_reactors.py`.**
  - Add a public function returning the existing `Assembly` class.
  - Expose `rotation_angle`, `number_of_tf_coils`, `pf_coil_case_thickness`, and `colors` where applicable, with paper-appropriate defaults.
  - Call `_validate()` for rotation angle and TF-coil count; use `_pf_coils_with_cases()` for PF winding packs and cases.
  - Define the plasma parameters, component dimensions, positions, and profile coordinates in cm; use degrees for angles.
  - Build the components represented in the paper, using stable, unique names. Follow existing names where applicable: `plasma`, `blanket`, `divertor`, `vessel`, `central_solenoid_N`, `pf_coil_N`, `pf_coil_case_N`, and `toroidal_field_coil`.
  - Handle partial sectors and a full 360-degree model, including TF placement and clipping. Reuse the existing revolution helpers where appropriate.
  - Define necessary overlap cuts and intended contacts. Derive touching surfaces from shared geometry where possible.
  - Return the assembly through `_build_assembly()` with component colors and `major_radius`, `minor_radius`, `elongation`, and `triangularity` metadata matching the built plasma.
  - Document the source paper, DOI, figure, units, parameter meanings, returned components, and any digitization estimates or geometry adjustments in the docstring/comments.

- [ ] **Export the constructor in `src/paramak/__init__.py`.**
  - Add its import and its name to `__all__`, enabling `paramak.arc_from_YYYY_paper(...)`.

- [ ] **Register shared tests in `tests/test_assemblies/test_paper_reactors.py`.**
  - Add the constructor to `PAPER_REACTORS`.
  - Add its required component names to `EXPECTED_PARTS`.
  - Add suitable minimum/maximum mesh sizes in `MESH_SIZES`.
  - Check that the existing shared-test assumptions fit the model: plasma/vessel volume scaling, plasma metadata ranges and bounds, and PF winding packs with cases.
  - This registration includes expected/unique names, valid positive-volume parts, plasma metadata, sector-volume scaling, color overrides, invalid inputs, PF-case behavior, and transport at 30, 180, and 360 degrees.

- [ ] **Register imprint tests in `tests/test_assemblies/test_imprint.py`.**
  - Add a builder to `REACTORS`, normally constructing a 180-degree model.
  - Specify the actual pairs of neighboring components that must share faces, including PF winding packs/cases where present.
  - Reuse `pf_coils_in_cases(count)` where appropriate.
  - The existing tests then check preserved solid count, absence of overlaps after imprinting, and the expected shared faces.

- [ ] **Add paper-specific regression tests.**
  - Add them to `tests/test_assemblies/test_paper_reactors.py`, or a dedicated reactor test module if substantial.
  - Check meaningful dimensions, component counts, and placements against independent values from the paper.
  - Check distinctive geometry, required contacts, intentional clearances, and any deliberate adjustments that generic tests cannot verify.

- [ ] **Add an export example in `examples/reactors_from_papers.py`.**
  - Construct the new reactor and export it to a clearly named STEP file, following the existing examples.

- [ ] **Document the public API in `docs/python_api.rst`.**
  - Add an `autofunction` entry for the constructor.

- [ ] **Document the model in `docs/examples_paper_reactors.rst`.**
  - Add a construction/rendering example, paper citation, figure reference, and explanation of approximations and represented components.

## Potentially required changes

- [ ] **New reusable component geometry: `src/paramak/workplanes/`.**
  - Add a component constructor only if existing shapes and profile-revolution helpers cannot express the geometry cleanly.
  - Add focused tests under `tests/test_workplanes/` for its construction, dimensions, validation, and relevant rotation behavior.
  - If public, export it in `src/paramak/__init__.py` and document it in `docs/python_api.rst`.

- [ ] **Additional input parameters or validation.**
  - Add parameters required by the new design, with documented defaults and focused invalid-input tests.
  - Extend shared helpers only for behavior that is also valid for existing reactors; otherwise validate in the new constructor.

- [ ] **Adapt shared tests for different reactor topology.**
  - If the model lacks a component expected by shared tests, or has different plasma shaping, change the relevant test configuration/assertions to express that difference explicitly.
  - Preserve coverage for the existing models and avoid skipping applicable checks merely to accommodate the new model.

- [ ] **New assembly metadata: `src/paramak/assemblies/assembly.py`.**
  - If metadata beyond the four current plasma attributes must survive assembly transformations, update `_copy_metadata()`.
  - Add tests in `tests/test_assemblies/test_assembly.py` verifying preservation through `rename()` and `split_solids()`.

- [ ] **New assembly methods or a reactor-specific class.**
  - A new paper reactor alone does not require either: current paper models are functions returning `Assembly`.
  - Add shared methods to `Assembly` only for generally useful assembly behavior, with focused tests and documentation.
  - If genuinely distinct state or behavior requires a subclass, test construction, metadata preservation, and the return types of methods that currently construct plain `Assembly` instances.

- [ ] **Animation integration: `examples/paper_reactors_rotation_animation.py`.**
  - Register the new constructor if it should appear in the paper-reactor animation.
  - Regenerate media and update `docs/index.rst` if the homepage presentation should include it.

- [ ] **CI changes: `.github/workflows/ci.yml`.**
  - No change is needed for ordinary test discovery: `pytest -v` includes geometry tests, and `pytest -v -k transport -rs` includes registered transport tests.
  - Add an explicit command if the new example script should also execute in CI.
  - Update dependencies/system packages only if the implementation introduces additional requirements.

- [ ] **Dependency changes: `pyproject.toml`.**
  - Required only if new runtime, test, transport, or documentation dependencies are introduced.

- [ ] **Materials or neutronics examples.**
  - Required only if realistic material assignments are part of the requested model scope.
  - Existing constructors provide geometry, names, and colors; shared transport tests assign placeholder H1 at 0.01 g/cm3.
  - Keep physical material definitions and component-to-material mapping explicit, and test any new mapping behavior.

## Tests to provide for a new paper reactor

Register the constructor in `PAPER_REACTORS`, `EXPECTED_PARTS`, and `MESH_SIZES` in `tests/test_assemblies/test_paper_reactors.py`. This adds the new model to the following existing tests; do not duplicate these functions for each reactor.

| Existing test | Expected behavior for the new reactor |
| --- | --- |
| `test_expected_parts` | Required names are present and every part name is unique. Uses the shared 180-degree model. |
| `test_solids_are_valid_with_positive_volume` | Every component is a valid CAD shape with positive volume at 180 degrees. |
| `test_plasma_metadata` | `major_radius > minor_radius > 0`, `elongation > 1`, and `0 < triangularity < 1`. |
| `test_plasma_metadata_matches_the_plasma` | At 180 degrees, plasma X bounds match plus/minus `(major_radius + minor_radius)` within 0.1 cm; height matches `2 * elongation * minor_radius` within relative tolerance 0.001. |
| `test_smaller_rotation_angle_gives_smaller_volumes` | The 90- and 180-degree models have the same names; plasma and vessel volumes approximately halve (5% relative tolerance), and total volume decreases. |
| `test_colors_override_defaults` | A custom plasma RGB color is retained in a 10-degree model. |
| `test_invalid_rotation_angle` | Values `0`, `-10`, and `361` raise `ValueError` identifying `rotation_angle`. |
| `test_invalid_number_of_tf_coils` | Values `0`, `-1`, and `2.5` raise `ValueError` identifying `number_of_tf_coils`. |
| `test_pf_coils_have_a_winding_pack_and_case` | PF packs/cases exist, have positive volumes, and cases surround packs; union volume equals the sum within relative tolerance `1e-6`. Uses the 180-degree model. |
| `test_pf_coil_case_thickness_changes_the_split_not_the_coil_size` | Comparing case thicknesses 1 and 5 cm at 10 degrees: case 1 grows, winding pack 1 shrinks, and combined volume is preserved within relative tolerance `1e-6`. |
| `test_invalid_pf_coil_case_thickness` | Values `0`, `-1`, `NaN`, and `1000` raise `ValueError` identifying `pf_coil_case_thickness`. |
| `test_transport` | At each of 30, 180, and 360 degrees, CAD-to-DAGMC meshing and OpenMC transport complete and calculated flux is positive. |

There are 12 shared paper-reactor test functions. With the current parameterization, these produce **21 cases per registered reactor**: 18 non-transport cases and 3 transport cases. Reactor-specific tests add further cases. If the design legitimately violates a shared assumption (for example, different plasma shaping or PF outer dimensions too small for a 5 cm case), adapt the relevant test configuration explicitly while preserving equivalent coverage.

Register a builder and expected touching pairs in `REACTORS` in `tests/test_assemblies/test_imprint.py` to add **two further cases**:

- `test_imprinting_adds_no_solids`: imprinting must preserve the original solid count and no resulting solid may have more than one originating component.
- `test_neighbouring_parts_share_faces`: specified neighbors must exist and share faces after imprinting. Include pack/case pairs and applicable blanket/divertor/vessel contacts. Do not list intentional gaps or contacts that only share a line.

Add dedicated regression tests for independent dimensions/counts/placements from the paper, distinctive geometry, intentional clearances, and required contacts. The existing EU DEMO vessel-contact test is an example: it checks zero separation, shared imprinted faces, and absence of overlaps. It is not automatically applied to a new reactor. Generic validity and positive transport flux do not establish fidelity to the paper or realistic neutronics performance.

## How to run the tests

Run commands from the repository root. The examples below assume the new constructor is named `arc_from_YYYY_paper` and its imprint registry key is `arc`; substitute the actual names. These selectors only work after registration. Do not accept an empty selection as a passing run.

### Install the geometry test dependencies

Use Python 3.12 to match CI, preferably in an activated virtual environment:

```bash
python -m pip install -e '.[tests]'
```

On Linux, CAD imports may need the system libraries listed in `.github/workflows/ci.yml`; use the same environment setup as that workflow if imports fail.

### Inspect collection and run only the new model

```bash
# Confirm the new model is registered: expect 21 shared paper-reactor cases.
python -m pytest --collect-only -q tests/test_assemblies/test_paper_reactors.py -k arc_from_YYYY_paper

# Geometry, metadata, colors, and invalid inputs: expect 18 shared cases.
python -m pytest -v tests/test_assemblies/test_paper_reactors.py -k 'arc_from_YYYY_paper and not transport'

# Imprinting: expect two cases for the arc registry key.
python -m pytest -v 'tests/test_assemblies/test_imprint.py::test_imprinting_adds_no_solids[arc]' 'tests/test_assemblies/test_imprint.py::test_neighbouring_parts_share_faces[arc]'
```

Run dedicated reactor-specific tests by their actual file or node IDs as well; constructor-name selection does not necessarily select separately named regression tests.

### Install and run transport tests

Follow the existing CI installation, including its OpenMC wheel index:

```bash
python -m pip install --extra-index-url https://shimwell.github.io/wheels -e '.[tests,transport]'
python -c 'import openmc, cad_to_dagmc'
python -m pytest -v tests/test_assemblies/test_paper_reactors.py -k 'arc_from_YYYY_paper and transport' -rs
```

Expect **three passed cases**, one per angle, with no skips. The current paper transport skip condition checks only for `cad_to_dagmc`; OpenMC must also be installed. Keep the explicit import check to catch an incomplete environment before running.

The paper tests use the repository's `tests/cross_sections.xml` and H1 data file `tests/ENDFB-7.1-NNDC_H1.h5`. Their placeholder material is H1 at 0.01 g/cm3. The XML also lists H2, but the paper tests request H1 only. OpenMC must support DAGMC and resolve the required H1 data. Tune the new entry in `MESH_SIZES` for the model's dimensions and smallest important features; a skipped test or failed mesh is not successful transport validation.

### Check all models for regressions

```bash
# All paper geometry/validation tests and all reactor imprint tests.
python -m pytest -v tests/test_assemblies/test_paper_reactors.py tests/test_assemblies/test_imprint.py -k 'not transport'

# All paper-reactor transport tests, with transport dependencies installed.
python -m pytest -v tests/test_assemblies/test_paper_reactors.py -k transport -rs

# Full suite, as in the main CI test job.
python -m pytest -v

# All transport tests, as in the separate CI transport job.
python -m pytest -v -k transport -rs
```

Transport tests can be expensive. Run focused new-model checks first, then paper-model regressions and the required full-suite checks. Without optional transport dependencies, the full suite may report transport skips; that does not replace the separate transport run.

## Validation before considering the implementation complete

- [ ] Run `ruff check .`.
- [ ] Run geometry/validation tests for all paper reactors and their imprint tests; verify existing models still pass.
- [ ] With transport dependencies and nuclear data installed, run the new reactor's transport cases at 30, 180, and 360 degrees.
- [ ] Run the complete test suite as required by CI.
- [ ] Run the new STEP-export example and check the documented example renders/builds successfully.
- [ ] Confirm the new constructor imports through `paramak` and its documented defaults match its implementation.

The existing CI workflow runs for pull requests targeting any branch and pushes to `main`. Pushing only to `arc-model` does not trigger it.

## ARC 2026 scaffold completion roadmap

- [ ] #ARC Verify paper citation, DOI, figure, and units; the API year is provisional attribution.
- [ ] #ARC Review remaining borrowed SPARC defaults and geometry placeholders in `arc_from_2026_paper`.
- [ ] #ARC Insert ARC dimensions/profiles, confirm component topology, contacts, clearances, and colors.
- [x] #ARC Return the implemented plasma, six solenoid envelopes, and ten PF packs/cases in an Assembly with matching metadata; other components remain pending.
- [ ] #ARC Replace scaffold tests with ARC-specific geometry regressions and register in `PAPER_REACTORS`, `EXPECTED_PARTS`, and `MESH_SIZES`.
- [ ] #ARC Register the `arc` imprint builder and expected touching pairs in `REACTORS`.
- [ ] #ARC Pass 18 shared geometry/validation cases, 2 imprint cases, and 3 transport cases, plus paper-specific regressions.
- [ ] #ARC Add executable rendering/export/animation examples only after full reactor geometry is implemented.

Every new Python scaffold comment uses the literal `#ARC` tag. Docstrings and Markdown use the same label; reStructuredText comments use `.. #ARC`. Existing unrelated comments are unchanged. Find completion points with:

```bash
rg -n '#ARC' src tests docs PAPER_REACTOR_CHECKLIST.md
```

Current plasma, solenoid, and PF pack/case validation (geometry, metadata, volume scaling, colors, and invalid inputs; no transport):

```bash
python -m pytest -v tests/test_assemblies/test_arc_scaffold.py
ruff check .
git diff --check
```

The constructor returns a plasma, solenoid, and PF pack/case approximation (R=462 cm, a=118 cm, elongation=1.8, primitive triangularity=arcsin(0.65)). TF count 18 is sourced from Hillesheim p.10; TF geometry now uses the supplied inner/outer polygons with assumed 40 cm total extrusion. PF-case thickness is now used to split ten JSON-derived PF envelopes into packs and cases; its 3 cm default and case-inclusive interpretation remain provisional. Six solenoid envelope solids are extracted from device_V3A.json and do not specify detailed turns/cases. It is exported but intentionally absent from active geometry, imprint, transport, animation, and export registries. Use the earlier focused ARC test commands after registering real geometry. No physical material assignments are introduced.


- [x] #ARC Build TF solids from the supplied outer/inner profiles, with assumed 40 cm total extrusion and 18 default placements. Princeton-D estimates are not used.
- [ ] #ARC Replace the assumed TF extrusion width with engineering data; check packing when changing coil count.


- [x] #ARC Add first_wall from the JSON tungsten layer's inner/outer contours (nominal 0.5 cm), with sector revolution, color overrides, and no runtime dependency on the reference JSON.
- [ ] #ARC Replace the smooth plasma approximation with a checked equilibrium boundary. It is currently clipped to the first-wall inner cavity because the analytical fit otherwise overlaps the sourced wall locally; preserve the supplied first-wall geometry.


- [x] #ARC Add inner_vessel, outer_vessel, and neutron_shield from explicit JSON contours, converted to cm and revolved through the requested sector. Preserve the first-wall/inner-vessel interface and the intervening vessel cooling gap.
- [ ] #ARC Construct the blanket tank shell; vessel cooling space is now represented by flibe_first_wall. Physical material assignments and shielding electrical breaks remain pending.


- [x] #ARC Add flibe_first_wall as the homogeneous nominal 4.5 cm cooling region between the sourced vessel faces, with sector scaling, color override, no overlap, and shared-face imprint checks. Individual channels/ribs and physical materials remain unspecified.


- [x] #ARC Add flibe_blanket from the tank inner contour minus the entire vessel envelope and neutron shield, preserving shared interfaces and separating bulk liquid from flibe_first_wall. Tank shell and physical material definitions remain pending.
