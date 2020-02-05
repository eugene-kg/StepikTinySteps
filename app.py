from flask import Flask, render_template, abort
import json

app = Flask(__name__)


class Teacher:
    def __init__(self):
        # File is not very big, so I download it into memory
        with open('data.json', 'r') as f:
            data = json.load(f)

        self.goals = data['goals']
        self.teachers = data['teachers']

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
    return render_template('goal.html')


# Teacher's profile
@app.route('/profiles/<id_teacher>/')
def get_profile(id_teacher):
    id_teacher = int(id_teacher)
    teacher = Teacher().get_teacher(id_teacher)
    if 'id' not in teacher:
        abort(404, description="Teacher not found")

    # Re-arranging dictionary of teacher time-table to simplify logic in the template
    time_table = dict()
    for DoW, time_statue in teacher['free'].items():
        for tm, status in time_statue.items():
            if tm in time_table:
                time_table[tm][DoW] = status
            else:
                time_table[tm] = {DoW: status}

    return render_template('profile.html', teacher=teacher, goals=Teacher().goals, time_table=time_table)


# Request for a teacher
@app.route('/request/')
def request_for_teacher():
    return render_template('request.html')


# Request for a teacher was received
@app.route('/request_done/')
def request_done():
    return render_template('request_done.html')


# Form for booking a teacher
@app.route('/booking/<id_teacher>/<day_of_week>/<time_of_day>/')
def booking_teacher(id_teacher, day_of_week, time_of_day):
    return render_template('booking.html')


# Booking request was received
@app.route('/booking_done/')
def booking_done():
    return render_template('booking_done.html')


@app.errorhandler(404)
def not_found(e):
    return "Ничего не нашлось! Вот неудача, отправляйтесь на главную!"


@app.errorhandler(500)
def server_error(e):
    return "Что-то не так, но мы все починим"


# Flask server (for debugging)
app.run()


# Run server with gunicorn
#if __name__ == '__main__':
#    app.run()