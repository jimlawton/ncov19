#!/usr/bin/env python3

import requests
import csv
import datetime
import pprint
from typing import List, Dict, Any

base_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'
cases_url = base_url + 'time_series_covid19_confirmed_global.csv'
deaths_url = base_url + 'time_series_covid19_deaths_global.csv'
recovered_url = base_url + 'time_series_covid19_recovered_global.csv'


def process_csv(data_type: str, csv_data: List, data_map: Dict[str, Dict[str, Any]] = {}) -> Dict:
    """Function to process the input CSV data and return a map."""

    assert(data_type)
    assert(csv_data)
    if data_map != {}:
        assert(data_map)

    # Use CSV reader to generate a list of values for each row, so now we have a list of lists.
    data = [row for row in csv.reader(csv_data)]
    # This will contain in its first element (row), the list of heading from the CSV data.
    # Separate the header:
    header = data[0]
    data = data[1:]
    assert(len(data) > 0)

    # The header is in this form:
    # ['Province/State', 'Country/Region', 'Lat', 'Long', '1/22/20', '1/23/20', ... ]
    # Let's process it a bit to put the dates in ISO format...

    # Make a list of all the date values. We'll need this later.
    # Assumption: the earliest dates will be in the cases file, since they start first.
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

    for i, row in enumerate(data):
        # 'i' increments with each row.
        country = row[1]
        assert(country != '')    # Country should never be blank.
        province = row[0]
        if country == 'United Kingdom':
            country = province
            province = ''
        latitude = row[2]
        longitude = row[3]
        row_data = row[4:]
        if country not in data_map:
            # This country is not already in the map. Add it.
            data_map[country] = {
                'latitude': latitude,
                'longitude': longitude,
                'cases': {},
                'deaths': {},
                'recovered': {}
            }

        for d in dates:
            for dtype in ('cases', 'deaths', 'recovered'):
                if d not in data_map[country][dtype]:
                    data_map[country][dtype][d] = 0

        for j, value in enumerate(row_data):
            # 'j' increments with each value in row_data: 0, 1, ...
            # We can use 'j' to find the corresponding date in the list of dates.
            if value == '':
                intval = 0
            else:
                intval = int(value)
            new_value = int(data_map[country][data_type][dates[j]]) + intval
            data_map[country][data_type][dates[j]] = f"{new_value}"

    return data_map


# Fetch the confirmed cases data.
r = requests.get(cases_url)
# The response (r) from the website contains, in its 'text' attribute, the raw data.
# The raw data is in CSV (Comma Separated Value) format, a row per line.
# Split the raw data into separate lines, giving a list of rows.
cases_csv: List[str] = r.text.splitlines()
data_map: Dict[str, Dict[str, Any]] = process_csv('cases', cases_csv)

# Fetch the deaths data.
r = requests.get(deaths_url)
deaths_csv: List[str] = r.text.splitlines()
data_map = process_csv('deaths', deaths_csv, data_map)

# Fetch the recovered cases data.
r = requests.get(recovered_url)
recovered_csv: List[str] = r.text.splitlines()
data_map = process_csv('recovered', recovered_csv, data_map)

countries = [
    "Albania", "Andorra", "Austria", "Belgium", "Bosnia and Herzegovina",
    "Bulgaria", "Croatia", "Cyprus", "Czechia", "Denmark", "Estonia", "Finland",
    "France", "Germany", "Gibraltar", "Greece", "Holy See", "Hungary", "Iceland",
    "Ireland", "Italy", "Kosovo", "Latvia", "Liechtenstein", "Lithuania",
    "Luxembourg", "Malta", "Monaco", "Montenegro", "Netherlands",
    "North Macedonia", "Norway", "Poland", "Portugal", "Romania", "San Marino",
    "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland",
    "United Kingdom",
]

filtered_map = {}
for country in data_map:
    if country not in countries:
        continue
    filtered_map[country] = data_map[country]

pprint.pprint(filtered_map)
