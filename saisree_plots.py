import pandas as pd
import numpy as np

import altair as alt

import dash
from dash import  dcc, html, Input, Output
import dash_bootstrap_components as dbc

class Procedures:

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
        # Formatting year column
        qdata['year'] = qdata['year'].str.replace('(/).*', "")
        qdata['year'] = pd.to_numeric(qdata['year'])

        # convert <5 string to median value of 3
        qdata = qdata.replace('<5', 3)

        # drop rows with NAs
        clean = qdata.dropna()
        count = qdata.iloc[:,0:7]

        # Data subsetting
        main = clean.query('procedure != "All Procedures" & hospital != "All Facilities" & health_authority != "All Health Authorities"')
        count = count.query('procedure != "All Procedures" & hospital != "All Facilities" & health_authority != "All Health Authorities"')
        all = clean.query('procedure == "All Procedures" & hospital == "All Facilities" & health_authority == "All Health Authorities"')

        # group by health authority
        authority = count.groupby(['health_authority', 'year', 'quarter']).sum().reset_index()

        # authority data with calculated complete case ratio
        authority['time'] = authority['year'].map(str)+authority['quarter']
        authority['ratio'] = authority['completed']/(authority['completed']+authority['waiting'])
        authority = authority.drop(columns = ['year', 'quarter'])

        # group Hospital within Northern Health Authority
        hospital_northern = count.query('health_authority == "Northern"').groupby(['hospital', 'year', 'quarter']).sum().reset_index()
        hospital_northern_melted = hospital_northern.melt(id_vars=['hospital','year','quarter'])
        hospital_northern_melted['time'] = hospital_northern_melted['year'].map(str)+hospital_northern_melted['quarter']
        hospital_northern_melted = hospital_northern_melted.drop(columns = ['year','quarter'])

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
        print("Fastest")
        print(self.fastest) 
        procedure_time_chart = alt.Chart(self.fastest,width=500,height=300).mark_bar(size=20,
                                                        point={"filled": False, "fill": "white"}).encode(
                                                        x=alt.X('wait_time_90',axis=alt.Axis(values=np.arange(0,14,2))),
                                                        y=alt.Y('procedure', scale=alt.Scale(zero=False)),
                                                        color=alt.Color('procedure',legend=None))
        procedure_time_chart=procedure_time_chart+ procedure_time_chart.mark_text(dx=15).encode(text="wait_time_90")
        return procedure_time_chart.to_html()

    def slowest_procedures(self,health_authority,year):   
          
        self.filtering(health_authority,year)
        print("Slowest")
        print(self.slowest) 
        procedure_time_chart = alt.Chart(self.slowest,width=500,height=300).mark_bar(size=20,
                                                        point={"filled": False, "fill": "white"}).encode(
                                                        x=alt.X('wait_time_90',axis=alt.Axis(values=np.arange(0,150,10))),
                                                        y=alt.Y('procedure', scale=alt.Scale(zero=False)),
                                                        color=alt.Color('procedure',legend=None))
        procedure_time_chart=procedure_time_chart+ procedure_time_chart.mark_text(dx=15).encode(text="wait_time_90")
        return procedure_time_chart.to_html()

procedures=Procedures()
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
        html.Iframe(
            id="procedure_plot_id",            
            srcDoc=procedures.fastest_procedures(health_authority="Interior",year=[2017,2022]),
            style={'border-width': '0', 'width': '100%', 'height': '400px'}
            )
        ])
    ])
    
])

@app.callback(
    Output("procedure_plot_id",'srcDoc'),   
    [Input("health_authority_buttons","value"),
    Input("year_slider","value"),
    Input("fastest_slowest_treatments_buttons","value")]
)
def update_procedure(health_authority,year,pace):
    print("pace is",pace)
    if(pace=="Slowest"):
        return procedures.slowest_procedures(health_authority,year)
    else:
        return procedures.fastest_procedures(health_authority,year)


if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.4')