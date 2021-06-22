
import paramak
import numpy as np


class IterFrom2020PaperDiagram(paramak.Reactor):
    """Creates geometry of a simplified ITER model. The geometry was based on
    "ITER Project: International Cooperation and Energy Investment"
    available at https://link.springer.com/chapter/10.1007/978-3-030-42913-3_26
    Many shapes are built-in paramak shapes therefore the model does not match
    the diagram exactly.

    Arguments:
        rotation_angle: the angle of the sector that is desired.
        number_of_tf_coils: the number of tf coils to include in the model
    """

    def __init__(
        self,
        rotation_angle: float = 360.,
        number_of_tf_coils: int = 18,
    ):

        super().__init__([])

        self.rotation_angle = rotation_angle
        self.number_of_tf_coils = number_of_tf_coils

    def create_tf_coils(self) -> list:
        """Creates a 3d solids for each tf coil.

        Args:


        Returns:
            A list of CadQuery solids: A list of 3D solid volumes
        """

        R1 = 219
        R2 = 1.026e3 + 30
        coil_thickness = R1 - 130

        tf_coil = paramak.ToroidalFieldCoilPrincetonD(
            R1=R1,
            R2=R2,
            thickness=coil_thickness,
            distance=coil_thickness,
            number_of_coils=self.number_of_tf_coils,
            rotation_angle=self.rotation_angle,
            stp_filename="tf_coils.stp",
            stl_filename="tf_coils.stl",
            material_tag='tf_coils_mat',
        )

        return [tf_coil]

    def create_vessel_components(self) -> list:
        """Creates a 3d solids for each vessel component.

        Returns:
            A list of CadQuery solids: A list of 3D solid volumes
        """

        # Blanket computed from plasma
        blanket = paramak.BlanketFP(
            plasma=self.plasma,
            thickness=4.06e2 - 3.52e2,
            start_angle=-70,
            stop_angle=230,
            rotation_angle=self.rotation_angle,
            vertical_displacement=self.plasma.vertical_displacement,
            offset_from_plasma=[[-70, 0, 90, 180, 230], [50, 20, 59, 16, 50]],
            stp_filename="blanket.stp",
            stl_filename="blanket.stl",
            material_tag='blanket_mat',
        )

        # SN Divertor
        divertor = paramak.ITERtypeDivertor(
            anchors=((4.34e2, -3.3e2), (5.56e2, -3.74e2)),
            coverages=(105, 125),
            lengths=(45, 75),
            radii=(68, 65),
            tilts=(-30, 2),
            dome_height=45,
            dome_pos=0.45,
            rotation_angle=self.rotation_angle,
            stp_filename="divertor.stp",
            stl_filename="divertor.stl",
            material_tag='divertor_mat',
        )

        # Vacuum vessel
        divertor.points  # trigger the building of the points for divertor
        # the inner part of the vacuum vessel is computed from the outer
        # points of the blanket and the divertor
        vac_vessel_inner = paramak.RotateMixedShape(
            points=blanket.outer_points + divertor.casing_points,
            rotation_angle=self.rotation_angle,
            stp_filename='vacvesselinner.stp',
            stl_filename='vacvesselinner.stl',
            material_tag="inner_vacuum_vessel_mat",
        )

        vac_vessel = paramak.RotateSplineShape(
            points=[
                (327.77, 36.5026668124882),
                (327.77, 73.37741270075162),
                (327.77, 108.31180820215741),
                (327.77, 143.2462037035632),
                (327.77, 178.18059920496898),
                (327.77, 213.11499470637477),
                (327.77, 248.04939020778068),
                (327.77, 282.98378570918646),
                (327.77, 317.9181812105922),
                (328.6121587814181, 368.23899806938385),
                (336.18303032328333, 422.4306297110355),
                (350.4835654579176, 457.5437492206628),
                (371.95910957013655, 492.47041663587777),
                (404.3208742000702, 522.0151685493631),
                (439.6516080621078, 544.4559826211985),
                (474.98234192414554, 556.3610266211815),
                (510.2245275810152, 564.0927634387052),
                (545.6438096482208, 565.1200145185009),
                (565.832800426528, 563.1864687746993),

                (580.9745435102584, 559.4390362932862),
                (616.3052773722961, 548.4109567158157),
                (651.6360112343338, 533.224020531035),
                (686.9667450963714, 515.3041214328789),
                (722.297478958409, 492.23516177329117),
                (757.6282128204466, 466.8689289401416),
                (792.9589466824843, 437.10619055069265),
                (825.7660566972336, 403.7167485984509),
                (853.525919017406, 369.42176700251196),
                (877.9209495411939, 333.90960594986575),
                (898.9511482685972, 300.5186330502012),
                (916.616515199616, 265.2383422522439),
                (932.5994662324425, 230.72194441870647),
                (946.0587934179808, 193.1122328856627),
                (956.1532888071343, 156.87835598377137),
                (962.8829523999035, 118.10702768634405),
                (967.9302000944803, 80.39197257542594),
                (968.7714080435763, 38.24754419835381),

                (968.7714080435763, 25.77097437642317),
                (964.5653682980957, -1.670738783514139),
                (956.9944967562304, -29.93883090626548),
                (956.1532888071343, -34.59540221679083),
                (946.0587934179808, -71.15339839027786),
                (931.7582582833464, -104.25874435511184),
                (914.9340993014238, -139.91477225259314),
                (898.9511482685972, -174.48160361826422),
                (883.8094051848669, -213.64300914878197),
                (867.8264541520404, -248.21908241802464),
                (851.0022951701176, -284.2078188440911),
                (834.1781361881949, -319.9470238737184),
                (818.1951851553683, -359.0978394110024),
                (800.5298182243495, -391.2313539579658),
                (776.1347877005617, -427.87174371008393),
                (744.1688856349085, -460.45530873911446),
                (708.8381517728709, -490.0255912806248),
                (673.5074179108332, -512.7040543014494),
                (638.1766840487956, -528.371873327094),
                (602.8459501867579, -539.0490644239661),
                (567.5152163247203, -546.1219131278361),
                (532.1844824626827, -548.9566889080664),
                (496.85374860064496, -547.7514325554811),
                (461.52301473860734, -541.3971156414638),
                (426.1922808765697, -527.596464992453),
                (390.8615470145321, -501.2796363633471),
                (360.57806084707124, -468.0473902249954),
                (340.389070068764, -431.4355817359209),
                (329.87397070506233, -399.072068113844),
                (327.770950832322, -357.4796824533661),
                (327.770950832322, -311.73270913617455),
                (327.770950832322, -276.79831363476876),
                (327.770950832322, -241.86391813336297),
                (327.770950832322, -206.92952263195718),
                (327.770950832322, -171.99512713055117),
                (327.770950832322, -137.06073162914538),
                (327.770950832322, -102.12633612773948),
                (327.770950832322, -67.19194062633369),

            ],
            cut=[vac_vessel_inner],  # to make a hollow shape
            rotation_angle=self.rotation_angle,
            stp_filename='vacvessel.stp',
            stl_filename='vacvessel.stl',
            material_tag="vacuum_vessel_mat",
        )

        return [divertor, blanket, vac_vessel, vac_vessel_inner]

    def create_plasma(self) -> list:
        """Creates a 3d solids for the plasma.

        Returns:
            A list of CadQuery solids: A list of 3D solid volumes
        """

        self.plasma = paramak.Plasma(
            major_radius=6.2e2,
            minor_radius=2e2,
            elongation=1.7,
            triangularity=0.33,
            vertical_displacement=5.7e1,
            configuration="single-null",
            rotation_angle=self.rotation_angle,
        )

        return [self.plasma]

    def create_pf_coils(self) -> list:
        """Creates a 3d solids for each pf coil.

        Returns:
            A list of CadQuery solids: A list of 3D solid volumes
        """

        # from diagram
        bot_lefts = np.array([
            (345.5429497568881, -788.0537547271744),
            (800.6482982171799, -703.3664235548353),
            (1160.9400324149108, -272.69381415451096),
            (1158.833063209076, 268.97622906537015),
            (798.5413290113453, 621.6369529983793),
            (345.5429497568881, 707.7795786061589),
        ])

        top_rights = np.array([
            (511.99351701782825, -690.4038357644516),
            (880.7131280388979, -611.8280659103187),
            (1222.0421393841166, -162.37506753106413),
            (1230.4700162074555, 379.2780929227446),
            (861.7504051863858, 681.9523230686117),
            (446.677471636953, 803.4508373851974),
        ])

        outboard_pf_coils = paramak.PoloidalFieldCoilSet(
            center_points=((bot_lefts + top_rights) / 2).tolist(),
            widths=(top_rights[:, 0] - bot_lefts[:, 0]).tolist(),
            heights=(top_rights[:, 1] - bot_lefts[:, 1]).tolist(),
            rotation_angle=self.rotation_angle,
            stl_filename='outboard_pf_coils.stl',
            stp_filename='outboard_pf_coils.stp',
            material_tag='outboard_pf_coils_mat',
        )

        x_inner, x_outer = 132.73905996758506, 202.26904376012968

        pf_coils_1 = paramak.RotateStraightShape(
            points=[
                (x_inner, -600),
                (x_outer, -600),
                (x_outer, -400),
                (x_inner, -400),
            ],
            rotation_angle=self.rotation_angle,
            stl_filename='pf_coils_1.stl',
            stp_filename='pf_coils_1.stp',
            material_tag='pf_coil_mat',
        )

        pf_coils_2 = paramak.RotateStraightShape(
            points=[
                (x_inner, -400),
                (x_outer, -400),
                (x_outer, -200),
                (x_inner, -200),
            ],
            rotation_angle=self.rotation_angle,
            stl_filename='pf_coils_2.stl',
            stp_filename='pf_coils_2.stp',
            material_tag='pf_coil_mat',
        )

        pf_coils_3 = paramak.RotateStraightShape(
            points=[
                (x_inner, -200),
                (x_outer, -200),
                (x_outer, 0),
                (x_inner, 0),
            ],
            rotation_angle=self.rotation_angle,
            stl_filename='pf_coils_3.stl',
            stp_filename='pf_coils_3.stp',
            material_tag='pf_coil_mat',
        )

        pf_coils_4 = paramak.RotateStraightShape(
            points=[
                (x_inner, 0),
                (x_outer, 0),
                (x_outer, 200),
                (x_inner, 200),
            ],
            rotation_angle=self.rotation_angle,
            stl_filename='pf_coils_4.stl',
            stp_filename='pf_coils_4.stp',
            material_tag='pf_coil_mat',
        )

        pf_coils_5 = paramak.RotateStraightShape(
            points=[
                (x_inner, 200),
                (x_outer, 200),
                (x_outer, 400),
                (x_inner, 400),
            ],
            rotation_angle=self.rotation_angle,
            stl_filename='pf_coils_5.stl',
            stp_filename='pf_coils_5.stp',
            material_tag='pf_coil_mat',
        )

        pf_coils_6 = paramak.RotateStraightShape(
            points=[
                (x_inner, 400),
                (x_outer, 400),
                (x_outer, 600),
                (x_inner, 600),
            ],
            rotation_angle=self.rotation_angle,
            stl_filename='pf_coils_6.stl',
            stp_filename='pf_coils_6.stp',
            material_tag='pf_coil_mat',
        )

        return [outboard_pf_coils, pf_coils_1, pf_coils_2, pf_coils_3,
                pf_coils_4, pf_coils_5, pf_coils_6]

    def create_solids(self):
        """Creates a 3d solids for each component.

        Returns:
            A list of CadQuery solids: A list of 3D solid volumes
        """

        plasma = self.create_plasma()
        pf_coils = self.create_pf_coils()
        tf_coil = self.create_tf_coils()
        vessel = self.create_vessel_components()

        shapes_and_components = plasma + \
            pf_coils + vessel[:-1] + tf_coil
        self.shapes_and_components = shapes_and_components

        return shapes_and_components
