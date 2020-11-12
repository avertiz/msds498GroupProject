from meteostat import Stations, Daily
from datetime import datetime

# Get closest weather station to Vancouver, BC
stations = Stations(lat = 49.2497, lon = -123.1193)
station = stations.fetch(1)

# Get daily data for 2018 at the selected weather station
data = Daily(station, start = datetime(2018, 1, 1), end = datetime(2018, 12, 31))
data = data.fetch()

# Plot line chart including average, minimum and maximum temperature
print(data.head(10))

data = Daily(['10637'], start = datetime(2018, 1, 1), end = datetime(2018, 12, 31))
data = data.normalize().aggregate(freq = '1Q').fetch()
data.head(10)

def main():
    print("To be constructed")
    return None


if __name__ == "__main__":
    main()
