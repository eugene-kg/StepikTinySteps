import os
import json
import random

from flask import Flask, render_template, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tiny_steps.db"
db = SQLAlchemy(app)
migrate = Migrate(app=app, db=db)

teacher_goal_association = db.Table(
    'teacher_goal_association',
    db.Column('goal', db.String(20), db.ForeignKey('dic_goals.goal'),
              nullable=False, primary_key=True),
    db.Column('id_teacher', db.Integer, db.ForeignKey('teachers.id'),
              nullable=False, primary_key=True)
)


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    about = db.Column(db.String(500))
    rating = db.Column(db.Float)
    picture = db.Column(db.String(500))
    price = db.Column(db.Integer)
    free = db.Column(db.String(2000))

    goals = db.relationship('Goal', secondary=teacher_goal_association,
                            back_populates='teachers')
    bookings = db.relationship('Booking', back_populates='teacher')


class AvailableTime(db.Model):
    __tablename__ = 'dic_available_time'

    time_key = db.Column(db.String(10), primary_key=True)
    rus_name = db.Column(db.String(100))


class DaysOfWeek(db.Model):
    __tablename__ = 'dic_days_of_week'

    weekday_key = db.Column(db.String(3), primary_key=True)
    rus_name = db.Column(db.String(50))
    rus_short_name = db.Column(db.String(2))


class DicGoals(db.Model):
    __tablename__ = 'dic_goals'

    goal = db.Column(db.String(20), primary_key=True)
    rus_name = db.Column(db.String(50))
    emblem = db.Column(db.String(100))

    teachers = db.relationship('Teacher', secondary=teacher_goal_association,
                               back_populates='goals')


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    id_teacher = db.Column(db.Integer, db.ForeignKey('teachers.id'),
                           nullable=False)
    weekday_key = db.Column(db.String(3),
                            db.ForeignKey('dic_days_of_week.weekday_key'),
                            nullable=False)
    time_of_day = db.Column(db.String(10), nullable=False)

    teacher = db.relationship('Teacher', back_populates='bookings')
    weekday = db.relationship('DaysOfWeek')

    __table_args__ = (db.Index('teacher_weekday_tod_idx',
                               id_teacher,
                               weekday_key,
                               time_of_day,
                               unique=True),)

