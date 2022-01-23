# Tutorial here: https://towardsdatascience.com/build-a-web-data-dashboard-in-just-minutes-with-python-d722076aee2b
# WIP a/o 1/23/22

import pandas
from os.path import join
import dash
import dash as dcc, html
from dash.dependencies import Input, Output

path_to_data_directory = "/Users/andrew/projects/covid-19-pediatric/combined_data/"

hospitalizations_df = pandas.read_csv(join(path_to_data_directory, "hospitalizations-by-state.csv"))

app = dash.Dash(__name__)
server = app.server

team_names = ["bob", "ryan", "mark"]

app.layout = html.Div([
    html.Div([dcc.Dropdown(id='group-select', options=[{'label': i, 'value': i} for i in team_names],
                           value='TOR', style={'width': '140px'})]),
    dcc.Graph('shot-dist-graph', config={'displayModeBar': False})])


@app.callback(
    Output('shot-dist-graph', 'figure'),
    [Input('group-select', 'value')]
)
def update_graph(grpname):
    import plotly.express as px
    return px.scatter(hospitalizations_df[hospitalizations_df.group == grpname], x='min_mid', y='player',
                      size='shots_freq',
                      color='pl_pps')


if __name__ == '__main__':
    app.run_server(debug=False)
