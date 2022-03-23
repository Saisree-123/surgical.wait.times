from io import BytesIO

import pandas as pd
import numpy as np

import altair as alt

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

import base64
from PIL import Image


class SurgicalPlots:
    def __init__(self):

        # read in data
        path = 'data/2009_2021-quarterly-surgical_wait_times.xlsx'
        qdata = pd.read_excel(path)
        newdata = pd.read_excel(
            'data/2021_2022-quarterly-surgical_wait_times-q3-interim.xlsx')
        qdata = pd.concat([qdata, newdata])
        qdata.columns = qdata.columns.str.lower()

        # Rename columns
        qdata.rename(columns={'fiscal_year': 'year',
                              'hospital_name': 'hospital',
                              'procedure_group': 'procedure',
                              'completed_50th_percentile': 'wait_time_50',
                              'completed_90th_percentile': 'wait_time_90'}, inplace=True)

        # Format year column
        qdata['year'] = qdata['year'].str.replace('(/).*', "")
        qdata['year'] = pd.to_numeric(qdata['year'])

        # convert <5 string to median value of 3
        qdata = qdata.replace('<5', 3)
        self.qdata = qdata
        # drop rows with NAs
        clean = qdata.dropna()
        count = qdata.iloc[:, 0:7]

        # drop "All" data
        main = clean.query(
            'procedure != "All Procedures" & hospital != "All Facilities" & health_authority != "All Health Authorities"')
        count = count.query(
            'procedure != "All Procedures" & hospital != "All Facilities" & health_authority != "All Health Authorities"')
        self.count = count
        all = clean.query(
            'procedure == "All Procedures" & hospital == "All Facilities" & health_authority == "All Health Authorities"')

        authority = count.groupby(
            ['health_authority', 'year', 'quarter']).sum().reset_index()

        # authority data with calculated complete case ratio
        authority_comp_prop = authority.copy()
        authority_comp_prop['ratio'] = authority_comp_prop['completed'] / \
            (authority_comp_prop['completed']+authority_comp_prop['waiting'])
        self.authority_comp_prop = authority_comp_prop

        # Cataract Surgery is a unique high volume procedure often performed in seperate OR facilities and will be excluded from a part of the analysis.
        self.no_cataract = main.query('procedure != "Cataract Surgery"')

    def filtering(self, health_authority, year):
        # rename health authority
        if(health_authority == "Provincial"):
            health_authority = "Provincial Health Services Authority"

        # filter health authority
        no_cataract_authority = self.no_cataract[self.no_cataract['health_authority']
                                                 == health_authority]

        # grouping by procedure
        procedure = no_cataract_authority.groupby(
            ['procedure', 'year', 'quarter']).mean().reset_index()

        # subsett from 2017 to current year
        procedure = procedure[(procedure['year'] >= year[0])
                              & (procedure['year'] <= year[1])]
        procedure['time'] = procedure['year'].map(str)+procedure['quarter']
        procedure_unite = procedure.drop(columns=['year', 'quarter'])

        # most treated and less treated surgeries
        procedure_order = procedure_unite.groupby(
            'procedure').mean().reset_index()
        procedure_order = procedure_order.sort_values('wait_time_90')

        # fastest and slowest procedures
        self.fastest = procedure_order.head(5)
        self.slowest = procedure_order.tail(5)

        # round off numbers to 2 decimal places
        self.fastest = self.fastest.round(2)
        self.slowest = self.slowest.round(2)

    def pace_procedures(self,health_authority,year,pace):              
        self.filtering(health_authority,year)  
          
        colors=['green','paleturquoise','navyblue','royalblue','black']    
        if(pace=="Fastest"):
            result=self.fastest
            axis_range=np.arange(0,14,2)
            sort_order=self.fastest['wait_time_90'].to_list()
        else:
            result=self.slowest
            axis_range=np.arange(0,150,10)
            sort_order=self.slowest['wait_time_90'].to_list()
        print(pace,result.head())
        procedure_time_chart = alt.Chart(result,width=500,height=300).mark_bar(size=30,
                                                        point={"filled": False, "fill": "white"},opacity=0.5).encode(
                                                        x=alt.X('wait_time_90',title="Wait time(in weeks)",axis=alt.Axis(values=axis_range,grid=False)),
                                                        y=alt.Y('procedure', scale=alt.Scale(zero=False),sort=sort_order,axis=alt.Axis(labels=False,grid=False)),
                                                        color=alt.Color('procedure',legend=None,scale=alt.Scale(range=colors)),
                                                        tooltip=['procedure','wait_time_90'])
        procedure_time_text_time_chart = alt.Chart(result,width=500,height=200).mark_bar(size=30,
                                                        point={"filled": False, "fill": "white"},opacity=0.5).encode(
                                                        x=alt.X('wait_time_90',axis=alt.Axis(values=axis_range)),
                                                        y=alt.Y('procedure', scale=alt.Scale(zero=False),sort=sort_order,axis=alt.Axis(labels=False)),                                                        
                                                        )
        procedure_time_text_procedure_chart = alt.Chart(result,width=500,height=200).mark_bar(size=30,
                                                        point={"filled": False, "fill": "white"},opacity=0.5).encode(
                                                        x=alt.X('wait_time_90',axis=alt.Axis(values=axis_range)),
                                                        y=alt.Y('procedure', scale=alt.Scale(zero=False),sort=sort_order,axis=alt.Axis(labels=False)),                                                        
                                                        )
        text_time=procedure_time_text_time_chart+procedure_time_text_time_chart.mark_text(dx=15,color='black',size=10).encode(text="wait_time_90")
        text_procedure=procedure_time_text_procedure_chart+procedure_time_text_procedure_chart.mark_text(align='left',dx=-165,color='black',size=10).encode(text="procedure")
        procedure_time_chart=procedure_time_chart+text_time+text_procedure 
        procedure_time_chart=procedure_time_chart.configure_view(strokeWidth=0)
        return procedure_time_chart.interactive().to_html()

    # data grouped by hospital for selected health authority and date range
    def data_by_hosp(self, health_authority, year, hospname):

        # filter and arrange data for plotting
        # print(self.count.health_authority.unique())

        # print(self.count[self.count['health_authority']==health_authority].groupby(['hospital', 'year', 'quarter'])['waiting','completed'].sum().reset_index()
        hosp_data = self.count[self.count['health_authority']
                               == health_authority]
        hosp_data = hosp_data.groupby(['hospital', 'year', 'quarter'])[
            'waiting', 'completed'].sum().reset_index()

        hosp_data = hosp_data[(hosp_data['year'] >= year[0])
                              & (hosp_data['year'] <= year[1])]

        hosp_data_melted = hosp_data.melt(
            id_vars=['hospital', 'year', 'quarter'])

        hosp_data_melted['time'] = hosp_data_melted['year'].map(
            str)+hosp_data_melted['quarter']

        hosp_data_melted = hosp_data_melted.drop(columns=['year', 'quarter'])

        # create hospital dropdown list
        self.hosp_list = hosp_data_melted.hospital.unique()

        # waiting and completed cases for chosen hospital
        self.one_hospital = hosp_data_melted[hosp_data_melted['hospital'] == hospname]

    def wait_complete_plot(self, health_authority, year, hospname):

        self.data_by_hosp(health_authority, year, hospname)
        wc_plot = alt.Chart(self.one_hospital).mark_bar(size=15).encode(
            x=alt.X('variable', axis=alt.Axis(
                title=None, labels=False, ticks=False)),
            y=alt.Y('value', scale=alt.Scale(zero=False),
                    axis=alt.Axis(grid=False)),
            color=alt.Color('variable', legend=alt.Legend(orient="top", title = "")),
            column=alt.Column('time', header=alt.Header(
                title=None, labelOrient='bottom', labelAngle=90))
        ).configure_view(stroke='transparent'
                         ).properties(height=250
                                      ).configure_facet(spacing=7
                                                        )
        return wc_plot.to_html()

    # data grouped by health authority for a date range
    def data_compprop(self, year, health_authority):
        # data subseted by health authority
        compprop_authority = self.authority_comp_prop[
            self.authority_comp_prop['health_authority'] == health_authority]

        # data selected for a date range
        compprop_authority_year = compprop_authority[(
            compprop_authority['year'] >= year[0]) & (compprop_authority['year'] <= year[1])]
        self.compprop = compprop_authority_year

    # complete proportion plot
    def comp_prop_plot(self, year, health_authority):
        self.data_compprop(year, health_authority)
