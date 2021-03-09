Parametric Reactors
===================

These are the current reactor designs that can be created using the Paramak.

.. image:: https://user-images.githubusercontent.com/8583900/99137324-fddfa200-2621-11eb-9063-f5f7f60ddd8d.png
   :width: 713
   :align: center

BallReactor()
^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/99136724-91af6f00-261e-11eb-9956-476b818a0ee3.png
   :width: 400
   :align: center

The above image is colored by components. The TF coils are blue, the PF coils
are red, PF coil cases are yellow, the center column shielding is dark green,
the blanket is light green, the divertor is orange, the firstwall is grey
and the rear wall of the blanket is teal.

.. image:: https://user-images.githubusercontent.com/8583900/99298720-09a9af00-2842-11eb-816b-86492555f97d.png
   :width: 450
   :align: center

.. automodule:: paramak.parametric_reactors.ball_reactor
   :members:
   :show-inheritance:

SegmentedBlanketBallReactor()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/99136727-94aa5f80-261e-11eb-965d-0ccceb2743fc.png
   :width: 400
   :align: center

The above image is colored by components. The TF coils are blue, the PF coils
are red, PF coil cases are yellow, the center column shielding is dark green,
the blanket is light green, the divertor is orange, the firstwall is grey
and the rear wall of the blanket is teal. 

Note that there is an odd number of blanket segments in this diagram so that
the blanket breeder zone and the first wall can be see in this 180 slice.

.. image:: https://user-images.githubusercontent.com/8583900/99431100-1db4e580-2902-11eb-82ce-3f864d13524c.png
   :width: 450
   :align: center

Note the above image has the plasma purposefully hidden on the right hand side
so that the internal blanket structure can be seen.

.. automodule:: paramak.parametric_reactors.segmented_blanket_ball_reactor
   :members:
   :show-inheritance:

SingleNullBallReactor()
^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/99136728-983de680-261e-11eb-8398-51ae433f5546.png
   :width: 400
   :align: center

The above image is colored by components. The TF coils are blue, the PF coils
are red, PF coil cases are yellow, the center column shielding is dark green,
the blanket is light green, the divertor is orange, the firstwall is grey and
the rear wall of the blanket is teal.

.. automodule:: paramak.parametric_reactors.single_null_ball_reactor
   :members:
   :show-inheritance:

SubmersionTokamak()
^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/99136719-8e1be800-261e-11eb-907d-a9bafaebdbb8.png
   :width: 400
   :align: center

The above image is colored by components, the TF coils are blue, the PF coils
are red, PF coil cases are yellow, the center column shielding is dark green, the blanket is light green, the
divertor is orange, the firstwall is grey and the rear wall of the blanket is
teal and the support legs are black.

.. image:: https://user-images.githubusercontent.com/8583900/99829028-aaa2ad80-2b53-11eb-9fd2-eba7521a0289.png
   :width: 450
   :align: center

.. automodule:: paramak.parametric_reactors.submersion_reactor
   :members:
   :show-inheritance:

SingleNullSubmersionTokamak()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/99136731-9aa04080-261e-11eb-87a5-502708dfebcc.png
   :width: 400
   :align: center

The above image is colored by component. The TF coils are blue, the PF coils
are red, PF coil cases are yellow, the center column shielding is dark green,
the blanket is light green, the divertor is orange, the firstwall is grey, the
rear wall of the blanket is teal and the supports are black.

.. automodule:: paramak.parametric_reactors.single_null_submersion_reactor
   :members:
   :show-inheritance:

CenterColumnStudyReactor()
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/99136734-9e33c780-261e-11eb-837b-16a0bc59f8a7.png
   :width: 400
   :align: center

The above image is colored by component. The center column shielding is dark
green, the blanket is light green, the divertor is orange, the firstwall is
grey and the blanket is teal.

Note this reactor is purposefully simple so that center column parameter
studies can be performed quickly.

.. image:: https://user-images.githubusercontent.com/8583900/98946297-9e7f7600-24eb-11eb-92cd-1c3bd13ad49b.png
   :width: 600
   :align: center

.. automodule:: paramak.parametric_reactors.center_column_study_reactor
   :members:
   :show-inheritance:

EuDemoFrom2015PaperDiagram()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/110224418-4f62b400-7ed3-11eb-85f1-e40dc74f5671.png
   :width: 400
   :align: center

The above image is colored by component.

.. automodule:: paramak.parametric_reactors.eu_demo_2015_reactor
   :members:
   :show-inheritance:

SparcFrom2020PaperDiagram()
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/100032191-5ae01280-2def-11eb-9654-47c3869b3a2c.png
   :width: 400
   :align: center

.. automodule:: paramak.parametric_reactors.sparc_paper_2020
   :members:
   :show-inheritance:
