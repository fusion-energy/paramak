# ARC V3A paper and supporting material

This folder contains the ARC V3A physics-basis overview paper and the five digital assets described in its Appendix A (pp. 40–43). The descriptions below are based on the local PDF and inspection of the data files. These are reference-design and simulation assets, not a final engineering design.

## Summary table

| File | Format / resolution | Contents and purpose |
| --- | --- | --- |
| [overview_of_the_physics_basis_for_the_arc_fusion_power_plant.pdf](overview_of_the_physics_basis_for_the_arc_fusion_power_plant.pdf) | Research paper | Explains the ARC V3A design, projected plasma performance, heating, operational scenarios, alpha-particle physics, pulse simulations, and remaining physics risks. Appendix A documents the accompanying data. |
| [device_V3A.json](device_V3A.json) | JSON; IMAS data schema | Reduced axisymmetric device description: coil geometry, circuits, nominal power supplies, limiter, vessel, blanket, and shielding. Contains no plasma equilibrium. |
| [geqdsk-ARCv3a](geqdsk-ARCv3a) | GEQDSK; 129 × 129 grid | FreeGS free-boundary magnetic equilibrium that supplied the plasma boundary for subsequent reference-scenario modelling. |
| [input.gacode_V3A](input.gacode_V3A) | GACODE text; 117 radial points, six ion species | Reference plasma profiles, flux-surface geometry, heating/radiation terms, and current-density quantities from the converged TRANSP calculation. |
| [ARC_V3A_kinetic_tokamaker_800res.eqdsk](ARC_V3A_kinetic_tokamaker_800res.eqdsk) | GEQDSK; 800 × 800 grid | Higher-resolution TokaMaker kinetic equilibrium incorporating bootstrap current; used for error-field and tearing-mode analysis. |
| [p100000.00001_V3A_800res](p100000.00001_V3A_800res) | Block-structured profile text; 800 points per profile | Kinetic profiles and their flux derivatives associated with the TokaMaker equilibrium, plus electric-field and flow-related quantities. |
| All six `*:Zone.Identifier` files | Windows download metadata | Each records `[ZoneTransfer]` and `ZoneId=3`; these sidecars contain no scientific data. |

## Paper overview

