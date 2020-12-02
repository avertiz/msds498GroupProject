# MSDS498GroupProject
This is the code repository for the capstone group project for MSDS 498
The project was built on the Google Cloud Platform, however, much of this coud is platform-agnostic.

## Here is an overview of what each file accomplished
#### requirements.txt
  * Packages needed for this project
#### Makefile
  * Basic scoffolding for environment setup and package installation
#### test.py
  * script for testing
#### etl.py
  * This script scrapes cragslist for a given site (city)
  * Things needed:
      * A Google BigQuery table with columns "id", "repost_of", "name", "url",
                         "create_date",
                         "last_updated",
                         "price",
                         "has_image",
                         "latitude",
                         "longitude",
                         "site",
                         "bedrooms",
                         "square_feet"
      * A site to scrape, a category, and possibly an area. For example, site = 'chicago', category = 'apa', and area = 'chc' would scrape https://chicago.craigslist.org/d/apartments-housing-for-rent/search/chc/apa
#### weather.py
  * Wei can you help me here???
#### score.py
  * This gathers all data from various sources and scores how well each city does relative to the other cities
  * It is what ultimately generates the recommendation of city to land in
#### plots.py
  * Plots that the are used by the app
#### app.py
  * The script that generated the web app.
  * This is run on the Dash framework
#### app.yaml
  * basic yaml file that Google App Engine needs to deploy the app
  
#### Here are the cloud services that were used to create this app:
  * Google BigQuery
  * Google Cloud Functions
  * Google Scheduler
  * Google App Engine
 