#        print(self.compprop)
        compprop_plot = alt.Chart(self.compprop, width=400, height = 270).mark_line().encode(
            x=alt.X('year:N'),
            y=alt.Y('ratio:Q', scale=alt.Scale(zero=False)),
            color=alt.Color('quarter', legend=alt.Legend(orient="top", title = "Quarter"))
            )
        compprop_plot = compprop_plot+compprop_plot.mark_circle()
        compprop_plot = compprop_plot.configure_axis(
            grid=False
            ).configure_view(strokeWidth=0)
        return compprop_plot.to_html()


surgical_plots = SurgicalPlots()


map_data = alt.Data(url='https://raw.githubusercontent.com/Jagdeep14/shapefile_data/main/HA_2018.geojson', format=alt.DataFormat(property='features',type='json'))

def map_plot(authority = 'Interior'):
    # plot1 is only for provincial authority
    if authority == "Provincial":
        plot1 = alt.Chart(map_data, width = 370, height = 350).mark_geoshape(stroke = "black", opacity = 0.5, fill = "blue"
        ).encode(
            tooltip = "properties.HA_Name:N"
        ).project(
            type='identity', reflectY=True
        ).configure_view(
        strokeWidth=0
    )
        return plot1.to_html()
    # Plot2 is for all other authorities other than provincial
    else:
        plot2 = alt.Chart(map_data, width = 370, height = 350).mark_geoshape(stroke = "black"
        ).encode(
            color= alt.Color("properties.HA_Name:N", legend = None),
            opacity=alt.condition(alt.datum['properties']['HA_Name'] == authority, alt.value(1), alt.value(0.3)),
            tooltip = "properties.HA_Name:N"
        ).project(
            type='identity', reflectY=True
        ).configure_view(
        strokeWidth=0
    )
        return plot2.to_html()
    

