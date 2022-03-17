Examples
========

Parametric Shapes
-----------------

make_CAD_from_points.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/56687624/88064585-641c5280-cb63-11ea-97b1-1b7dcfabc07c.gif
   :width: 450
   :height: 275
   :align: center

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_shapes/make_CAD_from_points.ipynb>`__


make_blanket_from_parameters.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/56687624/87058944-9e4f3100-c200-11ea-8bd3-669b3705c179.png
   :width: 400
   :height: 400
   :align: center

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_shapes/make_blanket_from_parameters.ipynb>`__


make_blanket_from_points.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/56687624/87058930-998a7d00-c200-11ea-846e-4084dbf82748.png
   :width: 400
   :height: 400
   :align: center

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_shapes/make_blanket_from_points.ipynb>`__


make_can_reactor_from_parameters.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/56687624/87060447-74970980-c202-11ea-8720-403c24dbabcc.gif
   :width: 1300
   :height: 450
   :align: center

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_shapes/make_can_reactor_from_parameters.ipynb>`__


make_can_reactor_from_points.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/56687624/87060447-74970980-c202-11ea-8720-403c24dbabcc.gif
   :width: 1300
   :height: 450
   :align: center

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_shapes/make_can_reactor_from_points.ipynb>`__


make_html_diagram_from_stp_file.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/117488160-fb705c00-af63-11eb-882e-27e284ceb79f.png
   :align: center

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_shapes/make_html_diagram_from_stp_file.ipynb>`__

Parametric Components
---------------------

make_components_blankets.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_components/make_components_blankets.ipynb>`__


make_components_center_column.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_components/make_components_center_column.ipynb>`__

make_components_magnets.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_components/make_components_center_column.ipynb>`__

make_components_other.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_components/make_components_other.ipynb>`__


make_demo_style_blankets.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/93619812-02e0f600-f9d1-11ea-903c-913c8bcb0f1b.png
   :width: 1050
   :height: 350
   :align: center

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_components/make_demo_style_blankets.ipynb>`__


make_firstwall_for_neutron_wall_loading.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/93807581-bc92cd80-fc42-11ea-8522-7fe14287b3c4.png
   :width: 437
   :height: 807
   :align: center

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_components/make_firstwall_for_neutron_wall_loading.ipynb>`__


make_magnet_set.ipynb
^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/99276201-5088ac00-2824-11eb-9927-a7ea1094b1e5.png
   :width: 500
   :align: center

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_components/make_magnet_set.ipynb>`__


make_plasmas.ipynb
^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/93624384-2e1b1380-f9d8-11ea-99d1-9bf9e4e5b838.png
   :width: 1050
   :height: 700
   :align: center

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_components/make_plasmas.ipynb>`__


make_vacuum_vessel_with_ports.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_components/make_vacuum_vessel_with_ports.ipynb>`__


make_varible_offset_firstwall.ipynb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_components/make_varible_offset_firstwall.ipynb>`__


Parametric Reactors
-------------------


FlfSystemCodeReactor
^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :include-source: true
   :gridsize: 0

   import paramak
   my_reactor = paramak.FlfSystemCodeReactor(
      inner_blanket_radius=100.,
      blanket_thickness=70.,
      blanket_height=500.,
      lower_blanket_thickness=50.,
      upper_blanket_thickness=40.,
      blanket_vv_gap=20.,
      upper_vv_thickness=10.,
      vv_thickness=10.,
      lower_vv_thickness=10.,
      rotation_angle=180,
   )

   cadquery_object = my_reactor.solid


