from flask import Flask, render_template, current_app
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def hello_world():  # put application's code here
    users = ['sam', 'hakeem', 'ethan']
    return render_template('index.html', members=users)

@app.route('/login')
def login():
    return current_app.send_static_file('login.html')

@app.route('/register')
def register():
    return current_app.send_static_file('register.html')


if __name__ == '__main__':
    socketio.run(app)
