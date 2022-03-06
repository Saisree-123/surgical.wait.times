
import dash
from dash import  dcc, html, Input, Output
import dash_bootstrap_components as dbc
import altair as alt
import json
import pandas as pd


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

###########################################################################
# map 

map_data = alt.Data(url='HA_2018.geojson', format=alt.DataFormat(property='features',type='json'))
plot1 = alt.Chart(map_data).mark_geoshape(stroke = "black", opacity = 0.5, fill = "blue"
    ).encode(
        tooltip = alt.Tooltip(alt.datum['properties']['HA_Name'])
    ).project(
        type='identity', reflectY=True
    )
 
#########################################################################

app.layout= html.Div(html.Iframe(
                id = 'map',
                srcDoc=plot1.to_html(), 
                style={'border-width': '0', 'width': '100%', 'height': '500px'})
            )


if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.4')
