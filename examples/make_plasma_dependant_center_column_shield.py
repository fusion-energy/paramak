
__doc__ = "This python script demonstrates the creation of a center column shield using plasma parameters"

from paramak.parametric_shapes import CenterColumnShieldPlasmaHyperbola

# Default shield parameters

# height = None
# inner_radius = None
# mid_offset = None
# edge_offset = None


# Default plasma parameters

# major_radius = 450
# minor_radius = 150
# triangularity = 0.55
# elongation = 2.0

# these parameters can also be specified as part of the CenterColumnShieldPlasmaHyperbola class


# using default plasma parameters

test_shape_1 = CenterColumnShieldPlasmaHyperbola(
    inner_radius=150, height=800, mid_offset=10, edge_offset=15
)
test_shape_1.export_stp("test_shape_1.stp")


# specifying plasma parameters

test_shape_2 = CenterColumnShieldPlasmaHyperbola(
    # plasma parameters
    major_radius=600,
    minor_radius=200,
    triangularity=0.7,
    elongation=1.5,
    # shield parameters
    inner_radius=50,
    height=1000,
    mid_offset=30,
    edge_offset=10,
)
test_shape_2.export_stp("test_shape_2.stp")
