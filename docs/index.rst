
Paramak documentation
=====================



**Version**: |version|


.. toctree::
   :maxdepth: 3
   :caption: Contents:
   :hidden:

   install
   examples
   python_api

Parameter driven CAD creation for fusion reactors.

Paramak provides parameter driven creation of Tokamak and Spherical Tokamak CAD models as well as DAGMC compatible neutronics models.

The style of reactor, sizes of components, plasma shape and number of radial or vertical layers can be specified. Reactors from published papers (SPARC, ITER and EU DEMO) can also be made.

.. raw:: html

    <div style="display: flex; justify-content: center;">
        <video width="32%" controls autoplay loop muted playsinline title="Spherical tokamak (paramak.spherical_tokamak_from_plasma and paramak.spherical_tokamak): a compact reactor with a blanket on the outboard side of the plasma and a centre column on the inboard side. The animation varies the thickness of each radial_build layer, the number of toroidal field coils, the poloidal field coil positions, the divertor size, the plasma elongation and triangularity, the poloidal_build segmentation of the first wall and blanket, and their toroidal_build segmentation into sectors, on their own and together with the poloidal segments.">
            <source src="_static/spherical_tokamak_animation.webm" type="video/webm">
            <source src="_static/spherical_tokamak_animation.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <video width="32%" controls autoplay loop muted playsinline title="Tokamak (paramak.tokamak_from_plasma and paramak.tokamak): a reactor with a blanket that goes around both the inboard and outboard sides of the plasma. The animation varies the thickness of each radial_build layer, the number of toroidal field coils, the poloidal field coil positions, the divertor size, the plasma elongation and triangularity, the poloidal_build segmentation into first wall tiles and first wall and blanket modules, and the toroidal_build segmentation of the first wall and blanket into sectors, on their own and together with the poloidal modules.">
            <source src="_static/tokamak_animation.webm" type="video/webm">
            <source src="_static/tokamak_animation.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <video width="32%" controls autoplay loop muted playsinline title="Reactors from papers, shown one after the other: SPARC (paramak.sparc_from_2020_paper, based on Figure 4 of Overview of the SPARC tokamak, 2020), ITER (paramak.iter_from_2020_paper, based on the diagram in ITER Project: International Cooperation and Energy Investment, 2020) and EU DEMO (paramak.eu_demo_from_2015_paper, based on Figure 2 of Definition of the basic DEMO tokamak geometry based on systems code studies, 2015). The animation varies the rotation_angle of each reactor in turn from 1 to 360 degrees and back.">
            <source src="_static/paper_reactors_animation.webm" type="video/webm">
            <source src="_static/paper_reactors_animation.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </div>

.. grid:: 1 1 3 3
    :gutter: 2

    .. grid-item-card::
        :img-top: _static/getting_started.svg
        :text-align: center

        Installation
        ^^^

        .. button-ref:: install
            :expand:
            :color: secondary
            :click-parent:

            To the installation guide

    .. grid-item-card::
        :img-top: _static/user_guide.svg
        :text-align: center

        Examples
        ^^^

        .. button-ref:: examples
            :expand:
            :color: secondary
            :click-parent:

            To the examples

    .. grid-item-card::
        :img-top: _static/api.svg
        :text-align: center

        API reference
        ^^^

        .. button-ref:: python_api
            :expand:
            :color: secondary
            :click-parent:

            To the reference guide

