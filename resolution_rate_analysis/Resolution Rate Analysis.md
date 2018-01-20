

```python
# Import Denpendencies
print('Importing libraries')
import pandas as pd
import numpy as np
import zipfile
from datetime import datetime
from matplotlib import pyplot as plt
from scipy import stats
print('Done importing')

# Load datafram from csv compressed in the zip file
print('Loading source file: %s' % datetime.now())
data_zip_path = '../data/main-data.zip'
zf = zipfile.ZipFile(data_zip_path)
main_df = pd.read_csv(zf.open('main-data.csv'))
print('File loaded: %s' % datetime.now())

print('Further cleaning: %s' % datetime.now())
main_df['zipcode'] = main_df.zipcode.apply(str)
main_df = main_df[~main_df.zipcode.isin(['94014', '94015', '94017', '94129'])]
print('Cleaned: %s' % datetime.now())

# Assign a resolution value for each resolution type ('NONE' = 0, all others = 1)
res_list = main_df.resolution.value_counts().index.tolist()
res_val_list = []

for resolution in res_list:
    if resolution == 'NONE':
        res_value = 0
    else:
        res_value = 1
    
    res_val_list.append(res_value)

resolution_df = pd.DataFrame({
    'resolution': res_list,
    'res_value': res_val_list
})

# Now add the resolution values to focus_df
main_rv_df = pd.merge(main_df, resolution_df, on='resolution')

# Look at the overall resolution rates by category
by_category = main_rv_df.groupby('category')
by_category_res_df = pd.DataFrame(by_category['res_value'].mean())
by_category_res_df.rename(columns={'res_value': 'resolution_rate'}, inplace=True)
by_category_res_df.sort_values('resolution_rate', inplace=True, ascending=False)
by_category_res_df.reset_index(inplace=True)

# Show citywide resolution rate by incident category
plt.figure(figsize=(15,7.5))

x_axis = np.arange(len(by_category_res_df))
plt.bar(x_axis, by_category_res_df['resolution_rate'], alpha=0.8)

plt.xticks(x_axis, list(by_category_res_df['category']), rotation=90)

for i in range(0, len(x_axis)):
    plt.text(x_axis[i]-0.4, by_category_res_df['resolution_rate'][i]+0.035, 
             str(round(by_category_res_df['resolution_rate'][i], 2)), rotation=45)

plt.title('SF Citywide Resolution Rate by Incident Category 2010-2017')
plt.xlabel('Incident Category', labelpad=20)
plt.ylabel('Resolution Rate', labelpad=20)
plt.ylim(0, 1)

plt.show()

# Load zipcode keys
census_2016_df = pd.read_csv('../data/census-2016.csv')
census_2015_df = pd.read_csv('../data/census-2015.csv')
census_2014_df = pd.read_csv('../data/census-2014.csv')
census_2013_df = pd.read_csv('../data/census-2013.csv')
census_2012_df = pd.read_csv('../data/census-2012.csv')
census_2011_df = pd.read_csv('../data/census-2011.csv')

census_files_lst = [census_2016_df, census_2015_df, census_2014_df, census_2013_df, census_2012_df, census_2011_df]

# Change zipcode data type to string
for df in census_files_lst:
    df['zipcode'] = df.zipcode.apply(str)

# Create the combined key for average values over the years
census_combined_df = pd.concat(census_files_lst)
census_key_allyears_df = census_combined_df.groupby('zipcode')[['household_income', 'population', 'per_capita_income', 'poverty_rate']].mean()
census_key_allyears_df.reset_index(inplace=True)

# Use this function to build prepare the data by zipcode for statistical testing
def build_zip_dictionary(df):
        zip_dict = {}
        zip_list = df['zipcode'].value_counts().index
        
        for zipcode in zip_list:    
            new_key = zipcode
            new_sample = df[df['zipcode'] == zipcode]['res_value'].tolist()
            zip_dict[new_key] = new_sample
            
        return zip_dict

# Use this function to run statistical test and output ot dataframe
def build_test_dataframe(df, dic):
    all_samples = df.res_value.tolist()
    
    zip_list = []
    diff_list = []
    p_list = []
    
    for key in dic:
        t, p = stats.ttest_ind(dic[key], all_samples, equal_var=False)
        zip_list.append(key)
        diff_list.append(np.mean(dic[key])-np.mean(all_samples))
        p_list.append(p)

    p_df = pd.DataFrame({
        'zipcode': zip_list,
        'difference': diff_list,
        'p_value': p_list
    })
    
    return p_df

# Use this function to determine the color of each zipcode's bar depending on p-value
def add_sig_color(df):
    sig_color_list = []
    for i in range(0, len(df)):
        if df['p_value'][i] < 0.05:
            color = 'green'
        else:
            color = 'red'
        sig_color_list.append(color)
    df['color'] = sig_color_list

# Use this function to output analysis dataframe for given category
def analyze_category(category, sort_by):
    cat_df = main_rv_df[main_rv_df['category'] == category]
    
    cat_dict = build_zip_dictionary(cat_df)
    
    cat_test_df = build_test_dataframe(cat_df, cat_dict)
    
    add_sig_color(cat_test_df)
    
    cat_analysis_df = pd.merge(cat_test_df, census_key_allyears_df, how='left', on='zipcode')
    
    cat_analysis_df.sort_values(sort_by, inplace=True)
    cat_analysis_df.reset_index(drop=True, inplace=True)
    
    return cat_analysis_df

"""
# Use this function to generate a bar plot for the given category analysis dataframe
# Note: need to manually add title
def generate_plot(cat_analysis_df):
    plt.figure(figsize=(10,6))
    plt.style.use('ggplot')

    x_axis = np.arange(len(cat_analysis_df))

    plt.bar(x_axis, 
            cat_analysis_df.difference, 
            color=cat_analysis_df['color'])

    x_labs = []
    for i in range(0, len(cat_analysis_df)):
        label = '%.2f%%  (%s)' % (cat_analysis_df['poverty_rate'][i], cat_analysis_df['zipcode'][i])
        x_labs.append(label)
    plt.xticks(x_axis, list(x_labs), rotation=90)
    plt.xlabel('Zipcodes Sorted by Ascending Poverty Rate', labelpad=20)
    plt.ylabel('Resolution Rate Difference from City Average', labelpad=20)
    """

# Use this function to generate a bar plot for the given category and sort by
def custom_bar(category, cat_analysis_df, sort_by):
    
    # Set size and style
    plt.figure(figsize=(10,6))
    plt.style.use('ggplot')
    
    # Set x-axis
    x_axis = np.arange(len(cat_analysis_df))
    
    # Plot the bars
    plt.bar(x_axis, 
            cat_analysis_df.difference, 
            color=cat_analysis_df['color'])
    
    # Text key for colors
    plt.text(0.95, 0.5, transform=plt.gcf().transFigure, fontsize=12,
             s='green: p-value < 0.05 \nred: p-value >= 0.05')
    
    # Set title
    plt.title('%s Resolution Rate by Zipcode' % category)

    # Set x label & ticks
    x_labs = []
    for i in range(0, len(cat_analysis_df)):
        if sort_by == 'poverty_rate':
            label = '%.2f%%  (%s)' % (cat_analysis_df[sort_by][i], cat_analysis_df['zipcode'][i])
            x_labs.append(label)
        else:
            label = '$%.2f  (%s)' % (cat_analysis_df[sort_by][i], cat_analysis_df['zipcode'][i])
            x_labs.append(label)
    plt.xticks(x_axis, list(x_labs), rotation=90)
    
    # Set y label
    plt.ylabel('Resolution Rate Difference from City Average', labelpad=20)
    if sort_by == 'poverty_rate':
        plt.xlabel('Zipcodes Sorted by Ascending Poverty Rate', labelpad=20)
    elif sort_by == 'per_capita_income':
        plt.xlabel('Zipcodes Sorted by Ascending Per Capita Income', labelpad=20)
    else:
        plt.xlabel('Zipcodes Sorted by Ascending Median Household Income', labelpad=20)

# Use this function to quickly create a bar graph from category and sort_by
def direct_bar(category, sort_by):
    print(category)
    cat_df = main_rv_df[main_rv_df['category'] == category]
    
    cat_dict = build_zip_dictionary(cat_df)
    
    cat_test_df = build_test_dataframe(cat_df, cat_dict)
    
    add_sig_color(cat_test_df)
    
    cat_analysis_df = pd.merge(cat_test_df, census_key_allyears_df, how='left', on='zipcode')
    
    cat_analysis_df.sort_values(sort_by, inplace=True)
    cat_analysis_df.reset_index(drop=True, inplace=True)
    
    graph = custom_bar(category, cat_analysis_df, sort_by)
    plt.show()

# Use this function to generate a scatter plot
def custom_scatter(category, cat_analysis_df, sort_by):
    
    plt.figure(figsize=(10,6))
    plt.style.use('ggplot')
    
    # Set x and y
    x = cat_analysis_df[sort_by][cat_analysis_df['p_value']<0.05]
    y = cat_analysis_df.difference[cat_analysis_df['p_value']<0.05]
    
    # Plot the points
    plt.scatter(x, y, 
                color='green', edgecolor='black', alpha=0.8, s=50
               )  
    
    # Plot the zero line
    zero_line = np.array([0 for i in range(0,len(x))])
    plt.plot(x, zero_line, linewidth=0.5, color='red') 
    
    # Plot the fitline
    fit = np.polyfit(x, y, deg=1)
    plt.plot(x, fit[0] * x + fit[1], color='blue', linewidth=0.5)
    
    # Display the statistical values of the fit line
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    plt.text(0.95, 0.5, transform=plt.gcf().transFigure, fontsize=12,
             s='Fit line r-value: %s \nFit line p-value: %s' % (r_value, p_value))
    
    # Set Title
    plt.title('%s Resolution Rate by Zipcode' % category)

    # Set x label
    x_labs = []
    for i in range(0, len(cat_analysis_df)):
        if sort_by == 'poverty_rate':
            label = '%.2f%%  (%s)' % (cat_analysis_df[sort_by][i], cat_analysis_df['zipcode'][i])
            x_labs.append(label)
        else:
            label = '$%.2f  (%s)' % (cat_analysis_df[sort_by][i], cat_analysis_df['zipcode'][i])
            x_labs.append(label)
    
    # Set y label
    plt.ylabel('Resolution Rate Difference from City Average', labelpad=20)
    if sort_by == 'poverty_rate':
        plt.xlabel('Poverty Rate (%)', labelpad=20)
    elif sort_by == 'per_capita_income':
        plt.xlabel('Per Capita Income', labelpad=20)
    else:
        plt.xlabel('Median Household Income', labelpad=20)
    
# Use this function to quickly make a scatter plot from category and sort_by
def direct_scatter(category, sort_by):
    print(category)
    cat_df = main_rv_df[main_rv_df['category'] == category]
    
    cat_dict = build_zip_dictionary(cat_df)
    
    cat_test_df = build_test_dataframe(cat_df, cat_dict)
    
    add_sig_color(cat_test_df)
    
    cat_analysis_df = pd.merge(cat_test_df, census_key_allyears_df, how='left', on='zipcode')
    
    cat_analysis_df.sort_values(sort_by, inplace=True)
    cat_analysis_df.reset_index(drop=True, inplace=True)
    
    graph = custom_scatter(category, cat_analysis_df, sort_by)
    plt.show()
```

    Importing libraries
    Done importing
    Loading source file: 2018-01-19 15:22:18.487281
    File loaded: 2018-01-19 15:22:21.595240
    Further cleaning: 2018-01-19 15:22:21.596243
    Cleaned: 2018-01-19 15:22:22.317161
    


