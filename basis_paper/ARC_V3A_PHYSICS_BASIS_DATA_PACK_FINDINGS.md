# ARC V3A overview paper and digital assets: additional modeling findings

## Scope and sources

**Main paper:** J. C. Hillesheim et al., *Overview of the physics basis for the ARC fusion power plant*, Journal of Plasma Physics **92**, E69 (2026), DOI https://doi.org/10.1017/S0022377826101706.

Local sources inspected:

- [Overview PDF](overview_of_the_physics_basis_for_the_arc_fusion_power_plant.pdf), including Table 2 and Appendix A, pp.40–43.
- [device_V3A.json](device_V3A.json).
- [FreeGS equilibrium](geqdsk-ARCv3a).
- [GACODE reference profiles](input.gacode_V3A).
- [TokaMaker kinetic equilibrium](ARC_V3A_kinetic_tokamaker_800res.eqdsk).
- [TokaMaker paired profiles](p100000.00001_V3A_800res).
- [Existing data-pack inventory](README.md).

Printed page numbers match PDF pages. Figures 2 (p.9) and 12 (p.40) were visually inspected. JSON arrays and equilibrium/profile headers were examined numerically. No repository code or source data was changed. The Windows `Zone.Identifier` sidecars contain download metadata, not scientific inputs.

This report extends the [four-paper synthesis](../articles/ARC_PAPER_FINDINGS_SYNTHESIS.md). It distinguishes explicit design statements, quantities calculated from the supplied files, and remaining engineering assumptions. Several uncertainties in that earlier synthesis are now resolved for the published V3A reference model, though this is still not a final engineering design.

## Most important additions

1. **18 TF coils are explicitly confirmed**, rather than merely inherited from SPARC (main paper p.10).
2. **The missing vessel coolant spacing is specified:** 4.5 cm of internal space for FLiBe cooling channels, between the 1 cm inner and 3 cm outer vanadium walls (p.10).
3. **Digital coil locations are available:** six central-solenoid modules and ten PF coils, arranged as upper/lower pairs, in `device_V3A.json`.
4. **Digital wall, vessel, blanket-envelope and shield contours are available**, reducing the need to digitize published figures.
5. **Dedicated central-solenoid shielding is tungsten carbide** in the V3A baseline (p.10), with electrical breaks assumed in the physics studies.
6. **Actual equilibrium boundaries and plasma profiles are supplied**, but FreeGS and TokaMaker describe different equilibria and the FreeGS boundary needs a data-quality check before direct CAD use.

## Confirmed paper values and conventions

| Quantity | Value | Evidence / use |
| --- | --- | --- |
| TF-coil count | **18** | Main paper p.10; the current ARC function's numerical default is correct for V3A and can be cited directly. |
| Major / minor radius | **4.62 / 1.18 m = 462 / 118 cm** | Abstract and Table 2, p.10; confirms the existing plasma implementation's nominal dimensions. |
| Separatrix elongation / triangularity | **1.8 / 0.65** | Table 2; retain distinctions between nominal shaping and individual equilibrium files. |
| Plasma volume / LCFS area | **189 m3 / 257 m2** | Table 2; full-device reference values, not guaranteed exact values for every supplied equilibrium or simplified fit. |
| Field / current | Magnitudes **11.4 T / 12 MA** | Table 2; paper specifies both directed clockwise from above, negative in its usual tokamak convention. |
| Coordinate convention | **COCOS 11** | p.11; preserve signs and flux conventions for field/profile import. |
| Tungsten armour | **5 mm = 0.5 cm** | p.10; reference material/thickness, subject to change. |
| Inner vanadium wall | **1 cm** | p.10 |
| Internal FLiBe cooling space | **4.5 cm** | p.10; a space containing cooling channels, not 4.5 cm of conducting vessel metal. |
| Outer vanadium wall | **3 cm** | p.10 |
| Conductivity evaluation temperature | Approximately **600 C** | p.10; not a complete thermal or material specification. |
| Dedicated shield | **Tungsten carbide** | p.10; electrical breaks assumed for toroidal currents, omitted from the reduced axisymmetric description. |

The armour-to-outer-wall nominal build is therefore **0.5 + 1 + 4.5 + 3 = 9 cm**. The earlier disruption paper's **4.5 cm effective conducting thickness** is the sum of the modeled metal layers, not the complete wall build. This resolves an important apparent ambiguity.

