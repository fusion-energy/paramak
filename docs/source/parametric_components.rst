Parametric Components
=====================

These are components that represent a selection of the components found in fusion
reactors and are created from parameters. These components all inherit from the 
parametric Shape classes.

Blankets
---------


BlanketConstantThicknessArcH()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.BlanketConstantThicknessArcH(
      inner_lower_point=(300, -200),
      inner_mid_point=(400, 0),
      inner_upper_point=(300, 200),
      thickness=100,
      rotation_angle=180
   )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/56687624/88293663-38c86d80-ccf3-11ea-9bfa-c166fc99c52c.png
   :width: 300

.. automodule:: paramak.parametric_components.blanket_constant_thickness_arc_h
   :members:
   :show-inheritance:


BlanketConstantThicknessArcV()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.BlanketConstantThicknessArcV(
      inner_lower_point=(300, -200),
      inner_mid_point=(500, 0),
      inner_upper_point=(300, 200),
      thickness=100,
      rotation_angle=180
   )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/56687624/88293666-39f99a80-ccf3-11ea-8c8d-84275fd0e0ce.png
   :width: 350

.. automodule:: paramak.parametric_components.blanket_constant_thickness_arc_v
   :members:
   :show-inheritance:


BlanketFP()
^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.BlanketFP(
      thickness=100,
      stop_angle=-80,
      start_angle=250,
      offset_from_plasma=30,
      rotation_angle=180
   )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/8583900/94867319-f0d36e80-0438-11eb-8516-7b8f2a7cc7ee.png
   :width: 350

.. automodule:: paramak.parametric_components.blanket_fp
   :members:
   :show-inheritance:


BlanketFPPoloidalSegments()
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.BlanketFPPoloidalSegments(
      num_segments=7,
      segments_gap = 10,
      thickness=100,
      stop_angle=250,
      start_angle=-90,
      rotation_angle=180
   )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/8583900/98870151-ca0e4c00-246a-11eb-8a37-e7620344d8c1.png
   :width: 350

.. automodule:: paramak.parametric_components.blanket_poloidal_segment
   :members:
   :show-inheritance:


Blanket Cutting Tools
---------------------


BlanketCutterParallels()
^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/97329670-32580d80-186f-11eb-8b1a-b7712ddb0e83.png
   :width: 400

.. automodule:: paramak.parametric_components.blanket_cutter_parallels
   :members:
   :show-inheritance:


BlanketCutterStar()
^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.BlanketCutterStar(
    height=2000,
    width=2000,
    distance=100
   )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/8583900/97103794-b0b58380-16a6-11eb-86f0-fb5530d630af.png
   :width: 400

.. automodule:: paramak.parametric_components.blanket_cutters_star
   :members:
   :show-inheritance:


PoloidalSegmenter()
^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.PoloidalSegments(
      shape_to_segment=None,
      center_point=(450, 0),
      number_of_segments=10,
      rotation_angle=180,
   )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/8583900/93811079-84da5480-fc47-11ea-9c6c-7fd132f6d72d.png
    :width: 605px
    :align: center

.. automodule:: paramak.parametric_components.poloidal_segmenter
   :members:
   :show-inheritance:


Center Columns
--------------

CenterColumnShieldCylinder()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.CenterColumnShieldCylinder(
      inner_radius=80,
      outer_radius=100,
      height=300,
      rotation_angle=180,
    )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/56687624/88293674-3c5bf480-ccf3-11ea-8197-8db75358ff36.png
   :width: 370px

.. automodule:: paramak.parametric_components.center_column_cylinder
   :members:
   :show-inheritance:


CenterColumnShieldHyperbola()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.CenterColumnShieldHyperbola(
      inner_radius=50,
      mid_radius=75,
      outer_radius=100,
      height=300,
      rotation_angle=180
    )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/56687624/88293672-3b2ac780-ccf3-11ea-9907-b1c8fd1ba0f0.png
   :width: 410px

.. automodule:: paramak.parametric_components.center_column_hyperbola
   :members:
   :show-inheritance:


CenterColumnShieldFlatTopHyperbola()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.CenterColumnShieldFlatTopHyperbola(
      inner_radius=50,
      mid_radius=75,
      outer_radius=100,
      arc_height=220,
      height=300,
      rotation_angle=180
    )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/56687624/88293680-3ebe4e80-ccf3-11ea-8603-b7a290e6bfb4.png
   :width: 370px

.. automodule:: paramak.parametric_components.center_column_flat_top_hyperbola
   :members:
   :show-inheritance:


CenterColumnShieldFlatTopCircular()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.CenterColumnShieldFlatTopCircular(
      inner_radius=50,
      mid_radius=75,
      outer_radius=100,
      arc_height=220,
      height=300,
      rotation_angle=180
    )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/56687624/88293678-3d8d2180-ccf3-11ea-97f7-da9a46beddbf.png
   :width: 370px

.. automodule:: paramak.parametric_components.center_column_flat_top_circular
   :members:
   :show-inheritance:


CenterColumnShieldPlasmaHyperbola()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.CenterColumnShieldPlasmaHyperbola(
      inner_radius=150,
      mid_offset=50,
      edge_offset=40,
      height=800,
      rotation_angle=180
    )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/56687624/86241464-d3bda400-bb9a-11ea-83b4-a3ff0bf630c4.png
    :width: 180px
    :align: center

.. automodule:: paramak.parametric_components.center_column_plasma_dependant
   :members:
   :show-inheritance:


InboardFirstwallFCCS()
^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak

   shield_to_build_from = paramak.CenterColumnShieldCylinder(
      inner_radius=80,
      outer_radius=100,
      height=300,
      rotation_angle=180,
   )

   my_component = paramak.InboardFirstwallFCCS(
      central_column_shield=shield_to_build_from,
      thickness=50,
      rotation_angle=180,
   )

   cadquery_object = my_component.solid


.. image:: https://user-images.githubusercontent.com/8583900/94197757-219e2b80-feae-11ea-8e41-0786d56c8b66.png
    :width: 786px
    :align: center

.. automodule:: paramak.parametric_components.inboard_firstwall_fccs
   :members:
   :show-inheritance:

Coolant Channels
----------------


CoolantChannelRingStraight()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.CoolantChannelRingStraight(
      height=200,
      channel_radius=10,
      ring_radius=70,
      number_of_coolant_channels=8,
      workplane="XY",
      rotation_axis="Z",
      )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/56687624/99048848-ff5f8a80-258d-11eb-9073-123185d7a4fb.png
   :width: 230

.. automodule:: paramak.parametric_components.coolant_channel_ring_straight
   :members:
   :show-inheritance:


CoolantChannelRingCurved()
^^^^^^^^^^^^^^^^^^^^^^^^^^

|CoolantChannelRingCurvedallstp| |CoolantChannelRingCurvedsvg| |CoolantChannelRingCurvedstp|

.. |CoolantChannelRingCurvedallstp| image:: https://user-images.githubusercontent.com/56687624/99049933-5ade4800-258f-11eb-96c1-4506a8f646a9.png
   :width: 200
.. |CoolantChannelRingCurvedsvg| image:: https://user-images.githubusercontent.com/56687624/99048853-0090b780-258e-11eb-862e-763f7a0f7ec6.png
   :width: 230
.. |CoolantChannelRingCurvedstp| image:: https://user-images.githubusercontent.com/56687624/99049900-4f8b1c80-258f-11eb-81be-bc101e2168e2.png
   :width: 100

.. automodule:: paramak.parametric_components.coolant_channel_ring_curved
   :members:
   :show-inheritance:


Cutting Tools
-------------


CuttingWedge()
^^^^^^^^^^^^^^

|CuttingWedgestp| |CuttingWedgesvg|

.. |CuttingWedgestp| image:: https://user-images.githubusercontent.com/8583900/94726081-a678c180-0354-11eb-93f2-98d4b4a6839e.png
    :width: 300px
.. |CuttingWedgesvg| image:: https://user-images.githubusercontent.com/8583900/94726514-433b5f00-0355-11eb-94d2-06b2bba1ed4a.png
    :width: 300px

