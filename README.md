---
alias: "Time based goals"
type: project
area: ["coding"]
description: "Fetch Timery data and update goals"
---
Project start date: [[2022-09-17]] 

# Opening

## What are your thoughts about this?

In [[2022-08 August]] I didn't accomplish my goals while I believed that I put more than enough effort in. It would have been better to have time based goals which can be accomplished no matter how large a task one is working on.

### Why are you doing it?

To put in the effort AND feel good about it. 

### Describe the completed project:

There are automatically updated goals in my monthly note in [[Obsidian]] which pulls data from Toggl and fills in how much I actually worked on a thing. 

## How do you solve it?

I think this could be a background [[UNIX]] process that runs every hour or... let's start with it running every time I run the Briefing [[Keyboard Maestro]] shortcut. Then there would be a [[Python]] script which finds the appropriate string in a specified file, gets how much time was tracked for the specific entry and rewrites the file with the updated value. Oh and it for sure makes a backup first. I don't want to be losing data. 


# Plans

## Next steps #project/back-burner #day/on  

- [x] Figure out how to get time track this month for specific description
- [x] Figure out how to rewrite text file with a single line changed
	- [x] What format to use?
- [x] Automate
- [x] Figure out time blocking



# Progress:



---

### [[2023-01-28]] 

Prepared snippet for [[Time Blocking]]  if I commit to it in the future.

```python

def evaluate_timeblocks(fields, rows, data_dic):  
    # loop through rows and find matching data entries in data_dic  
    #   
# csv file name  
filename = "/Users/yanbarta/Library/Mobile Documents/iCloud~is~workflow~my~workflows/Documents/time_blocks.csv"  
  
# initializing the titles and rows list  
fields = []  
rows = []  
  
# reading csv file  
with open(filename, 'r') as csvfile:  
    # creating a csv reader object    csvreader = csv.reader(csvfile)  
    # extracting field names through first row    fields = next(csvreader)  
    # extracting each data row one by one    for row in csvreader:        rows.append(row
```


---

### [[2023-01-27]] 

Functioning version in case I somehow mess up: 
```python
import datetime  
import json  
  
import requests  
from base64 import b64encode  
from datetime import timedelta, date  
import time  
  
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
data = requests.get('https://api.track.toggl.com/api/v9/me/time_entries', params={'since': {month_start}}, headers={'content-type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(b'...:api_token').decode("ascii")})  
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
  
file = "/Users/yanbarta/Library/Mobile Documents/iCloud~md~obsidian/Documents/The Foundation/Projects/Time tracking goals.md"  
print(hh_mmformat)  
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
for row in new:  
    writing_file.write(f"- [{row[0]}] {row[1]}: {row[2][0]}:{row[2][1]} / {row[3][0]}:{row[3][1]}\n")  
writing_file.close()  
  
#print("Worked fine")
```


### [[2022-11-26]] 


Managed to get it all working. Here is the code so far, let's see if there are any bugs. 

```python
import datetime
import json

import requests
from base64 import b64encode
from datetime import timedelta, date
import time

def time_conversion(sec):
   hour_value = sec // 3600
   min = (sec - (hour_value * 3600)) // 60
   return hour_value, min

# get today's date in UNIX timestamp
today = int(time.time())
# get beginning of month in unix timestamp
date_time = datetime.datetime(datetime.date.today().year, datetime.date.today().month, 1, 0, 0, 0)
month_start = int(time.mktime(date_time.timetuple()))

# fetch json data from toggl
data = requests.get('https://api.track.toggl.com/api/v9/me/time_entries', params={'since': {month_start}}, headers={'content-type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(b'...:api_token').decode("ascii")})
obj = data.json()

# Go through the entries and add up the time spent on them
totals = {}
for entry in obj:
    if entry['start'][0:7] != f"{date.today().year}-{date.today().month}" or entry['server_deleted_at'] is not None:
        continue
    if entry["description"] in totals:
        totals[entry["description"]] = totals[entry["description"]] + entry["duration"]
    else:
        totals[entry["description"]] = entry["duration"]


# reformat into human friendly format
hh_mmformat = {}
for category in totals:
    hh_mmformat[category] = time_conversion(int(totals[category]))

file = "/Users/yanbarta/Library/Mobile Documents/iCloud~md~obsidian/Documents/The Foundation/Projects/Time tracking goals.md"
print(hh_mmformat)
tracking_file = open(file, "r")
new = []
previously = tracking_file.readlines()
for line in previously:
    # Find first occurrence of ":"
    index = line.find(":")
    # Get tracked timer
    tracked = line[6:index]
    ticked = "x" if line[3] == "x" else " "
    if tracked in hh_mmformat.keys():
        # get how much was supposed to be tracked
        goal = tuple([x for x in line[-6:-1].split(":")])
        currently = hh_mmformat[tracked]
        new.append([ticked, tracked, currently, goal])
tracking_file.close()
writing_file = open(file, "w")
for row in new:
    writing_file.write(f"- [{row[0]}] {row[1]}: {row[2][0]}:{row[2][1]} / {row[3][0]}:{row[3][1]}\n")
writing_file.close()

#print("Worked fine")
```


---


---

### [[2022-11-19]] 

Got another dig at it and managed to fix the bug with time tracking, so now there is a precise number of our as shown in Timery. (The problem was that even deleted and modified entries were pulled and accounted for).

Managed to read the file and save whatever I am tracking.



### [[2022-10-09]] 

Code for fetching toggle data is done: 

```python
import datetime  
import json  
  
import requests  
from base64 import b64encode  
from datetime import timedelta, date  
import time  
  
# get today's date in UNIX timestamp  
today = int(time.time())  
# get beginning of month in unix timestamp  
date_time = datetime.datetime(datetime.date.today().year, datetime.date.today().month, 1, 0, 0, 0)  
month_start = int(time.mktime(date_time.timetuple()))  
print(month_start)  
  
#data = requests.get(f"https://api.track.toggl.com/reports/api/v2/details?workspace_id=4152190&since={month_start}&until={today}&user_agent=brthonza@gmail.com", headers={'content-type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(b'82e7cd357aff2d77d068e18d324eb43f:api_token').decode("ascii")})  
# fetch json data from toggl  
data = requests.get('https://api.track.toggl.com/api/v9/me/time_entries', params= {'since': {month_start}, 'until': {today}}, headers={'content-type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(b'...:api_token').decode("ascii")})  
print(data.json())  
#print(data.json())  
obj = data.json()  
  
  
totals = {}  
  
# go through the entries and add up time spent on them  
for entry in obj:  
    print(f"Entry name: {entry['description']}, duration: {entry['duration']}")  
    if entry["description"] in totals:  
        totals[entry["description"]] = totals[entry["description"]] + entry["duration"]  
    else:  
        totals[entry["description"]] = entry["duration"]  
  
# reformat into human friendly format  
for category in totals:  
    totals[category] = time.strftime("%H:%M", time.gmtime(totals[category]))  
    #totals[category] = str(timedelta(seconds=totals[category]))  
  
  
print(totals)
```


### [[2022-09-17]] 

Made plans. 
