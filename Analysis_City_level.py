# Dependencies

%matplotlib inline

import pandas as pd
import numpy as np
import zipfile
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import time

# Load zipfile

data_zip_path = 'data/main-data.zip'
zf = zipfile.ZipFile(data_zip_path) # having Police_Incidents.csv zipped file.
data_df = pd.read_csv(zf.open('main-data.csv'))
data_df.dtypes

main_df = data_df.drop(['day_w', 'time', 'location', 'zipcode', 'lat', 'lng', 'resolution'], axis=1)

# We take a look at the top 10 categories. 
# We have not ineterested on categories 'Other Offenses' and 'Non-criminal', because it is not personal and public safety.

categories = ['LARCENY/THEFT', 'ASSAULT', 'VANDALISM', 'WARRANTS', 'VEHICLE THEFT', 'SUSPICIOUS OCC', 
              'BURGLARY', 'DRUG/NARCOTIC', 'ROBBERY', 'FRAUD']

subset_df = main_df[main_df.category.isin(categories)]

# Get the totals of each category per year, and find which are the top 13.

group_cat_y = subset_df.groupby(['category', 'year'])
cat_year_df = group_cat_y["id"].size()
cat_year_df = cat_year_df.unstack()
cat_year_df= cat_year_df.fillna(0)
cat_year_df.stack()
top10_df = cat_year_df.nlargest(13,2010)

# Save to a csv files.
top10_df.to_csv('output/top13_categories_year.csv')

# Pivot Table at City Level for obtaining the totals for each category every single year from 2010 to 2017.

pvt_cat_year = subset_df.pivot_table(index=['year'], 
                                     columns=['category'], 
                                     values='id',  
                                     aggfunc='count', 
                                     fill_value=0)

# Save to a csv files.
pvt_cat_year.to_csv('output/top10_categories_year.csv')

# Change pivot table to records, for plotting using seaborn library

# Convert pivot table to records
new_data_df = pd.DataFrame(pvt_cat_year.to_records())

# Save to a csv files.
new_data_df.to_csv('output/top10_categories_year.csv', index=False)

new_data_df.columns = [hdr.replace("('id', ", "").replace(")", "") \
                     for hdr in new_data_df.columns]

new_data_df = new_data_df.melt('year', var_name='cols', value_name='vals')

# Graph of Totals incidents by year (Top 10 crimes)

g = sns.FacetGrid(new_data_df, hue="cols", size=6)
g = (g.map(plt.plot, "year", "vals", linewidth=2).add_legend())

fig = plt.gcf()
fig.set_size_inches(11, 8)

#Incorporate the other graph properties

plt.title("Top 10 Crimes Change by Year" , fontsize=18)
plt.ylabel("Number of Incidents", fontsize=16)
plt.xlabel("Type of Incident", fontsize=16)
plt.grid(True, ls='dashed')
plt.savefig('output/top10crimes.png')
plt.show()


# Function for plotting several lines

def plot_func(cat):
    
    plt.plot(pvt_cat_year[cat], marker='o', markersize=8, alpha=0.6, linestyle='dashed', linewidth=1)

 # Graph of Totals incidents by year (Top 10 crimes) 2nd. option.

plt.style.use('ggplot')
fig = plt.gcf()
fig.set_size_inches(14, 10.5)

for c in categories:
    plot_func(c)

# Put a legend below current axis
plt.title("Top 10 Crimes Change by Year" , fontsize=18)
plt.ylabel("Total of Incidents", fontsize=16)
plt.xlabel("Years", fontsize=16)
plt.grid(True, ls='dashed')

plt.legend(bbox_to_anchor=(1.04,1), loc="upper left")

plt.savefig('output/top10crimes2.png')
plt.show()

# Total of 10 categories or type of incidents by year. 
# This we usefull for calculating the overall rate of change of each in a particular period of time. 

group_by_year = subset_df.groupby(['year'])
totals_by_year = group_by_year["id"].count()
totals_by_year

# Calculate percentage using the Series 'totals_by_year' and the Dataframe top13

years=[2010,2011,2012,2013,2014,2015,2016,2017]

# New dataframe for holding percenatges of each category.
pctg_df = pd.DataFrame()

for y in years:
    # Obtain from series the totals for each year using get method.
    total = totals_by_year.get(y)
    
    # Create the name of the column
    name="pct_" + str(y)
    
    # Apply the totals for each column "Y" in df top10 which has the totals of each crime per year.
    pctg_df[name]  = top10_df[y]/total*100

# Save to a csv files.
pctg_df.to_csv('output/pct_categories_years.csv')

plt.style.use('ggplot')
fig = plt.figure()

plt.title("Mix of Top 10 Categories (2010)", fontsize=14)

# Put a legend below current axis
explode = [0.2, 0, 0, 0, 0, 0, 0, 0, 0, 0]

plt.pie(pctg_df['pct_2010'],  labels=categories, 
        autopct="{0:1.1f}%".format, shadow=True, explode=explode, startangle=80)
plt.savefig('output/pctg2010.png')
plt.show()

plt.style.use('ggplot')
fig = plt.figure()

plt.title("Mix of Top 10 Categories (2017)", fontsize=14)

# Put a legend below current axis
explode = [0.2, 0, 0, 0, 0, 0, 0, 0, 0, 0]

plt.pie(pctg_df['pct_2017'],  labels=categories, 
        autopct="{0:1.1f}%".format, shadow=True, explode=explode, startangle=80)
plt.savefig('output/pctg2017.png')
plt.show()

# Pivot Table by Meta Category at City Level

pvt_mcy = pd.pivot_table(subset_df, 
                        index=['year'], 
                        columns=['meta_cat'], 
                        values=['id'],
                        aggfunc='count',
                        #margins= True,
                        fill_value=0
                        )

# Save to a csv files.
pvt_mcy.to_csv('output/meta_categories_year.csv')

# Graph Change of Meta-categories by year at City Level

plt.style.use('ggplot')
fig = plt.figure()

pvt_mcy.plot(kind='bar',stacked=True)

plt.title("Meta-categories by Year at City Level " , fontsize=14)
plt.ylabel("Number of Incidents", fontsize=14)
plt.xlabel("Year", fontsize=14)
plt.grid(True, ls='dashed')

plt.xticks(rotation=(0.45))
plt.savefig('output/fig6.png')

# Put a legend below current axis
plt.legend(bbox_to_anchor=(1.04,1), loc="upper left")

plt.savefig('output/mcatyear.png')   