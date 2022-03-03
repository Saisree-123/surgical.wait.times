
import dash
from dash import  dcc, html, Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout=app.layout = dbc.Container([   
    html.Div([
    html.H1('SURGICAL WAIT TIMES',style={'color':'blue'}),
    html.Div([
        dcc.RangeSlider(
            id="year",min=2009, max=2022,
            step=1, marks={i: f'{i}' for i in range(2009, 2023)},
            value=[2017, 2022])        
        ]),        
    html.Div([
        dcc.RadioItems(
            id="health_authority",
            options=["Interior","Fraser","Vancouver Coastal","Vancouver Island","Northern","Provincial"],
            value='Interior')]),
        ])
])

if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.4')
