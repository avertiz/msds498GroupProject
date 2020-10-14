import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from craigslist import CraigslistHousing
from google.cloud import bigquery

# Parser function
def bs(content):
    return BeautifulSoup(content, 'html.parser')

# Logging function.....not sure if necessary
def requests_get(*args, **kwargs):
    """
    Retries if a RequestException is raised (could be a connection error or
    a timeout).
    """
    logger = kwargs.pop('logger', None)
    try:
        return requests.get(*args, **kwargs)
    except RequestException as exc:
        if logger:
            logger.warning('Request failed (%s). Retrying ...', exc)
        return requests.get(*args, **kwargs)

# Bedrooms and square feet
def extra_features(site, area, category, sort_by, limit):
    sorts = {'newest' : 'date',
            'price_asc' : 'priceasc',
            'price_desc' : 'pricedsc'}
    # Initiate lists to store features
    ids = []
    br = []
    ft2 = []
    # Iterate through pages
    for page in range(int(limit/120)):
        # Create URL
        if page == 0:
            url = 'https://' + site + '.craigslist.org/search/' + \
            area + '/' + category + '?sort=' + sorts[sort_by]
        else:
            url = 'https://' + site + '.craigslist.org/search/' + \
            area + '/' + category + '?s=' + str(page*120) + '&sort=' + sorts[sort_by]        
        # Get Response
        response = requests_get(url)
        soup = bs(response.content)
        # Extract Features
        for item in soup.find_all(attrs={"data-id": True}):
            ids.append(item['data-id'])
        overall_count = 0
        br_count = 0
        ft2_count = 0
        for desc in soup.find_all('span', {'class' : 'result-meta'}):
            overall_count += 1
            for h in desc.find_all('span', {'class' : 'housing'}):               
                text = h.get_text().split()
                for string in text:
                    if 'br' in string:
                        br_count += 1
                        br.append(string[0])
                    elif 'ft2' in string:
                        ft2_count += 1
                        ft2.append(string[:-3])
            if overall_count != br_count:
                br.append(None)
                br_count = overall_count
            if overall_count != ft2_count:
                ft2.append(None)
                ft2_count = overall_count
    dict_ = {'id' : ids, 'bedrooms' : br, 'square_feet' : ft2}
    df = pd.DataFrame(dict_)
    return(df)

# Normal craigslist features
def main_features(site, area, category, sort_by, limit, geotagged):
    # Use Craigslist package
    cl = CraigslistHousing(site= site, area= area, category= category)
    results = cl.get_results(sort_by= sort_by, geotagged= geotagged, limit = limit)
    df = {  'id': [],
            'repost_of': [],
            'name': [],
            'url': [],
            'create_date': [],
            'last_updated': [],
            'price': [],
            'where_': [],
            'has_image': [],
            'latitude': [],
            'longitude':[],
            'site': []      }
    for result in results:
        df['id'].append(result['id'])
        df['repost_of'].append(result['repost_of'])
        df['name'].append(result['name'])
        df['url'].append(result['url'])
        df['create_date'].append(result['datetime'])
        df['last_updated'].append(result['last_updated'])
        df['price'].append(result['price'][1:])
        df['where_'].append(result['where'])    
        df['has_image'].append(result['has_image'])
        if result['geotag'] == None:
                df['latitude'].append(0.0)
                df['longitude'].append(0.0)
        else:
            df['latitude'].append(result['geotag'][0])
            df['longitude'].append(result['geotag'][1])
        df['site'].append(site)        
    df = pd.DataFrame(df)
    df['price'] = pd.to_numeric(df['price'].str.replace(',', ''))
    return(df)

def combine_results(site, area, category, sort_by, limit, geotagged):
    main_feats = main_features(site = site, area = area, category = category, sort_by = sort_by, limit = limit, geotagged = geotagged)
    extra_feats = extra_features(site = site, area = area, category = category, sort_by = sort_by, limit = limit)    
    all_feats = pd.merge(main_feats, extra_feats, left_on='id', right_on='id')
    return(all_feats)


def update_cragslist(client, data, table_id):
    # Get current ids
    query = "SELECT id FROM " + table_id
    results = client.query(query)     
    ids = []
    for row in results:
        ids.append(int(row['id']))
    
    # insert new rows
    rows_to_insert = []
    for index, row in data.iterrows():
        if int(row['id']) not in ids:
             row_dict = {u"id": row['id'],
                         u"repost_of": row['repost_of'],
                         u"name": row['name'],
                         u"url": row['url'],
                         u"create_date": row['create_date'],
                         u"last_updated": row['last_updated'],
                         u"price": row['price'],
                         u"has_image": row['has_image'],
                         u"latitude": row['latitude'],
                         u"longitude": row['longitude'],
                         u"site": row['site'],
                         u"bedrooms": row['bedrooms'],
                         u"square_feet": row['square_feet']}
             rows_to_insert.append(row_dict)

    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors != []:
        print("Encountered errors while inserting rows: {}".format(errors))