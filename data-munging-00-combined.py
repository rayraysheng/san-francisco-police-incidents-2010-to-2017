
# coding: utf-8

# Import dependencies
print('Importing libraries')
import pandas as pd
import zipfile
import json
import requests as req
from datetime import datetime
print('Done importing')

# Load dataframe from csv compressed in the zip file
print('Loading source file: %s' % datetime.now())

data_zip_path = 'data/Police_Incidents.zip'
zf = zipfile.ZipFile(data_zip_path) # having Police_Incidents.csv zipped file.
police_incidents_df = pd.read_csv(zf.open('Police_Incidents.csv'))
print('File loaded: %s' % datetime.now())

# Function  get_ymd helps us to get year, month, and day
def get_ymd(data):
    
    months = []
    years = []
    days = []
    
    # For each row in the column Date
    for r_date in data['Date']:
         
        full_date = datetime.strptime(r_date, "%m/%d/%Y")
        months.append(str(full_date.month))
        years.append(str(full_date.year))
        days.append(str(full_date.day))
        
    # Create columns from the list
    data['Year'] = years
    data['Month'] = months
    data['Day_m'] = days

# Call function get_ymd for splitting column DATE in Year, Month and Day_m columns.
print('Converting dates: %s' % datetime.now())
get_ymd(police_incidents_df)   
print('Dates converted: %s' % datetime.now())

# Drop columns Descript, Date, Address and PdId which we will not used for any purpose.
print('Dropping columns: %s' % datetime.now())
police_incidents_df.drop(['Descript', 'Date', 'Address', 'PdId'], axis=1, inplace= True)
print('Columns dropped: %s' % datetime.now())

# Grab DataFrame rows where column years has certain values
print('Truncating by year: %s' % datetime.now())

years = ['2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010']
police_incidents_df = police_incidents_df[police_incidents_df.Year.isin(years)]

police_incidents_df_sorted = police_incidents_df.sort_values(by=['Year', 'Month', 'Day_m', 'Time'])

print('Data truncated: %s' % datetime.now())

# Rename the columns for future convenience
police_incidents_df_sorted.rename(columns={
    'IncidntNum': 'id',
    'Category': 'category',
    'DayOfWeek': 'day_w',
    'Time': 'time',
    'Resolution': 'resolution',
    'X': 'lng',
    'Y': 'lat',
    'Year': 'year',
    'Month': 'month',
    'Day_m': 'day_m',
    'PdDistrict': 'district',
    'Location': 'location'
}, inplace=True)

# Function map_crime helps get meta categories
def map_crime(cat):
    
    # Use this dictionary to add meta categories
    incident_map = {'BAD CHECKS': 'WC',
             'BRIBERY': 'WC',
             'EMBEZZLEMENT': 'WC',
             'EXTORTION' : 'WC',
             'FORGERY/COUNTERFEITING' : 'WC',
             'FRAUD' : 'WC',
             'SUSPICIOUS OCC' : 'WC',
             'ARSON' : 'BC',
             'ASSAULT' : 'BC',
             'BURGLARY' : 'BC',
             'DISORDERLY CONDUCT' : 'BC',
             'DRIVING UNDER THE INFLUENCE' : 'BC',
             'GAMBLING' : 'BC',
             'KIDNAPPING' : 'BC',
             'LARCENY/THEFT' : 'BC',
             'LIQUOR LAWS' : 'BC',
             'RECOVERED VEHICLE' : 'BC',
             'ROBBERY' : 'BC',
             'SEX OFFENSES, FORCIBLE' : 'BC',
             'STOLEN PROPERTY' : 'BC',
             'TRESPASS' : 'BC',
             'VANDALISM' : 'BC',
             'VEHICLE THEFT' : 'BC',
             'DRUG/NARCOTIC' : 'OI',
             'DRUNKENNESS' : 'OI',
             'FAMILY OFFENSES' : 'OI',
             'LOITERING' : 'OI',
             'MISSING PERSON' : 'OI',
             'NON-CRIMINAL' : 'OI',
             'OTHER OFFENSES' : 'OI',
             'PORNOGRAPHY/OBSCENE MAT' : 'OI',
             'PROSTITUTION' : 'OI',
             'RUNAWAY' : 'OI',
             'SECONDARY CODES' : 'OI',
             'SEX OFFENSES, NON FORCIBLE' : 'OI',
             'SUICIDE' : 'OI',
             'TREA' : 'OI',
             'WARRANTS' : 'OI',
             'WEAPON LAWS' : 'OI'}

    return incident_map[cat]

