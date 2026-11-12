# ARC disruption physics and strategy: modeling findings

## Source and scope

- **Paper:** Ryan Sweeney et al., *ARC disruption physics and strategy*, Journal of Plasma Physics **92**, E68 (2026).
- **DOI:** https://doi.org/10.1017/S0022377826101585
- **Local PDF:** [arc_disruption_physics_and_strategy.pdf](arc_disruption_physics_and_strategy.pdf).
- **Design:** ARC V3A, explicitly an evolving snapshot (p.5). Some early disruption simulations use V2A and scaling to V3A; do not mix their geometry indiscriminately.
- Printed page numbers match PDF pages. Figure 6 on p.15 was visually inspected in addition to the text review.

This report identifies geometry and material assumptions relevant to `arc_from_2026_paper`. No code was changed. Distinguish baseline machine assumptions, simplified analysis representations, optional mitigation concepts, and SPARC-specific examples throughout this paper.

## Baseline machine parameters

Table 1, p.3 provides:

| Quantity | Value | Use |
| --- | --- | --- |
| Major radius R | 4.62 m = **462 cm** | Independently corroborates the transport paper |
| Minor radius a | 1.18 m = **118 cm** | Independently corroborates the transport/MHD papers |
| Plasma volume | 189 m3 = **189,000,000 cm3** | Boundary-reconstruction reference, not a complete shape |
| Elongation quantity kappa_a | 1.55 | An areal shaping quantity; do not substitute for separatrix elongation 1.8 |
| Plasma current | 12.0 MA | Physics/load scenario metadata |
| Toroidal field | 11.4 T | Physics/load scenario metadata |
| Thermal / fast-ion energies | 231 / 30 MJ | Load-scenario inputs, not CAD dimensions |
| Average electron density | 2.44×10^20 m^-3 | Plasma-scenario input |

The text later discusses approximately 261 MJ when including fast-ion thermalization. This is an energy accounting choice, not a different plasma size. Precise agreement of a simplified CAD volume with 189 m3 requires an independently justified boundary approximation and tolerance.

## Vessel layers and material assumptions

The authors explicitly state on **p.5** that a **vanadium-based structural alloy and tungsten-based plasma-facing armour are placeholders**, with final choices dependent on R&D and engineering.

Section 5.1.1, **p.17**, represents the vessel in ThinCurr as three axisymmetric electromagnetic shells:

| Region | Thickness used | Resistivity used |
| --- | --- | --- |
| Inner-VV tungsten layer | **0.5 cm** | 330 nOhm m |
| Inner-VV vanadium layer | **1 cm** | 600 nOhm m |
| Outer-VV vanadium layer | **3 cm** | 600 nOhm m |

Each shell is positioned at the innermost surface of its corresponding volumetric region. These are useful layer-thickness assumptions for a paper-based model, but do not fully specify the volumetric boundaries or spacing of the inner and outer vessel walls. Do not collapse the three layers into one contiguous 4.5 cm wall without additional evidence.

On **p.43**, a simplified wall-time estimate uses **effective thickness 4.5 cm**, effective resistivity **550 nOhm m**, and estimates a **175 ms** wall time. This is an aggregate electromagnetic approximation, not a detailed cross-sectional construction prescription.

FLiBe exists in the vessel and immediately outside it; its electromagnetic contribution is neglected in the cited structural loading calculations (p.17). That omission does not justify omitting FLiBe in a neutronics model. Detailed composition, enrichment, temperatures/densities, cooling-channel dimensions, supports, and alloy fractions remain open inputs.

## Massive gas injection: baseline mitigation concept

Section 4.1, **pp.11–13**, scopes an ARC system with **12 valves** based on SPARC valve technology. Relevant dimensions and modeling assumptions include:

- Approximately **3 m** from the outboard-midplane plasma separatrix to the TF outer contour (p.12); this is a contextual radial distance, not a full TF profile.
- An additional **2 m** allowance for field reduction and a dog-leg path, giving a **5 m = 500 cm** barrel length (p.12).
- A real barrel inner diameter of **32 mm = 3.2 cm** (p.13).
- A **17 mm = 1.7 cm simulated effective diameter**, introduced to represent valve-orifice restriction in the one-dimensional flow model (p.13). Do not use this as the physical pipe diameter.
- A **0.5 litre = 500 cm3** plenum, **6 MPa** initial pressure, and **10/90 Ne/D2 mixture** for the scoped simulation (p.13).
- The dog leg is intended to prevent free neutron streaming, making realistic routing relevant to later neutronics modeling. The paper does not give a complete routing/port CAD specification.

