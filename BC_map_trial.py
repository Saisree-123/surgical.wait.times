
import dash
from dash import  dcc, html, Input, Output
import dash_bootstrap_components as dbc
import altair as alt
import json
import pandas as pd


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

###########################################################################
# map 
map_data = alt.Data(url='data\HA_2018.geojson', format=alt.DataFormat(property='features',type='json'))

def plot_map(authority = 'Interior'):
    if authority == "Provincial":
        plot1 = alt.Chart(map_data).mark_geoshape(stroke = "black", opacity = 0.5, fill = "blue"
        ).encode(
            tooltip = alt.Tooltip(alt.datum['properties']['HA_Name'])
        ).project(
            type='identity', reflectY=True
        )
        return plot1
    else:
        plot2 = alt.Chart(map_data).mark_geoshape(stroke = "black"
        ).encode(
            color= alt.Color(alt.datum['properties']['HA_Name'], legend = None),
            opacity=alt.condition(alt.datum['properties']['HA_Name'] == authority, alt.value(1), alt.value(0.3)),
            tooltip = alt.Tooltip(alt.datum['properties']['HA_Name'])
        ).project(
            type='identity', reflectY=True
        )
        return plot2
    

plot_map_object = html.Div([html.Iframe(
    id = 'map',
    srcDoc=plot_map(authority = 'Interior').to_html(), 
    style={'border-width': '0', 'width': '100%', 'height': '500px'})])

#########################################################################

app.layout= dbc.Container([   
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
            id="health_authority_button",
            options=[
                {"label": "Interior", "value": "interior"},
                {"label": "Fraser", "value": "fraser"},
                {"label": "Vancouver Coastal", "value": "vanCoastal"},
                {"label": "Vancouver Island", "value": "vanIsland"},
                {"label": "Northern", "value": "northern"},
                {"label": "Provincial","value": "provincial"}
            ],
            value='Interior')]),
        plot_map_object
        #dcc.Graph(figure=plot_map(authority = 'Interior'))
    ])
])



if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.4')
