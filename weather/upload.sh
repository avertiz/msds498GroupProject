gsutil cp ./weather.csv "gs://weather_msds-498-group-project/weather.csv"

bq rm -f -t 'msds-498-group-project:landing_spot.weather'

bq load \
--autodetect \
--source_format=CSV \
'msds-498-group-project:landing_spot.weather' \
"gs://weather_msds-498-group-project/weather.csv"