![png](output_0_1.png)



```python
# Plot all the graphs
category_list = main_rv_df.category.value_counts().index.tolist()
```


```python
for category in category_list:
    direct_bar(category, 'poverty_rate')
```

    LARCENY/THEFT
    


![png](output_2_1.png)


    OTHER OFFENSES
    


![png](output_2_3.png)


    NON-CRIMINAL
    


![png](output_2_5.png)


    ASSAULT
    


![png](output_2_7.png)


    VANDALISM
    


![png](output_2_9.png)


    WARRANTS
    


![png](output_2_11.png)


    VEHICLE THEFT
    


![png](output_2_13.png)


    DRUG/NARCOTIC
    


![png](output_2_15.png)


    SUSPICIOUS OCC
    


![png](output_2_17.png)


    BURGLARY
    


![png](output_2_19.png)


    MISSING PERSON
    


![png](output_2_21.png)


    ROBBERY
    


![png](output_2_23.png)


    FRAUD
    


![png](output_2_25.png)


    SECONDARY CODES
    


![png](output_2_27.png)


    WEAPON LAWS
    


![png](output_2_29.png)


    TRESPASS
    


![png](output_2_31.png)


    STOLEN PROPERTY
    


![png](output_2_33.png)


    SEX OFFENSES, FORCIBLE
    


