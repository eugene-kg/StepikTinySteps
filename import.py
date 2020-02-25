from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from sqlalchemy.ext.automap import automap_base

Base = automap_base()

engine = create_engine("sqlite:///tiny_steps.db")
# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()

# reflect the tables
Base.prepare(engine, reflect=True)


class Data:
    def __init__(self):
        with open('data.json', 'r') as f:
            data = json.load(f)

        self.__goals = data['goals']
        self.__days_of_week = data['days_of_week']
        self.__teachers = data['teachers']
        self.__available_time = data['available_time']

    def get_teacher(self, id_teacher):
        teacher = list(filter(lambda t: t['id'] == 0, self.teachers))[0]

        return teacher

    @property
    def goals(self):
        return self.__goals

    @property
    def days_of_week(self):
        return self.__days_of_week

    @property
    def teachers(self):
        return self.__teachers

    @property
    def available_time(self):
        return self.__available_time


data = Data()

DicGoals = Base.classes.dic_goals
AvailableTime = Base.classes.dic_available_time
DaysOfWeek = Base.classes.dic_days_of_week
Teacher = Base.classes.teachers

for k in data.goals.keys():
    session.add(DicGoals(goal=k,
                         rus_name=data.goals[k]['rus_name'],
                         emblem=data.goals[k]['emblem']
                         ))

available_time = data.available_time

for k in available_time:
    session.add(AvailableTime(time_key=k,
                              rus_name=available_time[k]['rus_name']))

days_of_week = data.days_of_week
for k in days_of_week:
    session.add(DaysOfWeek(weekday_key=k,
                           rus_name=days_of_week[k]['rus_name'],
                           rus_short_name=days_of_week[k]['rus_short_name']))

teachers = data.teachers

for v in teachers:
    t = Teacher(
        name=v['name'],
        about=v['about'],
        rating=v['rating'],
        picture=v['picture'],
        price=v['price'],
        free=json.dumps(v['free'])
    )

    for g in v['goals']:
        goal = session.query(DicGoals).filter(DicGoals.goal == g).first()
        t.dic_goals_collection.append(goal)

    session.add(t)
