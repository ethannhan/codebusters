from flask import Flask, render_template, current_app, request, make_response, send_from_directory, redirect, url_for, flash
from flask_socketio import SocketIO
import helper_functions
import pymongo
import sys
import bcrypt
import os
from werkzeug.utils import secure_filename


myclient = pymongo.MongoClient('localhost', 27017) #TODO mongo/localhost
userdatabase = myclient["accounts"]
userCollection = userdatabase['users']
imagesCollection = userdatabase["images"]
# imagesCollection.delete_many({})
# Store here,
# on "/", put all images to screen

UPLOAD_FOLDER = "./static/uploads"

tokenCollection = userdatabase['tokens']
statusCollection = userdatabase['statuses']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["TEMPLATES_AUTO_RELOAD"] = True
socketio = SocketIO(app)

users = []


@socketio.on('connect')
def test_connect(auth):
    username = request.cookies.get('username')
    print(username, file=sys.stderr)
    if username is not None:
        users.append(username)
    print('connected', file=sys.stderr)


@socketio.on('disconnect')
def test_disconnect():
    username = request.cookies.get('username')
    if username is not None:
        users.remove(username)
    print('Client disconnected', file=sys.stderr)


@app.route('/')
def hello_world():
    print("got here now dfsdgsf")
    all_image_names = []
    new_html = []
    for image in imagesCollection.find({}):
        print("image is : {}".format(image))
        all_image_names.append(image["file"])
    print("all image names are: {}".format(all_image_names))
    with open("./templates/index.html") as f:
        for line in f.readlines():
            if "<!--{{html_images}}-->" in line:
                new_html.append(line)

                for image in all_image_names:
                    # TODO - check if file is downloaded locally !!!
                    image_path = "../static/uploads/" + image
                    new_html.append("<img src=" + image_path + " height='60' width='60'>\n<p>")
            elif "<img src" in line:
                continue
            else:
                new_html.append(line)
    with open("./templates/index.html", 'w') as f:
        for line in new_html:
            f.write(line)
    print("index accessed")
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
    resp = make_response(current_app.send_static_file('status.html'))
    if request.method == 'POST':
        print('here', file=sys.stderr)
        print(request.form.get('status'), file=sys.stderr)
        status = request.form.get('status')
        username = request.cookies.get('username')
        token = request.cookies.get('token')
        for t in tokenCollection.find({}):
            print(t)
            if t.get('username') == username:
                if bcrypt.checkpw(token.encode(), t.get('token')):
                    statusCollection.insert_one({'username': username, 'status': status})
                    resp.set_cookie('status', status)
    return resp

@app.route("/image-upload", methods=["POST"])
def upload_image():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    imagesCollection.insert_one({"file": filename})
    print("initiating redirect")
    return redirect("http://localhost:5000/")





# @app.route('/', methods=['POST'])
# def upload_image():
#     if 'file' not in request.files:
#         flash('No file part')
#         return redirect(request.url)
#     file = request.files['file']
#     if file.filename == '':
#         flash('No image selected for uploading')
#         return redirect(request.url)
#     if file:
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         imagesCollection.insert_one({"file": filename})
#         return render_template('index.html', filename=filename)
#     else:
#         return redirect(request.url)
#
# @app.route('/display/<filename>')
# def display_image(filename):
#     return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == '__main__':
    socketio.run(app)
