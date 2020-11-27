from google.cloud import bigquery
import pandas as pd
import plotly.graph_objs as go

client = bigquery.Client()

# Income
def income_plot(client):
    query = """
            SELECT z.city_id, i.bracket, SUM(i.agi) / t.total as pct, c.FormattedName
                FROM `msds-498-group-project.landing_spot.income` i
                JOIN `msds-498-group-project.landing_spot.zip_codes` z
                    ON i.zip = z.zip
                LEFT JOIN ( SELECT z.city_id, SUM(i.agi) as total
                            FROM `msds-498-group-project.landing_spot.income` i
                            JOIN `msds-498-group-project.landing_spot.zip_codes` z
                                ON i.zip = z.zip 
                            GROUP BY z.city_id) t
                    ON t.city_id = z.city_id
                JOIN `msds-498-group-project.landing_spot.cities` c
                    ON z.city_id = c.city_id
                WHERE 1=1
                GROUP BY z.city_id, i.bracket, t.total, c.FormattedName
            """

    df = client.query(query).to_dataframe()

    cities = ['Atlanta', 
              'Chicago',
              'Dallas', 
              'Houston',
              'Los Angeles',            
              'Miami',
              'New York',
              'Philadelphia',
              'Phoenix',
              'Seattle',
              'Washington, D.C.']

    percentages1 = []
    for c in cities:
        percentages1.append(df[(df['FormattedName'] == c) & (df['bracket'] == '$1 under $25,000')].pct.item()*100)
    bar1 = go.Bar(
        x=cities, y=percentages1,
        name='$1 under $25,000'
    )

    percentages2 = []
    for c in cities:
        percentages2.append(df[(df['FormattedName'] == c) & (df['bracket'] == '$25,000 under $50,000')].pct.item()*100)
    bar2 = go.Bar(
        x=cities, y=percentages2,
        name='$25,000 under $50,000'
    )

    percentages3 = []
    for c in cities:
        percentages3.append(df[(df['FormattedName'] == c) & (df['bracket'] == '$50,000 under $75,000')].pct.item()*100)
    bar3 = go.Bar(
        x=cities, y=percentages3,
        name='$50,000 under $75,000'
    )

    percentages4 = []
    for c in cities:
        percentages4.append(df[(df['FormattedName'] == c) & (df['bracket'] == '$75,000 under $100,000')].pct.item()*100)
    bar4 = go.Bar(
        x=cities, y=percentages4,
        name='$75,000 under $100,000'
    )

    percentages5 = []
    for c in cities:
        percentages5.append(df[(df['FormattedName'] == c) & (df['bracket'] == '$100,000 under $200,000')].pct.item()*100)
    bar5 = go.Bar(
        x=cities, y=percentages5,
        name='$100,000 under $200,000'
    )

    percentages6 = []
    for c in cities:
        percentages6.append(df[(df['FormattedName'] == c) & (df['bracket'] == '$200,000 or more')].pct.item()*100)
    bar6 = go.Bar(
        x=cities, y=percentages6,
        name='$200,000 or more'
    )

    data = [bar1, bar2, bar3, bar4, bar5, bar6]
    layout = go.Layout(
        barmode='stack',
        xaxis= {'tickvals': cities},
        title = "Adjusted Gross Income Brackets by City",
        yaxis = {'title':'Percentage of Population'}
    )
    fig = go.Figure(data=data, layout=layout)
    return(fig)