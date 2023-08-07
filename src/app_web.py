##
## Notes:
## - Command to run: python3 -m flask --app app_web.py run --debug
## 

from flask import Flask, url_for, render_template

app = Flask(__name__)

@app.route("/test")
def hello_world():
    return "<p>Hello world</p>"

@app.route("/")
def application():
    return render_template('index.html')