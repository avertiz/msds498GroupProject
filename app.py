import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from google.cloud import bigquery
import score

external_stylesheets = ['https://codepen.io/chriddyp/pen/dZVMbK.css']

dropdown_options = [ {'label': 'Commute', 'value': 'Commute'},
                                        {'label': 'Weather', 'value': 'Weather'},
                                        {'label': 'Diversity', 'value': 'Diversity'},
                                        {'label': 'Education', 'value': 'Education'}]

dropdown_style = {'width': '50%', 'display': 'inline-block', 'vertical-align': 'middle', 'padding': '5px'}

client = bigquery.Client()

click_count = 0

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "LandingSpot"
app.layout = html.Div([

    html.H1("LandingSpot", style = {'text-align': 'center'}),
    html.H5("Where will you land?", style = {'text-align': 'center'}),
    html.Br(),  

    # Preferences  
    html.Div([
        
        html.H6("Tell me what you need...", style = {'text-align': 'left', 'padding': '5px'}),

        # Bedrooms Button
        html.Div([
            html.Label(["Bedrooms:",
                dcc.Dropdown(   id = 'bedrooms',
                                options = [ {'label': '1', 'value': 1},
                                            {'label': '2', 'value': 2},
                                            {'label': '3', 'value': 3},
                                            {'label': '4', 'value': 4}],
                                style = {'width': '35%', 'display': 'inline-block', 'vertical-align': 'middle', 'padding': '5px'}
                )
            ])
        ], style = {'width': '100%', 'padding': '5px'}),
        
        # Commute Button
        html.Div([
            html.Label(["How to do you want to get to work?",
                dcc.Dropdown(   id = 'commute',
                                options = [ {'label': 'Driving', 'value': 'Driving'},
                                            {'label': 'Public Transportation', 'value': 'Public Transportation'},
                                            {'label': 'Walking', 'value': 'Walking'},                                        
                                            {'label': 'Other', 'value': 'Other'}],
                                style = dropdown_style
                )
            ])
        ], style = {'width': '100%', 'padding': '5px'}),

        # Summer weather Button
        html.Div([
            html.Label(["Do you prefer a Warmer or Cooler Summer?",
                dcc.Dropdown(   id = 'summer',
                                options = [ {'label': 'Warmer', 'value': 'Warmer'},
                                            {'label': 'Cooler', 'value': 'Cooler'}],
                                style = dropdown_style
                )
            ])
        ], style = {'width': '100%', 'padding': '5px'}),

        # Winter weather
        html.Div([
            html.Label(["Do you prefer a Warmer or Cooler Winter?",
                dcc.Dropdown(   id = 'winter',
                                options = [ {'label': 'Warmer', 'value': 'Warmer'},
                                            {'label': 'Cooler', 'value': 'Cooler'}],
                                style = dropdown_style
                )
            ])
        ], style = {'width': '100%', 'padding': '5px'}),

        # Diversity Button
        html.Div([
            html.Label(["Diversity level of the city population:",
                dcc.Dropdown(   id = 'diversity',
                                options = [ {'label': 'Higher', 'value': 'Higher'},
                                            {'label': 'Lower', 'value': 'Lower'}],
                                style = dropdown_style
                )
            ])
        ], style = {'width': '100%', 'padding': '5px'}),

        # Education Button
        html.Div([
            html.Label(["Education level of the city population:",
                dcc.Dropdown(   id = 'education',
                                options = [ {'label': 'Higher', 'value': 'Higher'},
                                            {'label': 'Lower', 'value': 'Lower'}],
                                style = dropdown_style
                )
            ])
        ], style = {'width': '100%', 'padding': '5px'})

    ], style = {'width': '30%', 'border' : '2px solid DarkSlateGray', 'display': 'inline-block'}),

    # Ranking
    html.Div([
        html.H6("Tell me what you care about the most...", style = {'text-align': 'left', 'padding': '5px'}),

        html.Label(["1st",            
            dcc.Dropdown(   id = '1st',
                            options = dropdown_options,
                            style = dropdown_style
            )
        ], style = {'padding': '5px'}),

        html.Label(["2nd",            
            dcc.Dropdown(   id = '2nd',
                            options = dropdown_options,
                            style = dropdown_style
            )
        ], style = {'padding': '5px'}),

        html.Label(["3rd",            
            dcc.Dropdown(   id = '3rd',
                            options = dropdown_options,
                            style = dropdown_style
            )
        ], style = {'padding': '5px'})

    ], style = {'width': '30%', 'border' : '2px DodgerBlue solid', 'display': 'inline-block'}),

    html.Div([
    dcc.Loading(id = 'results_table_load', 
                type = 'circle',
                children = [
                    html.Div([html.H4(id = 'results_table_header'), dash_table.DataTable(id='results_table')], 
                             style = {'width': '50%', 'horizontalAlign': 'top'})
                            ]
    )], style={'width': '30%', 'display': 'inline-block', 'float' : 'right', 'horizontalAlign': 'top'}),

    html.Div([
        html.Button('Submit', 
                id='submit-val', 
                n_clicks = 0)
    ], style={'horizontalAlign': 'middle', 'display':'flex', 'padding': '5px'}),
    html.Br(),

    html.P("""
    *Your LandingSpot was chosen by aggregating data from various sources and giving them weight based on your preferences. 
    A city can score between 0 and 13.25.
    There is also other data being looked at in the background, such as crime data, that may impact a city's score.
    """),

    html.Br(),html.Br(),html.Br(),

    html.Footer("Sources:")

])

@app.callback(
    [Output(component_id='results_table_header', component_property='children'),
     Output(component_id='results_table', component_property='data'),
     Output(component_id='results_table', component_property='columns')],
    [Input(component_id = 'submit-val', component_property = 'n_clicks')],
    [State(component_id='bedrooms', component_property='value'),
     State(component_id = 'commute', component_property = 'value'),
     State(component_id = 'summer', component_property = 'value'),
     State(component_id = 'winter', component_property = 'value'),
     State(component_id = 'diversity', component_property = 'value'),
     State(component_id = 'education', component_property = 'value'),
     State(component_id = '1st', component_property = 'value'),
     State(component_id = '2nd', component_property = 'value'),
     State(component_id = '3rd', component_property = 'value')]
)
def show_results_table(n_clicks, beds, commute, summer, winter, diversity, education, first, second, third):
    if n_clicks == 0:
        raise PreventUpdate
    elif beds is None or commute is None or summer is None or winter is None or diversity is None or education is None or first is None or second is None or third is None:
        header = "Please fill out the entire form"
        df = pd.DataFrame()
        cols = []
        return(header, df.to_dict('records'), cols)
    else:
        df = score.output_table(client = client, 
                                bedrooms = beds, 
                                div_preference = diversity,
                                ed_preference = education, 
                                comm_preference = commute, 
                                summer_pref = summer,
                                winter_pref = winter,
                                first = first, 
                                second = second,
                                third = third)
        cols = [{"name": 'City', "id": 'FormattedName'},
                {"name": 'Score', "id": 'Score'}]
        header = "Looks like you're landing in {}!".format(df.iloc[0]['FormattedName'])
        return(header, df.to_dict('records'), cols)

if __name__ == '__main__':
    app.run_server(debug=True)