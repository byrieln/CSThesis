from flask import Flask
app = FLASK(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'
