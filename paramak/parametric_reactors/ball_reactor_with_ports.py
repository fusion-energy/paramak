
import warnings
from typing import Optional

import numpy as np
import paramak
from paramak.utils import perform_port_cutting


class BallReactorWithPorts(paramak.BallReactor):
    """Creates geometry for a simple ball reactor including a plasma,
    cylindrical center column shielding, square toroidal field coils
    and ports. There is no inboard breeder blanket on this ball reactor 
    like most spherical reactors.

    Arguments:
        port_type: type of port to be cut. Defaults to None.
        port_center_point: position of port center point in the workplane 
            given. Defaults to (0, 0).
        port_radius: radius of circular ports. Defaults to None.
        port_height: height of rectangular ports. Defaults to None.
        port_width: width of rectangular ports. Defaults to None.
        port_distance: extrusion distance of port cutter. Defaults to None.
        port_azimuth_placement_angle: azimuthal placement angle of each port. 
            Defaults to None if no ports are created. Defaults to list of 
            equally spaced floats between 0 and 360 of length equal to 
            number_of_ports if number_of_ports is provided but
            port_azimuth_placement_angle is not.
        port_start_radius: extrusion start point of port cutter. Defaults
            to major_radius.
        port_fillet_radius: fillet radius of rectangular ports. Defaults to 0.
    """

    def __init__(
            self,
            port_type: Optional[str] = None,
            port_center_point: Optional[tuple] = (0, 0),
            port_radius: Optional[float] = None,
            port_height: Optional[float] = None,
            port_width: Optional[float] = None,
            port_distance: Optional[float] = None,
            port_azimuth_placement_angle: Optional[list] = None,
            port_start_radius: Optional[float] = None,
            port_fillet_radius: Optional[float] = 0,
            **kwargs
    ):

        super().__init__(**kwargs)

        self.port_type=port_type
        self.port_center_point=port_center_point
        self.port_radius=port_radius
        self.port_height=port_height
        self.port_width=port_width
        self.port_distance=port_distance
        self.port_azimuth_placement_angle=port_azimuth_placement_angle
        self.port_start_radius=port_start_radius
        self.port_fillet_radius=port_fillet_radius

    @property
    def port_start_radius(self):
        return self._port_start_radius

    @port_start_radius.setter
    def port_start_radius(self, value):
        if value is None:
            self._port_start_radius = self.major_radius
        else:
            self._port_start_radius = value
