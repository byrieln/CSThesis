from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from flask import make_response
from flask import abort
from flask import send_file

app = Flask(__name__)

import mysql.connector
from getpass import getpass

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html')
def alt_home():
    return render_template('index.html')

@app.route('/navbar.html')
def navbar():
    return render_template('navbar.html')

@app.route('/range.html')
def range():
    return render_template('range.html')


@app.route('/favicon.ico')
def icon():
    return send_file('favicon.ico')

@app.route('/range', methods=['POST'])
def rangeInput():
    print("range")
    print(request.data)
    return "hi";

if __name__ == "__main__":
    app.run()
