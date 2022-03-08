import pandas as pd
import numpy as np

import altair as alt

import dash
from dash import  dcc, html, Input, Output
import dash_bootstrap_components as dbc

path = '2009_2021-quarterly-surgical_wait_times.xlsx'
qdata = pd.read_excel(path)
newdata = pd.read_excel('2021_2022-quarterly-surgical_wait_times-q3-interim.xlsx')
qdata = pd.concat([qdata, newdata])

qdata.columns = qdata.columns.str.lower()
qdata.rename(columns = {'fiscal_year': 'year',
                        'hospital_name': 'hospital',
                        'procedure_group': 'procedure',
                        'completed_50th_percentile': 'wait_time_50',
                        'completed_90th_percentile': 'wait_time_90'}, inplace = True)

qdata['year'] = qdata['year'].str.replace('(/).*', "")
qdata['year'] = pd.to_numeric(qdata['year'])


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout=app.layout = dbc.Container([   
    html.Div([
    html.H1('SURGICAL WAIT TIMES',style={'color':'blue'}),
    html.Div([
        dcc.RangeSlider(
            id="year_slider",min=2009, max=2022,
            step=1, marks={i: f'{i}' for i in range(2009, 2023)},
            value=[2017, 2022])        
        ]),        
    html.Div([
        dcc.RadioItems(
            id="health_authority_buttons",
            options=["Interior","Fraser","Vancouver Coastal","Vancouver Island","Northern","Provincial"],
            value='Interior')
        ]),
    html.Div([
        dcc.RadioItems(
            id="fastest_slowest_treatments_buttons",
            options=["Fastest","Slowest"],
            value='Fastest')
        ]),
    html.Div([
            html.Label("hosp:", style={'fontSize': 30, 'textAlign': 'center'}),
            dcc.Dropdown(
                id='hosp_dropdown',
                options=[],
                value=[],
                clearable=False
            )
        ])    
    ])    
])
@app.callback(
        Output('hosp_dropdown', 'options'),
        Output('hosp_dropdown', 'value'),
        Input('health_authority_buttons', 'value'),
    )
def set_county_options(health_athority):
    if(health_athority=="Provincial"):
        health_athority="Provincial Health Services Authority"
    dff =qdata[qdata.health_authority==health_athority]
    print(dff.columns)
    counties_of_state = [{'label': c, 'value': c} for c in sorted(dff.hospital.unique())]
    values_selected = [counties_of_state[0]]
    print(counties_of_state)
    print(values_selected[0]['label'])
    return counties_of_state, values_selected[0]['label']

if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.4')