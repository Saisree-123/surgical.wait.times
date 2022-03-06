
import dash
from dash import  dcc, html, Input, Output
import dash_bootstrap_components as dbc
import altair as alt
import json
import pandas as pd


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

###########################################################################
# data loading
olddata = pd.read_excel('data/2009_2021-quarterly-surgical_wait_times.xlsx')
newdata = pd.read_excel('data/2021_2022-quarterly-surgical_wait_times-q3-interim.xlsx')
qdata = pd.concat([olddata, newdata])

# rename columns
qdata.columns = qdata.columns.str.lower()
qdata.rename(columns = {'fiscal_year': 'year',
                        'hospital_name': 'hospital',
                        'procedure_group': 'procedure',
                        'completed_50th_percentile': 'wait_time_50',
                        'completed_90th_percentile': 'wait_time_90'}, inplace = True)

qdata['year'] = qdata['year'].str.replace('(/).*', "")

#convert <5 string to median value of 3
qdata = qdata.replace('<5', 3)
qdata['year'] = pd.to_numeric(qdata['year'])

# create count data as we do not have to remove NAs for that 
count = qdata.iloc[:,0:7]

def authority_bar(authority = 'interior', count = count):    
    if authority == "interior":
        authority = "Interior"
    elif authority == "fraser":
        authority = "Fraser"
    elif authority == "vanCoastal":
        authority = "Vancouver Coastal"
    elif authority == "vanIsland":
        authority = "Vancouver Island"
    elif authority == "northern":
        authority = "Northern"
    elif authority == "provincial":
        authority = "Provincial Health Services Authority"

    year_from = 2017
    year_to = 2022
    count = count.query('procedure != "All Procedures" & hospital != "All Facilities" & health_authority != "All Health Authorities"')
    new_authority = count.groupby(['health_authority', 'year', 'quarter']).sum().reset_index()
    authority_melted = new_authority.melt(id_vars=['health_authority','year', 'quarter'])
    authority_melted['time'] = authority_melted['year'].map(str)+authority_melted['quarter']
    subset_authority = authority_melted[(authority_melted['health_authority'] == authority) & (authority_melted['year']>=year_from) & (authority_melted['year'] <= year_to)]


    plot1 = alt.Chart(subset_authority, height = 200).mark_bar(size=10).encode(
                                x=alt.X('variable', axis=alt.Axis(title=None, labels=False, ticks=False)),
                                y=alt.Y('value', axis=alt.Axis(grid=False)),
                                color=alt.Color('variable'),
                                column = alt.Column('time', header=alt.Header(title=None, labelOrient='bottom', labelAngle=90))
    ).configure_view(stroke='transparent'
    ).properties(width=10
    ).configure_facet(spacing=7
    )
    return plot1.to_html()


plot_map_object = html.Div([html.Iframe(
    id = 'auth_bar',
    srcDoc=authority_bar(authority = 'interior'), 
    style={'border-width': '0', 'width': '500px', 'height': '350px','display': 'inline-block'})])

plot_map_object_dummy = html.Div([html.Iframe(
    id = 'auth_bar_dummy',
    srcDoc=authority_bar(authority = 'interior'), 
    style={'border-width': '0', 'width': '500px', 'height': '350px', 'display': 'inline-block'})])

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
            value='interior')])        
    ]),

    html.Div(children = [plot_map_object,
    
        plot_map_object_dummy], className="row")
])


#############################################
# call back for authority bar plot
@app.callback(
    Output('auth_bar', 'srcDoc'),
    Input('health_authority_button', 'value'))
def update_authority_bar(health_authority_button):
    return authority_bar(health_authority_button)


if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.4')