![png](output_2_35.png)


    FORGERY/COUNTERFEITING
    


![png](output_2_37.png)


    PROSTITUTION
    


![png](output_2_39.png)


    RECOVERED VEHICLE
    


![png](output_2_41.png)


    DRUNKENNESS
    


![png](output_2_43.png)


    DISORDERLY CONDUCT
    


![png](output_2_45.png)


    DRIVING UNDER THE INFLUENCE
    


![png](output_2_47.png)


    KIDNAPPING
    


![png](output_2_49.png)


    ARSON
    


![png](output_2_51.png)


    RUNAWAY
    

    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\numpy\core\fromnumeric.py:3146: RuntimeWarning: Degrees of freedom <= 0 for slice
      **kwargs)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\numpy\core\_methods.py:127: RuntimeWarning: invalid value encountered in double_scalars
      ret = ret.dtype.type(ret / rcount)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in greater
      return (self.a < x) & (x < self.b)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in less
      return (self.a < x) & (x < self.b)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:1818: RuntimeWarning: invalid value encountered in less_equal
      cond2 = cond0 & (x <= self.a)
    


![png](output_2_54.png)


    LIQUOR LAWS
    


![png](output_2_56.png)


    EMBEZZLEMENT
    


![png](output_2_58.png)


    LOITERING
    


