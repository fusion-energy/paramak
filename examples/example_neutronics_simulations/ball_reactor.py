import matplotlib.pyplot as plt
import paramak
import numpy as np
import neutronics_material_maker as nmm
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.interpolate import griddata
from scipy.interpolate import Rbf
from tqdm import tqdm

import os
os.environ["OPENMC_CROSS_SECTIONS"] = "/home/jshim/data/cross_sections.xml"
my_reactor = paramak.BallReactor(
    inner_bore_radial_thickness=1,
    inboard_tf_leg_radial_thickness=30,
    center_column_shield_radial_thickness=60,
    divertor_radial_thickness=50,
    inner_plasma_gap_radial_thickness=30,
    plasma_radial_thickness=300,
    outer_plasma_gap_radial_thickness=30,
    firstwall_radial_thickness=3,
    blanket_radial_thickness=100,
    blanket_rear_wall_radial_thickness=3,
    elongation=2.75,
    triangularity=0.5,
    number_of_tf_coils=16,
    rotation_angle=360,
)

df = pd.DataFrame()

for strucutral_material in ['SiC', 'eurofer']:
    for enrichment in np.linspace(0, 100, 3):
        for structural_fraction in np.linspace(0, 1, 3):

            blanket_material = nmm.MultiMaterial(
                materials=[
                    nmm.Material('Pb842Li158', temperature_in_K=500),
                    nmm.Material(strucutral_material)
                ],
                fracs=[1 - structural_fraction, structural_fraction]


                neutronics_model=paramak.NeutronicsModelFromReactor(
                    reactor=my_reactor,
                    materials={
                        'inboard_tf_coils_mat': 'eurofer',
                        'center_column_shield_mat': 'eurofer',
                        'divertor_mat': 'eurofer',
                        'firstwall_mat': 'eurofer',
                        'blanket_mat': blanket_material,
                        'blanket_rear_wall_mat': 'eurofer'},
                    outputs=['TBR'],
                    simulation_batches=5,
                    simulation_particles_per_batches=1e4,
                )
                neutronics_model.create_materials()
                neutronics_model.mats

                neutronics_model.simulate()

                df.append({
                    'tbr': neutronics_model.results['TBR']['result'],
                    'enrichemt': enrichment},
                    'strucutral_material': strucutral_material,
                    'structural_fraction': structural_fraction},
            )

fig = make_subplots(rows=2, cols=2, subplot_titles=(sampling_methods))

material_df = df['strucutral_material'] == 'SiC'

x = list(material_df['enrichment'])
y = list(material_df['structural_fraction'])
z = list(material_df['tbr'])

xi = np.linspace(0, 100, 100)
yi = np.linspace(0, 100, 100)
XI, YI = np.meshgrid(xi, yi)
rbf = Rbf(x, y, z, epsilon=2)
zi = rbf(XI, YI)

# contour plot showing interpoloated TBR values
fig.add_trace(
    go.Contour(
        z=zi,
        x=xi,
        y=yi,
        colorscale="Viridis",
        opacity=0.9,
        line=dict(width=1, smoothing=0.85),
        contours=dict(
            showlines=False,
            showlabels=False,
            coloring="heatmap",
            start=min(z),
            end=max(z),
            size=0.,
            labelfont=dict(size=15,),
        ),
    ),
    row=coords[0],
    col=coords[1]
)

# scatter plot showing simulation coordinates
fig.add_trace(
    go.Scatter(
        x=x,
        y=y,
        mode="markers",
        name=sample,
        # hovertext=[xval +'<br>' + yval + '<br>' + zval for xval, yval, zval in zip(x, y ,z)],
        hoverinfo="text",
        showlegend=False,
        marker={"color": "red", "size": 8},
    ),
    row=coords[0],
    col=coords[1],
)

fig.update_xaxes(title_text="Li6 enrichment percent")
fig.update_yaxes(title_text="Structural fraction in breeder zone")

fig.show()

fig.write_html("TBR_results.html")