# All the score cards
completed_cases_card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.P("Total Completed Cases", className="card-title",
                       style = {"fontSize": "17px", 'font-weight':'bolder'}),
                dbc.CardImg(src="/assets/total.png", top=True),
                html.P("This is some card text",
                       className="text-center", id="completed_cases_text",
                       style = {"fontSize": "22px", 'font-weight':'bolder'})
            ]
        ),
    ],
    style={"width": "20rem", "height": "14rem",'display': 'inline-block', 'background-color':'#becfe6',
           "justify-content": 'center', 'justify-content': 'center', "border": "6px #568cc1 solid"}
)

wait_cases_card = dbc.Card(
    [
        
        dbc.CardBody(
            [
                html.P("Total Waiting Cases", className="card-title",
                       style = {"fontSize": "17px", 'font-weight':'bolder'}),
                dbc.CardImg(src="/assets/waiting.png", top=True),
                html.P(
                    "This is some card text",
                       className="text-center", id="wait_cases_text", 
                       style = {"fontSize": "22px", 'font-weight':'bolder'})
            ]
        ),
    ],
    style={"width": "20rem", "height": "14rem",'display': 'inline-block', 'background-color':'#becfe6',
           "justify-content": 'center', 'justify-content': 'center', "border": "6px #568cc1 solid"}
)

wait_50_card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.P("Average Wait Time (in weeks) 50 %ile", className="card-title",
                       style = {"fontSize": "17px", 'font-weight':'bolder'}),
                dbc.CardImg(src="/assets/50.png", top=True),
                html.P("This is some card text", className="text-center",
                       id="mean_waiting_time_50%_text",
                       style = {"fontSize": "23px", 'font-weight':'bolder'})
            ]
        ),
    ],
    style={"width": "20rem", "height": "14rem",'display': 'inline-block', 'background-color':'#becfe6',
           "justify-content": 'center', 'justify-content': 'center', "border": "6px #568cc1 solid"}
)
wait_90_card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.P("Average Wait Time (in weeks) 90 %ile", className="card-title",
                       style = {"fontSize": "17px", 'font-weight':'bolder'}),
                dbc.CardImg(src="/assets/90.png", top=True),
                html.P("This is some card text", className="text-center",
                       id="mean_waiting_time_90%_text",
                       style = {"fontSize": "23px", 'font-weight':'bolder'})
            ]
        ),
    ],
    style={"width": "20rem", "height": "14rem",'display': 'inline-block', 'background-color':'#becfe6',
           "justify-content": 'center', 'justify-content': 'center', "border": "6px #568cc1 solid"}
)

