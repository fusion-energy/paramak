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
X-points, vessel, blanket, divertor, and TF coils remain unimplemented.
PF names pf_coil_1 through pf_coil_10 (and pf_coil_case_1 through pf_coil_case_10)
map to PF1U, PF1L, PF2U, PF2L, ..., PF5U, PF5L. JSON element envelopes are
assumed to be case-inclusive outer dimensions; changing case thickness changes
the winding/case split while preserving those dimensions.

.. #ARC Confirm PF-case thickness and case-inclusive envelope interpretation from engineering data.

No ARC rendering or export example is executed at this stage.