**J. C. Hillesheim et al., “Overview of the physics basis for the ARC fusion power plant,” Journal of Plasma Physics 92, E69 (2026).** DOI: [10.1017/S0022377826101706](https://doi.org/10.1017/S0022377826101706).

The paper presents the plasma-physics basis for Commonwealth Fusion Systems’ ARC V3A reference design: a high-field deuterium–tritium tokamak targeting approximately **1.13 GW of fusion power and 400 MW net electricity**. Nominal parameters include a 4.62 m major radius, 1.18 m minor radius, 11.4 T on-axis field, and 12 MA plasma current. Operation is pulsed, with a 900 s fusion-power flattop and approximately 60 s between flattops.

The design combines high-temperature superconducting magnets, a liquid FLiBe blanket, a replaceable vacuum vessel, and a double-null, long-legged X-point-target divertor. FLiBe provides cooling, tritium breeding, and shielding. Vessel replacement after roughly 1–2 full-power years would also allow changes to materials and geometry as experience accumulates.

The analysis covers empirical performance projections, H-mode access, hydrogen-minority ion-cyclotron heating, candidate operating regimes that avoid damaging edge-localised modes (ELMs), alpha-particle losses and instabilities, and full-pulse magnetic-flux consumption. Illustrative results include a minimum 50 MW coupled RF-heating capability, low predicted alpha losses for well-aligned coils, and about 181 Wb consumed from a 215 Wb flux allowance for the nominal 900 s scenario.

The performance values are design targets and model predictions. Higher-fidelity fusion-power predictions span approximately 600–1300 MW. Key unresolved issues include integrated confinement and exhaust, impurity control, ELM avoidance, disruption mitigation, and reliable operation. SPARC is intended to test many of these assumptions; long-pulse behaviour and cumulative material damage require additional evidence. Companion papers on transport, boundary physics, disruptions, and MHD stability are referenced but are not included in this folder.

## Supporting files

### `device_V3A.json` — device geometry and electrical model

The JSON uses IMAS data-dictionary version 3.41.0, with top-level sections `dataset_description`, `pf_active`, `summary`, and `wall`. It describes 16 central-solenoid/PF coils, 16 circuits, and 16 supplies. Coil elements include positions, cross-sectional geometry, and signed turn counts; the electrical model includes resistances, delays, and current/voltage limits. Wall entries describe the limiter, tungsten first wall, inner and outer vessel walls, blanket, and shielding.

This is the reduced device model underlying pulse-evolution and vertical-stability calculations (Figure 12). Appendix A explicitly states that the coil locations are correct, but turn subdivision and supply parameters are non-proprietary analogues. It omits ports and toroidal electrical breaks and should not be treated as detailed manufacturing geometry.

### `geqdsk-ARCv3a` — initial FreeGS equilibrium

This file contains the lower-resolution FreeGS equilibrium used to establish the reference plasma boundary (Figure 2). Its GEQDSK data describe the magnetic axis, poloidal-flux grid, pressure and magnetic-field functions, safety factor, and boundary/limiter coordinates. The plasma-current header is approximately −12 MA.

Appendix A identifies this boundary as the starting point for interpretative TRANSP calculations using PORTALS flux-matched profiles with TGLF and EPED. It is a distinct equilibrium from the TokaMaker file, rather than simply a coarser copy.

### `input.gacode_V3A` — transport and kinetic reference case

The file identifies itself as created with MITIM 3.0.0 and contains the medium-fidelity reference case from the converged TRANSP simulation, near the end of a sawtooth cycle. Its 117-point radial coordinate `rho` spans 0–1. Data include electron and species-resolved ion densities and temperatures, safety factor, flux-surface shaping, total pressure, RF and fusion heating, radiation, ohmic and bootstrap currents, and additional transport fields.

The six species are labelled `D T W B H He`; `B` represents the effective bulk thermal impurity used to reproduce dilution and effective charge, while H and He are marked as fast populations. Header comments specify units, including densities in 10¹⁹ m⁻³ and temperatures in keV. Some fields, including `w0` and the supplied particle-source and momentum-source arrays, are zero. This file supports the paper’s heating, alpha-loss, and Alfvén-mode calculations.

### `ARC_V3A_kinetic_tokamaker_800res.eqdsk` — kinetic stability equilibrium

This 800 × 800 GEQDSK file contains the TokaMaker equilibrium shown in Figure 15, based on kinetic profiles and bootstrap current calculated using the Sauter formula. It underlies the companion paper’s error-field and tearing-mode studies and is intended for analyses sensitive to the current profile.

Appendix A notes that bootstrap current changes the separatrix shape relative to the FreeGS equilibrium and slightly changes `q95`. Consequently, the two equilibria should be used with their respective modelling context. The TokaMaker header records approximately −11.4 T and −12 MA; signs and coordinate conventions matter when importing these files.

### `p100000.00001_V3A_800res` — profiles paired with TokaMaker

This file consists of named blocks, each normally containing 800 rows with three columns: normalised poloidal flux (`psinorm`, 0–1), the profile value, and its derivative with respect to that flux. Blocks cover electron/ion density and temperature, total pressure, angular-frequency quantities, radial electric field, poloidal-flow coefficient, and species/velocity information.

Units appear in the block headers: densities use 10²⁰ m⁻³, temperatures keV, and pressure keV × 10²⁰ m⁻³. Several flow-related arrays and the supplied `nz1`, `vtor1`, and `vpol1` arrays are zero. These profiles differ from the GACODE dataset in sampling and some values; they are not an identical resampling. Pair this file with the TokaMaker equilibrium for the corresponding kinetic/stability reference case.

### `*:Zone.Identifier` — download sidecars

There is one sidecar for each of the six source files listed above. All contain the same Windows Internet-zone marker (`ZoneId=3`). They provide download-origin metadata, not additional paper content, geometry, or plasma profiles.

## How the assets relate

The JSON supplies the reduced device geometry and electrical description. The FreeGS equilibrium supplies the initial boundary used in the transport workflow; the GACODE file holds the resulting reference profiles and transport quantities. The TokaMaker equilibrium and its 800-point profile file form a second pair tailored to current-profile-sensitive stability analysis. See Appendix A for the provenance and intended use of each asset, and check each file’s units and coordinates before combining datasets.
