"""
This python script creates all parametric reactors available and saves stp files
"""

from ball_reactor import make_ball_reactor
from ball_reactor_single_null import make_ball_reactor_sn
from center_column_study_reactor import make_center_column_study_reactor
from segmented_blanket_ball_reactor import make_ball_reactor_seg
from submersion_reactor import make_submersion
from submersion_reactor_single_null import make_submersion_sn


def main(outputs=['stp', 'svg', 'html']):

    make_submersion(outputs=outputs)
    make_submersion_sn(outputs=outputs)
    make_center_column_study_reactor(outputs=outputs)
    make_ball_reactor(outputs=outputs)
    make_ball_reactor_sn(outputs=outputs)
    make_ball_reactor_seg(outputs=outputs)


if __name__ == "__main__":
    main()
