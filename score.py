from google.cloud import bigquery
from functools import reduce
import pandas as pd

client = bigquery.Client()

###### Score Rentals ######

def get_rentals(bedrooms, client):
    query = """SELECT id, site, price, bedrooms, square_feet
               FROM `msds-498-group-project.landing_spot.craigslist`
               WHERE 1=1
               AND price > 100
               AND bedrooms is not null
               AND square_feet is not null
               AND bedrooms = {}
            """.format(bedrooms)
    results = client.query(query).to_dataframe()
    return(results)

def score_rentals(bedrooms, client):
    query = "SELECT city_id, city FROM `msds-498-group-project.landing_spot.cities`"
    cities = client.query(query).to_dataframe()
    rentals = get_rentals(bedrooms = bedrooms, client = client)
    rentals['rental_score'] = rentals['square_feet'] / rentals['price'] * rentals['bedrooms']
    scores = rentals[['site', 'rental_score']].groupby('site').mean().reset_index()
    scores = pd.merge(scores, cities, left_on = 'site', right_on = 'city')
    scores = scores[['city_id', 'rental_score']]
    return(scores)

###### Score Income ######

def get_income(client):
    query = """
    SELECT z.city_id, i.bracket, SUM(i.agi) / t.total as pct
    FROM `msds-498-group-project.landing_spot.income` i
    JOIN `msds-498-group-project.landing_spot.zip_codes` z
        ON i.zip = z.zip
    LEFT JOIN ( SELECT z.city_id, SUM(i.agi) as total
                FROM `msds-498-group-project.landing_spot.income` i
                JOIN `msds-498-group-project.landing_spot.zip_codes` z
                    ON i.zip = z.zip 
                GROUP BY z.city_id) t
        ON t.city_id = z.city_id
    WHERE 1=1
    GROUP BY z.city_id, i.bracket, t.total
            """
    results = client.query(query).to_dataframe()
    return(results)

def score_income(client):
    bracket_dict = {'$1 under $25,000': 1,
                    '$25,000 under $50,000': 2,
                    '$50,000 under $75,000': 3,
                    '$75,000 under $100,000': 4,
                    '$100,000 under $200,000': 5,
                    '$200,000 or more': 6}
    income_data = get_income(client)
    income_data['income_score'] = 0
    for key in bracket_dict.keys():
        income_data.loc[income_data['bracket'] == key, 'income_score'] = income_data.loc[income_data['bracket'] == key, 'pct'] * bracket_dict[key]
    scores = income_data[['city_id', 'income_score']].groupby('city_id').sum().reset_index()
    return(scores)

###### Rank Everything ######
def get_city_names(client):
    query = "SELECT city_id, FormattedName FROM `msds-498-group-project.landing_spot.cities`"
    results = client.query(query).to_dataframe()
    return(results)

def get_z_scores(df):
    cols = df.columns
    z_scores = pd.DataFrame(columns = cols)
    for col in cols:
        if col not in ['city_id', 'FormattedName']:
            z_scores[col] = (df[col] - df[col].mean())/df[col].std(ddof=0)
        else:
            z_scores[col] = df[col]
    return(z_scores)

def sum_rows(df):
    df['Score'] = df.drop(['city_id', 'FormattedName'], axis=1).sum(axis=1).round(3)
    return(df)

def output_table(bedrooms, client):    
    names = get_city_names(client = client)
    rentals = score_rentals(bedrooms = bedrooms, client = client)
    income = score_income(client = client)
    data_frames = [names, rentals, income]
    results = reduce(lambda left,right: pd.merge(left,right,on=['city_id'], how='outer'), data_frames)
    results = get_z_scores(df = results)
    results = sum_rows(df = results)
    results.sort_values(by=['Score'], inplace=True, ascending=False)
    return(results[['FormattedName', 'Score']])