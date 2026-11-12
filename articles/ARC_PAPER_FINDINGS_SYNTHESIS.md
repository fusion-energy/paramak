# ARC paper findings: agreement and implementation conclusions

## Decision summary

The four reviewed papers support a **paper-based ARC V3A plasma approximation and a set of geometry constraints**. They do **not** yet specify a complete, conclusively dimensioned reactor assembly.

For the existing constructor, `arc_from_2026_paper` (referred to in the request as `from_arc_paper`), the strongest supported inputs are **major radius 462 cm**, **minor radius 118 cm**, **separatrix shaping targets approximately 1.8 elongation and 0.65 triangularity**, and an **up–down symmetric double-null design**. A full-volume reference is **189 m3**. Numerical boundary data or explicitly documented approximations are still needed to turn these targets into an accurate plasma boundary and surrounding solids.

This document synthesizes the four local paper reviews. It introduces no code changes, new geometry digitization, or additional literature review. Paper values are design-study inputs, not as-built measurements or finalized engineering specifications.

## Sources

| Short name | Paper and findings report |
| --- | --- |
| MHD | Leuthold et al., *ARC physics basis–magnetohydrodynamics*, E49 (2026), DOI 10.1017/S0022377826101421. [Findings](ARC_PHYSICS_BASIS_MAGNETOHYDRODYNAMICS_FINDINGS.md), [PDF](arc_physics_basismagnetohydrodynamics.pdf). |
| Transport | Howard et al., *Performance and transport in the ARC tokamak*, E67 (2026), DOI 10.1017/S0022377826101573. [Findings](PERFORMANCE_AND_TRANSPORT_IN_THE_ARC_TOKAMAK_FINDINGS.md), [PDF](performance_and_transport_in_the_arc_tokamak.pdf). |
| Exhaust | Eich et al., *Power and particle exhaust for the ARC fusion power plant*, E66 (2026), DOI 10.1017/S002237782610155X. [Findings](POWER_AND_PARTICLE_EXHAUST_FOR_THE_ARC_FUSION_POWER_PLANT_FINDINGS.md), [PDF](power_and_particle_exhaust_for_the_arc_fusion_power_plant.pdf). |
| Disruptions | Sweeney et al., *ARC disruption physics and strategy*, E68 (2026), DOI 10.1017/S0022377826101585. [Findings](ARC_DISRUPTION_PHYSICS_AND_STRATEGY_FINDINGS.md), [PDF](arc_disruption_physics_and_strategy.pdf). |

All describe V3A, but some calculations use different equilibrium realizations, rounded representative values, earlier designs, or optional modifications. Agreement across papers is corroboration within a shared design program, not independent experimental verification. The MHD paper's separate update notice has not been reviewed.

## Where the papers agree

| Quantity or feature | Evidence | Conclusion |
| --- | --- | --- |
| Major radius | Transport p.3 and Disruptions Table 1, p.3: 4.62 m; Exhaust Table 1, p.7: rounded 4.6 m | Use **462 cm** for the nominal V3A size. |
| Minor radius | Transport p.3 and Disruptions Table 1: 1.18 m; MHD Figure 4, p.8: 1.18 m; Exhaust Table 1: rounded 1.2 m | Use **118 cm**; no evidence for SPARC's additional 6 cm shrinkage. |
| Full-plasma volume | Transport p.3, Disruptions Table 1, Exhaust p.13: 189 m3 | Use as a reference for the intended boundary, **189,000,000 cm3**. |
| Separatrix shaping | MHD p.2 and Transport p.4: approximately kappa=1.8 and delta=0.65 | Supported shaping targets; parameter conventions and boundary fidelity require care. |
| Double-null symmetry | MHD p.2 and Exhaust abstract/Figure 1 | Model upper/lower symmetry for the selected nominal configuration. |
| FLiBe blanket/coolant | MHD p.7, Exhaust pp.16–17, Disruptions pp.15–17 | A FLiBe region belongs in a sufficiently detailed model; its complete dimensions and material definition are not established. |
| Nominal field/current | Transport p.3 and Disruptions Table 1: 11.4 T / 12 MA; Exhaust uses representative rounded field | Consistent nominal physics metadata; these do not construct coil geometry. |