![png](output_2_60.png)


    SUICIDE
    


![png](output_2_62.png)


    FAMILY OFFENSES
    


![png](output_2_64.png)


    BRIBERY
    


![png](output_2_66.png)


    EXTORTION
    


![png](output_2_68.png)


    BAD CHECKS
    


![png](output_2_70.png)


    SEX OFFENSES, NON FORCIBLE
    


![png](output_2_72.png)


    GAMBLING
    


![png](output_2_74.png)


    PORNOGRAPHY/OBSCENE MAT
    


![png](output_2_76.png)


    TREA
    


![png](output_2_78.png)



```python
for category in category_list:
    direct_bar(category, 'per_capita_income')
```

    LARCENY/THEFT
    


![png](output_3_1.png)


    OTHER OFFENSES
    


![png](output_3_3.png)


    NON-CRIMINAL
    


![png](output_3_5.png)


    ASSAULT
    


![png](output_3_7.png)


    VANDALISM
    


![png](output_3_9.png)


    WARRANTS
    


![png](output_3_11.png)


    VEHICLE THEFT
    


![png](output_3_13.png)


    DRUG/NARCOTIC
    


![png](output_3_15.png)


    SUSPICIOUS OCC
    


![png](output_3_17.png)


    BURGLARY
    


![png](output_3_19.png)


    MISSING PERSON
    


![png](output_3_21.png)


    ROBBERY
    


![png](output_3_23.png)


    FRAUD
    


![png](output_3_25.png)


    SECONDARY CODES
    


![png](output_3_27.png)


    WEAPON LAWS
    


![png](output_3_29.png)


    TRESPASS
    


![png](output_3_31.png)


    STOLEN PROPERTY
    


![png](output_3_33.png)


    SEX OFFENSES, FORCIBLE
    