.. automodule:: paramak.parametric_components.cutting_wedge
   :members:
   :show-inheritance:


CuttingWedgeFS()
^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/94726081-a678c180-0354-11eb-93f2-98d4b4a6839e.png
    :width: 300px

.. automodule:: paramak.parametric_components.cutting_wedge_fs
   :members:
   :show-inheritance:


Divertors
---------

ITERtypeDivertor()
^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.ITERtypeDivertor(
      # default parameters
      rotation_angle=180
   )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/40028739/88180936-626b9100-cc2e-11ea-92df-1bac68b11e3b.png
    :width: 250px
    :align: center

.. automodule:: paramak.parametric_components.divertor_ITER
.. autoclass:: ITERtypeDivertor
   :members:
   :show-inheritance:


ITERtypeDivertorNoDome()
^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/56687624/91977407-871d5300-ed1a-11ea-91e5-922e5c9b31a0.png
    :width: 250px
    :align: center

.. automodule:: paramak.parametric_components.divertor_ITER_no_dome
.. autoclass:: ITERtypeDivertorNoDome
   :members:
   :show-inheritance:


Inner Toroidal Field Coils
--------------------------

InnerTfCoilsCircular()
^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.InnerTfCoilsCircular(
      inner_radius=25,
      outer_radius=100,
      number_of_coils=10,
      gap_size=5,
      height=300,
      rotation_angle=180
   )

   cadquery_object = my_component.solid

|InnerTfCoilsCircularstp| |InnerTfCoilsCircularsvg|

.. |InnerTfCoilsCircularstp| image:: https://user-images.githubusercontent.com/56687624/86241469-d9b38500-bb9a-11ea-935f-8644fa01ab8c.png
   :width: 210px
.. |InnerTFCoilsCircularsvg| image:: https://user-images.githubusercontent.com/56687624/88293695-41b93f00-ccf3-11ea-9ea8-338a64bb5566.png
   :width: 390px

.. automodule:: paramak.parametric_components.inner_tf_coils_circular
   :members:
   :show-inheritance:


InnerTfCoilsFlat()
^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.InnerTfCoilsFlat(
      inner_radius=25,
      outer_radius=100,
      number_of_coils=10,
      gap_size=5,
      height=300,
      rotation_angle=180
   )

   cadquery_object = my_component.solid

|InnerTfCoilsFlatstp| |InnerTfCoilsFlatsvg|

.. |InnerTfCoilsFlatstp| image:: https://user-images.githubusercontent.com/56687624/86241472-db7d4880-bb9a-11ea-8fb9-325b3342fe11.png
   :width: 210px
.. |InnerTfCoilsFlatsvg| image:: https://user-images.githubusercontent.com/56687624/88293697-42ea6c00-ccf3-11ea-9e92-dc698813f1ee.png
   :width: 390px

.. automodule:: paramak.parametric_components.inner_tf_coils_flat
   :members:
   :show-inheritance:


Poloidal Field coils
--------------------

PoloidalFieldCoil()
^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.PoloidalFieldCoil(
      center_point=(100, 100),
      height=20,
      width=20,
      rotation_angle=180
   )

   cadquery_object = my_component.solid

|PoloidalFieldCoilstp| |PoloidalFieldCoilsvg|

.. |PoloidalFieldCoilstp| image:: https://user-images.githubusercontent.com/56687624/86241487-dfa96600-bb9a-11ea-96ba-54f22ecef1ef.png
    :width: 330px
.. |PoloidalFieldCoilsvg| image:: https://user-images.githubusercontent.com/8583900/94807412-86461280-03e7-11eb-9854-ecf66489c262.png
    :width: 360px

.. automodule:: paramak.parametric_components.poloidal_field_coil
   :members:
   :show-inheritance:


PoloidalFieldCoilFP()
^^^^^^^^^^^^^^^^^^^^^

|PoloidalFieldCoilFPstp| |PoloidalFieldCoilFPsvg|

.. |PoloidalFieldCoilFPstp| image:: https://user-images.githubusercontent.com/56687624/86241487-dfa96600-bb9a-11ea-96ba-54f22ecef1ef.png
    :width: 330px
