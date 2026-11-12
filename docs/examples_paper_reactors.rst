Reactors from papers
====================

As well as the parametric reactors, the Paramak can be used to make non parametric reactors, where the shape of each component is given directly instead of being calculated from a few parameters.
The reactors on this page are examples of the types of reactors that can be made in this way.

- These functions create reactors with fixed geometry taken from figures in published papers.
- The coordinates were read off the figures, so they are approximate and the models do not exactly match the real machines.
- The rotation_angle, number_of_tf_coils and colors can be changed.

SPARC
-----

- Based on Figure 4 of A. J. Creely et al., "Overview of the SPARC tokamak", Journal of Plasma Physics 86(5) (2020), `doi:10.1017/S0022377820001257 <https://doi.org/10.1017/S0022377820001257>`_.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.sparc_from_2020_paper(rotation_angle=180)

ITER
----

- Based on the diagram in "ITER Project: International Cooperation and Energy Investment" (2020), `doi:10.1007/978-3-030-42913-3_26 <https://doi.org/10.1007/978-3-030-42913-3_26>`_.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.iter_from_2020_paper(rotation_angle=180)

EU DEMO
-------

- Based on Figure 2 of R. Kemp et al., "Definition of the basic DEMO tokamak geometry based on systems code studies", Fusion Engineering and Design (2015), `doi:10.1016/j.fusengdes.2015.06.097 <https://doi.org/10.1016/j.fusengdes.2015.06.097>`_.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.eu_demo_from_2015_paper(rotation_angle=180)

ARC scaffold
------------

.. #ARC Add vessel, blanket, divertor, and TF coils when sourced geometry is available.

``paramak.arc_from_2026_paper(rotation_angle=180.0, number_of_tf_coils=18,
pf_coil_case_thickness=3.0, colors=None)`` is an unfinished scaffold.
The default TF-coil count of 18 is sourced from Hillesheim et al. (2026), p.10.
Ten PF coils have separate winding packs and cases. The default 3 cm case
thickness is a provisional SPARC value, not a verified ARC dimension.
It returns a smooth plasma approximation using R=462 cm, a=118 cm,
elongation 1.8, and geometric triangularity target 0.65 from Howard et al.
(2026), doi:10.1017/S0022377826101573. The primitive uses an angular shaping
coefficient of arcsin(0.65), which is also reported as assembly triangularity.
Six central-solenoid modules are also included as rectangular solid envelopes
extracted from the public device_V3A.json element distributions (in cm). Names
central_solenoid_1 through central_solenoid_6 correspond to CS1U, CS1L, CS2U,
CS2L, CS3U, CS3L. These do not resolve turns or separate cases. Double-null
X-points, the blanket tank shell, and separate divertor target/baffle parts remain unimplemented.
PF names pf_coil_1 through pf_coil_10 (and pf_coil_case_1 through pf_coil_case_10)
map to PF1U, PF1L, PF2U, PF2L, ..., PF5U, PF5L. JSON element envelopes are
assumed to be case-inclusive outer dimensions; changing case thickness changes
the winding/case split while preserving those dimensions.

.. #ARC Confirm PF-case thickness and case-inclusive envelope interpretation from engineering data.

No ARC rendering or export example is executed at this stage.


.. #ARC Replace the assumed 40 cm TF extrusion when engineering data are available.

The TF part is built from the supplied outer (46 points) and inner (36 points)
R/Z perimeters, stored in metres and converted to cm. Straight segments join
consecutive points, with automatic closure. Their difference is extruded by
20 cm on each side of the placement plane: 40 cm total, an explicit modeling
assumption rather than a published ARC dimension. Eighteen coils are placed by
default and clipped to rotation_angle. No smoothing, Princeton-D fitting,
automatic PF cuts, or separate TF winding/case split is applied. Other coil
counts require checking packing with this fixed width.


.. #ARC Replace the cavity-clipped smooth plasma with a checked equilibrium boundary.

The first_wall part uses the tungsten first-wall inner/outer contours from
``device_V3A.json``, converted from metres to cm and revolved through rotation_angle.
Its nominal thickness is 0.5 cm; no new offset or thickness assumption is introduced.
The smooth plasma fit would protrude locally through the supplied wall, so it is
intersected with the inner cavity. This preserves the sourced wall geometry and
avoids overlap, but is an approximation rather than an equilibrium reconstruction.
The plasma metadata still describes the underlying analytical shaping inputs.
The wall has a neutral gray display color, overridable with colors["first_wall"].
A tungsten material composition/density is not assigned by the CAD constructor.


.. #ARC Add FLiBe cooling/blanket regions and the blanket tank from the remaining data.

The inner_vessel and outer_vessel parts use the explicit inner/outer JSON contours
for the nominal 1 cm inner and 3 cm outer vessel walls. The inner_vessel inner
surface reuses the first_wall outer contour so their interface matches exactly.
The nominal 4.5 cm cooling space between vessel walls is filled by flibe_first_wall.
The neutron_shield part revolves the supplied solid shield polygon. The paper
uses vanadium vessel walls and tungsten-carbide shielding as reference assumptions;
these CAD solids do not assign material compositions or densities. All three parts
support rotation_angle and colors keyed by their names. No offsets, inferred
thicknesses, shielding electrical breaks, or automatic clearance cuts are added.


.. #ARC Individual cooling channels/ribs and physical FLiBe composition remain unspecified.

The flibe_first_wall part is the entire inter-wall cooling region, constructed
from the outer perimeter of inner_vessel and the inner perimeter of outer_vessel.
Those faces are reused, so both interfaces match the surrounding vessel walls.
The homogeneous region is revolved through rotation_angle; its light green display
color can be overridden with colors["flibe_first_wall"]. It does not represent the
bulk blanket outside the vessel, and no FLiBe material composition or density is
assigned by the component name.


.. #ARC Add tank shell, detailed penetrations, and physical materials separately.

The flibe_blanket part is the homogeneous bulk liquid region inside the JSON
blanket-tank inner contour, excluding the complete outer vessel envelope and
neutron_shield. It therefore excludes both the plasma cavity and flibe_first_wall
cooling region. The inner tank contour is converted from metres to cm and the
resulting section is revolved through rotation_angle. The tank's thin annular
shell is not represented as liquid. The display color is overridable with
colors["flibe_blanket"]; composition, density, and lithium enrichment remain unspecified.