# year slider
yr_slider=html.Div([
        dcc.RangeSlider(
            id="year_slider",min=2015, max=2021,
            step=1, marks={i: f'{i}' for i in range(2009, 2022)},
            value=[2017, 2021]
            )        
        ], style={'font-weight':'bolder'})

# health authority radio buttons
ha_buttons = html.Div([
    dcc.Dropdown(
        id="health_authority_buttons",
        options=[
            {"label": "Interior", "value": "Interior"},
            {"label": "Fraser", "value": "Fraser"},
            {"label": "Vancouver Coastal", "value": "Vancouver Coastal"},
            {"label": "Vancouver Island", "value": "Vancouver Island"},
            {"label": "Northern", "value": "Northern"},
            {"label": "Provincial", "value": "Provincial"},
        ],
        value='Interior')],
        style = {'stroke-width': '20px'})

# hospital dropdown
hosp_dropdown=html.Div([
            dcc.Dropdown(
                id='hospital_dropdown',
                options=[],
                value=[],
                clearable=False
            )
        ],style={"width":"100%"})

# pace button
fast_slow_button = html.Div([
    dcc.RadioItems(
        id="fastest_slowest_treatments_buttons",
        options=[
            {"label": "Fastest", "value": "Fastest"},
            {"label": "Slowest", "value": "Slowest"},
        ],
        value="Fastest",
        labelStyle = {"cursor": "pointer", "margin-left":"20px"})
])

# Download button
download_button = html.Div([
    dbc.Button("Download-csv", id="btn-download",style={
             'background-color': '#568cc1',
              'color': 'aliceblue',
              'border': '0px',
              'hover': { 
                     'color': '#ffffff'
              }
      }),
    dcc.Download(id="download-df-csv")
])

link_github= html.Div([
    html.A('Github', href='https://github.com/Saisree-123/surgical.wait.times', target='_blank')
    ])

# 1st plot - proportion of completed cases
proportion_cases = html.Div([
    html.Iframe(
        id="comp_prop_plot_id",
        srcDoc=surgical_plots.comp_prop_plot(
            health_authority="Interior", year=[2017, 2022]),
        style={"border": "6px #568cc1 solid", 'background-color':'#ffffff', 'width': '100%', 'height': '400px'}
    )
])

# 2nd plot - BC map
plot_map_object = html.Div([html.Iframe(
    id='map',
    srcDoc=map_plot(authority='Interior'),
    style={"border": "6px #568cc1 solid", 'background-color':'#ffffff', 'width': '100%', 'height': '400px', 'align':"center"})
])

# 3rd plot - procedure plot
procedure_plot = html.Div([
    html.Iframe(
        id="procedure_plot_id",
        srcDoc=surgical_plots.pace_procedures(
            health_authority="Interior", year=[2017, 2022],pace="Fastest"),
        style={"border": "6px #568cc1 solid", 'background-color':'#ffffff', 'width': '100%', 'height': '400px'}
    )
])

# 4th plot - hospital wait and completed cases
hosp_wait_comp_cases = html.Div([
    html.Iframe(
        id="hosp_wait_comp_plot",
        srcDoc=surgical_plots.wait_complete_plot(
            health_authority="Interior", hospname="100 Mile District General Hospital", year=[2017, 2022]),
        style={"border": "6px #568cc1 solid", 'background-color':'#ffffff', 'width': '100%', 'height': '400px', 'display': 'inline-block'}
    )
])

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

#### Title row ################################
title_row = dbc.Row([
            html.Div(),
            html.H1('SURGICAL WAIT TIMES - BC', style={
                'background-color': '#568cc1', # navy blue
                'color': 'white', 
                'padding-top': '15px',
                'padding-bottom': '15px',
                'bottom-margin': '0',
                'left-padding': "30px"
                }),
            dbc.Col(html.Div(), width = 8),
            dbc.Col(link_github, width=1),
            dbc.Col(download_button, width=2, style={'padding-bottom': '5px'})
    ])


#### health authority buttons and slider ##############
authority_buttons_row = dbc.Row([
        dbc.Col(html.Div(), width = 1),
        dbc.Col(yr_slider, width = 6), 
        dbc.Col(html.Div(), width = 1),
        dbc.Col(ha_buttons, width = 3),
        dbc.Col(html.Div(), width = 1)
        ],
        style={
        'background-color': '#becfe6',
        'font-weight': 'bolder',
        'font-size': '16px',
        'padding-top': '15px',
        'padding-bottom': '15px',
        'top-margin': '0',
        'text-align': "center"}
        )
     
    

