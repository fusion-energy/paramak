Parametric Reactors
===================

These are the current reactor designs that can be created using the Paramak.

.. image:: https://user-images.githubusercontent.com/8583900/115291309-7fe17300-a14c-11eb-9859-be85075eb0b9.png
   :width: 713
   :align: center


FlfSystemCodeReactor()
^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/136050185-da7e3cc8-1ead-4e11-8c17-2cbe2e4a3ad2.png
   :width: 450
   :align: center

.. automodule:: paramak.parametric_reactors.flf_system_code_reactor
   :members:
   :show-inheritance:


BallReactors 
------------

BallReactor()
^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/99136724-91af6f00-261e-11eb-9956-476b818a0ee3.png
   :width: 400
   :align: center

The above image is colored by components. The TF coils are blue, the PF coils
are red, PF coil cases are yellow, the center column shielding is dark green,
the blanket is light green, the divertor is orange, the firstwall is grey
and the rear wall of the blanket is teal.

.. image:: https://user-images.githubusercontent.com/8583900/119011892-6458ca80-b98d-11eb-92b1-bbc370cb9c84.png
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


Submersion Tokamaks
-------------------

SubmersionTokamak()
^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/99136719-8e1be800-261e-11eb-907d-a9bafaebdbb8.png
   :width: 400
   :align: center

The above image is colored by components, the TF coils are blue, the PF coils
are red, PF coil cases are yellow, the center column shielding is dark green, the blanket is light green, the
divertor is orange, the firstwall is grey and the rear wall of the blanket is
teal and the support legs are black.

.. image:: https://user-images.githubusercontent.com/8583900/116117207-e36f2180-a6b3-11eb-8c65-4263336b6a68.png
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


Specific use case reactors
--------------------------

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


Reactors from publications
--------------------------

EuDemoFrom2015PaperDiagram()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/8583900/110224418-4f62b400-7ed3-11eb-85f1-e40dc74f5671.png
   :width: 400
   :align: center

The above image is colored by component.

.. automodule:: paramak.parametric_reactors.eu_demo_2015_reactor
   :members:
   :show-inheritance:

IterFrom2020PaperDiagram()
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/40028739/110248118-cf3e5c00-7f6f-11eb-9e68-864c1a1e8676.png
   :width: 400
   :align: center

The above image is colored by component.

.. automodule:: paramak.parametric_reactors.iter_paper_2020
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

NegativeTriangularityReactor()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://user-images.githubusercontent.com/85617935/144302746-181689dd-a4a8-43d4-9ed5-33518f36d4de.png
   :width: 300
   :align: left

.. image:: https://user-images.githubusercontent.com/85617935/144303187-8cb71e2d-fc35-450f-a8f4-88b6650d56b7.png
   :width: 300
   :align: right

The above image is coloured by component. On the left the low_aspect attribute is True, whereas on the right, the 
low_aspect attribute is set to False, as well as the PF coils outside were moved +200 units from default outward. 

.. image:: https://user-images.githubusercontent.com/85617935/144302481-022bf072-c7f7-409e-9701-1e24b7a9a7de.jpg
   :width: 400
   :align: center

.. automodule:: paramak.parametric_reactors.negative_triangularity_reactor
   :members:
   :show-inheritance: