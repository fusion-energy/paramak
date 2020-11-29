
import unittest

import numpy as np
import paramak


class TestInboardFirstwallFCCS(unittest.TestCase):

    def test_construction_with_CenterColumnShieldCylinder(self):
        """Makes a firstwall from a CenterColumnShieldCylinder and checks
        the volume is smaller than the shield."""

        a = paramak.CenterColumnShieldCylinder(
            height=100,
            inner_radius=20,
            outer_radius=80)
        b = paramak.InboardFirstwallFCCS(
            central_column_shield=a,
            thickness=20,
            rotation_angle=180)
        assert a.solid is not None
        assert b.solid is not None
        assert a.volume > b.volume

    def test_construction_with_CenterColumnShieldHyperbola(self):
        """Makes a firstwall from a CenterColumnShieldHyperbola and checks
        the volume is smaller than the shield."""

        a = paramak.CenterColumnShieldHyperbola(
            height=200,
            inner_radius=20,
            mid_radius=80,
            outer_radius=120)
        b = paramak.InboardFirstwallFCCS(
            central_column_shield=a,
            thickness=20,
            rotation_angle=180)
        assert a.solid is not None
        assert b.solid is not None
        assert a.volume > b.volume

    def test_construction_with_CenterColumnShieldFlatTopHyperbola(self):
        """Makes a firstwall from a CenterColumnShieldFlatTopHyperbola and
        checks the volume is smaller than the shield."""

        a = paramak.CenterColumnShieldFlatTopHyperbola(
            height=200,
            arc_height=100,
            inner_radius=50,
            mid_radius=80,
            outer_radius=100)
        b = paramak.InboardFirstwallFCCS(
            central_column_shield=a,
            thickness=20,
            rotation_angle=180)
        assert a.solid is not None
        assert b.solid is not None
        assert a.volume > b.volume

    def test_construction_with_CenterColumnShieldPlasmaHyperbola(self):
        """Makes a firstwall from a CenterColumnShieldPlasmaHyperbola and
        checks the volume is smaller than the shield."""

        a = paramak.CenterColumnShieldPlasmaHyperbola(
            height=601,
            inner_radius=20,
            mid_offset=50,
            edge_offset=0)
        b = paramak.InboardFirstwallFCCS(
            central_column_shield=a,
            thickness=20,
            rotation_angle=180)
        assert a.solid is not None
        assert b.solid is not None
        assert a.volume > b.volume

    def test_construction_with_CenterColumnShieldCircular(self):
        """Makes a firstwall from a CenterColumnShieldCircular and checks
        the volume is smaller than the shield."""

        a = paramak.CenterColumnShieldCircular(
            height=300,
            inner_radius=20,
            mid_radius=50,
            outer_radius=100)
        b = paramak.InboardFirstwallFCCS(
            central_column_shield=a,
            thickness=20,
            rotation_angle=180)
        assert a.solid is not None
        assert b.solid is not None
        assert a.volume > b.volume

    def test_construction_with_CenterColumnShieldFlatTopCircular(self):
        """Makes a firstwall from a CenterColumnShieldFlatTopCircular and
        checks the volume is smaller than the shield."""

        a = paramak.CenterColumnShieldFlatTopCircular(
            height=500,
            arc_height=300,
            inner_radius=30,
            mid_radius=70,
            outer_radius=120)
        b = paramak.InboardFirstwallFCCS(
            central_column_shield=a,
            thickness=20,
            rotation_angle=180)
        assert a.solid is not None
        assert b.solid is not None
        assert a.volume > b.volume

    def test_construction_with_wrong_column_shield_type(self):
        def test_construction_with_string():
            """Only CenterColumnShields are acceptable inputs for inputs, this
            should fail as it trys to use a string."""

            b = paramak.InboardFirstwallFCCS(
                central_column_shield="incorrect type",
                thickness=20,
                rotation_angle=180)
            b.solid

        self.assertRaises(
            ValueError,
            test_construction_with_string)

    def test_boolean_union(self):
        """Makes two halves of a 360 firstwall and performs a union and checks
        that the volume corresponds to 2 times the volume of 1 half."""

        a = paramak.CenterColumnShieldFlatTopCircular(
            height=500,
            arc_height=300,
            inner_radius=30,
            mid_radius=70,
            outer_radius=120)
        b = paramak.InboardFirstwallFCCS(
            central_column_shield=a,
            thickness=20,
            rotation_angle=180,
            azimuth_placement_angle=0)

        c = paramak.InboardFirstwallFCCS(
            central_column_shield=a,
            thickness=20,
            rotation_angle=180,
            azimuth_placement_angle=180,
            union=b)
        assert np.isclose(c.volume, 2 * b.volume)

    def test_azimuth_placement_angle(self):
        """Makes two 180 degree firstwalls (one is rotated 90 degree), performs
        a cut and checks that the volume corresponds to 0.5 times the volume of
        1 half."""

        a = paramak.CenterColumnShieldFlatTopCircular(
            height=500,
            arc_height=300,
            inner_radius=30,
            mid_radius=70,
            outer_radius=120)
        b = paramak.InboardFirstwallFCCS(
            central_column_shield=a,
            thickness=20,
            rotation_angle=180,
            azimuth_placement_angle=0)

        c = paramak.InboardFirstwallFCCS(
            central_column_shield=a,
            thickness=20,
            rotation_angle=180,
            azimuth_placement_angle=90,
            cut=b)
        assert np.isclose(c.volume, 0.5 * b.volume)

    def test_cut_attribute(self):
        """Creates a firstwall then resets its cut attribute and checks that
        the shape is not affected."""

        a = paramak.CenterColumnShieldCylinder(
            height=100,
            inner_radius=20,
            outer_radius=80)
        b = paramak.InboardFirstwallFCCS(
            central_column_shield=a,
            thickness=20,
            rotation_angle=180)

        volume_1 = b.volume
        b.cut = None
        volume_2 = b.volume
        assert np.isclose(volume_1, volume_2)
