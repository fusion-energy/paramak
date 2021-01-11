
import openmc
import paramak
import plotly.graph_objects as go

my_shape = paramak.CenterColumnShieldHyperbola(
    height=500,
    inner_radius=50,
    mid_radius=60,
    outer_radius=100,
    material_tag='center_column_shield_mat'
)

# makes the openmc neutron source at x,y,z 0, 0, 0 with isotropic directions
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.energy = openmc.stats.Discrete([14e6], [1])
source.angle = openmc.stats.Isotropic()


# converts the geometry into a neutronics geometry
my_model = paramak.NeutronicsModel(
    geometry=my_shape,
    source=source,
    materials={'center_column_shield_mat': 'Be'},
    cell_tallies=['heating', 'flux', 'TBR', 'spectra'],
    simulation_batches=10,
    simulation_particles_per_batch=200
)

# performs an openmc simulation on the model
output_filename = my_model.simulate(method='pymoab')

# this extracts the values from the results dictionary
energy_bins = my_model.results['center_column_shield_mat_photon_spectra']['Flux per source particle']['energy']
neutron_spectra = my_model.results['center_column_shield_mat_neutron_spectra']['Flux per source particle']['result']
photon_spectra = my_model.results['center_column_shield_mat_photon_spectra']['Flux per source particle']['result']

fig = go.Figure()

# this sets the axis titles and range
fig.update_layout(
    xaxis={'title': 'Energy (eV)',
           'range': (0, 14.1e6)},
    yaxis={'title': 'Neutrons per cm2 per source neutron'}
)

# this adds the neutron spectra line to the plot
fig.add_trace(go.Scatter(
    x=energy_bins[:-85],  # trims off the high energy range
    y=neutron_spectra[:-85],  # trims off the high energy range
    name='neutron spectra',
    line=dict(shape='hv')
)
)

# this adds the photon spectra line to the plot
fig.add_trace(go.Scatter(
    x=energy_bins[:-85],  # trims off the high energy range
    y=photon_spectra[:-85],  # trims off the high energy range
    name='photon spectra',
    line=dict(shape='hv')
)
)

# this adds the drop down menu fo log and linear scales
fig.update_layout(
    updatemenus=[
        go.layout.Updatemenu(
            buttons=list([
                dict(
                    args=[{
                        "xaxis.type": 'lin', "yaxis.type": 'lin',
                        'xaxis.range': (0, 14.1e6)
                    }],
                    label="linear(x) , linear(y)",
                    method="relayout"
                ),
                dict(
                    args=[{"xaxis.type": 'log', "yaxis.type": 'log'}],
                    label="log(x) , log(y)",
                    method="relayout"
                ),
                dict(
                    args=[{"xaxis.type": 'log', "yaxis.type": 'lin'}],
                    label="log(x) , linear(y)",
                    method="relayout"
                ),
                dict(
                    args=[{"xaxis.type": 'lin', "yaxis.type": 'log',
                           'xaxis.range': (0, 14.1e6)
                           }],
                    label="linear(x) , log(y)",
                    method="relayout"
                )
            ]),
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.5,
            xanchor="left",
            y=1.1,
            yanchor="top"
        ),
    ]
)

fig.show()