class RequestForTeacher(db.Model):
    __tablename__ = 'requests_for_teacher'
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String(20), db.ForeignKey('dic_goals.goal'), nullable=False)
    time = db.Column(db.String(10), db.ForeignKey('dic_available_time.time_key'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    client_phone = db.Column(db.String(50), nullable=False)

    goal_description = db.relationship('DicGoals')
    available_time = db.relationship('AvailableTime')

    __table_args__ = (db.UniqueConstraint(goal,
                                          time,
                                          client_name,
                                          client_phone,
                                          name='client_goal_uix'),)


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


@app.route('/')
def main():
    """
    Main page: contains main menu and list of random teachers
    :return: render main page
    """
    data = Data()
    teachers = data.teachers
    random.shuffle(teachers)
    return render_template('index.html',
                           goals=data.goals,
                           teachers=teachers)


@app.route('/goals/<goal>/')
def goal(goal):
    """
    Show list of teacher which can help to train for a specific goal
    :param goal: goal of studying
    :return: page with list of teachers
    """
    data = Data()

    # Keep only teachers who has the goal in their list of goals
    teachers_with_goal = list(filter(lambda t: goal in t['goals'],
                                     data.teachers))

    return render_template('goal.html',
                           teachers=teachers_with_goal,
                           goal=goal,
                           goals=data.goals)


@app.route('/profiles/<id_teacher>/')
def get_profile(id_teacher):
    """
    Teacher's profile
    :param id_teacher: id of teacher
    :return:
    """
    id_teacher = int(id_teacher)
    data = Data()
    teacher = data.get_teacher(id_teacher)
    if 'id' not in teacher:
        abort(404, description="Teacher not found")

    # Re-arranging dictionary of teacher time-table
    # to simplify logic in the template
    time_table = dict()
    for weekday_key, time_status in teacher['free'].items():
        for time_of_day, status in time_status.items():
            if time_of_day in time_table:
                time_table[time_of_day][weekday_key] = status
            else:
                time_table[time_of_day] = {weekday_key: status}

    return render_template('profile.html',
                           teacher=teacher,
                           goals=data.goals,
                           time_table=time_table)


@app.route('/request/')
def request_for_teacher():
    """
    Open form with request for a teacher
    :return:
    """
    data = Data()
    return render_template('request.html',
                           goals=data.goals,
                           available_time=data.available_time)


@app.route('/request_done/', methods=["POST"])
def request_done():
    """
    Process data from request for a teacher
    :return:
    """
    request_goal = request.form.get('goal')
    request_time = request.form.get('time')
    client_name = request.form.get('clientName')
    client_phone = request.form.get('clientPhone')

    request_details = dict()
    request_details['goal'] = request_goal
    request_details['time'] = request_time
    request_details['client_name'] = client_name
    request_details['client_phone'] = client_phone

    request_file_path = 'request.json'
    request_data = list()

    # Check if file for booking exists
    if os.path.exists(request_file_path):
        with open(request_file_path, "r") as f:
            request_data = json.load(f)

    request_data.append(request_details)
    with open(request_file_path, 'w') as f:
        json.dump(request_data, f)

    data = Data()
    return render_template('request_done.html',
                           request_details=request_details,
                           available_time=data.available_time,
                           goals=data.goals)


@app.route('/booking/<id_teacher>/<weekday_key>/<time_of_day>/')
def booking_teacher(id_teacher, weekday_key, time_of_day):
    """
    Form for booking a teacher
    :param id_teacher:
    :param weekday_key:
    :param time_of_day:
    :return:
    """
    data = Data()
    teacher = data.get_teacher(int(id_teacher))
    if 'id' not in teacher:
        abort(404, description="Teacher not found")
    day_of_week = data.days_of_week[weekday_key]

    return render_template('booking.html',
                           teacher=teacher,
                           time_of_day=time_of_day,
                           day_of_week=day_of_week)


@app.route('/booking_done/', methods=['POST'])
def booking_done():
    """
    Process booking of a teacher
    :return:
    """
    weekday_key = request.form.get('clientWeekday')
    time_of_day = request.form.get('clientTime')
    id_teacher = request.form.get('clientTeacher')
    client_name = request.form.get('clientName')
    client_phone = request.form.get('clientPhone')

    new_booking = dict()
    booking_key = '{}_{}_{}'.format(id_teacher, weekday_key, time_of_day)

    new_booking['weekday_key'] = weekday_key
    new_booking['time_of_day'] = time_of_day
    new_booking['id_teacher'] = id_teacher
    new_booking['client_name'] = client_name
    new_booking['client_phone'] = client_phone

    booking_file_path = 'booking.json'
    data = dict()

    # Check if file for booking exists and create it if not
    if os.path.exists(booking_file_path):
        with open(booking_file_path, "r") as f:
            data = json.load(f)

    data[booking_key] = new_booking
    with open(booking_file_path, 'w') as f:
        json.dump(data, f)

    day_of_week = Data().days_of_week[weekday_key]

    return render_template('booking_done.html',
                           day_of_week=day_of_week,
                           client_name=client_name,
                           client_phone=client_phone,
                           time_of_day=time_of_day)


@app.errorhandler(404)
def not_found(e):
    return "Ничего не нашлось! Вот неудача, отправляйтесь на главную!"


@app.errorhandler(500)
def server_error(e):
    return "Что-то не так, но мы все починим"


# Flask server (for debugging)
app.run()

# Run server with gunicorn
# if __name__ == '__main__':
#    app.run()
