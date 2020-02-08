# Read data from data.py and save it into JSON
import data
import json

data_dict = dict()

data_dict['teachers'] = data.teachers
data_dict['goals'] = data.goals
data_dict['days_of_week'] = data.days_of_week
data_dict['available_time'] = data.available_time

with open('data.json', 'w') as f:
    json.dump(data_dict, f)