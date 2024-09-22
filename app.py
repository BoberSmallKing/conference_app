from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

conferences = {}

def generate_conference_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_conference')
def create_conference():
    conference_id = generate_conference_id()
    conferences[conference_id] = []
    return redirect(url_for('conference', conference_id=conference_id))

@app.route('/conference/<conference_id>')
def conference(conference_id):
    if conference_id not in conferences:
        return "Конференция не найдена", 404
    return render_template('conference.html', conference_id=conference_id)

@socketio.on('join')
def handle_join(data):
    conference_id = data['conference_id']
    username = data['username']
    conferences[conference_id].append(username)
    emit('user_joined', {'username': username, 'users': conferences[conference_id]}, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    emit('receive_message', data, broadcast=True)

@socketio.on('offer')
def handle_offer(data):
    emit('offer', data, room=data['to'])

@socketio.on('answer')
def handle_answer(data):
    emit('answer', data, room=data['to'])

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    emit('ice_candidate', data, room=data['to'])

if __name__ == '__main__':
    socketio.run(app)