The paper explicitly leaves final materials and vessel/blanket-tank shape to further engineering and R&D. These are justified reference-model assumptions, not finalized alloy compositions, densities, or construction details.

## JSON device geometry: what can now be constructed

The file uses IMAS data-dictionary version 3.41.0. Its top-level keys are `dataset_description`, `pf_active`, `summary`, and `wall`; it contains **no plasma equilibrium or TF-coil geometry section**.

### Coil inventory and locations

`pf_active.coil` contains **16 coils**: `cs1u/l`, `cs2u/l`, `cs3u/l`, and `pf1u/l` through `pf5u/l`. Units for R/Z are metres; multiply by 100 for Paramak.

The following centres are calculated as the midpoints of the minimum/maximum element-centre coordinates. The envelope dimensions include each annular element's outer radius; they are a reproducible bound on the reduced coil representation, **not verified case or winding-pack dimensions**.

| Upper/lower pair | Centre R (cm) | Centre Z (cm) | Element-envelope width × height (cm), approximately |
| --- | ---: | ---: | ---: |
| CS1U/L | 110.5 | +/-75 | 75.620 × 138.657 |
| CS2U/L | 110.5 | +/-190 | 75.620 × 68.657 |
| CS3U/L | 110.5 | +/-270 | 75.620 × 68.657 |
| PF1U/L | 140 | +/-390 | 59.000 × 59.000 |
| PF2U/L | 190 | +/-475 | 68.957 × 68.957 |
| PF3U/L | 620 | +/-295 | 48.875 × 48.875 |
| PF4U/L | 620 | +/-225 | 48.875 × 48.875 |
| PF5U/L | 695 | +/-160 | 38.923 × 38.923 |

Extraction rule for an element at `(r,z)` with radius `b`: bounds are `min(r-b)`, `max(r+b)`, `min(z-b)`, `max(z+b)`. The data represent each CS1 coil with 1150 elements, each CS2/CS3 with 575, PF1 with 400, PF2 with 529, PF3/PF4 with 256, and PF5 with 169. Do not convert those counts directly into engineering turn counts.

Appendix A, **p.41**, explicitly says **coil locations are correct**, while turn subdivision and power-supply parameters are non-proprietary analogues. The 16 circuits and 16 supplies do not imply 16 TF coils.

For a simplified CAD model, bounding these distributions by rectangular annular coil solids is a documented modeling approximation. Adding a separate PF case still needs a case-thickness assumption; **the data pack does not justify the current provisional 3 cm PF-case default**. Do not label an element envelope as the paper's total case-inclusive outer dimensions and then silently shrink it to make a case.

### Wall, tank and shield contours

JSON paths below are zero-based. Arrays contain R/Z coordinates in metres and must be treated as paired polygon vertices.

| JSON location | Contents | Directly inspected bounds in metres |
| --- | --- | --- |
| `wall.description_2d[0].limiter.unit[0].outline` | 33-point closed limiter contour | R=3.42–5.82, Z=-4.09–4.09 |
| `wall.description_2d[1].vessel.unit[0].annular` | Tungsten first-wall inner/outer contours, 33 points each | Outer R=3.415–5.825, Z=-4.095–4.095 |
| Same, `unit[1].annular` | Inner vessel wall inner/outer contours | Outer R=3.405–5.835, Z=-4.105–4.105 |
| Same, `unit[2].annular` | Outer vessel wall inner/outer contours | Inner R=3.36–5.88, Z=-4.15–4.15; outer R=3.33–5.91, Z=-4.18–4.18 |
| `wall.description_2d[2].vessel.unit[0].annular` | Entry named `Blanket`, enclosing the device and shield | Inner R=2.48–7.20, Z=-4.68–4.68; outer R=2.46–7.22, Z approximately +/-4.7003 |
| `wall.description_2d[3].vessel.unit[0].element[0].outline` | 18-point shield polygon | R=2.48–4.11, Z=-4.37–4.37 |

These permit direct construction of axisymmetric profile solids. The limiter is a boundary, not automatically an extra solid to overlap the first wall. Use each contour's own ordering; some inner and outer arrays run in opposite directions. Equal vertex indices are not guaranteed to be corresponding normal-offset points. Check closure, orientation, self-intersections, containment, and positive region areas before revolution.