The earlier MHD-only report left the major radius open. Transport and Disruptions now close that specific gap; they do not contradict that report's statement about what the MHD paper itself supplied.

## Apparent differences and unresolved consistency checks

### Shaping values describe different quantities

- Separatrix elongation **1.8** is different from the Disruptions table's areal quantity **1.55**, Exhaust's representative areal elongation **1.6**, and its edge-calculation **kappa95=1.5**.
- Exhaust's **delta95=0.36** is not the same quantity as separatrix triangularity **0.65**.
- Do not average these numbers or substitute them for one another. Retain the definition and equilibrium associated with each value.

Paramak currently uses `R(theta)=R0+a*cos(theta+d*sin(theta))`. For this analytical curve, the geometric top-point triangularity is `sin(d)`, not `d`. Consequently, assigning `d=0.65` does not reproduce geometric triangularity 0.65. A conversion or fitted profile must be justified as an approximation; it does not recover the real X-point boundary.

### Figure anchors do not establish one exact combined equilibrium

Exhaust Figure 1, p.3 labels the lower primary X-point **(R,Z)=(390,-224) cm** and secondary X-point **(493,-364) cm**; Section 3.3, p.16 gives a target radius of **510 cm**. Upper mirror coordinates can be inferred from the stated symmetry.

Do not impose every label together with approximate shaping numbers as exact constraints without checking definitions and equilibrium provenance. For example, 224/118 is approximately **1.90**, whereas the quoted separatrix elongation is approximately 1.8. That comparison is a warning to reconcile definitions/configurations, not proof of a paper error. The secondary X-point is in the divertor region, not on the core LCFS. Choose one boundary dataset or document how an approximation reconciles these inputs.

### Performance values are scenario-dependent

Transport Table 1, p.13 predicts fusion powers from **677 to 1295 MW** depending on the model; POPCON gives **1133 MW**. Exhaust often adopts **120 MW separatrix power** for its scenario. These are not conflicting CAD dimensions and must not be combined into a single supposedly definitive performance result. Likewise, magnetic connection lengths of 120–170 m are not physical poloidal channel lengths.

### Material assumptions and optional hardware are conditional

- Disruptions p.5 explicitly calls the vanadium-alloy vessel and tungsten armour material choices placeholders. Their assumed electromagnetic properties do not specify final OpenMC materials.
- Disruptions p.17 uses **0.5 cm W**, **1 cm inner V**, and **3 cm outer V** shells. The **4.5 cm effective thickness** used on p.43 is not evidence for a contiguous three-layer wall with no coolant gap.
- MHD recommends external error-field correction coils; Disruptions explores an optional in-vessel runaway-electron mitigation coil. They have different functions and are not alternative specifications of the same coil.
- MHD's conclusion that dedicated in-vessel vertical-stability coils are unnecessary does not exclude the optional REMC.

## What can conclusively enter the constructor

“Conclusive” here means directly supported for the studied configuration, with the qualifications below; it does not imply the full component geometry is known.

| Input or requirement | Implementation status | Remaining qualification |
| --- | --- | --- |
| `major_radius = 462.0` cm | **Ready as a sourced nominal input** | Attach V3A provenance. |
| `minor_radius = 118.0` cm | **Ready as a sourced nominal input** | Do not retain SPARC's unexplained clearance shrinkage. |
| Separatrix elongation target 1.8 | **Ready as an approximate shape target** | Verify compatibility with the chosen boundary and X-point definition. |
| Geometric triangularity target 0.65 | **Ready as an approximate shape target** | Not automatically the current primitive's coefficient; resolve parameterization. |
| Up–down symmetry | **Ready as the nominal topology requirement** | Centering at Z=0 is a modeling coordinate choice consistent with the depicted symmetric configuration. |
| Double-null / long baffled outer-leg divertor concept | **Ready as a topology requirement** | Requires profiles; a smooth plasma primitive alone does not implement X-points or legs. |
| Approximately 2 cm HFS/LFS wall clearance | **Ready as a localized constraint** | MHD p.3; do not apply as a uniform offset throughout the divertor. |
| Plasma reference volume 189 m3 | **Ready as validation/reference data** | Not an argument to `_build_assembly`; simplified geometry needs a declared tolerance. |
| FLiBe blanket/coolant region | **Ready as a component requirement** | Geometry and detailed material properties still missing. |

