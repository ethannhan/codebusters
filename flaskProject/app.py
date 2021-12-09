from flask import Flask, render_template, send_from_directory, current_app, request, redirect, url_for, flash
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
import os
import secrets

UPLOAD_FOLDER = "./profile_pictures"
from flask import Flask, render_template, current_app, request, make_response
from flask_socketio import SocketIO
import helper_functions
import pymongo
import sys
import bcrypt

myclient = pymongo.MongoClient('mongo', 27017)
userdatabase = myclient["accounts"]
userCollection = userdatabase['users']
tokenCollection = userdatabase['tokens']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
    resp = make_response(current_app.send_static_file('login.html'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if userCollection.find_one({'username': username}) is not None:
            print("account found", file=sys.stderr)
            user = userCollection.find_one({'username': username})
            if bcrypt.checkpw(password.encode(), user['password']):
                print("logged in", file=sys.stderr)
                token = secrets.token_urlsafe(80)
                tokenh = bcrypt.hashpw(token.encode(), bcrypt.gensalt())
                build_entry = {'username': username, 'token': tokenh}
                tokenCollection.insert_one(build_entry)
                resp.set_cookie('username', username)
                resp.set_cookie('token', token)
    return resp

@app.route('/register', methods=['post', 'get'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_entry = helper_functions.create_account(username, password)
        userCollection.insert_one(user_entry)
        print("you made an account", file=sys.stderr)
        #put code for front end
    return current_app.send_static_file('register.html')


@app.route("/image-upload", methods=["POST", "GET"])
def profile_picture():
    uploaded_file = request.files["file"]
    print("filename is: {}".format(uploaded_file.filename))
    filename = secure_filename(uploaded_file.filename)
    if filename:
        print("filename is: {}".format(uploaded_file.filename))
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for("uploaded_file", filename=filename))


@app.route('/show/<filename>')
def uploaded_file(filename):
    filename = 'http://127.0.0.1:5000/uploads/' + filename
    return render_template('index.html', filename=filename)


@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    socketio.run(app)