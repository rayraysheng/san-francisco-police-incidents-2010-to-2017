
# coding: utf-8

# Dependencies
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import requests
from census import Census
from us import states
from datetime import datetime

# Use this function to retrieve content of a file
# # Mainly used for getting api keys from a local file
def get_file_contents(filename):
     #Given a filename,
       # return the contents of that file

    try:
        with open(filename, 'r') as f:
            # It's assumed our file contains a single line,
            # with our API key
            return f.read().strip()
    except FileNotFoundError:
        print("'%s' file not found" % filename)

census_api_key = get_file_contents('.census_api_key')

# Census API Key
c = Census(census_api_key)

# Retrieve census data for 2010 to 2017
years = list(range(2011, 2017))

for each in years:
    print('--------%s--------' % each)
    
    c = Census(census_api_key, year=each)
    
    # Get data using API
    print('Retrieving Data: %s' % datetime.now())
    census_data = c.acs5.get(('B01003_001E', 'B19301_001E', 'B19013_001E', 'B17001_002E'), 
                         {'for': 'zip code tabulation area:*'})

    print('Making DataFrame: %s' % datetime.now())    
    # Create and clean dataframe
    census_df = pd.DataFrame(census_data)
    census_df = census_df.rename(columns={'zip code tabulation area': 'zipcode',
                                          'B19301_001E': 'per_capita_income',
                                          'B19013_001E': 'household_income',
                                          'B01003_001E': 'population', 
                                          'B17001_002E': 'poverty_count',})
    
    # Keep only the rows with SF zipcodes
    sf_zipcodes = [str(x) for x in range(94102, 94189)]

    census_df = census_df[census_df.zipcode.isin(sf_zipcodes)]
    census_df.reset_index(drop=True, inplace=True)
    
    # Add in Poverty Rate (Poverty Count / Population)
    census_df['poverty_rate'] = 100 * census_df['poverty_count'].astype(int) / census_df['population'].astype(int)
    
    print('Exporting: %s' % datetime.now())
    # Export file for use
    census_df.to_csv('data/census-%s.csv' % each, index=False)

