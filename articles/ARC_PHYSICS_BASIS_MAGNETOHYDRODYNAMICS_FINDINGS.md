# ARC physics basis–magnetohydrodynamics: modeling findings

## Source and purpose

- **Paper:** N. Leuthold et al., *ARC physics basis–magnetohydrodynamics*, Journal of Plasma Physics **92**, E49 (2026).
- **DOI:** https://doi.org/10.1017/S0022377826101421
- **Local source:** [arc_physics_basismagnetohydrodynamics.pdf](arc_physics_basismagnetohydrodynamics.pdf).
- **Design studied:** ARC Version 3A; the authors state that the design is evolving.
- Page references below use the paper's printed page numbers, which match PDF page numbers in this copy.
- The title page notes an update notice at DOI https://doi.org/10.1017/S0022377826101822. That separate notice has not been reviewed for this report.

This report identifies information useful for implementing `arc_from_2026_paper`. It distinguishes explicit statements from figure-derived possibilities and implementation recommendations. No model code was changed. This paper provides physics and selected geometry constraints, rather than a complete CAD or manufacturing specification.

## Explicit plasma and surrounding-region information

| Finding | Source | Modeling use and limits |
| --- | --- | --- |
| Up–down symmetric double-null configuration | Section 2, p.2; Figure 2(a), p.4 | Model upper and lower divertor regions. Do not inherit a single-null configuration. |
| Elongation approximately 1.8 | Section 2, p.2 | A paper-supported shaping target in place of the provisional SPARC value 1.97. |
| Triangularity approximately 0.65 | Section 2, p.2 | A paper-supported geometric shaping target; check its correspondence to Paramak's parameterization before direct assignment. |
| Minor radius 1.18 m, or 118 cm | Figure 4 caption, p.8 | Explicitly stated for the baseline design used in that vertical-control study. Confirm consistency with the chosen equilibrium before combining dimensions from different figures. |
| Approximately 2 cm HFS and LFS gaps between wall and LCFS | Section 2.2, p.3 | Constrain high-field-side and low-field-side clearances. This is not evidence for a uniform 2 cm offset at every poloidal location. |
| Liquid-immersion FLiBe blanket | Section 3, p.7 | Include a blanket region with the cooling, breeding, neutron-multiplication, and shielding roles described by the paper. Exact boundaries and material specifications remain to be supplied. |
| Upper and lower PF5 coils can provide vertical control without dedicated in-vessel vertical-stability coils | Section 3, p.7; conclusion, pp.24–25 | Do not automatically transfer SPARC's dedicated VS coils. This conclusion applies to the studied configuration and control assumptions. |

HFS means high-field side, LFS low-field side, and LCFS last closed flux surface. Convert paper dimensions in metres to centimetres for Paramak; the 2 cm wall clearance is already in centimetres.

### Plasma boundary fidelity

Figure 2(a) shows X-points and extended divertor legs. The current `plasma_simplified` primitive constructs a smooth plasma boundary without explicit X-points or divertor legs. It can provide a first approximation, but cannot reproduce the complete equilibrium geometry merely by changing radii, elongation, and triangularity.

For closer fidelity, obtain equilibrium boundary data or digitize the figure and build an appropriate revolved profile. Distinguish the LCFS from open-field-line divertor extensions when deciding what the CAD plasma volume represents.

Paramak's shaping equation is `R(theta) = R0 + a * cos(theta + triangularity * sin(theta))`. Its coefficient should not be assumed identical to a geometric triangularity quoted in a paper. Confirm the convention or fit the boundary before treating 0.65 as a validated input.

## Error-field correction coils

Sections 5.2–5.3 describe geometry scans and a recommended arrangement, not a finalized engineering design.

| Feature | Information in the paper | Source / qualification |
| --- | --- | --- |
| Coil type | Picture-frame / window-frame three-dimensional coils | Section 5.2; Figure 10, p.17 |
| Placement | Inside the cryostat, outside the TF coils; subsequent studies mount coils directly on the TF exterior | Section 5.2, pp.17–18 |
| Recommended rows | Two off-midplane rows, symmetric above and below the LFS midplane | Sections 5.2.3–5.2.4, pp.19–21; Figure 15, p.21 |
| Poloidal position | Maximum-correctable-error-field optimum around plus/minus 60 degrees; favorable locations approximately 40–80 degrees off-midplane | Section 5.2.1, p.18; exact optimum depends on the scenario |
| Height | 2 m, or 200 cm, for the recommended arrangement | Section 5.2.4, p.21; shorter alternatives are also explored |
| Toroidal count | Six individual coils per row in the studied configurations | Section 5.3.2, p.23 |
| Neighboring toroidal gaps | Approximately 6 degrees in the depicted arrangement | Discussion of Figure 15, p.21; gap-size effects remain a future study |

The paper defines coil geometry through distance from the plasma, poloidal height, poloidal position angle, and tilt relative to the plasma surface. For TF-mounted coils, local TF shape sets the orientation. Coil-conductor dimensions and detailed supports are not fully specified here.

The correction-coil count must not be used as the TF-coil count. Their poloidal location angle also differs from Paramak's `rotation_angle`, which specifies the toroidal sector being constructed.

## Figures suitable for approximate geometry extraction

| Figure | Page | Potential use |
| --- | --- | --- |
| 2(a) | 4 | Plasma equilibrium, X-points, divertor-leg arrangement, and surrounding boundary. |
| 12(c) | 18 | Overall cross-section: central-solenoid modules, shaping coils, vacuum vessel, TF outline, and correction-coil locations. |
| 15 | 21 | Three-dimensional interpretation of the two off-midplane correction-coil rows. |

Figures 2(a) and 12(c) were visually inspected for this report. Figure 15's description and associated discussion were read; its three-dimensional geometry has not been digitized. No numerical profile coordinates were extracted. Any future image-derived dimensions must be labeled estimates, with source figure, scaling method, and tolerances. Confirm component boundaries rather than interpreting every plotted line as a physical solid.

## Information not established for a complete model

The review did not identify a complete numerical specification for the following:

- An explicit ARC major-radius value suitable for direct assignment. Plot axes permit estimation, but such an estimate is not a tabulated design value.
- TF-coil count, winding-pack dimensions, casing dimensions, and complete profiles.
- PF-coil centre coordinates, outer dimensions, and case thicknesses.
- Central-solenoid module dimensions and case construction.
- First-wall and vessel layer thicknesses, detailed blanket boundaries, and complete divertor profiles.
- Supports, ports, penetrations, cryostat construction, or a complete component inventory.
- Material compositions, densities, lithium enrichment, or a complete material-to-component mapping for neutronics.

These remain open inputs. The absence of a specification here does not establish that the real reactor lacks a component. Do not carry SPARC geometry over as verified ARC data.

## Modeling recommendations

1. Label the model as based on the Version 3A configuration studied in this paper.
2. Replace borrowed SPARC plasma assumptions with the documented ARC shaping targets and the 118 cm minor-radius value after checking equilibrium consistency and triangularity conventions.
3. Obtain a sourced major radius before finalizing plasma size; do not silently retain SPARC's 185 cm value.
4. Represent double-null topology and investigate the 2 cm HFS/LFS wall gaps without imposing that spacing on divertor regions.
5. Include a distinct FLiBe immersion-blanket region once its boundaries are known; keep detailed material assignment separate from CAD colors.
6. Reassess SPARC-specific VS, antenna, divertor-coil, and EFCCU components individually. Use the paper's correction-coil recommendation as an optional, explicitly sourced design feature.
7. Record missing inputs, digitized estimates, and intentional approximations with `#ARC` markers when implementing them.
8. Add regressions for documented dimensions, double-null symmetry, applicable clearances, and correction-coil placement. Use geometry validity, imprinting, and transport tests as additional workflow checks; they do not prove fidelity to the paper.

## Follow-up source

The paper refers readers to J. Hillesheim et al., *Overview of the physics basis for the ARC fusion power plant*, Journal of Plasma Physics **92**, E69 (2026), DOI https://doi.org/10.1017/S0022377826101706, for broader design and equilibrium-generation context. This follow-up paper has not been reviewed here.