.. |PoloidalFieldCoilFPsvg| image:: https://user-images.githubusercontent.com/8583900/95579521-ba47b600-0a2d-11eb-9bdf-7f0415396978.png
    :width: 360px

.. automodule:: paramak.parametric_components.poloidal_field_coil_fp
   :members:
   :show-inheritance:


PoloidalFieldCoilSet()
^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.PoloidalFieldCoilSet(
      heights=[10, 10, 20, 20],
      widths=[10, 10, 20, 40],
      center_points=[(100, 100), (100, 150), (50, 200), (50, 50)],
      rotation_angle=180,
   )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/8583900/93832861-eb269d80-fc6e-11ea-861c-45de724478a8.png
    :width: 395px
    :align: center

.. automodule:: paramak.parametric_components.poloidal_field_coil_set
   :members:
   :show-inheritance:


PoloidalFieldCoilCase()
^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.PoloidalFieldCoilCase(
      center_point=(100, 100),
      coil_height=20,
      coil_width=20,
      casing_thickness=10,
      rotation_angle=180,
   )

   cadquery_object = my_component.solid

|PoloidalFieldCoilCasestp| |PoloidalFieldCoilCasesvg|

.. |PoloidalFieldCoilCasestp| image:: https://user-images.githubusercontent.com/56687624/86241492-e1732980-bb9a-11ea-9331-586a39d32cfb.png
    :width: 300px
.. |PoloidalFieldCoilCasesvg| image:: https://user-images.githubusercontent.com/8583900/94807553-bab9ce80-03e7-11eb-9a2a-1b78a780b049.png
    :width: 370px

.. automodule:: paramak.parametric_components.poloidal_field_coil_case
   :members:
   :show-inheritance:


PoloidalFieldCoilCaseFC()
^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak

   pf_coil = paramak.PoloidalFieldCoil(
      center_point=(100, 100),
      height=20,
      width=20,
      rotation_angle=180
   )

   my_component = paramak.PoloidalFieldCoilCaseFC(
      pf_coil=pf_coil,
      casing_thickness=10,
      rotation_angle=180,
   )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/56687624/86241492-e1732980-bb9a-11ea-9331-586a39d32cfb.png
    :width: 220px
    :align: center

.. automodule:: paramak.parametric_components.poloidal_field_coil_case_fc
   :members:
   :show-inheritance:


PoloidalFieldCoilCaseSet()
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak

   my_component = paramak.PoloidalFieldCoilCaseSet(
      heights=[10, 10, 20, 20],
      widths=[10, 10, 20, 40],
      casing_thicknesses=[5, 5, 10, 10],
      center_points=[(100, 100), (100, 150), (50, 200), (50, 50)],
      rotation_angle=180,
   )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/8583900/93908750-e86f8b00-fcf6-11ea-938e-349dd09e5915.png
    :width: 586px
    :align: center

.. automodule:: paramak.parametric_components.poloidal_field_coil_case_set
   :members:
   :show-inheritance:


PoloidalFieldCoilCaseSetFC()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   pf_coil_set = paramak.PoloidalFieldCoilSet(
      heights=[10, 10, 20, 20],
      widths=[10, 10, 20, 40],
      center_points=[(100, 100), (100, 150), (50, 200), (50, 50)],
      rotation_angle=180
   )

   my_component = paramak.PoloidalFieldCoilCaseSetFC(
      pf_coils=pf_coil_set,
      casing_thicknesses=[5, 5, 10, 10],
      rotation_angle=180
   )

   cadquery_object = my_component.solid


.. image:: https://user-images.githubusercontent.com/8583900/93908750-e86f8b00-fcf6-11ea-938e-349dd09e5915.png
    :width: 586px
    :align: center

.. automodule:: paramak.parametric_components.poloidal_field_coil_case_set_fc
   :members:
   :show-inheritance:


Port Cutters
------------

PortCutterRotated()
^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   my_component = paramak.PortCutterRotated(
      center_point=(450, 0),
      polar_coverage_angle=20,
      rotation_angle=10,
      polar_placement_angle=45,
      azimuth_placement_angle=0
   )

   cadquery_object = my_component.solid

