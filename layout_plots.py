from io import BytesIO

import pandas as pd
import numpy as np

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

    
    def filtering(self,health_authority,year):
        # rename health authority
        if(health_authority=="Provincial"):
            health_authority="Provincial Health Services Authority"

        # filter health authority        
        no_cataract_authority=  self.no_cataract[self.no_cataract['health_authority']==health_authority]
        
        # grouping by procedure 
        procedure = no_cataract_authority.groupby(['procedure', 'year', 'quarter']).mean().reset_index()
        
        # subsett from 2017 to current year
        procedure = procedure[(procedure['year']>=year[0])&(procedure['year']<=year[1])]
        procedure['time'] = procedure['year'].map(str)+procedure['quarter']
        procedure_unite = procedure.drop(columns = ['year','quarter'])

        # most treated and less treated surgeries
        procedure_order = procedure_unite.groupby('procedure').mean().reset_index()
        procedure_order = procedure_order.sort_values('wait_time_90')

        # fastest and slowest procedures
        self.fastest = procedure_order.head(5)
        self.slowest = procedure_order.tail(5)

        # round off numbers to 2 decimal places
        self.fastest=self.fastest.round(2)
        self.slowest=self.slowest.round(2)

    def fastest_procedures(self,health_authority,year):              
        self.filtering(health_authority,year)  
        sort_order=self.fastest['wait_time_90'].to_list()      
        procedure_time_chart = alt.Chart(self.fastest,width=500,height=300).mark_bar(size=20,
                                                        point={"filled": False, "fill": "white"}).encode(
                                                        x=alt.X('wait_time_90',axis=alt.Axis(values=np.arange(0,14,2))),
                                                        y=alt.Y('procedure', scale=alt.Scale(zero=False),sort=sort_order),
                                                        color=alt.Color('procedure',legend=None))
        procedure_time_chart=procedure_time_chart+ procedure_time_chart.mark_text(dx=15).encode(text="wait_time_90")
        return procedure_time_chart.to_html()

    def slowest_procedures(self,health_authority,year):           
        self.filtering(health_authority,year)
        sort_order=self.slowest['wait_time_90'].to_list()        
        procedure_time_chart = alt.Chart(self.slowest,width=500,height=300).mark_bar(size=20,
                                                        point={"filled": False, "fill": "white"}).encode(
                                                        x=alt.X('wait_time_90',axis=alt.Axis(values=np.arange(0,150,10))),
                                                        y=alt.Y('procedure', scale=alt.Scale(zero=False),sort=sort_order),
                                                        color=alt.Color('procedure',legend=None))
        procedure_time_chart=procedure_time_chart+ procedure_time_chart.mark_text(dx=15).encode(text="wait_time_90")
        return procedure_time_chart.to_html()

    # data grouped by hospital for selected health authority and date range
    def data_by_hosp(self, health_authority,year, hospname):
        

        #filter and arrange data for plotting 
        #print(self.count.health_authority.unique())
        
        #print(self.count[self.count['health_authority']==health_authority].groupby(['hospital', 'year', 'quarter'])['waiting','completed'].sum().reset_index()
        hosp_data = self.count[self.count['health_authority']==health_authority]
        hosp_data = hosp_data.groupby(['hospital', 'year', 'quarter'])['waiting','completed'].sum().reset_index()
        
        hosp_data = hosp_data[(hosp_data['year']>=year[0]) & (hosp_data['year']<=year[1])]
        
        hosp_data_melted = hosp_data.melt(id_vars=['hospital','year','quarter'])
       
      
        hosp_data_melted['time'] = hosp_data_melted['year'].map(str)+hosp_data_melted['quarter']
        
        hosp_data_melted = hosp_data_melted.drop(columns = ['year','quarter'])

        #create hospital dropdown list
        self.hosp_list = hosp_data_melted.hospital.unique()

        #waiting and completed cases for chosen hospital
        self.one_hospital = hosp_data_melted[hosp_data_melted['hospital'] == hospname]
       

    def wait_complete_plot(self,health_authority, year, hospname):  
         
        
        self.data_by_hosp(health_authority,year, hospname) 
        wc_plot = alt.Chart(self.one_hospital).mark_bar(size=10).encode(
                            x=alt.X('variable', axis=alt.Axis(title=None, labels=False, ticks=False)),
                            y=alt.Y('value', scale=alt.Scale(zero=False), axis=alt.Axis(grid=False)),
                            color=alt.Color('variable'),
                            column = alt.Column('time', header=alt.Header(title=None, labelOrient='bottom', labelAngle=90))
        ).configure_view(stroke='transparent'
        ).properties(height=350
        ).configure_facet(spacing=7
        )       
        return wc_plot.to_html()

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
#        print(self.compprop)
        compprop_plot = alt.Chart(self.compprop,width=500,height=300).mark_line().encode(
                            x=alt.X('year:N'),
                            y=alt.Y('ratio:Q', scale=alt.Scale(zero=False)),
                            color=alt.Color('quarter'))
        compprop_plot = compprop_plot+compprop_plot.mark_circle()
        return compprop_plot.to_html()