![png](output_3_35.png)


    FORGERY/COUNTERFEITING
    


![png](output_3_37.png)


    PROSTITUTION
    


![png](output_3_39.png)


    RECOVERED VEHICLE
    


![png](output_3_41.png)


    DRUNKENNESS
    


![png](output_3_43.png)


    DISORDERLY CONDUCT
    


![png](output_3_45.png)


    DRIVING UNDER THE INFLUENCE
    


![png](output_3_47.png)


    KIDNAPPING
    


![png](output_3_49.png)


    ARSON
    


![png](output_3_51.png)


    RUNAWAY
    

    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\numpy\core\fromnumeric.py:3146: RuntimeWarning: Degrees of freedom <= 0 for slice
      **kwargs)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\numpy\core\_methods.py:127: RuntimeWarning: invalid value encountered in double_scalars
      ret = ret.dtype.type(ret / rcount)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in greater
      return (self.a < x) & (x < self.b)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in less
      return (self.a < x) & (x < self.b)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:1818: RuntimeWarning: invalid value encountered in less_equal
      cond2 = cond0 & (x <= self.a)
    


![png](output_3_54.png)


    LIQUOR LAWS
    


![png](output_3_56.png)


    EMBEZZLEMENT
    


![png](output_3_58.png)


    LOITERING
    


![png](output_3_60.png)


    SUICIDE
    


![png](output_3_62.png)


    FAMILY OFFENSES
    


![png](output_3_64.png)


    BRIBERY
    


![png](output_3_66.png)


    EXTORTION
    


![png](output_3_68.png)


    BAD CHECKS
    


![png](output_3_70.png)


    SEX OFFENSES, NON FORCIBLE
    


![png](output_3_72.png)


    GAMBLING
    


![png](output_3_74.png)


    PORNOGRAPHY/OBSCENE MAT
    


![png](output_3_76.png)


    TREA
    


![png](output_3_78.png)



```python
for category in category_list:
    direct_bar(category, 'household_income')
```

    LARCENY/THEFT
    


![png](output_4_1.png)


    OTHER OFFENSES
    


![png](output_4_3.png)


    NON-CRIMINAL
    


![png](output_4_5.png)


    ASSAULT
    


![png](output_4_7.png)


    VANDALISM
    


![png](output_4_9.png)


    WARRANTS
    


![png](output_4_11.png)


    VEHICLE THEFT
    


![png](output_4_13.png)


    DRUG/NARCOTIC
    


![png](output_4_15.png)


    SUSPICIOUS OCC
    


![png](output_4_17.png)


    BURGLARY
    


![png](output_4_19.png)


    MISSING PERSON
    


![png](output_4_21.png)


    ROBBERY
    


![png](output_4_23.png)


    FRAUD
    


![png](output_4_25.png)


    SECONDARY CODES
    


![png](output_4_27.png)


    WEAPON LAWS
    


![png](output_4_29.png)


    TRESPASS
    


![png](output_4_31.png)


    STOLEN PROPERTY
    


![png](output_4_33.png)


    SEX OFFENSES, FORCIBLE
    


![png](output_4_35.png)


    FORGERY/COUNTERFEITING
    


![png](output_4_37.png)


    PROSTITUTION
    


![png](output_4_39.png)


    RECOVERED VEHICLE
    


![png](output_4_41.png)


    DRUNKENNESS
    


![png](output_4_43.png)


    DISORDERLY CONDUCT
    


![png](output_4_45.png)


    DRIVING UNDER THE INFLUENCE
    


![png](output_4_47.png)


    KIDNAPPING
    


![png](output_4_49.png)


    ARSON
    


![png](output_4_51.png)


    RUNAWAY
    

    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\numpy\core\fromnumeric.py:3146: RuntimeWarning: Degrees of freedom <= 0 for slice
      **kwargs)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\numpy\core\_methods.py:127: RuntimeWarning: invalid value encountered in double_scalars
      ret = ret.dtype.type(ret / rcount)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in greater
      return (self.a < x) & (x < self.b)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in less
      return (self.a < x) & (x < self.b)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:1818: RuntimeWarning: invalid value encountered in less_equal
      cond2 = cond0 & (x <= self.a)
    


