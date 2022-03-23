## Analysis of Chicago Neighborhoods by Amenities 
This project creates a map that shows the Shannon Index (see bottom) by neighborhood in Chicago and shows locations of liraries, pharmacies, murals and Starbucks on the map. 

### How to run
1. Run source install.sh to create a virtual environment and install packages
2. Run python app.py in the command line
3. Click "Open in Browser" OR copy and paste the link to your preferred web browser to see the map. Please ignore the warning message if you see it
"WARNING: This is a development server. Do not use it in a production deployment." 
4. Type Ctrl + C to kill the dash output
5. Run deactivate to exit out of virtual environment

### Front End
We used Dash to create a map of Chicago and have toggles for the data points we're analyzing - libraries, pharmacies, murals and Starbucks. The map also displays the Shannon Index for each neighborhood based.

### Backend
Our main data source is the Chicago Data Portal from where we accessed data on libraries, pharmacies and murals via an API. We collected data on Starbucks from Mapquest via an API. WE got the Domographic and Socioeconomic data via CSV from the the Chicago Metropolitan Agency and Chicago Open Data Portal and Shapefile data from TK via TK.   After cleaning up the data from these sources into dataframes, we input them to dash which creates the map. 

### Files names and description
- README.md: this file
- install.sh: shell script for creating a virtual environment and installing libraries
- app.py: the main file that imports data from the other files and runs the dash output
- cdp.py: python file that gets data from Chicago Open Data Portal on Libraries, Pharmacies and Murals
- demographics.py: python file that imports demographic and socioeconomic data from csv
- map_util.py: helper functions for rendering our community shape files for the choropleth
- starbucks.py: python file that gets data on Starbucks 
- requirements.txt: text file with all required libraries to run this project 

#### Sources 
1. Shannon Index source:
Graells-Garrido, E., Serra-Burriel, F., Rowe, F., Cucchietti, F. M., & Reyes, P. (2021). A city of cities: Measuring how 15-minutes urban accessibility shapes human mobility in Barcelona. PloS one, 16(5), e0250080.https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0250080
2. Population and racial data source: https://datahub.cmap.illinois.gov/dataset/community-data-snapshots-raw-data
(2020 Census Supplement: Chicago Community Area csv)
3. Income source: https://data.cityofchicago.org/Health-Human-Services/Per-Capita-Income/r6ad-wvtk
