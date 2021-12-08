from flask import Flask, render_template, current_app, request, make_response
from flask_socketio import SocketIO
import helper_functions
import pymongo
import sys
import bcrypt

myclient = pymongo.MongoClient('mongo', 27017)
userdatabase = myclient["accounts"]
userCollection = userdatabase['users']

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


if __name__ == '__main__':
    socketio.run(app)