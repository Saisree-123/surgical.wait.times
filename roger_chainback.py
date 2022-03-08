import pandas as pd
import numpy as np
import altair as alt
import dash
from dash import  dcc, html, Input, Output
import dash_bootstrap_components as dbc

class Waitcomplete:

    def __init__(self):
        print("I'm trapped in init!")
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
        self.qdata = qdata.replace('<5', 3)

        # drop rows with NAs
        clean = qdata.dropna()
        count = qdata.iloc[:,0:7]

        # drop "All" data
        main = clean.query('procedure != "All Procedures" & hospital != "All Facilities" & health_authority != "All Health Authorities"')
        self.count = count.query('procedure != "All Procedures" & hospital != "All Facilities" & health_authority != "All Health Authorities"')
        all = clean.query('procedure == "All Procedures" & hospital == "All Facilities" & health_authority == "All Health Authorities"')
        
    #-------------------

    # data grouped by hospital for selected health authority and date range
    def data_by_hosp(self, year, hospname):
        

        #filter and arrange data for plotting 
        #print(self.count.health_authority.unique())
        hosp_data = self.count.groupby(['hospital', 'year', 'quarter']).sum().reset_index()
        hosp_data = hosp_data[(hosp_data['year']>=year[0]) & (hosp_data['year']<=year[1])]
        print("Printing hospital data")
        print(hosp_data.head())
        hosp_data_melted = hosp_data.melt(id_vars=['hospital','year','quarter'])
        
        print("lala",hosp_data_melted)  ############################################################### Empty dataframe here

        hosp_data_melted['time'] = hosp_data_melted['year'].map(str)+hosp_data_melted['quarter']
        print(hosp_data_melted.head())
        hosp_data_melted = hosp_data_melted.drop(columns = ['year','quarter'])

        #create hospital dropdown list
        self.hosp_list = hosp_data_melted.hospital.unique()

        #waiting and completed cases for chosen hospital
        self.one_hospital = hosp_data_melted[hosp_data_melted['hospital'] == hospname]
        print("###################################################################################")
        print(hosp_data_melted.hospital.unique())
        print(hospname)
        print(self.one_hospital.head())

    def wait_complete_plot(self, year, hospname):   
        
        self.data_by_hosp(year, hospname) 
        wc_plot = alt.Chart(self.one_hospital).mark_bar(size=10).encode(
                            x=alt.X('variable', axis=alt.Axis(title=None, labels=False, ticks=False)),
                            y=alt.Y('value', scale=alt.Scale(zero=False), axis=alt.Axis(grid=False)),
                            color=alt.Color('variable'),
                            column = alt.Column('time', header=alt.Header(title=None, labelOrient='bottom', labelAngle=90))
        ).configure_view(stroke='transparent'
        ).properties(width=10
        ).configure_facet(spacing=7
        )       
        return wc_plot.to_html()

waitcomplete = Waitcomplete()

hosp_list = waitcomplete.count.hospital.unique()

# interior_hosp = waitcomplete.count[waitcomplete.count.health_authority.eq('Interior')].hospital.unique() 
# fraser_hosp = waitcomplete.count[waitcomplete.count.health_authority.eq('Fraser')].hospital.unique()
# vanCoastal_hosp = waitcomplete.count[waitcomplete.count.health_authority.eq('Vancouver Coastal')].hospital.unique()
# vanIsland_hosp = waitcomplete.count[waitcomplete.count.health_authority.eq('Vancouver Island')].hospital.unique()
# northern_hosp = waitcomplete.count[waitcomplete.count.health_authority.eq('Northern')].hospital.unique()
# provincial_hosp = waitcomplete.count[waitcomplete.count.health_authority.eq('Provincial Health Services Authority')].hospital.unique()

# all_options = {
#     'Interior': interior_hosp,
#     'Fraser': fraser_hosp,
#     'Vancouver Coastal': vanCoastal_hosp,
#     'Vancouver Island': vanIsland_hosp,
#     'Northern': northern_hosp,
#     'Provincial Health Services': provincial_hosp
# }

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout=app.layout = dbc.Container([   
    html.Div([
    html.H1('SURGICAL WAIT TIMES',style={'color':'blue'}),
    html.Div([
        dcc.RangeSlider(
            id="year_slider",min=2009, max=2022,
            step=1, marks={i: f'{i}' for i in range(2009, 2023)},
            value=[2017, 2022])]),        
    html.Div([
        dcc.RadioItems(
            id="health_authority_buttons",
            options=[
                {"label": "Interior", "value": "interior"},
                {"label": "Fraser", "value": "fraser"},
                {"label": "Vancouver Coastal", "value": "vanCoastal"},
                {"label": "Vancouver Island", "value": "vanIsland"},
                {"label": "Northern", "value": "northern"},
                {"label": "Provincial", "value": "provincial"},
            ],    
            value='Interior')]),
    html.Div([
            html.Label("hosp:", style={'fontSize': 30, 'textAlign': 'center'}),
            dcc.Dropdown(
                id='hospital_dropdown',
                options=[],
                value=[],
                clearable=False
            )
        ]),       
    html.Div([
        html.Iframe(
            id="hosp_wait_comp_plot",            
            srcDoc=waitcomplete.wait_complete_plot(hospname="100 Mile District General Hospital", year=[2017,2022]),
            style={'border-width': '0', 'width': '500px', 'height': '350px','display': 'inline-block'})])
        ])
    ])


@app.callback(
        [Output('hospital_dropdown', 'options'),
        Output('hospital_dropdown', 'value')],
        Input('health_authority_buttons', 'value'),
    )
def set_county_options(health_athority):
    if(health_athority=="Provincial"):
        health_athority="Provincial Health Services Authority"
    dff =waitcomplete.qdata[waitcomplete.qdata.health_authority==health_athority]
    print(dff.columns)
    counties_of_state = [{'label': c, 'value': c} for c in sorted(dff.hospital.unique())]
    values_selected = [counties_of_state[0]]
    print(counties_of_state)
    print(values_selected[0]['label'])
    return counties_of_state, values_selected[0]['label']

@app.callback(
    Output("hosp_wait_comp_plot",'srcDoc'),   
    [
    Input("year_slider","value"),
    Input("hospital_dropdown","value")]
)

def update_wait_complete_plot(year, hospname):
    print(hospname)
    return waitcomplete.wait_complete_plot(year, hospname)

if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.3')