|PortCutterRotatedstp| |PortCutterRotatedsvg|

.. |PortCutterRotatedstp| image:: https://user-images.githubusercontent.com/8583900/95115392-511a2700-073d-11eb-9cb9-d6d2bec80e2c.png
    :width: 300px
.. |PortCutterRotatedsvg| image:: https://user-images.githubusercontent.com/8583900/95115923-267c9e00-073e-11eb-898b-bafbb2626b02.png
    :width: 380px

.. automodule:: paramak.parametric_components.port_cutters_rotated
   :members:
   :show-inheritance:


PortCutterRectangular()
^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   my_component = paramak.PortCutterRectangular(
      distance=3,
      center_point=(0, 0),
      height=0.2,
      width=0.4,
      fillet_radius=0.02,
      azimuth_placement_angle=[0, 45, 90, 180]
   )

   cadquery_object = my_component.solid

|PortCutterRectangularstp| |PortCutterRectangularsvg|

.. |PortCutterRectangularstp| image:: https://user-images.githubusercontent.com/8583900/95790579-8f808a80-0cd7-11eb-83e1-872a98fe0bc8.png
    :width: 300px
.. |PortCutterRectangularsvg| image:: https://user-images.githubusercontent.com/8583900/99831528-1fc3b200-2b57-11eb-9b73-8efab06cf3ef.png
    :width: 300px

.. automodule:: paramak.parametric_components.port_cutters_rectangular
   :members:
   :show-inheritance:


PortCutterCircular()
^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   my_component = paramak.PortCutterCircular(
      distance=3,
      center_point=(0.25, 0),
      radius=0.1,
      azimuth_placement_angle=[0, 45, 90],
   )

   cadquery_object = my_component.solid

|PortCutterCircularstp| |PortCutterCircularsvg|

.. |PortCutterCircularstp| image:: https://user-images.githubusercontent.com/8583900/95790580-90b1b780-0cd7-11eb-944f-14fe290f8442.png
    :width: 300px
.. |PortCutterCircularsvg| image:: https://user-images.githubusercontent.com/8583900/99830949-53eaa300-2b56-11eb-886e-d5ee04c85b4a.png
    :width: 300px

.. automodule:: paramak.parametric_components.port_cutters_circular
   :members:
   :show-inheritance:


Plasmas
-------

Plasma()
^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.Plasma(
      major_radius=620,
      minor_radius=210,
      triangularity=0.33,
      elongation=1.85,
      rotation_angle=180,
   )

   cadquery_object = my_component.solid

|Plasmastp| |Plasmasvg|

.. |Plasmastp| image:: https://user-images.githubusercontent.com/8583900/87316638-f39b8300-c51d-11ea-918b-5194d600d068.png
    :width: 300px
.. |Plasmasvg| image:: https://user-images.githubusercontent.com/8583900/94805331-226e1a80-03e4-11eb-8623-3e6db0aa1489.png
    :width: 380px

.. automodule:: paramak.parametric_components.tokamak_plasma
   :members:
   :show-inheritance:


PlasmaFromPoints()
^^^^^^^^^^^^^^^^^^

|PlasmaFPstp| |PlasmaFPsvg|

.. |PlasmaFPstp| image:: https://user-images.githubusercontent.com/8583900/87316638-f39b8300-c51d-11ea-918b-5194d600d068.png
    :width: 300px
.. |PlasmaFPsvg| image:: https://user-images.githubusercontent.com/8583900/94805330-213ced80-03e4-11eb-80b4-b162f2f7a565.png
    :width: 380px

.. automodule:: paramak.parametric_components.tokamak_plasma_from_points
   :members:
   :show-inheritance:


PlasmaBoundaries()
^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.PlasmaBoundaries(
      A=-0.155,
      major_radius=620,
      minor_radius=210,
      triangularity=0.33,
      elongation=1.85,
      rotation_angle=180
   )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/8583900/97366104-a958ca80-189e-11eb-8bc6-9892b04ab053.png
    :width: 300px