The six-valve arrangement and Figure 20 elsewhere in the paper describe **SPARC**, not a six-valve ARC baseline. Valve count alone does not establish ARC port coordinates or equal toroidal spacing. Gas-mixture fractions are injection assumptions, not structural material fractions.

## Optional runaway-electron mitigation coil (REMC)

Section 4.2, **pp.14–16**, and Figure 6 describe an option that is **not established as part of the baseline**:

| Feature | Preliminary specification | Modeling implication |
| --- | --- | --- |
| Coil | Non-insulated tungsten, supported by vanadium, with an internal FLiBe cooling channel | Distinct conductor, support, and coolant regions if represented in detail |
| Outer cross-section | **15 × 15 cm** | Explicit preliminary dimension; central coolant-channel dimensions are not supplied |
| Geometry | SPARC-like n=1 non-axisymmetric coil | Cannot be represented faithfully as a simple axisymmetric toroidal ring |
| Vessel modification | Up to **20 cm** axisymmetric outward displacement around toroidal runs | Optional vessel variant, not a global 20 cm wall-thickness increase |
| Vertical legs | Inset into vessel channels; inner coil surface conformal to original first wall | Requires dedicated profile/clearance definition |
| Constraint | Must not intersect the limiter contour | Useful regression condition once actual boundaries exist |

The bump-outs displace FLiBe and may affect shielding of the outboard PF coils (pp.15–16). A detailed model must update coolant/blanket volume consistently rather than allowing coil/vessel overlaps. Figure 6 provides a qualitative layout, not complete numerical three-dimensional centreline data.

## Figures, analysis limits, and missing inputs

- **Figure 6, p.15:** useful for the optional vessel bump-out and REMC concept; visually inspected, not digitized.
- **Figure 7 and associated text, pp.17 onward:** electromagnetic vessel-shell/loading representation. Thin-shell meshes are analysis representations, not automatically watertight CAD solids.
- **Figure 19, p.41:** GEANT4–MEMENTO calculations use a **SPARC tungsten-heavy-alloy tile geometry**. The authors distinguish it from planned pure tungsten in ARC. Do not copy that tile as ARC engineering geometry or treat room-temperature simulation conditions as ARC operating temperatures.
- V2A disruption evolutions and V3A baseline dimensions must remain labeled separately. A disrupted/moving plasma boundary is not the nominal CAD plasma boundary.

Still missing are full R/Z layer profiles, inner/outer vessel separation and cooling geometry, precise REMC centreline and channel size, MGI routing and valve positions, TF/PF/solenoid dimensions and casing definitions, material densities/compositions, and a finalized port/support inventory. Electrical resistivity is not material density and cannot substitute for an OpenMC material definition.

## Recommendations and validation

1. #ARC Use the confirmed 462/118 cm machine radii with the selected V3A equilibrium and retain distinct separatrix/areal shaping definitions.
2. #ARC If adopting the vessel model, label 0.5 cm W, 1 cm inner V, and 3 cm outer V as this paper's provisional layer assumptions; source their actual profiles and coolant separations separately.
3. #ARC Keep the 12-valve MGI concept and optional REMC as distinct features; do not silently include REMC bump-outs in the nominal baseline.
4. #ARC For an optional REMC model, check 15×15 cm outer section, limiter clearance, non-axisymmetric routing, bump-out envelope, and displaced FLiBe volume without inferring the unknown coolant-hole size.
5. #ARC Use 3.2 cm physical barrel bore if modeling the scoped injection pipe; preserve 1.7 cm only as the effective flow-model parameter.
6. #ARC Add meaningful dimension/contact/clearance regressions and the shared validity, imprint, and neutron-transport checks. These do not validate disruption mitigation, thermal survival, or structural loads.

Read alongside [the transport findings](PERFORMANCE_AND_TRANSPORT_IN_THE_ARC_TOKAMAK_FINDINGS.md), [the exhaust findings](POWER_AND_PARTICLE_EXHAUST_FOR_THE_ARC_FUSION_POWER_PLANT_FINDINGS.md), and [the MHD findings](ARC_PHYSICS_BASIS_MAGNETOHYDRODYNAMICS_FINDINGS.md). This report adds conditional vessel-layer and mitigation-hardware information absent from the MHD review; it does not finalize material choices.
