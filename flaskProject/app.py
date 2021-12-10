from werkzeug.utils import secure_filename
import os
import secrets

UPLOAD_FOLDER = "./static/uploads"
from flask import Flask, render_template, current_app, request, make_response, redirect
from flask_socketio import SocketIO
import helper_functions
import pymongo
import sys
import bcrypt

myclient = pymongo.MongoClient('mongo', 27017)
userdatabase = myclient["accounts"]
userCollection = userdatabase['users']
tokenCollection = userdatabase['tokens']
statusCollection = userdatabase['statuses']
imagesCollection = userdatabase["images"]


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["TEMPLATES_AUTO_RELOAD"] = True
socketio = SocketIO(app)

users = []
sids = {}
statusmessage = []

@socketio.on('connect')
def test_connect(auth):
    username = request.cookies.get('username')
    sid = request.sid
    print(username, file=sys.stderr)
    if username is not None:
        users.append(username)
        sids[username] = sid
    print(request.sid, file=sys.stderr)
    print('connected', file=sys.stderr)


@socketio.on('disconnect')
def test_disconnect():
    username = request.cookies.get('username')
    if username is not None:
        users.remove(username)
    print('Client disconnected', file=sys.stderr)


@socketio.on('dm')
def dm(data):
    username = request.cookies.get('username')
    message = data[0]
    receiver = data[1]
    message = helper_functions.clean_inputs(message)
    print(message, file=sys.stderr)
    print(sids[receiver], file=sys.stderr)
    message = username + " has DMed you! they said: " + message
    socketio.emit('send dm', message, to=sids[receiver])

@socketio.on('statusmessage')
def dm(data):
   messagestr= str(request.cookies.get('username')) + "- "
   messagestr += str(data)
   #statusmessage[request.cookies.get('username')] = data
   statusmessage.append(messagestr)
   print(statusmessage, file=sys.stderr)


@app.route('/', methods=['post', 'get'])
def hello_world():
    all_image_names = []
    new_html = []
    for image in imagesCollection.find({}):
        all_image_names.append(image["file"])
    with open("./templates/index.html") as f:
        for line in f.readlines():
            if "<!--{{html_images}}-->" in line:
                new_html.append(line)
                for image in all_image_names[::-1]:
                    # TODO - check if file is downloaded locally !!!
                    html_image_path = "../static/uploads/" + image
                    os_image_path = "./static/uploads/" + image
                    print(os.path.exists(os_image_path))
                    if os.path.exists(os_image_path):
                        new_html.append("<img src=" + html_image_path + " height='60' width='60'><p>\n")
            elif "<img src" in line:
                continue
            else:
                new_html.append(line)
    with open("./templates/index.html", 'w') as f:
        for line in new_html:
            f.write(line)
    return render_template('index.html', members=users, statuschat=statusmessage)

@app.route('/login', methods=['post', 'get'])
def login():
    resp = make_response(current_app.send_static_file('login.html'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        username = helper_functions.clean_inputs(username)
        password = helper_functions.clean_inputs(password)
        if userCollection.find_one({'username': username}) is not None:
            print("account found", file=sys.stderr)
            user = userCollection.find_one({'username': username})
            if bcrypt.checkpw(password.encode(), user['password']):
                for d in statusCollection.find({}):
                    if d.get('username') == username:
                        status = d.get('status')
                        resp.set_cookie('status', status, max_age=60 * 60 * 24, httponly=True)
                print("logged in", file=sys.stderr)
                token = secrets.token_urlsafe(80)
                tokenh = bcrypt.hashpw(token.encode(), bcrypt.gensalt())
                build_entry = {'username': username, 'token': tokenh}
                tokenCollection.insert_one(build_entry)
                resp.set_cookie('username', username, max_age=60 * 60 * 24, httponly=True)
                resp.set_cookie('token', token, max_age=60 * 60 * 24, httponly=True)
    return resp

@app.route('/register', methods=['post', 'get'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        username = helper_functions.clean_inputs(username)
        password = helper_functions.clean_inputs(password)
        user_entry = helper_functions.create_account(username, password)
        userCollection.insert_one(user_entry)
        print("you made an account", file=sys.stderr)
        #put code for front end
    return current_app.send_static_file('register.html')

@app.route('/status', methods=['POST', 'GET'])
def set_status():
    resp = make_response(current_app.send_static_file('status.html'))
    if request.method == 'POST':
        print('here', file=sys.stderr)
        print(request.form.get('status'), file=sys.stderr)
        status = request.form.get('status')
        status = helper_functions.clean_inputs(status)
        username = request.cookies.get('username')
        token = request.cookies.get('token')
        for t in tokenCollection.find({}):
            if t.get('username') == username:
                if bcrypt.checkpw(token.encode(), t.get('token')):
                    statusCollection.insert_one({'username': username, 'status': status})
                    resp.set_cookie('status', status, max_age=60 * 60 * 24, httponly=True)
    return resp


@app.route("/image-upload", methods=["POST"])
def upload_image():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    imagesCollection.insert_one({"file": filename})
    return redirect("http://localhost:5000/")


if __name__ == '__main__':
    socketio.run(app)