ball_reactor
^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :include-source: true
   :gridsize: 0

   import paramak
   my_reactor = paramak.BallReactor(
      inner_bore_radial_thickness=10,
      inboard_tf_leg_radial_thickness=30,
      center_column_shield_radial_thickness=60,
      divertor_radial_thickness=150,
      inner_plasma_gap_radial_thickness=30,
      plasma_radial_thickness=300,
      outer_plasma_gap_radial_thickness=30,
      plasma_gap_vertical_thickness=50,
      firstwall_radial_thickness=30,
      blanket_radial_thickness=50,
      blanket_rear_wall_radial_thickness=30,
      elongation=2,
      triangularity=0.55,
      number_of_tf_coils=16,
      rotation_angle=90,
      pf_coil_case_thicknesses=[10, 10, 10, 10],
      pf_coil_radial_thicknesses=[20, 50, 50, 20],
      pf_coil_vertical_thicknesses=[20, 50, 50, 20],
      pf_coil_radial_position=[500, 575, 575, 500],
      pf_coil_vertical_position=[300, 100, -100, -300],
      rear_blanket_to_tf_gap=50,
      outboard_tf_coil_radial_thickness=100,
      outboard_tf_coil_poloidal_thickness=50
   )

   cadquery_object = my_reactor.solid

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_reactors/ball_reactor.ipynb>`__


ball_reactor_single_null
^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :include-source: true
   :gridsize: 0

   import paramak
   my_reactor = paramak.SingleNullBallReactor(
      inner_bore_radial_thickness=50,
      inboard_tf_leg_radial_thickness=50,
      center_column_shield_radial_thickness=50,
      divertor_radial_thickness=90,
      inner_plasma_gap_radial_thickness=50,
      plasma_radial_thickness=200,
      outer_plasma_gap_radial_thickness=50,
      plasma_gap_vertical_thickness=30,
      firstwall_radial_thickness=50,
      blanket_radial_thickness=100,
      blanket_rear_wall_radial_thickness=50,
      elongation=2,
      triangularity=0.55,
      number_of_tf_coils=16,
      rotation_angle=90,
      pf_coil_case_thicknesses=[10, 10, 10, 10],
      pf_coil_radial_thicknesses=[20, 50, 50, 20],
      pf_coil_vertical_thicknesses=[20, 50, 50, 20],
      pf_coil_radial_position=[500, 575, 575, 500],
      pf_coil_vertical_position=[300, 100, -100, -300],
      rear_blanket_to_tf_gap=50,
      outboard_tf_coil_radial_thickness=100,
      outboard_tf_coil_poloidal_thickness=50,
      divertor_position="lower"
   )

   cadquery_object = my_reactor.solid

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_reactors/ball_reactor_single_null.ipynb>`__


center_column_study_reactor
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :include-source: true
   :gridsize: 0

   import paramak
   my_reactor = paramak.CenterColumnStudyReactor(
      inner_bore_radial_thickness=20,
      inboard_tf_leg_radial_thickness=50,
      center_column_shield_radial_thickness_mid=50,
      center_column_shield_radial_thickness_upper=100,
      inboard_firstwall_radial_thickness=20,
      divertor_radial_thickness=100,
      inner_plasma_gap_radial_thickness=80,
      plasma_radial_thickness=200,
      outer_plasma_gap_radial_thickness=90,
      elongation=2.3,
      triangularity=0.45,
      plasma_gap_vertical_thickness=40,
      center_column_arc_vertical_thickness=520,
      rotation_angle=90
   )

   cadquery_object = my_reactor.solid

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_reactors/center_column_study_reactor.ipynb>`__

eu_demo_from_2015_paper
^^^^^^^^^^^^^^^^^^^^^^^


.. cadquery::
   :select: cadquery_object
   :include-source: true
   :gridsize: 0

   import paramak
   my_reactor = paramak.EuDemoFrom2015PaperDiagram(
      rotation_angle=90
   )

   cadquery_object = my_reactor.solid

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_reactors/eu_demo_from_2015_paper.ipynb>`__


make_animation
^^^^^^^^^^^^^^


|animation1| |animation2|

.. |animation1| image:: https://user-images.githubusercontent.com/8583900/107040396-155ca000-67b7-11eb-8b99-4aa9bf8a8655.gif
   :width: 300
.. |animation2| image:: https://user-images.githubusercontent.com/8583900/107030664-e2131480-67a8-11eb-84bb-59656e9e7722.gif
   :width: 300

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_reactors/submersion_reactor.ipynb>`__


segmented_blanket_ball_reactor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :include-source: true
   :gridsize: 0

   import paramak
   my_reactor = paramak.SegmentedBlanketBallReactor(
      inner_bore_radial_thickness=5,
      inboard_tf_leg_radial_thickness=25,
      center_column_shield_radial_thickness=45,
      divertor_radial_thickness=150,
      inner_plasma_gap_radial_thickness=50,
      plasma_radial_thickness=300,
      outer_plasma_gap_radial_thickness=50,
      plasma_gap_vertical_thickness=30,
      firstwall_radial_thickness=15,
      blanket_radial_thickness=50,
      blanket_rear_wall_radial_thickness=30,
      elongation=2,
      triangularity=0.55,
      number_of_tf_coils=16,
      pf_coil_case_thicknesses=[10, 10, 10, 10],
      pf_coil_radial_thicknesses=[20, 50, 50, 20],
      pf_coil_vertical_thicknesses=[20, 50, 50, 20],
      pf_coil_radial_position=[500, 550, 550, 500],
      pf_coil_vertical_position=[270, 100, -100, -270],
      rear_blanket_to_tf_gap=50,
      rotation_angle=90,
      outboard_tf_coil_radial_thickness=100,
      outboard_tf_coil_poloidal_thickness=50,
      gap_between_blankets=30,
      number_of_blanket_segments=15,
      blanket_fillet_radius=15,
   )

   cadquery_object = my_reactor.solid

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_reactors/segmented_blanket_ball_reactor.ipynb>`__