# Add meta categories
incident_list = []

print('Adding meta categories: %s' % datetime.now())
for i in police_incidents_df_sorted['category']:
    incident_list.append(map_crime(i))

police_incidents_df_sorted['meta_cat'] = incident_list
print('Meta categories added: %s' % datetime.now())

# Rearrange columns 
police_incts_df = police_incidents_df_sorted[['id', 'year', 'month', 'day_m', 'day_w', 'time', 
                                              'category', 'meta_cat', 'resolution', 'location', 'lat', 'lng']]

# Trim down the dataframe to only what we need
print('Preparing coordinate-zipcode table: %s' % datetime.now())

incdt_loc_df= police_incts_df.drop_duplicates(subset= ['location'], keep="first")
coords_df = incdt_loc_df.filter(['location', 'lat', 'lng'], axis=1)
coords_df.reset_index(drop=True, inplace=True)
print('Setup ready: %s' % datetime.now())

# Use this function to retrieve content of a file. Mainly used for getting api keys from a local file.
# It's assumed our file contains a single line, with our API key
def get_file_contents(filename):

    try:
        with open(filename, 'r') as f:
            
            return f.read().strip()
    except FileNotFoundError:
        print("'%s' file not found" % filename)

# Use this function to get the zipcode from a lat/lng pair
def get_zip_code(lat, lng):
    base_url = 'http://ws.geonames.net/findNearbyPostalCodesJSON?'
    full_url = base_url + 'lat=%s&lng=%s&username=%s' % (lat, lng, geonames_username)
    
    zipcode = req.get(full_url).json()['postalCodes'][0]['postalCode']
    
    return zipcode

geonames_username = get_file_contents('.geonames_username')

# Retrieve zip codes using API calls function
zip_list = []

print('Retrieving zipcodes')
for i in range(0, len(coords_df)):
    print('%s: %s' % (i, datetime.now()))
    zipcode = str(get_zip_code(coords_df['lat'][i], coords_df['lng'][i]))
    zip_list.append(zipcode)
    
# Add zip codes to dataframe
coords_df['zipcode'] = zip_list

# Export coordinates zipcode and compress it using zipfile library
print('Exporting: %s' % datetime.now())
coords_df.to_csv('data/coord-zipcode-table.csv', index=False)

coords_zip = zipfile.ZipFile('data/coord-zipcode-table.zip', 'w')
coords_zip.write('data/coord-zipcode-table.csv', compress_type=zipfile.ZIP_DEFLATED)
 
coords_zip.close()
print('All done: %s' % datetime.now())

#  Rename column 'name'of schools dataframe and merge both dataframes (tables) 
print('Add zipcode column: %s' % datetime.now())
data_merged_df = pd.merge(police_incts_df, coords_df, on="location")

# Delete duplicate columns and rename them
data_merged_df.drop(['lng_x', 'lat_y'], axis=1, inplace= True)
data_merged_df.rename(columns={'lat_x': 'lat', 'lng_y' : 'lng'}, inplace=True)
final_data_df = data_merged_df.sort_values(by=['year', 'month', 'day_m', 'time'])
final_data_df.reset_index(drop=True, inplace=True)

print('Done: %s' % datetime.now())

# Export final main data file
print('Exporting: %s' % datetime.now()) 

final_data_df.to_csv('main-data.csv', index=False)

main_data_zip = zipfile.ZipFile('data/main-data.zip', 'w') 
main_data_zip.write('main-data.csv',compress_type=zipfile.ZIP_DEFLATED)

main_data_zip.close()

print('All done: %s' % datetime.now())

