try:
    # this works for python 3.7 and lower
    from importlib.metadata import version, PackageNotFoundError
except (ModuleNotFoundError, ImportError):
    # this works for python 3.8 and higher
    from importlib_metadata import version, PackageNotFoundError
try:
    __version__ = version("paramak")
except PackageNotFoundError:
    from setuptools_scm import get_version

    __version__ = get_version(root="..", relative_to=__file__)

__all__ = ["__version__"]


from .shape import Shape
from .reactor import Reactor
from .utils import (
    rotate,
    extend,
    distance_between_two_points,
    diff_between_angles,
    find_center_point_of_circle,
    angle_between_two_points_on_circle,
    find_radius_of_circle,
    export_solids_to_brep,
    export_solids_to_dagmc_h5m,
    get_center_of_bounding_box,
)
from .utils import EdgeLengthSelector, FaceAreaSelector

from .parametric_shapes.extruded_mixed_shape import ExtrudeMixedShape
from .parametric_shapes.extruded_spline_shape import ExtrudeSplineShape
from .parametric_shapes.extruded_straight_shape import ExtrudeStraightShape
from .parametric_shapes.extruded_circle_shape import ExtrudeCircleShape

from .parametric_shapes.rotate_mixed_shape import RotateMixedShape
from .parametric_shapes.rotate_spline_shape import RotateSplineShape
from .parametric_shapes.rotate_straight_shape import RotateStraightShape
from .parametric_shapes.rotate_circle_shape import RotateCircleShape

from .parametric_shapes.sweep_mixed_shape import SweepMixedShape
from .parametric_shapes.sweep_spline_shape import SweepSplineShape
from .parametric_shapes.sweep_straight_shape import SweepStraightShape
from .parametric_shapes.sweep_circle_shape import SweepCircleShape

from .parametric_components.circular_port import CircularPort
from .parametric_components.hexagon_pin import HexagonPin

from .parametric_components.tokamak_plasma import Plasma
from .parametric_components.tokamak_plasma_from_points import PlasmaFromPoints
from .parametric_components.tokamak_plasma_plasmaboundaries import PlasmaBoundaries

from .parametric_components.blanket_constant_thickness_arc_h import (
    BlanketConstantThicknessArcH,
)
from .parametric_components.blanket_constant_thickness_arc_v import (
    BlanketConstantThicknessArcV,
)
from .parametric_components.blanket_fp import BlanketFP
from .parametric_components.blanket_poloidal_segment import BlanketFPPoloidalSegments

from .parametric_components.divertor_ITER import ITERtypeDivertor
from .parametric_components.divertor_ITER_no_dome import ITERtypeDivertorNoDome

from .parametric_components.center_column_cylinder import CenterColumnShieldCylinder
from .parametric_components.center_column_hyperbola import CenterColumnShieldHyperbola
from .parametric_components.center_column_flat_top_hyperbola import (
    CenterColumnShieldFlatTopHyperbola,
)
from .parametric_components.center_column_plasma_dependant import (
    CenterColumnShieldPlasmaHyperbola,
)
from .parametric_components.center_column_circular import CenterColumnShieldCircular
from .parametric_components.center_column_flat_top_circular import (
    CenterColumnShieldFlatTopCircular,
)

from .parametric_components.coolant_channel_ring_straight import (
    CoolantChannelRingStraight,
)
from .parametric_components.coolant_channel_ring_curved import CoolantChannelRingCurved

from .parametric_components.inboard_firstwall_fccs import InboardFirstwallFCCS

from .parametric_components.poloidal_field_coil import PoloidalFieldCoil
from .parametric_components.poloidal_field_coil_fp import PoloidalFieldCoilFP
from .parametric_components.poloidal_field_coil_case import PoloidalFieldCoilCase
from .parametric_components.poloidal_field_coil_case_fc import PoloidalFieldCoilCaseFC
from .parametric_components.poloidal_field_coil_set import PoloidalFieldCoilSet
from .parametric_components.poloidal_field_coil_case_set import PoloidalFieldCoilCaseSet
from .parametric_components.poloidal_field_coil_case_set_fc import (
    PoloidalFieldCoilCaseSetFC,
)
from .parametric_components.extrude_rectangle import ExtrudeRectangle
from .parametric_components.extrude_hollow_rectangle import ExtrudeHollowRectangle

from .parametric_components.poloidal_segmenter import PoloidalSegments
from .parametric_components.port_cutters_rotated import PortCutterRotated
from .parametric_components.port_cutters_rectangular import PortCutterRectangular
from .parametric_components.port_cutters_circular import PortCutterCircular
from .parametric_components.rotated_trapezoid import RotatedTrapezoid
from .parametric_components.rotated_isosceles_triangle import RotatedIsoscelesTriangle
from .parametric_components.cutting_wedge import CuttingWedge
from .parametric_components.cutting_wedge_fs import CuttingWedgeFS
from .parametric_components.blanket_cutter_parallels import BlanketCutterParallels
from .parametric_components.blanket_cutters_star import BlanketCutterStar

from .parametric_components.inner_tf_coils_circular import InnerTfCoilsCircular
from .parametric_components.inner_tf_coils_flat import InnerTfCoilsFlat

from .parametric_components.toroidal_field_coil_coat_hanger import (
    ToroidalFieldCoilCoatHanger,
)
from .parametric_components.toroidal_field_coil_rectangle import (
    ToroidalFieldCoilRectangle,
)
from .parametric_components.toroidal_field_coil_triple_arc import (
    ToroidalFieldCoilTripleArc,
)
from .parametric_components.toroidal_field_coil_princeton_d import (
    ToroidalFieldCoilPrincetonD,
)
from .parametric_components.tf_coil_casing import TFCoilCasing
from .parametric_components.toroidal_field_coil_round_corners import (
    ToroidalFieldCoilRectangleRoundCorners,
)

from .parametric_components.constant_thickness_dome import ConstantThicknessDome
from .parametric_components.vacuum_vessel import VacuumVessel

from .parametric_components.dished_vacuum_vessel import DishedVacuumVessel
from .parametric_components.vacuum_vessel_inner_leg import VacuumVesselInnerLeg
from .parametric_components.capsule_vacuum_vessel import CapsuleVacuumVessel
from .parametric_components.hollow_cube import HollowCube
from .parametric_components.shell_fs import ShellFS

from .parametric_reactors.eu_demo_2015_reactor import EuDemoFrom2015PaperDiagram
from .parametric_reactors.ball_reactor import BallReactor
from .parametric_reactors.submersion_reactor import SubmersionTokamak
from .parametric_reactors.single_null_submersion_reactor import (
    SingleNullSubmersionTokamak,
)
from .parametric_reactors.single_null_ball_reactor import SingleNullBallReactor
from .parametric_reactors.segmented_blanket_ball_reactor import (
    SegmentedBlanketBallReactor,
)
from .parametric_reactors.center_column_study_reactor import CenterColumnStudyReactor
from .parametric_reactors.sparc_paper_2020 import SparcFrom2020PaperDiagram
from .parametric_reactors.iter_paper_2020 import IterFrom2020PaperDiagram
from .parametric_reactors.flf_system_code_reactor import FlfSystemCodeReactor
from .parametric_reactors.negative_triangularity_reactor import (
    NegativeTriangularityReactor,
)