surgical_plots=SurgicalPlots()


def map_image_plot(authority):
    print(authority)
    if authority == "Interior":
        print("Image found")
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
   


# All the score cards
wait_cases_card = dbc.Card(
    [
        dbc.CardHeader("Total waiting cases"),
        dbc.CardBody(
            [                
                html.P("This is some card text", className="text-center",id="wait_cases_text")                
            ]
        ),        
    ],
    style={"width": "20rem",'display': 'inline-block',"justify-content":"center"}
)
completed_cases_card = dbc.Card(
    [
        dbc.CardHeader("Total completed cases"),
        dbc.CardBody(
            [                
                html.P("This is some card text", className="text-center",id="completed_cases_text")                
            ]
        ),        
    ],
    style={"width": "20rem",'display': 'inline-block'}
)
wait_50_card = dbc.Card(
    [
        dbc.CardHeader("Mean waiting time(weeks) - 50 %le"),
        dbc.CardBody(
            [                
                html.P("This is some card text", className="text-center",id="mean_waiting_time_50%_text")                
            ]
        ),        
    ],
    style={"width": "20rem",'display': 'inline-block','align-items':'center', 'justify-content':'center'}
)
wait_90_card = dbc.Card(
    [
        dbc.CardHeader("Mean waiting time(weeks) - 90 %le"),
        dbc.CardBody(
            [                
                html.P("This is some card text", className="text-center",id="mean_waiting_time_90%_text")
            ]
        ),        
    ],
    style={"width": "20rem",'display': 'inline-block','align-items':'center', 'justify-content':'center'}
)

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

# pace button
fast_slow_button=html.Div([
        dcc.RadioItems(
            id="fastest_slowest_treatments_buttons",
            options=["Fastest","Slowest"],
            value='Fastest')
            ])

# hospital dropdown
hosp_dropdown=html.Div([            
            dcc.Dropdown(
                id='hospital_dropdown',
                options=[],
                value=[],
                clearable=False
            )
        ])

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
    style={'border-width': '0', 'width': '100%', 'height': '500px'})
    ])

# 3rd plot - procedure plot
procedure_plot = html.Div([
        html.Iframe(
            id="procedure_plot_id",            
            srcDoc=surgical_plots.fastest_procedures(health_authority="Interior",year=[2017,2022]),
            style={'border-width': '0', 'width': '100%', 'height': '400px'}
            )
        ])

# 4th plot - hospital wait and completed cases
hosp_wait_comp_cases =html.Div([
        html.Iframe(
            id="hosp_wait_comp_plot",            
            srcDoc=surgical_plots.wait_complete_plot(health_authority="Interior",hospname="100 Mile District General Hospital", year=[2017,2022]),
            style={'border-width': '0', 'width': '500px', 'height': '350px','display': 'inline-block'}
            )
        ])
        
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

