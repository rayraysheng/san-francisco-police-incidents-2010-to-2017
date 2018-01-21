
## Project Title: Analysis of Police Incidents in the City and County of San Francisco

### Team Members:
* Abdullah ALfai
* Alex Leontiev
* Ray Sheng
* Beatriz Shetkar

### Project Description:
For this project, we analyzed the San Francisco Police Department (SFPD) Incident Report, containing a detailed record of police incidents from 2003 to date—January 2018 as of the date of this project. This report contains over 2 million records, which complicated data movement. To amileriate this issue, we narrowed down the scope of our analysis to the 01/01/2010 to 12/31/2017 time span. 

In addition to the SFPD report, we also used Census Bureau American Community Survey (ACS) reports for each of the years included in the study report.  These reports provided demographic and socioeconomic information that were correlated with the SFPD report to address various questions we explored.

### Research Questions to Explore:
* What are general trends and makeup of types of crime in SF?
* Are there temporal and geographic area correlations with criminal activity?
* Are there any socioeconomic relationships?

### Data Sets to be Used:
##### Main Data Set:
* SF Police Department Incidents (2.16M rows total): https://data.sfgov.org/Public-Safety/Police-Department-Incidents/tmnf-yvry

##### Supporting Data Sets: 
* US Census Data: https://www.census.gov/topics/income-poverty/poverty/guidance/data-sources/acs-vs-cps.html

### Highlights of our findings and observations:
* The general increase in the number of incidents for all of San Francisco is commensurate with the population increase during the study period.
* The make-up of categories of incidents for the city as a whole remains mostly unchanged during the study period.
	- A notable exception to this pattern is drug related incidents, which declined by nearly 80% during the study period.
	- This decline was accompanied by a nearly 50% increase in the incidents of theft.
* The two patterns described above were present in each of the zip codes in San Francisco.
* We observed the following temporal correlations in the incident data
	- The highest number of incidents occurs on Fridays and Saturdays, theft representing the most common category. The third highest number of incidents occurs on Sundays.
	- The number of incidents is generally lower in the early morning hours (2-6AM); begins to rise thereafter and peaks at around noon; drops off a bit in the early afternoon hours; steadily climbs and reaches another peak at around 6PM; finally it begins to decline for the remainder of the evening and early morning hours.
* There is a strong correlation between the percentage of incidents resolved in, and the affluence of a given zip code.
	- A significant number of incidents in the poor areas is unresolved, as compared to the average for the City as a whole.
	- Auto theft represents the highest percentage of unresolved incidents—over 90% of incidents are unresolved.

