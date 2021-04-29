
import paramak
import numpy as np


class EuDemoFrom2015PaperDiagram(paramak.Reactor):
    """Creates geometry of a simplified EU DEMO model based on the published
    diagram in Figure 2 of Definition of the basic DEMO tokamak geometry based
    on systems code studies. Published in Fusion Engineering and Design
    http://dx.doi.org/10.1016/j.fusengdes.2015.06.097 . Coordinates extracted
    from the figure are not exact and therefore this model does not perfectly
    represent the reactor.

    Arguments:
        rotation_angle: the angle of the sector that is desired.
        number_of_tf_coils: the number of tf coils to include in the model
    """

    def __init__(
        self,
        rotation_angle: float = 360.,
        number_of_tf_coils: int = 16,
    ):

        super().__init__([])

        self.method = 'trelis'

        self.rotation_angle = rotation_angle
        self.number_of_tf_coils = number_of_tf_coils

    def create_tf_coils(self, vac_vessel_inner, vac_vessel) -> list:
        """Creates a 3d solids for each tf coil.

        Args:
            vac_vessel (Paramak.Shape): The vac_vessel that is used in a
                Boolean cut opperation to prevent overlaps
            vac_vessel_inner (Paramak.Shape): The vac_vessel_inner that is
                used in a Boolean cut opperation to prevent overlaps

        Returns:
            A list of CadQuery solids: A list of 3D solid volumes
        """
        # coil could be approximated with a ToroidalFieldCoilPrincetonD but is
        # not included in the paper diagram
        # R1 = 511 - 50 / 2
        # R2 = 1340 + 50 / 2
        # coil_thickness = 25

        tf_coil_casing = paramak.ExtrudeMixedShape(
            points=[
                (805.5787769784172, 755, "spline"),
                (956.8024674963419, 744.1181924666533, "spline"),
                (1019.8101517726496, 731.2212103849513, "spline"),
                (1082.8178360489574, 710.3882685687647, "spline"),
                (1145.8255203252652, 680.4042517472378, "spline"),
                (1208.833204601573, 642.5177956124913, "spline"),
                (1271.8408888778808, 593.9467051995316, "spline"),
                (1332.8160672097915, 533.1872171654991, "spline"),
                (1382.6124628475186, 468.4187133516837, "spline"),
                (1420.2138228188637, 405.19488907747836, "spline"),
                (1450.1932854987194, 339.5005122098444, "spline"),
                (1472.0427244009875, 273.43725790865426, "spline"),
                (1486.7783924978662, 209.78591729219943, "spline"),
                (1498.1749436860923, 130.9324032157914, "spline"),

                (1506.997123663055, -64.35717673922625, "spline"),
                (1499.4815546503473, -158.26084228529953, "spline"),
                (1489.8271514144617, -227.50802018403465, "spline"),
                (1473.5671038592855, -301.2681259821559, "spline"),
                (1453.7501709014145, -371.5510611717634, "spline"),
                (1429.3600995686502, -437.8837368553043, "spline"),
                (1402.4293958053895, -500.68420005071425, "spline"),
                (1367.3686682645407, -566.760952419447, "spline"),
                (1327.1758632140895, -630.9951968657044, "spline"),
                (1276.5156525499938, -694.4364968444456, "spline"),
                (1214.930722434764, -753.1636044922695, "spline"),
                (1151.9230381584562, -796.9412746643368, "spline"),
                (1088.9153538821483, -828.8191952873351, "spline"),
                (1025.9076696058407, -851.7220231166343, "spline"),
                (962.899985329533, -866.3620671041153, "spline"),

                (805.5787769784172, -875., "straight"),
                (377.70287769784176, -875., "straight"),
                (375.4508992805756, 755, "straight"),
            ],
            distance=200,
            cut=[vac_vessel_inner, vac_vessel],
            # azimuth placement angle can't start at
            # zero nor end at 360 until #757 is solved
            azimuth_placement_angle=np.linspace(
                0 + 20, 360 + 20, self.number_of_tf_coils),
            rotation_angle=self.rotation_angle,
            stp_filename="tf_coil_casing.stp",
            stl_filename="tf_coil_casing.stl",
            material_tag="tf_coil_casing_mat",
            color=(1., 1., 0.498),
        )

        return [tf_coil_casing]

    def create_vessel_components(self) -> list:
        """Creates a 3d solids for each vessel component.

        Returns:
            A list of CadQuery solids: A list of 3D solid volumes
        """

        blanket = paramak.RotateMixedShape(
            points=[
                (1028.5051619363035, -506.43908961374075, "spline"),
                (1192.275810836831, -281.2815003658492, "spline"),
                (1257.92101205376, -56.43827165248217, "spline"),
                (1244.8344044363996, 216.28835367966997, "spline"),
                (1153.671764932414, 400.5162013324601, "spline"),
                (988.2423861054414, 520.3252882504712, "spline"),
                (807.595124581199, 539.8030669696149, "spline"),
                (670.5280987407093, 475.18311549274034, "spline"),
                (584.8527692840913, 334.5130635036775, "spline"),
                (574.292831670967, 81.767193745908, "spline"),
                (579.3751030153657, -158.89465706473618, "spline"),
                (580.3587684368622, -363.4679185119577, "straight"),
                (686.29567682058, -355.1059282936036, "spline"),
                (657.9911865059497, -182.71061116031922, "straight"),
                (657.4125597874224, -62.3733985443065, "straight"),
                (656.6796326106211, 90.05373743597613, "straight"),
                (671.3960388185003, 294.67729656872143, "spline"),
                (725.9412508183462, 379.089387299264, "spline"),
                (804.2487333923825, 419.4532799322212, "spline"),
                (1036.1333908422225, 356.0153240651591, "spline"),
                (1095.4908483844877, 255.92292987253006, "spline"),
                (1127.4889059190507, 131.6750722070317, "spline"),
                (1128.4147086686944, -60.864467978588436, "spline"),
                (1082.0859960719372, -221.46497785651047, "spline"),
                (945.6554596218276, -418.4558632109989, "straight"),
            ],
            rotation_angle=self.rotation_angle,
            stp_filename="blanket.stp",
            stl_filename="blanket.stl",
            material_tag="blanket_mat",
            color=(0., 1., 0.498),
        )

        # SN Divertor
        divertor = paramak.RotateMixedShape(
            points=[
                (580.3587684368622, -363.4679185119577, "straight"),
                (678.5035036777448, -367.1647983979668, "straight"),
                (698.2057434436014, -383.14688797319684, "straight"),
                (706.2100797165632, -415.21166249470514, "straight"),
                (698.4950568028651, -443.3154942812033, "straight"),
                (694.7436269110794, -479.42923248738805, "straight"),
                (690.8764716755882, -491.47552817037024, "straight"),
                (726.2209203989679, -495.3735987984752, "straight"),
                (745.6917094774136, -463.22080332730013, "straight"),
                (769.222529364193, -459.1341163784806, "straight"),
                (788.8861940154811, -467.093725112643, "straight"),
                (808.5691462240535, -479.0645742673395, "straight"),
                (863.866572957985, -551.0908599376131, "straight"),
                (891.3995609812453, -563.0365602495477, "straight"),
                (895.1702784303153, -530.9340624638968, "straight"),
                (883.2602118072937, -502.8931027843033, "straight"),
                (886.9923541417953, -462.76812415758457, "straight"),
                (945.6554596218276, -418.4558632109989, "straight"),
                (1028.5051619363035, -506.43908961374075, "straight"),
                (985.8893041167635, -622.9033804444106, "straight"),
                (946.7548503870296, -647.096567181423, "straight"),
                (801.5291878153039, -647.5618207725194, "straight"),
                (675.5814387491815, -575.7618746871029, "straight"),
                (612.3761135287094, -491.72701659798975, "straight"),
                (584.5345245889013, -415.60146955751554, "straight"),
            ],
            rotation_angle=self.rotation_angle,
            stp_filename="divertor.stp",
            stl_filename="divertor.stl",
            material_tag="divertor_mat",
            color=(1., 0.667, 0.),
        )

        # Vacuum vessel
        vac_vessel_inner = paramak.RotateSplineShape(
            points=[
                (574.1267649651465, 101.10991818268735),
                (578.248235352396, 276.2517419573795),
                (576.2157294079991, 183.80759081183805),
                (574.6913499497014, 165.8825455403886),
                (592.9839034492745, 356.1350119397756),
                (618.3902277542372, 410.1718551122461),
                (660.0565996143763, 462.707847631295),
                (711.8855011965004, 503.98791778753997),
                (763.7144027786246, 528.2384308674821),
                (800.8076362638702, 535.0747131490673),
                (957.8187204685404, 529.1614255259608),
                (1009.6476220506645, 511.7304778365887),
                (1061.4765236327887, 484.3593637684569),
                (1113.3054252149127, 445.67421552338743),
                (1160.0530619360443, 396.81085941923095),
                (1196.1300424490914, 343.45306647581924),
                (1221.5363667540544, 290.06656753580216),
                (1239.3207937675284, 234.97736402844578),
                (1251.5158294339103, 177.39960361334886),
                (1259.8999164545482, 119.15248445488135),
                (1262.8978627225338, 91.48061850063345),
                (1257.7636381996099, -69.66392221833257),
                (1248.4670705173148, -117.9739684683608),
                (1236.2720348509329, -162.39122749437956),
                (1219.5038608096575, -215.31064328924913),
                (1198.1625483934886, -267.65634357273507),
                (1171.7399711163273, -320.87421415048993),
                (1140.7442554642726, -372.27816805066277),
                (1102.6347690068283, -425.0006755712611),
                (1058.9358912022924, -476.2931568156555),
                (1022.8589106892452, -523.1641842564957),
                (998.4688393564809, -582.3229466099988),
                (961.8837323573345, -633.8322193152558),
                (788.1044741113889, -641.8422854712626),
                (746.4381022512498, -626.4054742155761),
                (694.6092006691258, -595.170356965071),
                (646.3371844896964, -549.174826941633),
                (610.7683304627485, -496.43258230780384),
                (588.9188915604805, -442.35157799696844),
                (578.1466100551762, -383.4976698929381),
                (577.6991331872189, -343.8423522802541),
                (576.2157294079991, -254.96634344146696),
                (576.2157294079991, -201.97055742152952),
                (576.2157294079991, -148.97477140159208),
                (576.2157294079991, -95.97898538165487),
            ],
            rotation_angle=self.rotation_angle,
            # avoid overlap between VV and blanket divertor
            union=[blanket, divertor],
            material_tag="vacuum_vessel_inner_mat",
            stp_filename='vacvesselinner.stp',
            stl_filename='vacvesselinner.stl',
        )
        vac_vessel = paramak.RotateSplineShape(
            points=[
                (515.494614319138, 96.83488831627005),
                (515.494614319138, 142.76183497286695),
                (515.8212670602018, 194.68137603861783),
                (518.0121500911752, 287.54134932536317),
                (532.0087251173638, 362.3780050073017),
                (553.3500375335325, 416.5461291634835),
                (586.3782591299841, 470.34782313240567),
                (631.601516392818, 520.0453534354622),
                (683.4304179749421, 557.8818925196001),
                (735.2593195570662, 582.9203420676915),
                (785.0557151947934, 596.532729851823),
                (975.0950209959151, 588.576086076301),
                (1026.9239225780393, 570.6573643071777),
                (1078.7528241601635, 545.2847562872191),
                (1130.5817257422875, 510.37733286778285),
                (1181.9228258977564, 463.9075673559904),
                (1225.5731493936205, 410.0396175787416),
                (1258.121473753201, 357.0383914794887),
                (1283.0196715720645, 304.7333152394166),
                (1302.3284780438362, 252.00512715901004),
                (1316.5560196546153, 198.48201099512573),
                (1326.9576677230002, 139.3967559638328),
                (1333.0932271113002, 100.84655663599938),
                (1343.486723417876, -64.80499360522106),
                (1336.0857506855605, -109.3437847848545),
                (1327.3439358210303, -183.2032210908526),
                (1318.0168833021507, -232.47769228107745),
                (1302.8366045299354, -287.56146830105854),
                (1285.5603040025608, -341.50033045928376),
                (1263.7108651002927, -396.8254592659823),
                (1237.2882878231312, -451.74417276722556),
                (1207.308825143275, -505.037036237552),
                (1172.7562240885259, -556.0143836057805),
                (1128.0410933117912, -612.4026336941533),
                (1076.7203182157664, -658.2571906430871),
                (1024.8914166336422, -689.9315329406068),
                (973.0625150515181, -711.7812967192153),
                (799.7913832916718, -721.926761925964),
                (771.8444265562126, -713.390499628048),
                (720.0155249740885, -692.618352547739),
                (668.6744248186197, -662.2813242945683),
                (617.902426327582, -618.1096350415803),
                (575.7076029218998, -565.7680010488721),
                (546.7443932142421, -511.7869024735646),
                (524.9457669605843, -451.3051510254827),
                (516.7486775621876, -393.5263922426077),
                (516.7486775621876, -334.6332113145754),
                (516.7486775621876, -281.637425294638),
                (516.7486775621876, -228.64163927470076),
                (516.7486775621876, -175.64585325476332),
                (516.7486775621876, -107.40944903301386),
            ],
            cut=vac_vessel_inner,  # hollow shape
            rotation_angle=self.rotation_angle,
            stp_filename='vacvessel.stp',
            stl_filename='vacvessel.stl',
            material_tag="vacuum_vessel_mat",
            color=(0., 1., 1.),
        )

        return [divertor, blanket, vac_vessel, vac_vessel_inner]

    def create_plasma(self) -> list:
        """Creates a 3d solids for the plasma.

        Returns:
            A list of CadQuery solids: A list of 3D solid volumes
        """

        plasma = paramak.PlasmaFromPoints(
            outer_equatorial_x_point=1118,
            inner_equatorial_x_point=677,
            high_point=(853, 368),
            configuration="single-null",
            rotation_angle=self.rotation_angle,
            stp_filename='plasma.stp',
        )

        return [plasma]

    def create_pf_coils(self) -> list:
        """Creates a 3d solids for each pf coil.

        Returns:
            A list of CadQuery solids: A list of 3D solid volumes
        """

        outboard_pf_coils = paramak.PoloidalFieldCoilSet(
            center_points=[
                (689, -985),
                (1421, -689),
                (1580, -252),
                (1550, 293),
                (1400, 598),
                (621, 811),
            ],
            widths=[
                803 - 599,
                1492 - 1351,
                1628 - 1526,
                1598 - 1503,
                1439 - 1360,
                684 - 563
            ],
            heights=[
                803 - 599,
                1492 - 1351,
                1628 - 1526,
                1598 - 1503,
                1439 - 1360,
                684 - 563
            ],
            rotation_angle=self.rotation_angle,
            stl_filename='outboard_pf_coils.stl',
            stp_filename='outboard_pf_coils.stp',
            material_tag='outboard_pf_coils_mat',
        )

        pf_coils_1 = paramak.RotateStraightShape(
            points=[
                (263.6088589363423, -881.6221003581469),
                (263.6088589363423, -609.1721122963762),
                (363.04586051526934, -609.1721122963762),
                (363.04586051526934, -881.6221003581469),
            ],
            rotation_angle=self.rotation_angle,
            stl_filename='pf_coils_1.stl',
            stp_filename='pf_coils_1.stp',
            material_tag='pf_coils_mat',
        )

        pf_coils_2 = paramak.RotateStraightShape(
            points=[
                (266.2030353910733, -332.3839488581665),
                (357.77071359802824, -332.3839488581665),
                (357.77071359802824, -600.8478453421652),
                (266.2030353910733, -600.8478453421652),
            ],
            rotation_angle=self.rotation_angle,
            stl_filename='pf_coils_2.stl',
            stp_filename='pf_coils_2.stp',
            material_tag='pf_coils_mat',
        )

        pf_coils_3 = paramak.RotateStraightShape(
            points=[
                (263.5606400431317, 217.1559887549579),
                (360.3263149381907, 217.1559887549579),
                (360.3263149381907, -316.0372010628879),
                (263.5606400431317, -316.0372010628879),
            ],
            rotation_angle=self.rotation_angle,
            stl_filename='pf_coils_3.stl',
            stp_filename='pf_coils_3.stp',
            material_tag='pf_coils_mat',
        )

        pf_coils_4 = paramak.RotateStraightShape(
            points=[
                (262.2297985905187, 493.9315777717868),
                (357.70320714753336, 493.9315777717868),
                (357.70320714753336, 229.49149612970268),
                (262.2297985905187, 229.49149612970268),
            ],
            rotation_angle=self.rotation_angle,
            stl_filename='pf_coils_4.stl',
            stp_filename='pf_coils_4.stp',
            material_tag='pf_coils_mat',
        )

        pf_coils_5 = paramak.RotateStraightShape(
            points=[
                (261.01468248161126, 746.6397242654133),
                (356.35307813763615, 746.6397242654133),
                (356.35307813763615, 510.27832556706545),
                (261.01468248161126, 510.27832556706545),
            ],
            rotation_angle=self.rotation_angle,
            stl_filename='pf_coils_5.stl',
            stp_filename='pf_coils_5.stp',
            material_tag='pf_coils_mat',
        )

        return [outboard_pf_coils, pf_coils_1, pf_coils_2, pf_coils_3,
                pf_coils_4, pf_coils_5]

    def create_solids(self):
        """Creates a 3d solids for each component.

        Returns:
            A list of CadQuery solids: A list of 3D solid volumes
        """

        plasma = self.create_plasma()
        pf_coils = self.create_pf_coils()
        vessel = self.create_vessel_components()
        tf_coil_casing = self.create_tf_coils(vessel[-1], vessel[-2])

        shapes_and_components = plasma + \
            pf_coils + vessel[:-1] + tf_coil_casing
        self.shapes_and_components = shapes_and_components

        return shapes_and_components