.. automodule:: paramak.parametric_components.tokamak_plasma_plasmaboundaries
   :members:
   :show-inheritance:


Toroidal Field Coils
--------------------

TFCoilCasing()
^^^^^^^^^^^^^^

|TFCoilCasingallstp| |TFCoilCasingaCutstp| |TFCoilCasingsvg|

.. |TFCoilCasingallstp| image:: https://user-images.githubusercontent.com/8583900/98821523-94943f00-2427-11eb-8047-68f2762c56d7.png
    :width: 200px
.. |TFCoilCasingaCutstp| image:: https://user-images.githubusercontent.com/8583900/98821532-96f69900-2427-11eb-99e1-e2461be67511.png
    :width: 130px
.. |TFCoilCasingsvg| image:: https://user-images.githubusercontent.com/8583900/99081345-904c5b00-25ba-11eb-8a4f-956d4ad6bbc0.png
    :width: 310px

.. automodule:: paramak.parametric_components.tf_coil_casing
   :members:
   :show-inheritance:


ToroidalFieldCoilRectangle()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

|ToroidalFieldCoilRectangleallstp| |ToroidalFieldCoilRectanglesvg| |ToroidalFieldCoilRectangleastp|

.. |ToroidalFieldCoilRectangleallstp| image:: https://user-images.githubusercontent.com/8583900/86822598-bcdbed80-c083-11ea-820e-f6c13d639170.png
    :width: 200px
.. |ToroidalFieldCoilRectangleastp| image:: https://user-images.githubusercontent.com/8583900/94585086-6abbfa00-0277-11eb-91de-0b2548601587.png
    :width: 130px
.. |ToroidalFieldCoilRectanglesvg| image:: https://user-images.githubusercontent.com/56687624/98582375-cd62d580-22ba-11eb-8002-ea7c731bad8a.png
    :width: 310px

.. automodule:: paramak.parametric_components.toroidal_field_coil_rectangle
   :members:
   :show-inheritance:


ToroidalFieldCoilCoatHanger()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

|ToroidalFieldCoilCoatHangerallstp| |ToroidalFieldCoilCoatHangersvg| |ToroidalFieldCoilCoatHangerastp|

.. |ToroidalFieldCoilCoatHangersvg| image:: https://user-images.githubusercontent.com/56687624/98582371-cb991200-22ba-11eb-8e15-86d273a8b819.png
   :width: 300px
.. |ToroidalFieldCoilCoatHangerastp| image:: https://user-images.githubusercontent.com/8583900/98979392-3775b780-2513-11eb-9649-46839571f5dd.png
   :width: 130px
.. |ToroidalFieldCoilCoatHangerallstp| image:: https://user-images.githubusercontent.com/8583900/87075236-f04f8100-c217-11ea-9ffa-4791b722b9e7.png
   :width: 210px

.. automodule:: paramak.parametric_components.toroidal_field_coil_coat_hanger
   :members:
   :show-inheritance:


ToroidalFieldCoilPrincetonD()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.ToroidalFieldCoilPrincetonD(
      R1=80,
      R2=300,
      thickness=30,
      distance=30,
      number_of_coils=1
   )

   cadquery_object = my_component.solid

|ToroidalFieldCoilPrincetonDallstp| |ToroidalFieldCoilPrincetonDsvg| |ToroidalFieldCoilPrincetonDastp|

.. |ToroidalFieldCoilPrincetonDallstp| image:: https://user-images.githubusercontent.com/56687624/92124475-bd7bd080-edf5-11ea-9c49-1db6422d77a0.png
   :width: 250px
.. |ToroidalFieldCoilPrincetonDsvg| image:: https://user-images.githubusercontent.com/56687624/112809879-69c32400-9072-11eb-8f9f-34379d74659f.png
   :width: 280px
.. |ToroidalFieldCoilPrincetonDastp| image:: https://user-images.githubusercontent.com/8583900/94479853-4c012900-01cd-11eb-9b59-0fcd5f4dc531.png
   :width: 170px

.. automodule:: paramak.parametric_components.toroidal_field_coil_princeton_d
   :members:
   :show-inheritance:


ToroidalFieldCoilTripleArc()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.ToroidalFieldCoilTripleArc(
      R1=80,
      h=200,
      radii=(70, 100),
      coverages=(60, 60),
      thickness=30,
      distance=30,
      number_of_coils=1,
   )

   cadquery_object = my_component.solid



|ToroidalFieldCoilTripleArcallstp| |ToroidalFieldCoilTripleArcstp| |ToroidalFieldCoilTripleArcsvg|

.. |ToroidalFieldCoilTripleArcallstp| image:: https://user-images.githubusercontent.com/56687624/92124454-b654c280-edf5-11ea-96d2-c0957f37a733.png
   :width: 240px
.. |ToroidalFieldCoilTripleArcstp| image:: https://user-images.githubusercontent.com/8583900/94835218-51e34e00-0409-11eb-9372-0272c43a4844.png
   :width: 190px
.. |ToroidalFieldCoilTripleArcsvg| image:: https://user-images.githubusercontent.com/8583900/99848162-2eb75e00-2b71-11eb-80d2-6c695b56821d.png
   :width: 320px

.. automodule:: paramak.parametric_components.toroidal_field_coil_triple_arc
   :members:
   :show-inheritance:


ToroidalFieldCoilRectangleRoundCorners()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.ToroidalFieldCoilRectangleRoundCorners(
      with_inner_leg=False,
      lower_inner_coordinates=(0, 0),
      mid_point_coordinates=(100, 100),
      thickness=30,
      number_of_coils=1,
      distance=20,
      rotation_angle=180,
   )

   cadquery_object = my_component.solid

|TFCoilRoundCornersvg| |TFCoilRoundCornersvg2| |TFCoilRoundCornerstp|

.. |TFCoilRoundCornersvg| image:: https://user-images.githubusercontent.com/85617935/125979064-c9aff900-4a07-462d-91bd-53af3bc66559.png
   :width: 255
.. |TFCoilRoundCornersvg2| image:: https://user-images.githubusercontent.com/85617935/125979248-1dbbd7be-916b-4921-86ed-a942b6cda757.png
   :width: 255
.. |TFCoilRoundCornerstp| image:: https://user-images.githubusercontent.com/85617935/125977357-3b893496-fc6b-4f06-8a95-10164cb70d7c.png
   :width: 255

.. automodule:: paramak.parametric_components.toroidal_field_coil_round_corners
   :members:
   :show-inheritance:


Vacuum Vessels
--------------

VacuumVessel()
^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.VacuumVessel(
      height=20,
      inner_radius=10,
      thickness=2,
      rotation_angle=180,
   )

   cadquery_object = my_component.solid

|VacuumVesselstp| |VacuumVesselsvgWP| |VacuumVesselsvg|

.. |VacuumVesselstp| image:: https://user-images.githubusercontent.com/8583900/95792842-2d765400-0cdc-11eb-8a8a-e3a88e923bc0.png
   :width: 150
.. |VacuumVesselsvgWP| image:: https://user-images.githubusercontent.com/8583900/95792839-2c452700-0cdc-11eb-9313-edfd2bfad5dc.png
   :width: 350
.. |VacuumVesselsvg| image:: https://user-images.githubusercontent.com/8583900/95792893-4ed74000-0cdc-11eb-9d19-c66cdb3a5ca3.png
   :width: 255

.. automodule:: paramak.parametric_components.vacuum_vessel
   :members:
   :show-inheritance:


VacuumVesselInnerLeg()
^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.VacuumVesselInnerLeg(
      inner_height=760,
      inner_radius=400,
      inner_leg_radius=250,
      thickness=20,
      rotation_angle=180,
   )

   cadquery_object = my_component.solid


|VacuumVesselInnerLegstp| |VacuumVesselInnerLegsvg|

.. |VacuumVesselInnerLegstp| image:: https://user-images.githubusercontent.com/8583900/116575888-fa598200-a906-11eb-8c87-1fcfb7917342.png
   :width: 255
.. |VacuumVesselInnerLegsvg| image:: https://user-images.githubusercontent.com/58937462/116578576-76ed6000-a909-11eb-9592-d87f2e702514.png
   :width: 255

.. automodule:: paramak.parametric_components.vacuum_vessel_inner_leg
   :members:
   :show-inheritance:


CapsuleVacuumVessel()
^^^^^^^^^^^^^^^^^^^^^
.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.CapsuleVacuumVessel(
      outer_start_point=(0, -600),
      radius = 300,
      thickness=30,
      rotation_angle=180
   )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/85617923/125429341-e5bdf20d-1739-41ce-953b-eabc01c04511.png
   :width: 255

.. automodule:: paramak.parametric_components.capsule_vacuum_vessel
   :members:
   :show-inheritance:


Other components
----------------

ExtrudeRectangle()
^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component =  paramak.ExtrudeRectangle(
       height=10,
       width= 10,
       distance=20,
       center_point=(20, 20)
   )

   cadquery_object = my_component.solid

.. automodule:: paramak.parametric_components.extrude_rectangle
   :members:
   :show-inheritance:

ExtrudeHollowRectangle()
^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.ExtrudeHollowRectangle(
      height=10,
      width=15,
      casing_thickness=1,
      distance=2
   )

   cadquery_object = my_component.solid

.. image:: https://user-images.githubusercontent.com/8583900/145905435-87d05386-d2e5-4de3-8f03-5a08cc5a4b22.png
    :width: 200px

.. automodule:: paramak.parametric_components.extrude_hollow_rectangle
   :members:
   :show-inheritance:

HexagonPin()
^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.HexagonPin(
      length_of_side=5,
      distance=10,
      center_point=(10, 20)
   )

   cadquery_object = my_component.solid

|HexagonPinstp| |HexagonPinsvg|

.. |HexagonPinstp| image:: https://user-images.githubusercontent.com/8583900/107092190-07307300-67fb-11eb-995c-b5622de717ee.png
    :width: 300px
.. |HexagonPinsvg| image:: https://user-images.githubusercontent.com/8583900/107092487-9c336c00-67fb-11eb-8eb1-755462493140.png
    :width: 300px

.. automodule:: paramak.parametric_components.hexagon_pin
   :members:
   :show-inheritance:


RotatedTrapezoid()
^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.RotatedTrapezoid(
      length_1=10,
      length_2=20,
      length_3=30,
      pivot_angle=0,
      pivot_point=(100, 50),
      rotation_angle=180
   )

   cadquery_object = my_component.solid

|RotatedTrapezoidstp| |RotatedTrapezoidsvg|

.. |RotatedTrapezoidstp| image:: https://user-images.githubusercontent.com/8583900/101964551-b42aad00-3c09-11eb-8ff2-fc0e52ba33cc.png
   :width: 240px
.. |RotatedTrapezoidsvg| image:: https://user-images.githubusercontent.com/8583900/101966787-06230100-3c11-11eb-8d70-587b50aaf987.png
   :width: 510px

.. automodule:: paramak.parametric_components.rotated_trapezoid
   :members:
   :show-inheritance:


RotatedIsoscelesTriangle
^^^^^^^^^^^^^^^^^^^^^^^^

.. cadquery::
   :select: cadquery_object
   :gridsize: 0

   import paramak
   my_component = paramak.RotatedIsoscelesTriangle(
      height=20,
      base_length=15,
      pivot_angle=0,
      pivot_point=(100, 50),
      rotation_angle=180,
      workplane='XY'
   )

   cadquery_object = my_component.solid

|RotatedIsoscelesTrianglestp| |RotatedIsoscelesTrianglesvg|

.. |RotatedIsoscelesTrianglestp| image:: https://user-images.githubusercontent.com/8583900/102000883-e0b2f780-3ce3-11eb-94aa-4cd69d2647e2.png
   :width: 240px
.. |RotatedIsoscelesTrianglesvg| image:: https://user-images.githubusercontent.com/8583900/102001079-c37f2880-3ce5-11eb-967e-f9263a231257.png
   :width: 510px

.. automodule:: paramak.parametric_components.rotated_isosceles_triangle
   :members:
   :show-inheritance:
