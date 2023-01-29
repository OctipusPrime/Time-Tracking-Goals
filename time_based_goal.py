import datetime
import json

import requests
from base64 import b64encode
from datetime import timedelta, date
import time
import csv


def time_conversion(sec):
    hour_value = sec // 3600
    minute_value = (sec - (hour_value * 3600)) // 60
    # make sure there are always at least 2 digits, prepending 0 if necessary
    return '{:02d}'.format(hour_value), '{:02d}'.format(minute_value)

# get today's date in UNIX timestamp
today = int(time.time())
# get beginning of month in unix timestamp
date_time = datetime.datetime(datetime.date.today().year, datetime.date.today().month, 1, 0, 0, 0)
month_start = int(time.mktime(date_time.timetuple()))

# fetch json data from toggl
with open("/Users/yanbarta/toggl_api_token.txt", "r") as api_token:
    token = api_token.read()
data = requests.get('https://api.track.toggl.com/api/v9/me/time_entries', params={'since': {month_start}}, headers={'content-type': 'application/json', 'Authorization' : 'Basic %s' % b64encode(bytes(token + ':api_token','ascii')).decode("ascii")})
obj = data.json()

# Go through the entries and add up the time spent on them
totals = {}
for entry in obj:
    if entry['start'][0:7] != f"{date.today().year}-{'{:02d}'.format(date.today().month)}" or entry['server_deleted_at'] is not None:
        continue
    if entry["description"] in totals:
        totals[entry["description"]] = totals[entry["description"]] + entry["duration"]
    else:
        totals[entry["description"]] = entry["duration"]


# reformat into human friendly format
hh_mmformat = {}
for category in totals:
    hh_mmformat[category] = time_conversion(int(totals[category]))
print(hh_mmformat)

# Get last version of the tracking file inside of Obsidian
file = "/Users/yanbarta/Library/Mobile Documents/iCloud~md~obsidian/Documents/The Foundation/Projects/Time tracking goals.md"
tracking_file = open(file, "r")
new = []
previously = tracking_file.readlines()
for line in previously:
    # check for an errand free line top or bottom
    if line == '\n':
        continue
    # Find first occurrence of ":"
    index = line.find(":")
    # Get tracked timer
    tracked = line[6:index]
    # save whether it was marked as completed
    ticked = "x" if line[3] == "x" else " "
    goal = tuple([x for x in line[-6:-1].split(":")])
    if tracked in hh_mmformat.keys():
        # get how much was supposed to be tracked
        currently = hh_mmformat[tracked]
    else:
        currently = ('00', '00')
    new.append([ticked, tracked, currently, goal])
tracking_file.close()
writing_file = open(file, "w")
# rewrite the file in a prescribed format
for row in new:
    writing_file.write(f"- [{row[0]}] {row[1]}: {row[2][0]}:{row[2][1]} / {row[3][0]}:{row[3][1]}\n")
writing_file.close()