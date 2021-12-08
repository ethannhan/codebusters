from flask import Flask, render_template, current_app, request, redirect, url_for, flash
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
import os

UPLOAD_PATH = "./profile_pictures"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_PATH'] = UPLOAD_PATH
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
    return current_app.send_static_file('login.html')

@app.route('/register', methods=['post', 'get'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
    return current_app.send_static_file('register.html')


@app.route("/image-upload", methods=["POST", "GET"])
def profile_picture():
    uploaded_file = request.files["file"]
    print("filename is: {}".format(uploaded_file.filename))
    filename = secure_filename(uploaded_file.filename)
    if filename:
        print("filename is: {}".format(uploaded_file.filename))
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return redirect("http://localhost:5000")



if __name__ == '__main__':
    socketio.run(app)