A standalone **plasma-only approximation** can therefore be constructed and passed to `_build_assembly`, with radius/shape metadata reflecting the actual modeled shape. It should be labeled incomplete, and it will not satisfy the existing full paper-reactor tests that assume a vessel, PF coils/cases, and other registered parts. Passing an empty assembly or invented vessel merely to satisfy the API would not establish a paper-based reactor model.

## What can be included only as a documented variant or assumption

| Item | Sourced information | What still prevents complete CAD construction |
| --- | --- | --- |
| Vessel/armour layers | Disruptions: 0.5 cm W, 1 cm inner V, 3 cm outer V | Complete profiles, wall separation, coolant geometry, and final materials |
| Correction-coil option | MHD: two rows, six coils per row, approximately 200 cm height near plus/minus 60 degrees poloidally | Coil cross-sections, centreline data, supports, and accurate TF mounting surface |
| REMC option | Disruptions: 15×15 cm cross-section, internal FLiBe channel, up to 20 cm vessel bump-outs | Three-dimensional routing, coolant-hole dimensions, supports, and confirmation of adoption |
| MGI concept | Disruptions: 12 valves, 500 cm barrel length, 3.2 cm physical bore | Port coordinates, routing, bend geometry, external dimensions and materials |
| X-point/target anchors | Exhaust: coordinates and target radius above | A consistent equilibrium, wall/baffle/target profiles, thicknesses and tilt |

Keep optional REMC bump-outs out of the nominal vessel unless that variant is explicitly chosen. Do not replace the real 3.2 cm MGI bore with the 1.7 cm effective diameter used in a simplified flow calculation.

## Inputs that must remain unresolved

The four reviews do not establish a defensible replacement for the current provisional **TF-coil count 18** or **PF-case thickness 3 cm**. They also do not establish full TF geometry, PF/solenoid coordinates and dimensions, blanket thicknesses, cryostat geometry, port/support layouts, or final material densities/compositions and lithium enrichment.

Six correction coils per row are not six TF coils. Twelve injection valves are not a specified twelve-port equally spaced CAD layout. The 180-degree constructor sector is a software presentation default, not a machine design result. Preserve `colors` as a display option; colors do not assign materials.

No reviewed source justifies automatically retaining SPARC's exact antenna, inner-vessel profile, dedicated VS coils, divertor coils, EFCCU geometry, or solenoid module dimensions. Review each component independently; missing evidence is not evidence that the real machine lacks it.

## Implementation and validation recommendation

1. #ARC Start with a clearly labeled V3A plasma approximation using the sourced radii and reconciled shaping conventions, or obtain a numerical equilibrium boundary before implementing detailed topology.
2. #ARC Use Exhaust Figure 1 and the MHD cross-sections as profile-reconstruction sources, recording any digitization estimates and resolving the anchor/shaping consistency first.
3. #ARC Obtain missing engineering dimensions before claiming a complete paper reactor. The commonly cited Hillesheim overview (DOI 10.1017/S0022377826101706) remains an unreviewed follow-up source in these reports.
4. #ARC Add vessel/blanket/divertor and magnet components with explicit provenance and assumptions; keep optional hardware variants distinct.
5. #ARC Test nominal radii, actual modeled shaping and metadata, declared symmetry, relevant gaps, layer geometry, and volume agreement at a justified tolerance. Add X-point assertions only when the boundary representation actually contains them.
6. #ARC Register the completed model for the existing geometry, imprint, and transport cases. Passing those tests checks the CAD workflow; it does not validate detachment, MHD stability, disruption resilience, or realistic neutron response.

**Conclusion:** the papers agree sufficiently to replace SPARC's plasma-size placeholders and define the intended ARC V3A topology. They do not yet support a complete dimensioned reactor or finalized materials assignment without additional data or openly labeled modeling assumptions.