app.layout= dbc.Container([  
    html.Div([
        dbc.Row([ha_buttons]),
        
        yr_slider,        
        proportion_cases,
        plot_map_object,   
        fast_slow_button,
        procedure_plot,
        hosp_dropdown,
        hosp_wait_comp_cases               
    ]),
    html.Div([
                dbc.Row
                (
                    [
                        dbc.Col(wait_cases_card),
                        dbc.Col(completed_cases_card),
                        dbc.Col(wait_50_card),
                        dbc.Col(wait_90_card)
                    ]
                )             
            ])
])
# app.layout= dbc.Container([  
#     html.Div([
#         dbc.Row([
#             dbc.Col([
#                 html.H1('SURGICAL WAIT TIMES',style={'color':'blue'}),
#                 ha_buttons
#             ])
#         ])
#     ]),
    
#     html.Div([
#         dbc.Row([
#             dbc.Col([
#                 yr_slider,
#                 fast_slow_button,
#                 procedure_plot
#             ]),
            
#         ])                    
             
#     ])
# ])

# 1st plot - callback
@app.callback(
    Output("comp_prop_plot_id",'srcDoc'),   
    [
    Input("year_slider","value"),
    Input("health_authority_buttons","value")]
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

# chainback dropdown - callback
@app.callback(
        [Output('hospital_dropdown', 'options'),
        Output('hospital_dropdown', 'value')],
        Input('health_authority_buttons', 'value'),
    )
def set_hosp_dropdown(health_athority):
    
    if(health_athority=="Provincial"):
        health_athority="Provincial Health Services Authority"
    filtered_data=surgical_plots.count[surgical_plots.count.health_authority==health_athority]
    
    dropdown_options = [{'label': c, 'value': c} for c in sorted(filtered_data.hospital.unique())]
    #values_selected = [dropdown_options[0]]
    
    return dropdown_options, dropdown_options[0]['label']

# 4th plot - callback
@app.callback(
    Output("hosp_wait_comp_plot",'srcDoc'),   
    [
    Input("health_authority_buttons","value"),
    Input("year_slider","value"),
    Input("hospital_dropdown","value")]
)

def update_wait_complete_plot(health_authority,year, hospname):
    if(health_authority=="Provincial"):
        health_authority="Provincial Health Services Authority"
    
    return surgical_plots.wait_complete_plot(health_authority,year, hospname)

# 3rd plot - callback
@app.callback(
    Output("procedure_plot_id",'srcDoc'),   
    [Input("health_authority_buttons","value"),
    Input("year_slider","value"),
    Input("fastest_slowest_treatments_buttons","value")]
)
def update_procedure_plot(health_authority,year,pace):    
    if(pace=="Slowest"):
        return surgical_plots.slowest_procedures(health_authority,year)
    else:
        return surgical_plots.fastest_procedures(health_authority,year)

# score cards - callback
@app.callback(
    [
        Output('wait_cases_text','children'),
        Output('completed_cases_text','children'),
        Output('mean_waiting_time_50%_text','children'),        
        Output('mean_waiting_time_90%_text','children')
    ],
    [
        Input("health_authority_buttons","value"),
        Input("year_slider","value")
    ]
)
def update_score_cards(health_authority,year):
    if(health_authority=="Provincial"):
            health_authority="Provincial Health Services Authority"
    filtered_data = surgical_plots.qdata[
                                    (surgical_plots.qdata['health_authority']==health_authority)&
                                    (surgical_plots.qdata['year']>=year[0])&
                                    (surgical_plots.qdata['year']<=year[1])
                                    ]    
    total_waiting = filtered_data['waiting'].sum()
    total_completed = filtered_data['completed'].sum()
    mean_wait_time_50= filtered_data['wait_time_50'].mean()
    mean_wait_time_90=filtered_data['wait_time_90'].mean()
    return total_waiting,total_completed,round(mean_wait_time_50),round(mean_wait_time_90)

if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.7')