sparc_from_2020_paper
^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :include-source: true
   :gridsize: 0

   import paramak
   my_reactor = paramak.SparcFrom2020PaperDiagram(
      rotation_angle=90
   )

   cadquery_object = my_reactor.solid

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_reactors/sparc_from_2020_paper.ipynb>`__


submersion_reactor
^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :include-source: true
   :gridsize: 0

   import paramak
   my_reactor = paramak.SubmersionTokamak(
      inner_bore_radial_thickness=30,
      inboard_tf_leg_radial_thickness=30,
      center_column_shield_radial_thickness=30,
      divertor_radial_thickness=80,
      inner_plasma_gap_radial_thickness=50,
      plasma_radial_thickness=200,
      outer_plasma_gap_radial_thickness=50,
      firstwall_radial_thickness=30,
      blanket_rear_wall_radial_thickness=30,
      number_of_tf_coils=16,
      rotation_angle=180,
      support_radial_thickness=90,
      inboard_blanket_radial_thickness=30,
      outboard_blanket_radial_thickness=30,
      elongation=2.00,
      triangularity=0.50,
      pf_coil_case_thicknesses=[10, 10, 10, 10],
      pf_coil_radial_thicknesses=[20, 50, 50, 20],
      pf_coil_vertical_thicknesses=[20, 50, 50, 20],
      pf_coil_radial_position=[500, 550, 550, 500],
      pf_coil_vertical_position=[270, 100, -100, -270],
      rear_blanket_to_tf_gap=50,
      outboard_tf_coil_radial_thickness=30,
      outboard_tf_coil_poloidal_thickness=30,
   )
   cadquery_object = my_reactor.solid

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_reactors/submersion_reactor.ipynb>`__


submersion_reactor_single_null
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :include-source: true
   :gridsize: 0

   import paramak
   my_reactor = paramak.SingleNullSubmersionTokamak(
      inner_bore_radial_thickness=30,
      inboard_tf_leg_radial_thickness=30,
      center_column_shield_radial_thickness=30,
      divertor_radial_thickness=80,
      inner_plasma_gap_radial_thickness=50,
      plasma_radial_thickness=200,
      outer_plasma_gap_radial_thickness=50,
      firstwall_radial_thickness=30,
      blanket_rear_wall_radial_thickness=30,
      number_of_tf_coils=16,
      rotation_angle=180,
      support_radial_thickness=90,
      inboard_blanket_radial_thickness=30,
      outboard_blanket_radial_thickness=30,
      elongation=2.00,
      triangularity=0.50,
      pf_coil_case_thicknesses=[10, 10, 10, 10],
      pf_coil_radial_thicknesses=[20, 50, 50, 20],
      pf_coil_vertical_thicknesses=[20, 50, 50, 20],
      pf_coil_radial_position=[500, 550, 550, 500],
      pf_coil_vertical_position=[270, 100, -100, -270],
      rear_blanket_to_tf_gap=50,
      outboard_tf_coil_radial_thickness=30,
      outboard_tf_coil_poloidal_thickness=30,
      divertor_position="lower",
      support_position="lower"
   )

   cadquery_object = my_reactor.solid

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_reactors/submersion_reactor_single_null.ipynb>`__


iter_from_2020_paper
^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :include-source: true
   :gridsize: 0

   import paramak
   my_reactor = paramak.IterFrom2020PaperDiagram(
      rotation_angle=90
   )

   cadquery_object = my_reactor.solid

`Link to notebook <https://github.com/fusion-energy/paramak/blob/develop/examples/example_parametric_reactors/iter_from_2020_paper.ipynb>`__
