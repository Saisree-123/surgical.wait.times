import pandas as pd
import numpy as np
from io import BytesIO
import altair as alt

import dash
from dash import  dcc, html, Input, Output
import dash_bootstrap_components as dbc

import base64
from PIL import Image

class SurgicalPlots:
    def __init__(self):
        
        # read in data        
        path = '2009_2021-quarterly-surgical_wait_times.xlsx'
        qdata = pd.read_excel(path)
        newdata = pd.read_excel('2021_2022-quarterly-surgical_wait_times-q3-interim.xlsx')
        qdata = pd.concat([qdata, newdata])
        qdata.columns = qdata.columns.str.lower()

        # Rename columns
        qdata.rename(columns = {'fiscal_year': 'year',
                                'hospital_name': 'hospital',
                                'procedure_group': 'procedure',
                                'completed_50th_percentile': 'wait_time_50',
                                'completed_90th_percentile': 'wait_time_90'}, inplace = True)
        
        # Format year column
        qdata['year'] = qdata['year'].str.replace('(/).*', "")
        qdata['year'] = pd.to_numeric(qdata['year'])

        # convert <5 string to median value of 3
        qdata = qdata.replace('<5', 3)
        self.qdata = qdata
        # drop rows with NAs
        clean = qdata.dropna()
        count = qdata.iloc[:,0:7]

        # drop "All" data
        main = clean.query('procedure != "All Procedures" & hospital != "All Facilities" & health_authority != "All Health Authorities"')
        count = count.query('procedure != "All Procedures" & hospital != "All Facilities" & health_authority != "All Health Authorities"')
        self.count = count
        all = clean.query('procedure == "All Procedures" & hospital == "All Facilities" & health_authority == "All Health Authorities"')

        authority = count.groupby(['health_authority', 'year', 'quarter']).sum().reset_index()

        # authority data with calculated complete case ratio
        authority_comp_prop = authority.copy()
        authority_comp_prop['ratio'] = authority_comp_prop['completed']/(authority_comp_prop['completed']+authority_comp_prop['waiting'])
        self.authority_comp_prop = authority_comp_prop

       
        # Cataract Surgery is a unique high volume procedure often performed in seperate OR facilities and will be excluded from a part of the analysis.
        self.no_cataract = main.query('procedure != "Cataract Surgery"')

        
    # data grouped by health authority for a date range
    def data_compprop(self, year, health_authority):
        #data subseted by health authority
        compprop_authority = self.authority_comp_prop[self.authority_comp_prop['health_authority']==health_authority]   

        #data selected for a date range
        compprop_authority_year = compprop_authority[(compprop_authority['year']>=year[0])&(compprop_authority['year']<=year[1])]    
        self.compprop = compprop_authority_year
        
    #complete proportion plot
    def comp_prop_plot(self, year, health_authority):   
        self.data_compprop(year, health_authority) 
        compprop_plot = alt.Chart(self.compprop,width=500,height=300).mark_line().encode(
                            x=alt.X('year:N'),
                            y=alt.Y('ratio:Q', scale=alt.Scale(zero=False)),
                            color=alt.Color('quarter'))
        compprop_plot = compprop_plot+compprop_plot.mark_circle()
        return compprop_plot.to_html()

surgical_plots=SurgicalPlots()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def map_image_plot(authority):
    
    if authority == "Interior":
       
        img = Image.open('data/images/interior.png')
    elif authority == "Fraser":
        img = Image.open('data/images/fraser.png')
    elif authority == "Vancouver Coastal":
        img = Image.open('data/images/vancoastal.png')
    elif authority == "Vancouver Island":
        img = Image.open('data/images/vanisland.png')
    elif authority == "Northern":
        img = Image.open('data/images/northern.png')
    elif authority == "Provincial":
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
   
# year slider
yr_slider=html.Div([
        dcc.RangeSlider(
            id="year_slider",min=2009, max=2022,
            step=1, marks={i: f'{i}' for i in range(2009, 2023)},
            value=[2017, 2022],
            vertical=True
            )        
        ])

# health authority radio buttons
ha_buttons=html.Div([
        dcc.RadioItems(
            id="health_authority_buttons",
            options=[
                {"label": "Interior", "value": "Interior"},
                {"label": "Fraser", "value": "Fraser"},
                {"label": "Vancouver Coastal", "value": "Vancouver Coastal"},
                {"label": "Vancouver Island", "value": "Vancouver Island"},
                {"label": "Northern", "value": "Northern"},
                {"label": "Provincial", "value": "Provincial"},
            ],    
            value='Interior')])

# 1st plot - proportion of completed cases
proportion_cases=html.Div([
        html.Iframe(
            id="comp_prop_plot_id",            
            srcDoc=surgical_plots.comp_prop_plot(health_authority="Interior", year=[2017,2022]),
            style={'border-width': '0', 'width': '100%', 'height': '400px'}
            )
        ])

# 2nd plot - BC map
plot_map_object = html.Div([html.Iframe(
    id = 'map',
    srcDoc=map_image_plot(authority = 'Interior'), 
    style={'border-width': '0', 'width': '100%', 'height': '100%'})
    ])

app.layout= html.Div([  
           
        dbc.Row(
            [
            dbc.Col([dbc.Col(proportion_cases)]),
            dbc.Col([dbc.Col(plot_map_object)])
        ]
        )            
    
])

# 1st plot - callback
@app.callback(
    Output("comp_prop_plot_id",'srcDoc'),   
    
    Input("year_slider","value"),
    Input("health_authority_buttons","value")
)
def update_comp_prop_plot(year, health_authority):
    if health_authority=="Provincial":
        health_authority="Provincial Health Services Authority"
    return surgical_plots.comp_prop_plot(year, health_authority)

# 2nd plot - map
@app.callback(
    Output('map', 'srcDoc'),
    Input('health_authority_buttons', 'value'))
def update_map_image_plot(authority):
    return map_image_plot(authority)


if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.3')