![png](output_4_54.png)


    LIQUOR LAWS
    


![png](output_4_56.png)


    EMBEZZLEMENT
    


![png](output_4_58.png)


    LOITERING
    


![png](output_4_60.png)


    SUICIDE
    


![png](output_4_62.png)


    FAMILY OFFENSES
    


![png](output_4_64.png)


    BRIBERY
    


![png](output_4_66.png)


    EXTORTION
    


![png](output_4_68.png)


    BAD CHECKS
    


![png](output_4_70.png)


    SEX OFFENSES, NON FORCIBLE
    


![png](output_4_72.png)


    GAMBLING
    


![png](output_4_74.png)


    PORNOGRAPHY/OBSCENE MAT
    


![png](output_4_76.png)


    TREA
    


![png](output_4_78.png)



```python
for category in category_list:
    direct_scatter(category, 'poverty_rate')
```

    LARCENY/THEFT
    


![png](output_5_1.png)


    OTHER OFFENSES
    


![png](output_5_3.png)


    NON-CRIMINAL
    


![png](output_5_5.png)


    ASSAULT
    


![png](output_5_7.png)


    VANDALISM
    


![png](output_5_9.png)


    WARRANTS
    


![png](output_5_11.png)


    VEHICLE THEFT
    


![png](output_5_13.png)


    DRUG/NARCOTIC
    


![png](output_5_15.png)


    SUSPICIOUS OCC
    


![png](output_5_17.png)


    BURGLARY
    


![png](output_5_19.png)


    MISSING PERSON
    


![png](output_5_21.png)


    ROBBERY
    


![png](output_5_23.png)


    FRAUD
    


![png](output_5_25.png)


    SECONDARY CODES
    


![png](output_5_27.png)


    WEAPON LAWS
    


![png](output_5_29.png)


    TRESPASS
    


![png](output_5_31.png)


    STOLEN PROPERTY
    


![png](output_5_33.png)


    SEX OFFENSES, FORCIBLE
    


![png](output_5_35.png)


    FORGERY/COUNTERFEITING
    


![png](output_5_37.png)


    PROSTITUTION
    


![png](output_5_39.png)


    RECOVERED VEHICLE
    


![png](output_5_41.png)


    DRUNKENNESS
    


![png](output_5_43.png)


    DISORDERLY CONDUCT
    


![png](output_5_45.png)


    DRIVING UNDER THE INFLUENCE
    


![png](output_5_47.png)


    KIDNAPPING
    


![png](output_5_49.png)


    ARSON
    


![png](output_5_51.png)


    RUNAWAY
    

    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\numpy\core\fromnumeric.py:3146: RuntimeWarning: Degrees of freedom <= 0 for slice
      **kwargs)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\numpy\core\_methods.py:127: RuntimeWarning: invalid value encountered in double_scalars
      ret = ret.dtype.type(ret / rcount)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in greater
      return (self.a < x) & (x < self.b)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in less
      return (self.a < x) & (x < self.b)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:1818: RuntimeWarning: invalid value encountered in less_equal
      cond2 = cond0 & (x <= self.a)
    


![png](output_5_54.png)


    LIQUOR LAWS
    


![png](output_5_56.png)


    EMBEZZLEMENT
    


![png](output_5_58.png)


    LOITERING
    


![png](output_5_60.png)


    SUICIDE
    

    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\ipykernel_launcher.py:253: RankWarning: Polyfit may be poorly conditioned
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_stats_mstats_common.py:106: RuntimeWarning: invalid value encountered in double_scalars
      slope = r_num / ssxm
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_stats_mstats_common.py:116: RuntimeWarning: invalid value encountered in sqrt
      t = r * np.sqrt(df / ((1.0 - r + TINY)*(1.0 + r + TINY)))
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_stats_mstats_common.py:118: RuntimeWarning: invalid value encountered in double_scalars
      sterrest = np.sqrt((1 - r**2) * ssym / ssxm / df)
    


