from meteostat import Stations, Daily
import pandas as pd
from datetime import datetime

look_back_yrs = 10

end_yr = 2019
start_yr = end_yr - look_back_yrs
start = datetime(start_yr, 12, 1)
end = datetime(end_yr, 11, 30)

season_by_start_month = {12: 'Winter', 3: 'Spring', 6: 'Summer', 9: 'Fall'}

cols = ['tavg', 'tmin', 'tmax', 'prcp']
cols_we_care = ['time'] + cols + ['station']
aggregations = {
    'time': 'first',
    'tavg': 'mean',
    'tmin': 'min',
    'tmax': 'max',
    'prcp': 'sum',
  }


def get_station(lat, lon, cnt=10):
    return Stations(lat = lat, lon = lon).fetch(cnt) # get closest station to given coordinates


def get_station_id(lat, lon, seq_no=0):
    return get_station(lat, lon).iloc[seq_no, 0]


def get_raw_data(station_id, start=start, end=end):
    data_daily = Daily([station_id], start=start, end=end)
    return data_daily.fetch()


def aggregate_data_by_season_year(df):
  # not sure why the API returned two rows of dummy data as station and time
  df = df.drop(index=['station', 'time'])
  df = df[cols_we_care]
  # 'Q-FEB' means quarter ends in Feb which are how The Meteorological Seasons decided
  return df.groupby(['station', pd.Grouper(key = 'time', freq = 'Q-FEB')]).agg(aggregations)


def aggregate_data_by_season(df):
  df['season'] = df.time.apply(lambda dt: f"{season_by_start_month[dt.month]}")
  df.drop(columns='time', inplace=True)
  df.reset_index(drop=True, inplace=True)
  return df.groupby('season').mean().reset_index()


def add_city(city, df):
  df.insert(0, 'city', city)
  return df


def main():
    ''


if __name__ == "__main__":
    main()
