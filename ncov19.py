#!/usr/bin/env python3

import requests
import csv
import datetime

cases_url = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'
deaths_url = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv'
recovered_url = 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv'

# Fetch the confirmed cases data.
r = requests.get(cases_url)
# The response (r) from the website contains, in its 'text' attribute, the raw data.
# The raw data is in CSV (Comma Separated Value) format, a row per line.
# Split the raw data into separate lines, giving a list of rows.
cases_csv = r.text.splitlines()
# Use CSV reader to generate a list of values for each row, so now we have a list of lists.
cases_data = [row for row in csv.reader(cases_csv)]

# Fetch the deaths data.
r = requests.get(deaths_url)
deaths_csv = r.text.splitlines()
deaths_data = [row for row in csv.reader(deaths_csv)]

# Fetch the recovered cases data.
r = requests.get(recovered_url)
recovered_csv = r.text.splitlines()
recovered_data = [row for row in csv.reader(recovered_csv)]

# This will contain in its first element (row), the list of heading from the CSV data.
# Separate the header:
header = cases_data[0]
cases_data = cases_data[1:]
deaths_data = deaths_data[1:]
recovered_data = recovered_data[1:]

assert(len(cases_data) == len(deaths_data) == len(recovered_data))

# The header is in this form:
# ['Province/State', 'Country/Region', 'Lat', 'Long', '1/22/20', '1/23/20', ... ]
# Let's process it a bit to put the dates in ISO format...

# Make a list of all the date values. We'll need this later.
dates = []
# Skip the first 4 headers, the rest will all be dates.
for field in header[4:]:
    date = datetime.datetime.strptime(field, '%m/%d/%y')
    # This converts '3/23/20' into '2020-03-23T00:00:00'.
    # Strip off the last 9 characters, we don't care about the H:M:S.
    new_date = str(date.isoformat())[:-9]
    dates.append(new_date)

# Now let's make a dictionary (map), which is easier to refer to and process.
# We'll key the dictionary by country. So, it will look something like:
# Province/State is not used, we'll roll up the data by country.
#
# {
#     'latitude': '15.0',
#     'longitude': '101.0',
#     'data': {
#         '2020-01-22': '2',
#         '2020-01-23': '3',
#         ...
#     }
# }

data_map = {}
for i, row in enumerate(cases_data):
    # 'i' increments with each row.
    # We can use 'i' to find the corresponding row in the deaths and recovered data.
    country = row[1]
    assert(country != '')    # Country should never be blank.
    province = row[0]
    if country == 'United Kingdom':
        country = province
        province = ''
    latitude = row[2]
    longitude = row[3]
    cases_row_data = row[4:]
    deaths_row = deaths_data[i]
    deaths_row_data = deaths_row[4:]
    recovered_row = recovered_data[i]
    recovered_row_data = recovered_row[4:]

    # These should be the same, just check in case something has gone wrong.
    assert(len(cases_row_data) == len(deaths_row_data) == len(recovered_row_data) == len(dates))

    if country not in data_map:
        print(f"{country}")
        # This country is not already in the map. Add it.
        data_map[country] = {
            'latitude': latitude,
            'longitude': longitude,
            'cases': {},
            'deaths': {},
            'recovered': {}
        }
        for d in dates:
            data_map[country]['cases'][d] = 0
            data_map[country]['deaths'][d] = 0
            data_map[country]['recovered'][d] = 0

    for j, value in enumerate(cases_row_data):
        # 'j' increments with each value in row_data: 0, 1, ...
        # We can use 'j' to find the corresponding date in the list of dates.
        # This country is already in the map. Add the data to existing data.
        if value == '':
            intval = 0
        else:
            intval = int(value)
        new_value = int(data_map[country]['cases'][dates[j]]) + intval
        data_map[country]['cases'][dates[j]] = f"{new_value}"

    for j, value in enumerate(deaths_row_data):
        if value == '':
            intval = 0
        else:
            intval = int(value)
        new_value = int(data_map[country]['deaths'][dates[j]]) + intval
        data_map[country]['deaths'][dates[j]] = f"{new_value}"

    for j, value in enumerate(recovered_row_data):
        if value == '':
            intval = 0
        else:
            intval = int(value)
        new_value = int(data_map[country]['recovered'][dates[j]]) + intval
        data_map[country]['recovered'][dates[j]] = f"{new_value}"


import pprint
pprint.pprint(data_map)