![png](output_5_63.png)


    FAMILY OFFENSES
    


![png](output_5_65.png)


    BRIBERY
    


![png](output_5_67.png)


    EXTORTION
    


![png](output_5_69.png)


    BAD CHECKS
    


![png](output_5_71.png)


    SEX OFFENSES, NON FORCIBLE
    


![png](output_5_73.png)


    GAMBLING
    


![png](output_5_75.png)


    PORNOGRAPHY/OBSCENE MAT
    


![png](output_5_77.png)


    TREA
    


![png](output_5_79.png)



```python
for category in category_list:
    direct_scatter(category, 'per_capita_income')
```

    LARCENY/THEFT
    


![png](output_6_1.png)


    OTHER OFFENSES
    


![png](output_6_3.png)


    NON-CRIMINAL
    


![png](output_6_5.png)


    ASSAULT
    


![png](output_6_7.png)


    VANDALISM
    


![png](output_6_9.png)


    WARRANTS
    


![png](output_6_11.png)


    VEHICLE THEFT
    


![png](output_6_13.png)


    DRUG/NARCOTIC
    


![png](output_6_15.png)


    SUSPICIOUS OCC
    


![png](output_6_17.png)


    BURGLARY
    


![png](output_6_19.png)


    MISSING PERSON
    


![png](output_6_21.png)


    ROBBERY
    


![png](output_6_23.png)


    FRAUD
    


![png](output_6_25.png)


    SECONDARY CODES
    


![png](output_6_27.png)


    WEAPON LAWS
    


![png](output_6_29.png)


    TRESPASS
    


![png](output_6_31.png)


    STOLEN PROPERTY
    


![png](output_6_33.png)


    SEX OFFENSES, FORCIBLE
    


![png](output_6_35.png)


    FORGERY/COUNTERFEITING
    


![png](output_6_37.png)


    PROSTITUTION
    


![png](output_6_39.png)


    RECOVERED VEHICLE
    


![png](output_6_41.png)


    DRUNKENNESS
    


![png](output_6_43.png)


    DISORDERLY CONDUCT
    


![png](output_6_45.png)


    DRIVING UNDER THE INFLUENCE
    


![png](output_6_47.png)


    KIDNAPPING
    


![png](output_6_49.png)


    ARSON
    


![png](output_6_51.png)


    RUNAWAY
    

    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\numpy\core\fromnumeric.py:3146: RuntimeWarning: Degrees of freedom <= 0 for slice
      **kwargs)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\numpy\core\_methods.py:127: RuntimeWarning: invalid value encountered in double_scalars
      ret = ret.dtype.type(ret / rcount)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in greater
      return (self.a < x) & (x < self.b)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in less
      return (self.a < x) & (x < self.b)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:1818: RuntimeWarning: invalid value encountered in less_equal
      cond2 = cond0 & (x <= self.a)
    


![png](output_6_54.png)


    LIQUOR LAWS
    


![png](output_6_56.png)


    EMBEZZLEMENT
    


![png](output_6_58.png)


    LOITERING
    


![png](output_6_60.png)


    SUICIDE
    

    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\ipykernel_launcher.py:253: RankWarning: Polyfit may be poorly conditioned
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_stats_mstats_common.py:106: RuntimeWarning: invalid value encountered in double_scalars
      slope = r_num / ssxm
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_stats_mstats_common.py:116: RuntimeWarning: invalid value encountered in sqrt
      t = r * np.sqrt(df / ((1.0 - r + TINY)*(1.0 + r + TINY)))
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_stats_mstats_common.py:118: RuntimeWarning: invalid value encountered in double_scalars
      sterrest = np.sqrt((1 - r**2) * ssym / ssxm / df)
    


![png](output_6_63.png)


    FAMILY OFFENSES
    


![png](output_6_65.png)


    BRIBERY
    


![png](output_6_67.png)


    EXTORTION
    


![png](output_6_69.png)


    BAD CHECKS
    


![png](output_6_71.png)


    SEX OFFENSES, NON FORCIBLE
    


![png](output_6_73.png)


    GAMBLING
    


