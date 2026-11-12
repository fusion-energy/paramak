# Performance and transport in the ARC tokamak: modeling findings

## Source and scope

- **Paper:** N. T. Howard et al., *Performance and transport in the ARC tokamak*, Journal of Plasma Physics **92**, E67 (2026).
- **DOI:** https://doi.org/10.1017/S0022377826101573
- **Local PDF:** [performance_and_transport_in_the_arc_tokamak.pdf](performance_and_transport_in_the_arc_tokamak.pdf).
- **Design:** ARC V3A, explicitly distinguished from the earlier 2015 concept.
- Printed page numbers match PDF page numbers. Table 1 on p.13 was also visually inspected.

This report assesses inputs for `arc_from_2026_paper`; it does not change code. The paper is primarily about plasma performance and transport, rather than component engineering. Its plasma dimensions close an important gap in the earlier MHD-paper review.

## Directly useful geometric information

| Parameter / feature | Paper value | Paramak interpretation | Source |
| --- | --- | --- | --- |
| Major radius | 4.62 m | **462 cm**; replace the provisional SPARC 185 cm value | Section 2, p.3 |
| Minor radius | 1.18 m | **118 cm**; independently confirms the MHD paper's Figure 4 value | Section 2, p.3 |
| Plasma volume | 189 m3 | **189,000,000 cm3**; reference for assessing a reconstructed boundary | Section 2, p.3 |
| Separatrix elongation | 1.8 | Boundary shaping target, not an areal elongation | Section 2, p.4 |
| Separatrix triangularity | 0.65 | Boundary shaping target; verify parameterization convention | Section 2, p.4 |
| Magnet technology | High-temperature superconductors, anticipated REBCO | Design context; not enough to define a homogenized material | Section 2, p.3 |
| Demountable coils and interchangeable vessel concepts | Explicit design features | Model configuration variants rather than assuming one immutable vessel profile | Section 2, p.4; p.13 |

The paper gives no reason to retain the SPARC-only 6 cm minor-radius reduction. Any ARC clearance adjustment should be independently justified and documented.

The current `plasma_simplified` shaping coefficient is not automatically identical to geometric triangularity: its equation is `R(theta) = R0 + a*cos(theta + triangularity*sin(theta))`. Fit or verify the shape convention before assigning 0.65 literally. A smooth analytical boundary also does not reproduce double-null X-points and divertor legs. Treat the stated volume as a useful reference, not an exact acceptance criterion for a deliberately simplified boundary without an agreed approximation tolerance.

## Operating and source-model information

| Quantity | Value / assumption | Source and interpretation |
| --- | --- | --- |
| On-axis toroidal field | 11.4 T | Section 2, p.3; physics metadata, not a CAD dimension |
| Plasma current | 12.0 MA | Section 2, p.3 |
| Flattop duration | Approximately 900 s, pulsed operation | Section 2, pp.3–4 |
| Auxiliary heating | Up to 50 MW, hydrogen-minority ICRH around 180 MHz | Section 2, p.4; does not specify antenna dimensions |
| POPCON fusion power | 1133 MW | Table 1, p.13; a projection rather than guaranteed output |
| Other fusion predictions | 879 MW TRANSP–PORTALS; 895 MW ASTRA; 1295 MW TORAX; 677 MW PORTALS–CGYRO | Table 1, p.13; do not combine as one consistent scenario |
| POPCON average electron density | 2.44 × 10^20 m^-3 | Table 1, p.13 |
| POPCON average electron / ion temperatures | 11.4 / 10.3 keV | Table 1, p.13 |
| Species assumptions | D, T, H minority, lumped impurity, W; Zeff=1.5, n(D+T)/ne=0.85, nW/ne=1.5×10^-5 | Section 3, p.10; H-minority baseline discussed on p.6 |

These can inform a separately specified neutron-source or plasma scenario. They are not solid-material definitions and should not replace the existing CAD transport smoke tests' placeholder materials without an explicit neutronics workflow. The paper's turbulent plasma transport is different from the repository's OpenMC neutron-transport geometry tests.

## Missing inputs and modeling implications

The paper does not provide complete vessel/blanket profiles, wall-layer thicknesses, TF count or winding/case dimensions, PF locations and case sizes, solenoid module dimensions, port layouts, or engineering material compositions. The statement about REBCO does not establish bulk magnet composition, density, or superconducting volume fraction.

The authors discuss multiple vessel/plasma possibilities. Select one documented V3A configuration before mixing a boundary from another paper with the dimensions here. Keep geometric separatrix shaping separate from the areal/95%-flux quantities used in the other analyses.

## Recommended implementation and validation inputs

1. #ARC Use R=462 cm and a=118 cm as sourced V3A dimensions, with citation and page comments.
2. #ARC Use separatrix elongation 1.8 and triangularity 0.65 as geometry targets; document the shaping approximation or obtain equilibrium boundary data.
3. #ARC Compare a reconstructed full-plasma volume against 189 m3 with a tolerance justified by the chosen boundary approximation; keep this separate from exact CAD validity checks.
4. #ARC Keep pulse, field, current, and performance scenarios separate from constructor geometry parameters unless a clear API use is established.
5. #ARC Add dimension and metadata regressions, then existing geometry, imprint, and neutron-transport checks. Successful smoke tests do not validate plasma-performance predictions.

For engineering geometry, the authors refer to Hillesheim et al., *Overview of the physics basis for the ARC fusion power plant*, DOI https://doi.org/10.1017/S0022377826101706. That separate paper was not reviewed here.

## Relationship to the earlier report

This paper explicitly supplies the major radius that was not established in [the MHD findings](ARC_PHYSICS_BASIS_MAGNETOHYDRODYNAMICS_FINDINGS.md). It corroborates the 118 cm minor radius and the separatrix shaping targets. The earlier report remains a record of that paper alone.
