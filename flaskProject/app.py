from flask import Flask, render_template, current_app, request, make_response, send_from_directory, redirect, url_for, flash
from flask_socketio import SocketIO
import helper_functions
import pymongo
import sys
import bcrypt
import os
from werkzeug.utils import secure_filename


myclient = pymongo.MongoClient('localhost', 27017)
userdatabase = myclient["accounts"]
userCollection = userdatabase['users']

UPLOAD_FOLDER = "./static/uploads"

tokenCollection = userdatabase['tokens']
statusCollection = userdatabase['statuses']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)


@socketio.on('connect')
def test_connect(auth):
    print('connected')


@app.route('/')
def hello_world():
    users = ['sam', 'hakeem', 'ethan', "nitya"]
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
        resp.set_cookie('username', username)
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


@app.route('/status', methods=['POST', 'GET'])
def set_status():
    print("cookies are: {}".format(request.cookies))
    resp = make_response(current_app.send_static_file('status.html'))
    if request.method == 'POST':
        print('here', file=sys.stderr)
        print(request.form.get('status'), file=sys.stderr)
        status = request.form.get('status')
        username = request.cookies.get('username')
        token = request.cookies.get('token')
        for t in tokenCollection.find({}):
            if t.get('username') == username:
                if bcrypt.checkpw(token.encode(), t.get('token')):
                    statusCollection.insert_one({'username': username, 'status': status})
                    resp.set_cookie('status', status)
    return resp


@app.route('/', methods=['POST'])
def upload_image():
    print("cookies are: {}".format(request.cookies))
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('index.html', filename=filename)
    else:
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == '__main__':
    socketio.run(app)