![png](output_6_75.png)


    PORNOGRAPHY/OBSCENE MAT
    


![png](output_6_77.png)


    TREA
    


![png](output_6_79.png)



```python
for category in category_list:
    direct_scatter(category, 'household_income')
```

    LARCENY/THEFT
    


![png](output_7_1.png)


    OTHER OFFENSES
    


![png](output_7_3.png)


    NON-CRIMINAL
    


![png](output_7_5.png)


    ASSAULT
    


![png](output_7_7.png)


    VANDALISM
    


![png](output_7_9.png)


    WARRANTS
    


![png](output_7_11.png)


    VEHICLE THEFT
    


![png](output_7_13.png)


    DRUG/NARCOTIC
    


![png](output_7_15.png)


    SUSPICIOUS OCC
    


![png](output_7_17.png)


    BURGLARY
    


![png](output_7_19.png)


    MISSING PERSON
    


![png](output_7_21.png)


    ROBBERY
    


![png](output_7_23.png)


    FRAUD
    


![png](output_7_25.png)


    SECONDARY CODES
    


![png](output_7_27.png)


    WEAPON LAWS
    


![png](output_7_29.png)


    TRESPASS
    


![png](output_7_31.png)


    STOLEN PROPERTY
    


![png](output_7_33.png)


    SEX OFFENSES, FORCIBLE
    


![png](output_7_35.png)


    FORGERY/COUNTERFEITING
    


![png](output_7_37.png)


    PROSTITUTION
    


![png](output_7_39.png)


    RECOVERED VEHICLE
    


![png](output_7_41.png)


    DRUNKENNESS
    


![png](output_7_43.png)


    DISORDERLY CONDUCT
    


![png](output_7_45.png)


    DRIVING UNDER THE INFLUENCE
    


![png](output_7_47.png)


    KIDNAPPING
    


![png](output_7_49.png)


    ARSON
    


![png](output_7_51.png)


    RUNAWAY
    

    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\numpy\core\fromnumeric.py:3146: RuntimeWarning: Degrees of freedom <= 0 for slice
      **kwargs)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\numpy\core\_methods.py:127: RuntimeWarning: invalid value encountered in double_scalars
      ret = ret.dtype.type(ret / rcount)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in greater
      return (self.a < x) & (x < self.b)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:879: RuntimeWarning: invalid value encountered in less
      return (self.a < x) & (x < self.b)
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_distn_infrastructure.py:1818: RuntimeWarning: invalid value encountered in less_equal
      cond2 = cond0 & (x <= self.a)
    


![png](output_7_54.png)


    LIQUOR LAWS
    


![png](output_7_56.png)


    EMBEZZLEMENT
    


![png](output_7_58.png)


    LOITERING
    


![png](output_7_60.png)


    SUICIDE
    

    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\ipykernel_launcher.py:253: RankWarning: Polyfit may be poorly conditioned
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_stats_mstats_common.py:106: RuntimeWarning: invalid value encountered in double_scalars
      slope = r_num / ssxm
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_stats_mstats_common.py:116: RuntimeWarning: invalid value encountered in sqrt
      t = r * np.sqrt(df / ((1.0 - r + TINY)*(1.0 + r + TINY)))
    C:\Users\Ray\AppData\Local\conda\conda\envs\PythonData01\lib\site-packages\scipy\stats\_stats_mstats_common.py:118: RuntimeWarning: invalid value encountered in double_scalars
      sterrest = np.sqrt((1 - r**2) * ssym / ssxm / df)
    


![png](output_7_63.png)


    FAMILY OFFENSES
    


![png](output_7_65.png)


    BRIBERY
    


![png](output_7_67.png)


    EXTORTION
    


![png](output_7_69.png)


    BAD CHECKS
    


![png](output_7_71.png)


    SEX OFFENSES, NON FORCIBLE
    


![png](output_7_73.png)


    GAMBLING
    


![png](output_7_75.png)


    PORNOGRAPHY/OBSCENE MAT
    


![png](output_7_77.png)


    TREA
    


![png](output_7_79.png)

