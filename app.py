from flask import Flask, render_template

app = Flask(__name__)


# Main page
@app.route('/')
def main():

    return render_template('index.html')


# Page with result according to a goal of studying
@app.route('/goals/<goal>/')
def get_goal(goal):
    return render_template('goal.html')


# Teacher's profile
@app.route('/profiles/<id_teacher>/')
def get_profile(id_teacher):
    return render_template('profile.html')


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