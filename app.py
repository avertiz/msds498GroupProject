import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from google.cloud import bigquery
import score

client = bigquery.Client()
app = dash.Dash(__name__)

app.layout = html.Div([
    
    html.H1("LandingSpot", style = {'text-align': 'center'}),
    html.H4("Where will you land?", style = {'text-align': 'center'}),
    html.Br(),html.Br(),html.Br(),

    html.Label(["How many bedrooms do you need?",
        dcc.Dropdown(   id = 'bedrooms',
                        options = [ {'label': '1', 'value': 1},
                                    {'label': '2', 'value': 2},
                                    {'label': '3', 'value': 3},
                                    {'label': '4', 'value': 4}],
                        style = {'width': '23%'}
        )
    ]),

    html.Br(),
    
    dcc.Loading(id = 'results_table_load', 
                type = 'circle',
                children = [
                    html.Div([html.H4(id = 'results_table_header'), dash_table.DataTable(id='results_table')], 
                             style = {'width': '15%'})
                            ]
    ),

    html.Br(),html.Br(),html.Br(),
    
    html.Footer("Sources:")

])

@app.callback(
    [Output(component_id='results_table_header', component_property='children'),
     Output(component_id='results_table', component_property='data'),
     Output(component_id='results_table', component_property='columns'),
     Output(component_id='results_table', component_property='style_table')],
    [Input(component_id='bedrooms', component_property='value')]
)
def show_results_table(bedrooms_input):
    if bedrooms_input is None:
        raise PreventUpdate    
    df = score.output_table(bedrooms = bedrooms_input, client = client)
    cols = [{"name": 'City', "id": 'FormattedName'},
            {"name": 'Score', "id": 'Score'}]
    style_table = {'overflowX': 'scroll'}
    header = "Looks like you're landing in {}!".format(df.iloc[0]['FormattedName'])
    return(header, df.to_dict('records'), cols, style_table)

if __name__ == '__main__':
    app.run_server(debug = True)