"""
This python script demonstrates the creation of all parametric shapes available
in the paramak tool
"""

import os
import paramak
from make_all_parametric_reactors import main

def export_images():

    all_reactors = main()
    
    for reactor in all_reactors:
        reactor.solid = reactor.solid.rotate(startVector=(0,1,0), endVector=(0,0,1), angleDegrees=180)
        reactor.export_svg(reactor.name+'.svg')

if __name__ == "__main__":
    export_images()



