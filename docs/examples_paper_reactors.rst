Reactors from papers
====================

- These functions create reactors with fixed geometry taken from figures in published papers.
- The coordinates were read off the figures, so they are approximate and the models do not exactly match the real machines.
- The rotation_angle, number_of_tf_coils and colors can be changed.

SPARC
-----

- Based on Figure 4 of A. J. Creely et al., "Overview of the SPARC tokamak", Journal of Plasma Physics 86(5) (2020), doi:10.1017/S0022377820001257.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.sparc_from_2020_paper(rotation_angle=180)

ITER
----

- Based on the diagram in "ITER Project: International Cooperation and Energy Investment" (2020), doi:10.1007/978-3-030-42913-3_26.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.iter_from_2020_paper(rotation_angle=180)

EU DEMO
-------

- Based on Figure 2 of R. Kemp et al., "Definition of the basic DEMO tokamak geometry based on systems code studies", Fusion Engineering and Design (2015), doi:10.1016/j.fusengdes.2015.06.097.

.. cadquery::
    :select: result
    :width: 100%
    :height: 600px

    import paramak

    result = paramak.eu_demo_from_2015_paper(rotation_angle=180)
