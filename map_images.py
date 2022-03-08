
import dash
from dash import  dcc, html, Input, Output
import dash_bootstrap_components as dbc
import altair as alt
import pandas as pd
from io import BytesIO
import base64
from PIL import Image


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


###########################################################################
# map plot stuff 

def map_image_plot(authority = 'interior'):
    if authority == "interior":
        img = Image.open('data/images/interior.png')
    elif authority == "fraser":
        img = Image.open('data/images/fraser.png')
    elif authority == "vanCoastal":
        img = Image.open('data/images/vancoastal.png')
    elif authority == "vanIsland":
        img = Image.open('data/images/vanisland.png')
    elif authority == "northern":
        img = Image.open('data/images/northern.png')
    elif authority == "provincial":
        img = Image.open('data/images/provincial.png')

    def image_formatter2(im):
        with BytesIO() as buffer:
            im.save(buffer, 'png')
            data = base64.encodebytes(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{data}"

    source = pd.DataFrame([
        {"x": 0, "y": 0, "img": image_formatter2(img)}
    ])

    plot_img = alt.Chart(source).mark_image(
        width=400,
        height=400
    ).encode(
        x=alt.X('x', axis=None),
        y=alt.Y('y', axis=None),
        url='img'
    ).configure_axis(
        grid=False
    ).configure_view(
        strokeWidth=0
    )
    return plot_img.to_html()

plot_map_object = html.Div([html.Iframe(
    id = 'map',
    srcDoc=map_image_plot(authority = 'interior'), 
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
            value='interior')]),
        plot_map_object    # map plot object
    ])
])



#############################################
# call back for map plot
@app.callback(
    Output('map', 'srcDoc'),
    Input('health_authority_button', 'value'))
def update_map_image_plot(health_authority_button):
    return map_image_plot(health_authority_button)


if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.4')