The entry named `Blanket` is a thin **annular envelope** (approximately 2 cm at the radial extrema), consistent with a blanket-tank shell representation. It is **not itself the entire liquid FLiBe inventory**. Liquid regions must be constructed from the tank interior minus the vessel envelope, shield, and any other explicitly represented displacements, with a documented interpretation of the reduced model. Do not revolve just that thin annulus and claim it represents the bulk breeding liquid.

Likewise, a central-solenoid shield polygon should not be simultaneously assigned to FLiBe. The tank material is not conclusively specified by its JSON name or its electrical resistivity.

### Analysis-model properties versus material specifications

JSON first-wall resistivity is **9e-7 Ohm m**, while the disruption analysis used **3.3e-7 Ohm m** for tungsten. Inner/outer vessel values are **6e-7 Ohm m**; the `Blanket` annular entry is **7.4e-7 Ohm m**. These are analysis inputs, not interchangeable finalized materials. Record the dataset and temperature/model context; do not overwrite one with the other or infer compositions from resistivity.

## Equilibrium files: real boundaries, different reference cases

Both files were parsed using the standard GEQDSK field order: 20 scalar header values, four radial function arrays, the R/Z flux grid, the safety-factor array, then boundary/limiter counts and coordinate pairs. Values below are direct file observations; they are not fresh equilibrium solutions.

| File | Grid | Boundary / limiter points | Important observations |
| --- | --- | --- | --- |
| `geqdsk-ARCv3a` | 129×129 | 102 / 33 | FreeGS reference. Magnetic-axis R approximately 4.69959 m; current -12 MA. Limiter matches the JSON limiter bounds. |
| `ARC_V3A_kinetic_tokamaker_800res.eqdsk` | 800×800 | 800 / 2144 | Kinetic TokaMaker case. Reference radius approximately 4.617919 m, field approximately -11.4051 T, magnetic-axis R approximately 4.66706 m, current approximately -12 MA. |

**Do not equate magnetic-axis R with the nominal geometric major radius.** The FreeGS header uses reference radius 1 m and reference field -52.668 T; their product represents the reference toroidal-field normalization. Those header fields are not evidence that the machine has a 1 m major radius or a nominal 52.668 T field.

### Data-quality finding: FreeGS boundary outlier

At **zero-based boundary index 89**, the supplied FreeGS coordinate pair is approximately **(R,Z)=(2.685469681,-5.655071464) m**. It is far outside the expected core region and outside the flux grid's lower Z extent (-5.5 m). It breaks the otherwise expected plasma-boundary symmetry and inflates extrema and inferred volume.

This is a concrete import-quality flag, not a proven explanation of its origin. Confirm parsing with an established reader and inspect the flux-derived contour before accepting or repairing it. **Do not silently delete the point, spline through it, or use the raw boundary extrema to redefine ARC radii.** No source file was repaired during this review.

### TokaMaker contour and reference-volume checks

The 800-point kinetic boundary has approximately:

- R range **3.448610–5.787229 m**.
- Z range **-2.259297–2.260341 m**.
- Geometric radial midpoint **4.617919 m** and radial half-width **1.169310 m**.
- Full-turn polygon-revolution volume approximately **184.56 m3**, about **2.35% below** the nominal 189 m3.

The volume was calculated from the closed R/Z polygon via `V = abs(pi/3 * sum((Ri+Ri+1)*(Ri*Zi+1-Ri+1*Zi)))`. It assumes straight connections between supplied vertices and is a geometry diagnostic, not a meshed CAD validation result. It does not include open-field-line divertor extensions outside the closed plasma boundary.

Appendix A, **pp.42–43**, explicitly explains that bootstrap current changes the TokaMaker separatrix relative to FreeGS and slightly changes q95. The high-resolution file is **not merely a refined copy** of the low-resolution one. Differences in boundary extent, volume, and shaping must retain their reference-case provenance. Do not force exact nominal 189 m3 onto every supplied contour by undisclosed rescaling.

## Profiles: additional physics inputs, not solid geometry

### GACODE file

`input.gacode_V3A` has 117 radial points and six named species, `D T W B H He`. H and He are marked fast populations; B is a lumped effective impurity in the model, not automatically a literal boron material region. The paper describes a medium-fidelity TRANSP reference near the end of a sawtooth cycle paired with the FreeGS boundary (Appendix A, p.42).

Examples of directly read values:

| Field | Inner endpoint | Outer endpoint | Units / interpretation |
| --- | ---: | ---: | --- |
| `rmin` | approximately 0 | 1.1807495 | m |
| `rmaj` | 4.6885208 | 4.6228898 | m; radial profile, not a uniform magnetic-axis location |
| `kappa` | 1.2500411 | 1.8911119 | File's fitted flux-surface geometry |
| `delta` | -0.0018922 | 0.5580260 | File's fitted shape parameter; do not assume identical to paper delta_sep or Paramak's angular coefficient |
| `ne` | 31.335698 | 8.4 | 10^19 m^-3, so approximately 3.13357e20 to 8.4e19 m^-3 |
| `te` | 24.448745 | 0.075 | keV |

These endpoint shaping differences reinforce the need to distinguish nominal table targets, fitted transport geometry, and a chosen equilibrium contour. Species masses/charges can be effective model values; do not promote them to nuclear material definitions without interpreting the model.

### Paired TokaMaker profiles

`p100000.00001_V3A_800res` contains 19 named blocks of 800 rows each. Blocks use normalized poloidal flux plus the profile and its flux derivative, and include densities, temperatures, pressure, electric field, and flow-related quantities. The electron-density unit is **10^20 m^-3**, different from GACODE's **10^19 m^-3**. Preserve headers, signs, units, and equilibrium pairing when using these profiles.

These data can support a future spatial neutron-source/plasma model, but do not specify solid densities, isotopic enrichments, or validated neutron transport materials. Plasma transport calculations and the repository's OpenMC geometry smoke tests remain different workflows.

## What is now ready, and what remains inferred

### Supported additions to the ARC model

- #ARC Cite **18 TF coils** as the main paper's baseline rather than a borrowed SPARC guess.
- #ARC Use the supplied **six CS / ten PF coil locations**, preserving upper/lower identities. Simplified coil envelopes need an explicit approximation label and separate case assumptions.
- #ARC Build tungsten first wall, inner/outer vessel solids, and the intervening **4.5 cm cooling-space region** from the digital contours.
- #ARC Build the nominal tank envelope and dedicated shield from JSON profiles; identify the baseline shield as tungsten carbide while leaving detailed material specifications open.
- #ARC Prefer a checked equilibrium boundary over a guessed smooth fit where higher fidelity is needed. Choose FreeGS/transport or TokaMaker/stability provenance deliberately.

### Still unresolved or intentionally reduced

- Full numerical TF case contours are not supplied in the JSON. Figure 2 depicts the two-dimensional outline, and the alpha-loss section explicitly says the study assumed internal windings scaled from SPARC and interpolated between case contours. Do not present those assumptions as final ARC winding engineering.
- Three-dimensional TF extrusion/case widths, winding composition, joints, supports, PF-case thicknesses, and detailed cooling-channel geometry remain open.
- Ports, pumps, antennas, and shielding electrical breaks are omitted from the reduced device model. Revolving the JSON contours does not recover them.
- Coil element subdivisions, turn counts, supply limits, and delays are public analogues, not engineering specifications (Appendix A, p.41).
- The vessel/blanket materials remain provisional despite the much stronger geometric specification.

## Recommended checks before importing the data into CAD

1. #ARC Validate schema, coordinate lengths, finiteness, metre-to-centimetre conversion, closures and contour orientation; preserve the raw data and provenance.
2. #ARC Resolve the FreeGS outlier using an independent reader/flux-contour check; report any eventual repair explicitly.
3. #ARC Test the 16-coil inventory and paired centre positions; label envelope-derived sizes rather than treating element distributions as case-inclusive winding dimensions.
4. #ARC Verify shared interfaces between armour/inner wall, containment of the cooling-space region, and outer-wall/tank/shield relationships. Construct the bulk FLiBe region without overlapping shield or vessel solids.
5. #ARC Compare boundary-derived volume/shaping against the selected dataset, using nominal paper values as references with justified tolerances.
6. #ARC Run valid-solid, no-overlap, imprint and sector-volume checks before full neutron-transport tests. A watertight reduced geometry is not a finalized engineering or material model.

**Conclusion:** this data pack substantially advances the model from a plasma-only approximation toward a sourced axisymmetric reactor. It resolves the TF count, coil placement, vessel coolant spacing, and many profile-coordinate gaps. Data-quality checks, equilibrium selection, three-dimensional magnet construction, and explicit engineering/material assumptions remain necessary.
