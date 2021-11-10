from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return '<a href="/login" >Login</a>'

@app.route('/login')
def login():
    return """<form action="/action_page.php">
  <label for="fname">First name:</label>
  <input type="text" id="fname" name="fname"><br><br>
  <label for="lname">Last name:</label>
  <input type="text" id="lname" name="lname"><br><br>
  <input type="submit" value="Submit">
</form>"""


if __name__ == '__main__':
    app.run()