##### Cards column ###################
col1 = html.Div(
    [  dbc.Row([dbc.Col(html.Div(), width=3),
        dbc.Col([
        dbc.Row(completed_cases_card),
        html.Br(),
        dbc.Row(wait_cases_card),
        html.Br(),
        html.Br(),
        dbc.Row(wait_50_card),
        html.Br(),
        dbc.Row(wait_90_card),
    ], width = 10),
    dbc.Col(html.Div(), width=5)])
    ],
    style={
        'border-color':'#1f77b4',
        'padding-left': 15, 
        'padding-right': 0,
        'text-align': "center"}
    )

############ col2 #######################
###### column 2 needs five rows ########
# row1 elements (titles of top two plots)
row1_col1 = dbc.Row(html.Div("Proportion of completed cases", style = {
                            "font-weight": "bolder", 'text-align': "center", 'font-size':'18px'}))
row1_col2 = dbc.Row(html.Div("Health authority", style = {
                            "font-weight": "bolder", 'text-align': "center", 'font-size':'18px'}))

row1 = html.Div([dbc.Row(
    [
        dbc.Col(row1_col1, md = 6),
        dbc.Col(row1_col2, md = 6)
    ]
    )]
)

# row 2 elements (top two plots)
row2_col1 = dbc.Row(proportion_cases)
row2_col2 = dbc.Row(plot_map_object)

row2 = html.Div([dbc.Row(
    [
        dbc.Col(row2_col1, md = 6),
        dbc.Col(row2_col2, md = 6)
    ]
    )], 
    style={"padding-bottom": 50}
)

# text for top 2 plots
row3_1_col1 = dbc.Row(html.Div(
                    "Efficiency of a health authority in selected years (by quarter)", style = {
                    'text-align': "center",'color':'#204e74'}))
row3_1_col2 = dbc.Row(html.Div(
                    "Health authority geographic boundaries", style = {
                    'text-align': "center",'color':'#204e74'}))

row3_1 = html.Div([dbc.Row(
    [
        dbc.Col(row3_1_col1, md = 6),
        dbc.Col(row3_1_col2, md = 6)
    ]
    )]
)

# row 3 elements (titles of bottom two plots)
row3_col1 = dbc.Row(html.Div("Fastest/Slowest treated procedures", style = {
                            "font-weight": "bolder", 'text-align': "center", 'font-size':'18px'}))
row3_col2 = dbc.Row(html.Div("Completed and waiting cases", style = {
                            "font-weight": "bolder", 'text-align': "center", 'font-size':'18px'}))

row3 = html.Div([dbc.Row(
    [
        dbc.Col(row3_col1, md = 6),
        dbc.Col(row3_col2, md = 6)
    ]
    )]
)

# row 4 elements (buttons and dropdown of bottom two plots)
row4_col1 = dbc.Row([
    dbc.Col(html.Div(), width=3),
    dbc.Col(fast_slow_button, width=5),
    dbc.Col(html.Div(), width=4)], style={'font-size':'16px','font-weight':'bolder'})
row4_col2 = dbc.Row([
    dbc.Col(html.Div(), width=2),
    dbc.Col(hosp_dropdown, width=8),
    dbc.Col(html.Div(), width=2)])

row4 = html.Div([dbc.Row(
    [
        dbc.Col(row4_col1, md = 6),
        dbc.Col(row4_col2, md = 6)
    ]
    )],
    #style={"padding-bottom": 0, "padding-top": 0}
)

# row 5 elements (bottom two plots)
row5_col1 = dbc.Row(procedure_plot)
row5_col2 = dbc.Row(hosp_wait_comp_cases)

row5 = html.Div([dbc.Row(
    [
        dbc.Col(row5_col1, md = 6),
        dbc.Col(row5_col2, md = 6)
    ]
    )], 
    style={"padding-bottom": 0}
)

# text for bottom 2 plots
row5_1_col1 = dbc.Row(html.Div(
                    "Five fastest/slowest procedures using 90th percentile wait time", style = {
                    'text-align': "center",'color':'#204e74'}))
row5_1_col2 = dbc.Row(html.Div(
                    "Number of completed and waiting cases for selected hospital", style = {
                    'text-align': "center",'color':'#204e74'}))

