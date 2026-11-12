# Power and particle exhaust for the ARC fusion power plant: modeling findings

## Source and scope

- **Paper:** Thomas H. Eich et al., *Power and particle exhaust for the ARC fusion power plant*, Journal of Plasma Physics **92**, E66 (2026).
- **DOI:** https://doi.org/10.1017/S002237782610155X
- **Local PDF:** [power_and_particle_exhaust_for_the_arc_fusion_power_plant.pdf](power_and_particle_exhaust_for_the_arc_fusion_power_plant.pdf).
- **Design:** ARC V3A; the first-wall and divertor engineering design is explicitly not final.
- Printed page numbers match PDF pages. Figure 1 on p.3 was visually inspected; its labeled coordinates below are read from the figure, not estimated by digitizing pixels.

This report concerns geometry, component topology, and related constraints for `arc_from_2026_paper`. No code was changed.

## Explicit geometry and topology

| Finding | Paper location | Modeling interpretation |
| --- | --- | --- |
| Up–down symmetric divertors with secondary X-points in long, tightly baffled outer legs | Abstract, p.1; Section 3, pp.14–17; Figure 1, p.3 | Include upper/lower divertor regions, long outer-leg channels, and physical baffles. A simple single-null divertor is inadequate. |
| Lower primary X-point R=3.90 m, Z=-2.24 m | Figure 1, p.3 | **(390, -224) cm**; useful boundary/topology anchor |
| Lower secondary X-point R=4.93 m, Z=-3.64 m | Figure 1, p.3 | **(493, -364) cm**; magnetic anchor near the outer target region |
| Primary X-point radius 3.9 m; target radius 5.1 m | Section 3.3, p.16 | **390 / 510 cm**; target placed radially outward to increase flux expansion |
| Rounded reference major/minor radii 4.6 / 1.2 m | Table 1, p.7 | Representative heat-flux inputs, not higher-precision replacements for 4.62 / 1.18 m in the transport paper |
| Plasma volume 189 m3 | Section 2.4, p.13 | Corroborates the transport paper; volume is not a full boundary specification |
| Liquid FLiBe coolant and breeding blanket | Section 3.4, pp.16–17 | Helps permit later vessel/divertor changes; no complete blanket CAD profile supplied |

For an up–down symmetric approximation, mirroring the labeled lower X-points produces upper anchors at Z=+224 and +364 cm. This is a modeling inference from symmetry, not a separately tabulated coordinate set. X-points belong to the magnetic topology: do not create solid components at those points or equate the LCFS with the entire divertor cavity.

Figure 1's midplane inset labels core, pedestal, SOL, wall, and magnetic surfaces near R=5.8 m. These closely spaced labels describe distinct surfaces/regions. They must not be interpreted as wall thicknesses or copied into a uniform layer stack without checking the equilibrium definitions.

## Connection lengths are not CAD lengths

Section 3.3, p.16 distinguishes:

- **170 m** field-line connection length from outboard midplane to target, with **123 m** in the divertor leg for the reference field line.
- A conservative analysis reduction to **120 m total**, including **73 m** in the divertor leg.
- Approximately **1.15 toroidal** and **5.5 poloidal** flux expansion between the mid-leg and secondary X-point for the described near-SOL surface.

These are magnetic-field-line and flux-tube quantities. Do not draw a 73 m or 123 m tall divertor in CAD. The actual poloidal channel shape must come from the cross-section or equilibrium data.

## Shaping definitions and operating assumptions

Table 1, p.7 uses representative **areal elongation 1.6** and **delta95=0.36** for heat-flux estimates. Section 2, p.10 uses **kappa95=1.5** in an edge calculation. These differ in definition and/or approximation from **separatrix elongation 1.8 and triangularity 0.65** in the transport/MHD papers. Do not treat the numbers as interchangeable constructor inputs.

Other useful physics context includes Psep=120 MW, Ip=12 MA, representative density 2.4×10^20 m^-3, and upstream heat-flux width 0.56 mm (Table 1, p.7). The heat-flux width is a plasma-transport scale, not a mandatory CAD layer thickness or global mesh size.

The study predicts detachment using impurity seeding and discusses helium exhaust. Argon concentration around 0.9% in the divertor, neutral pressure around 20 Pa, and impurity enrichment assumptions are scenario-dependent plasma/neutral quantities, not material compositions for vessel solids. Tungsten sputtering/erosion estimates on pp.8–9 do not specify an armour thickness.

## Figure use, missing inputs, and design uncertainty

- **Figure 1, p.3:** strongest source here for overall plasma-facing contour, baffles, divertor entrances, primary/secondary topology, and labeled anchors.
- **Figure 4, p.15:** conceptual explanation of baffles and detachment; not an engineering drawing.
- **Figure 5, p.16:** field strength along a selected field line; useful for interpreting topology, not direct solid coordinates.
- Section 3.4, p.17 explicitly leaves divertor-leg width and first-wall geometry open and discusses a possible super-X alternative. Preserve configuration provenance rather than assuming the X-point-target geometry is final.

Missing engineering data include full numerical R/Z wall and target profiles, baffle thicknesses, target tilts, pumping-duct geometry, armour and cooling-channel dimensions, vessel layers, magnet dimensions, and complete material specifications. Do not infer all of these from the figure line widths.

## Recommendations for implementation and tests

1. #ARC Use the X-point-target, symmetric double-null concept for this specific V3A snapshot; label any simpler model as an approximation.
2. #ARC Obtain the first-wall/baffle/target profiles from numerical data or calibrated digitization of Figure 1, preserving the labeled anchors and documenting tolerances.
3. #ARC Separate plasma, wall/armour, divertor targets/baffles, and surrounding regions according to the intended simulation scope; magnetic separatrices are not material interfaces by default.
4. #ARC Test up–down symmetry, target radial placement, and the resulting channel/clearance geometry. If equilibrium data are represented, also test the magnetic anchors.
5. #ARC Supplement those paper-specific checks with valid-solids, no-overlap, intended-contact imprinting, and neutron-transport checks. CAD tests cannot establish detachment stability or particle-exhaust performance.

Read alongside [the transport findings](PERFORMANCE_AND_TRANSPORT_IN_THE_ARC_TOKAMAK_FINDINGS.md) for precise machine radii and [the MHD findings](ARC_PHYSICS_BASIS_MAGNETOHYDRODYNAMICS_FINDINGS.md) for wall-gap and correction-coil constraints. A complete profile has not been digitized in this review.
