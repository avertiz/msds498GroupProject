import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
from google.cloud import bigquery
import score

client = bigquery.Client()

df = score.get_z_scores(bedrooms = 2, client = client)

app = dash.Dash(__name__)

app.layout = html.Div([
    
    html.H1("LandingSpot", style = {'text-align': 'center'}),
    html.H4("Where will you land?", style = {'text-align': 'center'}),

    html.Label(["How many bedrooms do you need?",
        dcc.Dropdown(   id = 'bedrooms',
                        options = [ {'label': '1', 'value': 1},
                                    {'label': '2', 'value': 2},
                                    {'label': '3', 'value': 3},
                                    {'label': '4', 'value': 4}],
                        style = {'width': '40%'}
        )
    ]),

    
    dash_table.DataTable(id='results',
                            columns=[{"name": i, "id": i} for i in df.columns],
                            data = df.to_dict('records'))


])

# @app.callback(
#     Output(component_id='results', component_property='data'),
#     [Input(component_id='bedrooms', component_property='value')]
# )
# def show_results_table(bedrooms_input):
#     if bedrooms_input is None:
#         raise PreventUpdate
#     df = score.get_z_scores(bedrooms = bedrooms_input, client = client)
#     return(df.to_dict())

if __name__ == '__main__':
    app.run_server(debug = True)