row5_1 = html.Div([dbc.Row(
    [
        dbc.Col(row5_1_col1, md = 6),
        dbc.Col(row5_1_col2, md = 6)
    ]
    )]
)
# row6 = html.Div([dbc.Row(
#     [
# #        dbc.Col(md = 6),
#         dbc.Col(download_button, md = 3),
#         dbc.Col(link_github , md=3)
#     ]
#     )]
# )

col2 = html.Div(
    [
        row1,       # has titles of plots of first row
        row3_1,
        row2,      # has top two plots
    #    row3_1,
        row3,
        row4,
        row5_1,
        row5,
    #    row5_1,
        # row6
    ],
    style={'padding-left': 0, "padding-right": 0}
    )


########### columns for slider, cards and plots############
main_row = html.Div([
    dbc.Row([
        dbc.Col(col1, md=2),    # Cards column
        dbc.Col(col2, width=9)  # plots column
    ])
],
style={'padding-top': "30px"})


########## layout ################################
app.layout = html.Div([
    title_row,
    authority_buttons_row,
    main_row
],
style={"background-color": "#7ba2cd", "width": "100%"})


############## call backs ######################################################
# 1st plot - callback
@app.callback(
    Output("comp_prop_plot_id", 'srcDoc'),
    [
        Input("year_slider", "value"),
        Input("health_authority_buttons", "value")]
)
def update_comp_prop_plot(year, health_authority):
    if health_authority == "Provincial":
        health_authority = "Provincial Health Services Authority"
    return surgical_plots.comp_prop_plot(year, health_authority)

# 2nd plot - map


@app.callback(
    Output('map', 'srcDoc'),
    Input('health_authority_buttons', 'value'))
def update_map_plot(authority):
    return map_plot(authority)

# chainback dropdown - callback


@app.callback(
    [Output('hospital_dropdown', 'options'),
     Output('hospital_dropdown', 'value')],
    Input('health_authority_buttons', 'value'),
)
def set_hosp_dropdown(health_athority):

    if(health_athority == "Provincial"):
        health_athority = "Provincial Health Services Authority"
    filtered_data = surgical_plots.count[surgical_plots.count.health_authority == health_athority]

    dropdown_options = [{'label': c, 'value': c}
                        for c in sorted(filtered_data.hospital.unique())]
    #values_selected = [dropdown_options[0]]

    return dropdown_options, dropdown_options[0]['label']

# 4th plot - callback


@app.callback(
    Output("hosp_wait_comp_plot", 'srcDoc'),
    [
        Input("health_authority_buttons", "value"),
        Input("year_slider", "value"),
        Input("hospital_dropdown", "value")]
)
def update_wait_complete_plot(health_authority, year, hospname):
    if(health_authority == "Provincial"):
        health_authority = "Provincial Health Services Authority"

    return surgical_plots.wait_complete_plot(health_authority, year, hospname)

# 3rd plot - callback


@app.callback(
    Output("procedure_plot_id", 'srcDoc'),
    [Input("health_authority_buttons", "value"),
     Input("year_slider", "value"),
     Input("fastest_slowest_treatments_buttons", "value")]
)
def update_procedure_plot(health_authority, year, pace):
    return surgical_plots.pace_procedures(health_authority, year,pace)

# score cards - callback


@app.callback(
    [
        Output('wait_cases_text', 'children'),
        Output('completed_cases_text', 'children'),
        Output('mean_waiting_time_50%_text', 'children'),
        Output('mean_waiting_time_90%_text', 'children')
    ],
    [
        Input("health_authority_buttons", "value"),
        Input("year_slider", "value")
    ]
)
def update_score_cards(health_authority, year):
    if(health_authority == "Provincial"):
        health_authority = "Provincial Health Services Authority"
    filtered_data = surgical_plots.qdata[
        (surgical_plots.qdata['health_authority'] == health_authority) &
        (surgical_plots.qdata['year'] >= year[0]) &
        (surgical_plots.qdata['year'] <= year[1])
    ]
    total_waiting = filtered_data['waiting'].sum()
    total_completed = filtered_data['completed'].sum()
    mean_wait_time_50 = filtered_data['wait_time_50'].mean()
    mean_wait_time_90 = filtered_data['wait_time_90'].mean()
    return total_waiting, total_completed, round(mean_wait_time_50), round(mean_wait_time_90)


if __name__ == '__main__':
    app.run_server(debug=True)