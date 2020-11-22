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
    rentals['rental_score'] = rentals['price'] / rentals['square_feet']  * rentals['bedrooms']
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

###### Score Demographics ######

# diversity
def get_diversity(client):
    query = """SELECT c.city_id, d.Diversity____ as diversity
               FROM `msds-498-group-project.landing_spot.demographics` d
               JOIN `msds-498-group-project.landing_spot.cities` c
               ON d.Cities = c.city
            """
    results = client.query(query).to_dataframe()
    return(results)

def score_diversity(client, preference):
    diversity_data = get_diversity(client = client)
    if preference == 'Higher':
        return(diversity_data)
    elif preference == 'Lower':
        diversity_data['diversity'] = -diversity_data['diversity']
        return(diversity_data)

# education
def get_education(client):
    query = """SELECT c.city_id, d.Education__Bachelor_s_degree_or_higher__ as education
               FROM `msds-498-group-project.landing_spot.demographics` d
               JOIN `msds-498-group-project.landing_spot.cities` c
               ON d.Cities = c.city
            """
    results = client.query(query).to_dataframe()
    return(results)

def score_education(client, preference):
    education_data = get_education(client = client)
    if preference == 'Higher':
        return(education_data)
    elif preference == 'Lower':
        education_data['education'] = -education_data['education']
        return(education_data)

# commute
def get_commute(client, preference):
    if preference == 'Driving':
        query = """SELECT c.city_id, d.Commuting_To_Work__Car__truck__or_van___drove_alone__ as commute
                   FROM `msds-498-group-project.landing_spot.demographics` d
                   JOIN `msds-498-group-project.landing_spot.cities` c
                   ON d.Cities = c.city
                """
        results = client.query(query).to_dataframe()
        return(results)
    elif preference == 'Public Transportation':
        query = """SELECT c.city_id, d.Commuting_To_Work__Public_transportation__excluding_taxicab___ as commute
                   FROM `msds-498-group-project.landing_spot.demographics` d
                   JOIN `msds-498-group-project.landing_spot.cities` c
                   ON d.Cities = c.city
                """
        results = client.query(query).to_dataframe()
        return(results)
    elif preference == 'Walking':
        query = """SELECT c.city_id, d.Commuting_To_Work__Walked__ as commute
                   FROM `msds-498-group-project.landing_spot.demographics` d
                   JOIN `msds-498-group-project.landing_spot.cities` c
                   ON d.Cities = c.city
                """
        results = client.query(query).to_dataframe()
        return(results)
    elif preference == 'Other':
        query = """SELECT c.city_id, d.Commuting_To_Work__Other_means__ as commute
                   FROM `msds-498-group-project.landing_spot.demographics` d
                   JOIN `msds-498-group-project.landing_spot.cities` c
                   ON d.Cities = c.city
                """
        results = client.query(query).to_dataframe()
        return(results)    

def score_commute(client, preference):
    commute_data = get_commute(client = client, preference = preference)
    return(commute_data)

###### Rank Everything ######

def get_city_names(client):
    query = "SELECT city_id, FormattedName FROM `msds-498-group-project.landing_spot.cities`"
    results = client.query(query).to_dataframe()
    return(results)

def normalize_scores(df):
    cols = df.columns
    normalized_scores = pd.DataFrame(columns = cols)
    for col in cols:
        if col not in ['city_id', 'FormattedName']:
            min_ = df[col].min()
            max_ = df[col].max()
            normalized_scores[col] = (df[col] - min_) / (max_ - min_) # (x_i−min(x)) / (max(x)−min(x))
        else:
            normalized_scores[col] = df[col]
    return(normalized_scores)

def add_weights(df, first, second, third):
    col_dict = {'Commute':'commute',
                'Weather':'weather',
                'Diversity':'diversity',
                'Education':'education'}
    df[col_dict[first]] = df[col_dict[first]] * 3
    df[col_dict[second]] = df[col_dict[second]] * 2
    df[col_dict[third]] = df[col_dict[third]] * 1.25
    return(df)

def sum_rows(df):
    df['Score'] = df.drop(['city_id', 'FormattedName'], axis=1).sum(axis=1).round(3)
    return(df)

def output_table(client, bedrooms, div_preference, ed_preference, comm_preference, first, second, third):    
    names = get_city_names(client = client)
    rentals = score_rentals(bedrooms = bedrooms, client = client)
    income = score_income(client = client)
    diversity = score_diversity(client = client, preference = div_preference)
    education = score_education(client = client, preference = ed_preference)
    commute = score_commute(client = client, preference = comm_preference)
    data_frames = [names, rentals, income, diversity, education, commute]
    results = reduce(lambda left,right: pd.merge(left,right,on=['city_id'], how='outer'), data_frames)
    results = normalize_scores(df = results)
    results = add_weights(df = results, first = first, second = second, third = third)
    results = sum_rows(df = results)
    results.sort_values(by=['Score'], inplace=True, ascending=False)
    return(results[['FormattedName', 'Score']])