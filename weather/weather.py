import pandas as pd
from google.cloud import bigquery
from core import get_raw_data, aggregate_data_by_season_year, aggregate_data_by_season, add_city

#client = bigquery.Client()
client = bigquery.Client.from_service_account_json('debug-9527.json')
project_id = 'msds-498-group-project'

sql = """
SELECT
  city,
  station
FROM
  `landing_spot.cities`
  """


def proc_city(city, station_id):
    df = get_raw_data(station_id)
    df = aggregate_data_by_season_year(df)
    df = aggregate_data_by_season(df)
    return add_city(city, df)


def proc_cities(cities):
    df = pd.DataFrame()
    for row in cities:
        _df = proc_city(row.city, row.station)
        df = df.append(_df, ignore_index=True)
    return df


def main():
    cities = client.query(sql, project=project_id)
    data = proc_cities(cities)
    data.to_csv('weather.csv', index=False)


if __name__ == "__main__":
    main()
