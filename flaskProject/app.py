from flask import Flask, render_template, current_app, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@socketio.on('connect')
def test_connect(auth):
    print('connected')


@app.route('/')
def hello_world():  # put application's code here
    users = ['sam', 'hakeem', 'ethan']
    return render_template('index.html', members=users)

@app.route('/login', methods=['post', 'get'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username)
        print(password)
    return current_app.send_static_file('login.html')

@app.route('/register')
def register():
    return current_app.send_static_file('register.html')

@app.route("/profile_picture")
def profile_picture():



if __name__ == '__main__':
    socketio.run(app)
