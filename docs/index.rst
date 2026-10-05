
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

The style of reactor, sizes of components, plasma shape and number of radial or vertical layers can be specified.

.. raw:: html

    <div style="display: flex; justify-content: center;">
        <video width="45%" controls autoplay loop muted playsinline title="Spherical tokamak (paramak.spherical_tokamak_from_plasma and paramak.spherical_tokamak): a compact reactor with a blanket on the outboard side of the plasma and a centre column on the inboard side. The animation varies the thickness of each radial_build layer, the number of toroidal field coils, the poloidal field coil positions, the divertor size, the plasma elongation and triangularity, and the poloidal_build segmentation of the first wall and blanket.">
            <source src="_static/spherical_tokamak_animation.webm" type="video/webm">
            <source src="_static/spherical_tokamak_animation.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <video width="45%" controls autoplay loop muted playsinline title="Tokamak (paramak.tokamak_from_plasma and paramak.tokamak): a reactor with a blanket that goes around both the inboard and outboard sides of the plasma. The animation varies the thickness of each radial_build layer, the number of toroidal field coils, the poloidal field coil positions, the divertor size, the plasma elongation and triangularity, and the poloidal_build segmentation into first wall tiles and first wall and blanket modules.">
            <source src="_static/tokamak_animation.webm" type="video/webm">
            <source src="_static/tokamak_animation.mp4" type="video/mp4">
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

