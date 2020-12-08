from flask import Flask, request, render_template, redirect, url_for, make_response, abort, send_file
from range import rangeResponse
from route import routeResponse, getFleet
app = Flask(__name__)

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
    print(request.data)
    return rangeResponse(request.data)
    
@app.route('/route.html')
def route():
    return render_template('route.html')

@app.route('/route', methods=['POST'])
def routeInput():
    print(request.data)
    return routeResponse(request.data)

@app.route('/fleet', methods=['POST'])
def fleet():
    print("Fleet Request")
    return getFleet()

if __name__ == "__main__":
    app.run()
