from flask import Flask, render_template, abort, request
import json
import os

app = Flask(__name__)


class Data:
    def __init__(self):
        # File is not very big, so I download it into memory
        with open('data.json', 'r') as f:
            data = json.load(f)

        self.goals = data['goals']
        self.days_of_week = data['days_of_week']
        self.teachers = data['teachers']
        self.available_time = data['available_time']

    def get_teacher(self, id_teacher):
        teacher = dict()
        for t in self.teachers:
            if t['id'] == id_teacher:
                teacher = t

        return teacher


# Main page
@app.route('/')
def main():
    return render_template('index.html')


# Page with result according to a goal of studying
@app.route('/goals/<goal>/')
def goal(goal):
    teachers = Data().teachers

    # Filling in a new list of teachers, using the condition that the goal is among the teacher goals
    teachers_with_goal = list()
    for teacher in teachers:
        if goal in teacher['goals']:
            teachers_with_goal.append(teacher)

    return render_template('goal.html', teachers=teachers_with_goal, goal=goal, goals=Data().goals)


# Teacher's profile
@app.route('/profiles/<id_teacher>/')
def get_profile(id_teacher):
    id_teacher = int(id_teacher)
    teacher = Data().get_teacher(id_teacher)
    if 'id' not in teacher:
        abort(404, description="Teacher not found")

    # Re-arranging dictionary of teacher time-table to simplify logic in the template
    time_table = dict()
    for weekday_key, time_status in teacher['free'].items():
        for time_of_day, status in time_status.items():
            if time_of_day in time_table:
                time_table[time_of_day][weekday_key] = status
            else:
                time_table[time_of_day] = {weekday_key: status}

    return render_template('profile.html', teacher=teacher, goals=Data().goals, time_table=time_table)


# Request for a teacher
@app.route('/request/')
def request_for_teacher():
    return render_template('request.html', goals=Data().goals, available_time=Data().available_time)


# Request for a teacher was received
@app.route('/request_done/', methods=["POST"])
def request_done():
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
    data = list()

    # Check if file for booking exists
    if os.path.exists(request_file_path):
        with open(request_file_path, "r") as f:
            data = json.load(f)

    data.append(request_details)
    with open(request_file_path, 'w') as f:
        json.dump(data, f)

    return render_template('request_done.html', request_details=request_details, available_time=Data().available_time,
                           goals=Data().goals)


# Form for booking a teacher
@app.route('/booking/<id_teacher>/<weekday_key>/<time_of_day>/')
def booking_teacher(id_teacher, weekday_key, time_of_day):
    teacher = Data().get_teacher(int(id_teacher))
    if 'id' not in teacher:
        abort(404, description="Teacher not found")
    day_of_week = Data().days_of_week[weekday_key]

    return render_template('booking.html', teacher=teacher, time_of_day=time_of_day, day_of_week=day_of_week)


# Booking request was received
@app.route('/booking_done/', methods=['POST'])
def booking_done():
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

    # Check if file for booking exists
    if os.path.exists(booking_file_path):
        with open(booking_file_path, "r") as f:
            data = json.load(f)

    data[booking_key] = new_booking
    with open(booking_file_path, 'w') as f:
        json.dump(data, f)

    day_of_week = Data().days_of_week[weekday_key]

    return render_template('booking_done.html', day_of_week=day_of_week, client_name=client_name,
                           client_phone=client_phone, time_of_day=time_of_day)


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
