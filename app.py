import os
import json
import random

from flask import Flask, render_template, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField
from wtforms.validators import InputRequired, Length
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tiny_steps.db"
app.secret_key = 'fdopa7435nhf&%%$)(nf'
db = SQLAlchemy(app)
migrate = Migrate(app=app, db=db)
csrf = CSRFProtect(app)


teacher_goal_association = db.Table(
    'teacher_goal_association',
    db.Column('goal_key', db.String(20), db.ForeignKey('dic_goals.goal_key'),
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

    goals = db.relationship('DicGoals', secondary=teacher_goal_association,
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

    goal_key = db.Column(db.String(20), primary_key=True)
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
    client_name = db.Column(db.String(100), nullable=False)
    client_phone = db.Column(db.String(50), nullable=False)

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
    goal_key = db.Column(db.String(20), db.ForeignKey('dic_goals.goal_key'), nullable=False)
    time_key = db.Column(db.String(10), db.ForeignKey('dic_available_time.time_key'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    client_phone = db.Column(db.String(50), nullable=False)

    goal_description = db.relationship('DicGoals')
    available_time = db.relationship('AvailableTime')

    __table_args__ = (db.UniqueConstraint(goal_key,
                                          time_key,
                                          client_name,
                                          client_phone,
                                          name='client_goal_uix'),)


class BookingForm(FlaskForm):
    weekday_key = StringField('clientWeekday')
    time_of_day = StringField('clientTime')
    id_teacher = IntegerField('clientTeacher')
    client_name = StringField('Вас зовут', [InputRequired(message="Укажите ваше имя"), Length(min=1)])
    client_phone = StringField('Ваш телефон', [InputRequired(message="Укажите ваш телефон")])


class Data:
    def __init__(self):
        self.__goals = db.session.query(DicGoals)
        self.__days_of_week = db.session.query(DaysOfWeek)
        self.__teachers = db.session.query(Teacher)
        self.__available_time = db.session.query(AvailableTime)

    @property
    def goals(self):
        return self.__goals.all()

    @property
    def days_of_week(self):
        return self.__days_of_week.all()

    @property
    def teachers(self):
        return self.__teachers.all()

    @property
    def available_time(self):
        return self.__available_time.all()

    def get_teacher(self, id_teacher):
        teacher = self.__teachers.filter_by(id=id_teacher).first()
        return teacher

    def get_goal(self, goal_key):
        goal = self.__goals.filter_by(goal_key=goal_key).first()
        return goal

    def get_day_of_week(self, weekday_key):
        day_of_week = self.__days_of_week.filter_by(weekday_key=weekday_key).first()
        return day_of_week


class RequestForm(FlaskForm):

    goals = Data().goals
    available_time = Data().available_time

    goal_key = RadioField('Какая цель занятий?', choices=[(goal.goal_key, goal.rus_name) for goal in goals])
    time_key = RadioField('Какая цель занятий?', choices=[(tm.time_key, tm.rus_name) for tm in available_time])
    client_name = StringField('Вас зовут', [InputRequired(message="Укажите ваше имя"), Length(min=1)])
    client_phone = StringField('Ваш телефон', [InputRequired(message="Укажите ваш телефон")])


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


@app.route('/goal/<goal_key>/')
def goal(goal_key):
    """
    Show list of teacher which can help to train for a specific goal
    :param goal_key: goal of studying
    :return: page with list of teachers
    """
    data = Data()
    goal = data.get_goal(goal_key)

    # Keep only teachers who has the goal in their list of goals
    gl: object
    teachers_with_goal = list(filter(
        lambda t: goal.goal_key in [gl.goal_key for gl in t.goals],
        data.teachers))

    return render_template('goal.html',
                           teachers=teachers_with_goal,
                           goal=goal)


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
    if not teacher:
        abort(404, description="Teacher is not found")

    # Re-arranging dictionary of teacher time-table
    # to simplify logic in the template
    time_table = dict()
    time_table_data = json.loads(teacher.free)
    for weekday_key, time_status in time_table_data.items():
        for time_of_day, status in time_status.items():
            if time_of_day in time_table:
                time_table[time_of_day][weekday_key] = status
            else:
                time_table[time_of_day] = {weekday_key: status}

    return render_template('profile.html',
                           teacher=teacher,
                           goals=data.goals,
                           time_table=time_table)


@app.route('/request/', methods=['POST', 'GET'])
def request_for_teacher():
    """
    Open form with request for a teacher
    :return:
    """
    data = Data()
    request_form = RequestForm()

    if request.method == 'POST':
        if request_form.validate_on_submit():
            rq_for_teacher = RequestForTeacher()

            rq_for_teacher.goal_key = request_form.goal_key.data
            rq_for_teacher.time_key = request_form.time_key.data
            rq_for_teacher.client_name = request_form.client_name.data
            rq_for_teacher.client_phone = request_form.client_phone.data

            db.session.add(rq_for_teacher)
            db.session.commit()

            return render_template('request_done.html',
                                   request_details=rq_for_teacher,
                                   available_time=data.available_time,
                                   goals=data.goals)

    return render_template('request.html',
                           goals=data.goals,
                           available_time=data.available_time,
                           form=request_form)


@app.route('/request_done/', methods=["POST"])
def request_done():
    """
    Process data from request for a teacher
    :return:
    """
    request_goal_key = request.form.get('goal_key')
    request_time = request.form.get('time_key')
    client_name = request.form.get('clientName')
    client_phone = request.form.get('clientPhone')

    request_details = dict()
    request_details['goal_key'] = request_goal_key
    request_details['time_key'] = request_time
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


@app.route('/booking/<id_teacher>/<weekday_key>/<time_of_day>/', methods=['POST', 'GET'])
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
    if not teacher:
        abort(404, description="Teacher is not found")
    day_of_week = data.get_day_of_week(weekday_key)

    booking_form = BookingForm()

    if request.method == 'POST':

        booking = Booking()

        if booking_form.validate_on_submit():
            booking.id_teacher = id_teacher
            booking.time_of_day = time_of_day
            booking.weekday_key = day_of_week.weekday_key
            booking.client_name = booking_form.client_name.data
            booking.client_phone = booking_form.client_phone.data

            db.session.add(booking)
            db.session.commit()

            return render_template('booking_done.html',
                                   day_of_week=booking.weekday,
                                   client_name=booking.client_name,
                                   client_phone=booking.client_phone,
                                   time_of_day=booking.time_of_day)

    return render_template('booking.html',
                           teacher=teacher,
                           time_of_day=time_of_day,
                           day_of_week=day_of_week,
                           form=booking_form)


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
